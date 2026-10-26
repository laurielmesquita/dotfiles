import Foundation

enum SyncError: Error { case invalidSettings }

func updateTheme(at url: URL, appearance: String) throws -> Bool {
    let data = try Data(contentsOf: url)
    guard var settings = try JSONSerialization.jsonObject(with: data) as? [String: Any] else {
        throw SyncError.invalidSettings
    }
    let theme = appearance == "dark" ? "codex-dark" : "codex-light"
    if settings["term:theme"] as? String == theme { return false }
    settings["term:theme"] = theme
    var output = try JSONSerialization.data(withJSONObject: settings, options: [.prettyPrinted, .sortedKeys, .withoutEscapingSlashes])
    output.append(10)
    let attributes = try FileManager.default.attributesOfItem(atPath: url.path)
    try output.write(to: url, options: .atomic)
    if let permissions = attributes[.posixPermissions] {
        try FileManager.default.setAttributes([.posixPermissions: permissions], ofItemAtPath: url.path)
    }
    return true
}

func systemAppearance() throws -> String {
    let process = Process()
    let output = Pipe()
    process.executableURL = URL(fileURLWithPath: "/usr/bin/defaults")
    process.arguments = ["read", "-g", "AppleInterfaceStyle"]
    process.standardOutput = output
    process.standardError = FileHandle.nullDevice
    try process.run()
    let data = output.fileHandleForReading.readDataToEndOfFile()
    process.waitUntilExit()
    return String(data: data, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() == "dark" ? "dark" : "light"
}

let arguments = CommandLine.arguments
if arguments.contains("--self-test") {
    let directory = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
    try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
    defer { try? FileManager.default.removeItem(at: directory) }
    let fixture = directory.appendingPathComponent("settings.json")
    try Data("{\"term:fontfamily\":\"Fira Code\",\"term:fontsize\":14,\"term:disablewebgl\":true}".utf8).write(to: fixture)
    for appearance in ["light", "dark"] {
        let changed = try updateTheme(at: fixture, appearance: appearance)
        let value = try JSONSerialization.jsonObject(with: Data(contentsOf: fixture)) as! [String: Any]
        precondition(changed && value["term:theme"] as? String == "codex-\(appearance)")
        precondition(value["term:fontfamily"] as? String == "Fira Code")
        precondition(value["term:disablewebgl"] as? Bool == true)
        let repeated = try updateTheme(at: fixture, appearance: appearance)
        precondition(!repeated)
    }
    try Data("invalid JSON".utf8).write(to: fixture)
    do {
        _ = try updateTheme(at: fixture, appearance: "light")
        fatalError("Invalid configuration must not be overwritten")
    } catch {}
    let invalidContents = try String(contentsOf: fixture, encoding: .utf8)
    precondition(invalidContents == "invalid JSON")
    print("Self-test passed: light, dark, preserved settings, no redundant writes, invalid JSON preserved.")
    exit(0)
}

let config = FileManager.default.homeDirectoryForCurrentUser.appendingPathComponent(".config/waveterm/settings.json")
func synchronize() {
    do {
        let appearance = try systemAppearance()
        if try updateTheme(at: config, appearance: appearance) {
            print("Wave terminal theme synchronized: codex-\(appearance)")
            fflush(stdout)
        }
    } catch {
        FileHandle.standardError.write(Data("Wave theme sync failed: \(error)\n".utf8))
    }
}

synchronize()
if arguments.contains("--once") { exit(0) }
let observer = DistributedNotificationCenter.default().addObserver(
    forName: Notification.Name("AppleInterfaceThemeChangedNotification"),
    object: nil,
    queue: .main
) { _ in
    DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) { synchronize() }
}
withExtendedLifetime(observer) { RunLoop.main.run() }
