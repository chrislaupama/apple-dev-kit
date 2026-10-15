---
name: simulator-use
description: Observe or operate the running app in the Simulator or on a device — inspecting UI, testing behavior, tapping, typing, taking screenshots, changing appearance or settings, sending pushes or deep links, and reading run logs. Use only when a request requires the running app; not for code-only changes or explanations.
---

# Simulator Use

Prefer purpose-built connectors, APIs, or CLIs when they can do the job. Use the simulator for what only the running app shows.

The simulator runs whatever build was last installed. Run `xc preview -platform <p>` (see the xcode-build skill) after code changes so it shows your latest code. `xc sims` lists simulators and their UDIDs; `booted` works in place of a UDID when one simulator is booted.

## Tools, in order of preference

1. **Xcode's device interaction** (the `xcode-integration` plugin's MCP tools, `mcp__…xcode__DeviceInteraction*`). It reads the app's UI hierarchy with exact tap points, synthesizes taps, swipes and typing, and works on the Simulator *and* on a real device. This is the closest match to Bitrig's simulator tool. Follow the `xcode-integration:device-interaction` skill: it runs as a subagent. In short:
   - Xcode must be running with the project open. For a Project.json project, run `xc gen` first, then open the generated `.xcodeproj` with `XcodeOpenWorkspace`. `XcodeListWorkspaces` shows what's open.
   - Pick the device with `XcodeListRunDestinations` / `XcodeSwitchRunDestination` (or the device identifier on session start), and the scheme with `XcodeSwitchScheme`.
   - `DeviceInteractionStartWorkspaceSession` early (it boots in the background) → `DeviceInteractionInstallAndRun` after each code change (it builds) → `DeviceInteractionSynthesize` to act and observe → `DeviceInteractionEndSession` when done, since open sessions are resource-heavy.
   - Tap the hierarchy's `hitPoint` coordinates rather than guessing from screenshots. `GetConsoleOutput` reads the app's stdout/stderr/OSLog for the run.
   - `InstallAndRun` launches the Xcode way, so a scheme's StoreKit configuration applies (unlike `xc preview`).
2. **The host's simulator tool**, when the session has one (for example a `…iOS_Simulator__control` tool in the Claude desktop app) and Xcode isn't available. It taps, swipes, types, presses hardware buttons, opens URLs and takes screenshots by device-point coordinates. Screenshot first, act, then screenshot again to confirm before the next step.
3. **`xcrun simctl`** for everything that isn't touch input (below). It works without Xcode open.
4. **XCUITest**, through `xc test -only-testing:<UITestTarget>/<Test>`, for repeatable scripted interaction.

There is no touch input in `simctl`. Don't try to fake taps with AppleScript; use one of the tools above, or ask the user to do the step.

## `simctl` recipes

```bash
xcrun simctl io booted screenshot /path/shot.png             # screenshot (PNG at native pixels)
xcrun simctl io booted recordVideo /path/clip.mov            # stop with Ctrl-C / kill
xcrun simctl ui booted appearance dark                       # light | dark
xcrun simctl ui booted content_size extra-extra-large        # Dynamic Type
xcrun simctl ui booted increase_contrast enabled
xcrun simctl status_bar booted override --time 9:41 --batteryState charged --batteryLevel 100 --cellularBars 4 --wifiBars 3
xcrun simctl status_bar booted clear
xcrun simctl openurl booted 'myapp://route?id=1'             # deep links / universal links
xcrun simctl push booted <bundle-id> payload.apns            # JSON with a top-level "aps" dictionary
xcrun simctl privacy booted grant location <bundle-id>       # also: photos, contacts, calendar, microphone, camera…
xcrun simctl location booted set 37.3349,-122.0090
xcrun simctl launch --terminate-running-process booted <bundle-id>
xcrun simctl terminate booted <bundle-id>
xcrun simctl get_app_container booted <bundle-id> data       # app's sandbox, to inspect files/UserDefaults
xcrun simctl spawn booted log stream --level debug --style compact --predicate 'process == "<App>"'
xcrun simctl erase <udid>                                    # factory reset (only when the user agrees)
```

`xc logs -platform iOS` streams the app's log for you. Always bound log streaming with a timeout or run it in the background.

## Screenshots for the App Store

Use the right device so captures come out at an accepted size: the newest Pro Max iPhone for the 6.9" group, a 13-inch iPad Pro for iPad, the newest Apple Watch Ultra, Apple TV 4K. Apply the status bar override above first. Check sizes with `sips -g pixelWidth -g pixelHeight <file>` and never resize a capture to make it fit; recapture on the right device.

## Accessibility

Good accessibility labels are also what makes UI testable: Xcode's UI hierarchy and XCUITest both identify elements by label and identifier. Add `.accessibilityIdentifier` to elements you need to drive repeatedly.

## iPhone Duo

When the installed Simulator has an iPhone Duo device (iOS 27.1 runtime), use the Simulator app's fold and rotate controls to reach each pose; see the iphone-duo skill. `simctl` has no hinge control.
