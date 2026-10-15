---
name: xcode-build
description: Use before building, previewing, running, testing, or checking an Apple-platform project for build errors, and whenever you would otherwise run xcodebuild by hand. Covers the `xc` tool (`xc preview`, `xc build`, `xc test`, `xc provision`, `xc logs`), its options, output, exit codes, and build logs.
---

# Previewing, building and testing with `xc`

`xc` wraps XcodeGen and xcodebuild. It lives in this plugin's `bin/` folder; the session-start context gives its absolute path, and it is normally on `PATH` as `xc`. Run it from anywhere inside the project, or pass `-C <path>`.

When the project has a `Project.json` (or `project.yml`), every `xc` command regenerates the `.xcodeproj` from it first, so never edit the generated `.xcodeproj` by hand in those projects.

**Whenever you finish changes that affect the app, run `xc preview -platform <platform> ...`**, naming every platform your changes affect. It builds for a simulator, installs, and relaunches the app so the user sees the new version. Nothing rebuilds automatically when you change code, so without it the user sees the old app.

Use the other commands only when you have a reason:

- **`xc build [-platform <p> ...]`** builds without launching, to check that the code compiles. Defaults to iOS.
- **`xc test [-scheme <name>] [-only-testing:<test>]`** runs tests in an iPhone simulator, or on the Mac with `-platform macOS`. `xc list` names the schemes.
- **`xc provision [-platform <p>]`** builds for a real device with `-allowProvisioningUpdates` so Xcode registers the App ID and capabilities. See the capability-provisioning skill.
- **`xc logs -platform iOS`** streams the running app's unified log from the simulator (stop it with a timeout).
- **`xc sims [<platform>]`** lists simulators; pass one with `-device "<name>"` or `-device <udid>` to preview or test on it.

Rules:

- Builds and test runs can take several minutes. Run them as a background task if you can; otherwise use a long timeout (10 minutes).
- A failing build (compile or link errors) is not a reason to switch to raw xcodebuild. Fix the errors and run `xc` again.
- For detail beyond the printed errors, `tail` or `grep` the log whose path `xc` prints first.
- If the sandbox blocks a command, rerun it outside the sandbox.
- `xc preview` launches with `simctl`, not Xcode, so a scheme's StoreKit configuration file is *not* applied. Tell the user to run from Xcode when they need local StoreKit testing.
- Run on a physical device or install a Mac app into /Applications only when the user explicitly asks; there's no `xc` command for that, so use Xcode or `xcodebuild` with a device destination.

## Xcode's MCP tools

When the `xcode-integration` plugin is connected and Xcode has the project open, its tools complement `xc`:

- **Use `xc`** for routine builds and previews: it needs no Xcode window, regenerates from Project.json, and its logs and errors are easy to grep.
- **Use Xcode's tools** for what `xc` can't do: `DeviceInteraction*` to see and drive the running app (see the simulator-use skill), `GetConsoleOutput` for the app's logs, `InvokeDebuggerCommand` for lldb, `RunSomeTests` / `GetTestList` for structured test results, `XcodeRefreshCodeIssuesInFile` for a file's live diagnostics, `RunCodeSnippet` to try code in a file's context, `GetTopCrashIssues` / `GetCrashIssueLogs` for crashes from the field, `DocumentationSearch` for Apple's current documentation, and `LocalizationPlanner` / `StringCatalog*` with the `xcode-integration:translation` skill.
- `RenderPreview` needs a `#Preview` in the file. These guidelines say not to add previews, so use it only when the project already has them or the user asks.
- In a **Project.json project**, don't use the tools that change the Xcode project itself: `AddEntitlement`, `AddInfoPlist`, `UpdateTargetBuildSetting`, `UpdateFileCompilerFlags`, `XcodeNewTarget`, and `XcodeWrite` / `XcodeMV` / `XcodeRM` / `XcodeMakeDir` for project membership. The next `xc gen` overwrites their changes. Edit Project.json and the files on disk instead, then `xc gen`; Xcode reloads the regenerated project.

## Output

`xc` writes progress, errors and the log path to stderr. The last stdout line is one of `** BUILD SUCCEEDED **`, `** BUILD FAILED **`, `** TEST SUCCEEDED **`, `** TEST FAILED **`, `** PROVISIONING SUCCEEDED **` or `** PROVISIONING FAILED **`.

- `build` prints `app: <path>` for each built platform.
- `preview` prints `launched: <bundle id> on <device> (<udid>)`, or the Mac app it opened.
- `test` prints `resultBundle: <path>.xcresult`. On failure it also prints the failing test lines; for more, use `xcrun xcresulttool get test-results tests --path <bundle>`.
- On failure, the errors are deduplicated `file:line: error:` lines. When the log has no error lines, its last 25 lines are printed instead.

Logs and DerivedData live in `~/Library/Developer/Xcode/DerivedData/xc-<project>-<hash>/`; `xc` keeps the 20 most recent logs.

Exit status: 0 success, 65 build or tests failed, 64 usage error, 70 internal error (no simulator, no project, install or launch failed).

## `xc help`

```
usage: xc preview -platform <name> [-platform <name> ...] [-scheme <name>] [-device <name|udid>]
                  [-configuration Debug|Release] [-verbose]
       xc build   [-platform <name> ...] [-scheme <name>] [-configuration Debug|Release] [-verbose]
       xc test    [-scheme <name>] [-platform <name>] [-device <name|udid>] [-testPlan <name>]
                  [-only-testing:<test> ...] [-skip-testing:<test> ...] [-verbose]
       xc provision [-platform <name> ...] [-scheme <name>]
       xc gen | xc list [-json] | xc sims [<platform>] | xc logs [<platform>]

  -platform   iOS (default), macOS, watchOS, tvOS or visionOS. Simulator builds for all but macOS.
  -scheme     Defaults to the first application target's scheme.
  -device     Simulator name ("iPhone 17 Pro") or UDID. Defaults to the booted simulator of
              that platform, else the newest matching device, which xc boots.
  -C <path>   Project folder (default: walk up from the current directory).
```

## Without `xc`

If `xc` is unavailable, the equivalent is:

```bash
xcodegen generate --spec Project.json --use-cache        # only when Project.json exists
xcodebuild -project Project.xcodeproj -scheme <App> -destination 'id=<sim udid>' -derivedDataPath <dir> build
xcrun simctl install <udid> <dir>/Build/Products/Debug-iphonesimulator/<App>.app
xcrun simctl launch --terminate-running-process <udid> <bundle id>
```
