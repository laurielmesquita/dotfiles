#!/usr/bin/env python3
"""Back up and merge the curated configuration; mutations require --apply."""
import argparse
import datetime
import json
import os
from pathlib import Path
import plistlib
import re
import shutil
import subprocess
import sys
import tempfile
from xml.sax.saxutils import escape

REPO = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((REPO / "manifest.json").read_text())
LABEL = "local.waveterm.codex-system-theme"
AGENT = f"Library/LaunchAgents/{LABEL}.plist"
BINARY = ".config/waveterm/system-theme-sync/wave-theme-sync"
BEGIN = "# BEGIN DOTFILES OH MY ZSH"
END = "# END DOTFILES OH MY ZSH"


def jsonc(text):
    """Accept JSON comments/trailing commas without changing quoted values."""
    out, index, quoted, escaped = [], 0, False, False
    while index < len(text):
        char = text[index]
        if quoted:
            out.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
            out.append(char)
        elif text[index:index + 2] == "//":
            stop = text.find("\n", index)
            index = len(text) if stop < 0 else stop
            continue
        elif text[index:index + 2] == "/*":
            stop = text.find("*/", index + 2)
            if stop < 0:
                raise ValueError("Unterminated JSON comment")
            out.append(" ")
            index = stop + 2
            continue
        else:
            out.append(char)
        index += 1
    text = "".join(out)
    out, quoted, escaped = [], False, False
    for index, char in enumerate(text):
        if not quoted and char == "," and text[index + 1:].lstrip().startswith(("}", "]")):
            continue
        out.append(char)
        if escaped:
            escaped = False
        elif quoted and char == "\\":
            escaped = True
        elif char == '"':
            quoted = not quoted
    value = json.loads("".join(out))
    if not isinstance(value, dict):
        raise ValueError("Configuration must be a JSON object")
    return value


