import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("dotfiles", Path(__file__).parents[1] / "scripts/dotfiles.py")
dotfiles = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dotfiles)


class DotfilesTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.home = Path(self.directory.name)
        self.zsh = self.home / ".zshrc"
        self.original = 'export KEEP_ME="local-value"\nplugins=(git custom-plugin)\nsource "$ZSH/oh-my-zsh.sh"\n'
        self.zsh.write_text(self.original)
        self.zsh.chmod(0o640)
        settings = self.home / ".config/zed/settings.json"
        settings.parent.mkdir(parents=True)
        settings.write_text('// local settings\n{"terminal":{"env":{"KEEP":"yes"}},"custom":{"enabled":true},}\n')

    def quietly(self, callback, *args, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return callback(*args, **kwargs)

    def test_jsonc_preserves_quoted_comment_markers_and_trailing_comma_text(self):
        text = '{/* note */"url":"https://example.test/a/*b*/",// note\n"literal":",}","values":[1,2,],}'
        self.assertEqual(dotfiles.jsonc(text), {"url": "https://example.test/a/*b*/", "literal": ",}", "values": [1, 2]})

    def test_preview_does_not_write_to_home(self):
        before = {str(p.relative_to(self.home)): p.read_bytes() for p in self.home.rglob("*") if p.is_file()}
        self.quietly(dotfiles.install, self.home)
        after = {str(p.relative_to(self.home)): p.read_bytes() for p in self.home.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_install_merges_unknown_preferences_and_preserves_shell(self):
        self.quietly(dotfiles.install, self.home, apply=True)
        config = json.loads((self.home / ".config/zed/settings.json").read_text())
        self.assertTrue(config["custom"]["enabled"])
        self.assertEqual(config["terminal"]["env"], {"KEEP": "yes"})
        shell = self.zsh.read_text()
        self.assertIn('export KEEP_ME="local-value"', shell)
        self.assertIn("custom-plugin", shell)
        self.assertLess(shell.index(dotfiles.BEGIN), shell.index('source "$ZSH/oh-my-zsh.sh"'))
        self.assertEqual(self.zsh.stat().st_mode & 0o777, 0o640)

    def test_repeated_install_does_not_duplicate_managed_shell_block(self):
        self.quietly(dotfiles.install, self.home, apply=True)
        self.quietly(dotfiles.install, self.home, apply=True)
        self.assertEqual(self.zsh.read_text().count(dotfiles.BEGIN), 1)

    def test_restore_recovers_original_bytes_modes_and_missing_files(self):
        settings = self.home / ".config/zed/settings.json"
        original_json = settings.read_bytes()
        snapshot = self.quietly(dotfiles.install, self.home, apply=True)
        self.quietly(dotfiles.restore, self.home, snapshot, apply=True)
        self.assertEqual(self.zsh.read_text(), self.original)
        self.assertEqual(self.zsh.stat().st_mode & 0o777, 0o640)
        self.assertEqual(settings.read_bytes(), original_json)
        self.assertFalse((self.home / ".config/zed/themes/codex.json").exists())
        self.assertEqual((snapshot / "snapshot.json").stat().st_mode & 0o777, 0o600)

    def test_invalid_existing_config_aborts_before_any_write(self):
        settings = self.home / ".config/zed/settings.json"
        settings.write_text("invalid JSON")
        with self.assertRaises(ValueError):
            self.quietly(dotfiles.install, self.home, apply=True)
        self.assertEqual(self.zsh.read_text(), self.original)
        self.assertFalse((self.home / ".config/waveterm/settings.json").exists())

    def test_symlink_destination_is_rejected(self):
        other = self.home / "other"
        other.write_text("keep")
        target = self.home / ".config/waveterm/settings.json"
        target.parent.mkdir(parents=True)
        target.symlink_to(other)
        with self.assertRaises(ValueError):
            self.quietly(dotfiles.install, self.home, apply=True)
        self.assertEqual(other.read_text(), "keep")

    def test_restore_rejects_path_traversal(self):
        snapshot = self.home / "fake-backup"
        snapshot.mkdir()
        (snapshot / "snapshot.json").write_text(json.dumps({"schema_version": 1, "files": {"../outside": {"existed": False}}}))
        with self.assertRaises(ValueError):
            self.quietly(dotfiles.restore, self.home, snapshot, apply=True)

    def test_capture_does_not_export_credentials_or_terminal_environment(self):
        wave = self.home / ".config/waveterm/settings.json"
        wave.parent.mkdir(parents=True)
        wave.write_text(json.dumps({"term:fontfamily": "Fira Code", "ai:apitoken": "private-fixture"}))
        exported = self.home / "exported-repository"
        with patch.object(dotfiles, "REPO", exported):
            self.quietly(dotfiles.capture, self.home, apply=True)
        self.assertEqual(json.loads((exported / "wave/settings.json").read_text()), {"term:fontfamily": "Fira Code"})
        captured = json.loads((exported / "zed/settings.json").read_text())
        self.assertNotIn("env", captured["terminal"])
        self.assertNotIn("private-fixture", (exported / "wave/settings.json").read_text())


if __name__ == "__main__":
    unittest.main()