def encode(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()


def merge(existing, wanted):
    result = dict(existing)
    for key, value in wanted.items():
        result[key] = merge(result[key], value) if isinstance(result.get(key), dict) and isinstance(value, dict) else value
    return result


def safe_path(home, relative):
    relative = Path(relative)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Unsafe relative path: {relative}")
    path = home / relative
    for current in [path, *path.parents]:
        if current == home:
            break
        if current.is_symlink():
            raise ValueError(f"Refusing to replace a symlink: {current}")
    return path


def atomic_write(path, data, mode=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = mode if mode is not None else ((path.stat().st_mode & 0o777) if path.exists() else 0o600)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def targets():
    return [entry["target"] for entry in MANIFEST["settings"] + MANIFEST["files"]] + [".zshrc", AGENT, BINARY]


def backup(home, paths=None):
    parent = home / ".local/state/dotfiles/backups"
    parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ-")
    destination = Path(tempfile.mkdtemp(prefix=stamp, dir=parent))
    entries = {}
    for relative in paths if paths is not None else targets():
        source = safe_path(home, relative)
        if source.exists() and not source.is_file():
            raise ValueError(f"Expected file: {source}")
        entries[relative] = {"existed": source.exists()}
        if source.exists():
            entries[relative]["mode"] = source.stat().st_mode & 0o777
            atomic_write(destination / relative, source.read_bytes(), 0o600)
    atomic_write(destination / "snapshot.json", encode({"schema_version": 1, "files": entries}), 0o600)
    return destination


def zsh_config(text):
    block = f'{BEGIN}\nsource "$HOME/.config/dotfiles/zsh.zsh"\n{END}\n'
    if BEGIN in text or END in text:
        pattern = re.escape(BEGIN) + r"\n.*?" + re.escape(END) + r"\n?"
        text, count = re.subn(pattern, "", text, flags=re.S)
        if count != 1 or BEGIN in text or END in text:
            raise ValueError("Ambiguous managed Zsh block")
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        if re.match(r"\s*(source|\.)\s+", line) and "oh-my-zsh.sh" in line:
            lines.insert(index, block)
            return "".join(lines)
    if text.strip():
        raise ValueError("No recognizable Oh My Zsh source line; existing .zshrc was preserved")
    return 'export ZSH="$HOME/.oh-my-zsh"\n' + block + 'source "$ZSH/oh-my-zsh.sh"\n'


def plan(home):
    result = {}
    for entry in MANIFEST["settings"] + MANIFEST["files"]:
        source = REPO / entry["source"]
        target = safe_path(home, entry["target"])
        data = source.read_bytes()
        if entry in MANIFEST["settings"] or entry.get("merge"):
            existing = jsonc(target.read_text()) if target.exists() else {}
            data = encode(merge(existing, jsonc(data.decode())))
        result[entry["target"]] = data
    zsh = safe_path(home, ".zshrc")
    result[".zshrc"] = zsh_config(zsh.read_text() if zsh.exists() else "").encode()
    template = (REPO / "macos/wave-theme-sync/LaunchAgent.plist.in").read_text()
    agent = template.replace("__HOME__", escape(str(home)))
    plistlib.loads(agent.encode())
    result[AGENT] = agent.encode()
    return result


def set_service(home, start):
    target = f"gui/{os.getuid()}"
    subprocess.run(["/bin/launchctl", "bootout", f"{target}/{LABEL}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if start and (home / AGENT).exists() and (home / BINARY).exists():
        subprocess.run(["/bin/launchctl", "bootstrap", target, str(home / AGENT)], check=True)


def install(home, apply=False, enable_sync=False):
    changes = plan(home)  # Validate every destination before writing anything.
    for relative, data in changes.items():
        path = safe_path(home, relative)
        print(("UNCHANGED " if path.exists() and path.read_bytes() == data else "UPDATE    ") + str(path))
    if enable_sync and home != Path.home().resolve():
        raise ValueError("Service activation is allowed only for the real user HOME")
    if not apply:
        print("Preview only. Use --apply to write; --enable-sync also compiles and loads the Wave helper.")
        return None
    with tempfile.TemporaryDirectory(prefix="dotfiles-build-") as temporary:
        if enable_sync:
            binary = Path(temporary) / "wave-theme-sync"
            subprocess.run(["/usr/bin/swiftc", "-O", str(REPO / "macos/wave-theme-sync/main.swift"), "-o", str(binary)], check=True)
            subprocess.run([str(binary), "--self-test"], check=True)
            changes[BINARY] = binary.read_bytes()
        snapshot = backup(home, changes)
        if enable_sync:
            set_service(home, False)
        try:
            for relative, data in changes.items():
                atomic_write(safe_path(home, relative), data, 0o755 if relative == BINARY else None)
            if enable_sync:
                set_service(home, True)
        except Exception:
            print(f"Installation stopped. Original files are preserved in {snapshot}", file=sys.stderr)
            raise
    print(f"BACKUP {snapshot}")
    return snapshot


def restore(home, snapshot, apply=False, enable_sync=False):
    if enable_sync and home != Path.home().resolve():
        raise ValueError("Service activation is allowed only for the real user HOME")
    record = json.loads((snapshot / "snapshot.json").read_text())
    if record.get("schema_version") != 1 or not set(record["files"]).issubset(set(targets())):
        raise ValueError("Unrecognized backup manifest")
    changes = {}
    for relative, entry in record["files"].items():
        safe_path(home, relative)
        changes[relative] = safe_path(snapshot, relative).read_bytes() if entry["existed"] else None
        print(("RESTORE " if entry["existed"] else "REMOVE  ") + str(home / relative))
    if not apply:
        print("Preview only. Use --apply to restore.")
        return None
    undo = backup(home, changes)
    if enable_sync:
        set_service(home, False)
    for relative, data in changes.items():
        path = safe_path(home, relative)
        if data is None:
            if path.exists():
                path.unlink()
        else:
            atomic_write(path, data, record["files"][relative]["mode"])
    if enable_sync:
        set_service(home, True)
    print(f"UNDO BACKUP {undo}")
    return undo


def capture(home, apply=False):
    for entry in MANIFEST["settings"]:
        current = jsonc(safe_path(home, entry["target"]).read_text())
        selected = {key: current[key] for key in entry["keys"] if key in current}
        for key, allowed in entry.get("nested_keys", {}).items():
            if key in selected:
                selected[key] = {name: value for name, value in selected[key].items() if name in allowed}
        print(f"CAPTURE {entry['source']} (appearance allowlist)")
        if apply:
            atomic_write(REPO / entry["source"], encode(selected))
    print("Themes, Swift and Zsh are maintained in the repository; capture only exports the listed appearance preferences.")


def check():
    for entry in MANIFEST["settings"] + MANIFEST["files"]:
        source = REPO / entry["source"]
        if source.suffix == ".json":
            jsonc(source.read_text())
    wave = json.loads((REPO / "wave/termthemes.json").read_text())
    zed = json.loads((REPO / "zed/themes/codex.json").read_text())
    for theme in zed["themes"]:
        colors = wave["codex-" + theme["appearance"]]
        for color in ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]:
            assert theme["style"]["terminal.ansi." + color] == colors[color]
            assert theme["style"]["terminal.ansi.bright_" + color] == colors["bright" + color.title()]
    subprocess.run(["/bin/zsh", "-n", str(REPO / "zsh/prompt.zsh")], check=True)
    plistlib.loads((REPO / "macos/wave-theme-sync/LaunchAgent.plist.in").read_bytes())
    print("OK: configuration JSON, light/dark ANSI correspondence, Zsh syntax and LaunchAgent template.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check", "backup", "install", "restore", "capture"])
    parser.add_argument("--home", type=Path, default=Path.home(), help="Target HOME; use a temporary directory for testing")
    parser.add_argument("--snapshot", type=Path, help="Backup directory for restore")
    parser.add_argument("--apply", action="store_true", help="Actually write files (default: preview)")
    parser.add_argument("--enable-sync", action="store_true", help="Compile/activate the Wave LaunchAgent; real HOME only")
    args = parser.parse_args()
    home = args.home.expanduser().resolve()
    if args.command == "check":
        check()
    elif args.command == "backup":
        print(backup(home))
    elif args.command == "install":
        install(home, args.apply, args.enable_sync)
    elif args.command == "capture":
        capture(home, args.apply)
    else:
        if args.snapshot is None:
            parser.error("restore requires --snapshot")
        restore(home, args.snapshot.expanduser().resolve(), args.apply, args.enable_sync)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
