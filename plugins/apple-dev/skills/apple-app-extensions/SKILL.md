---
name: apple-app-extensions
description: Use when adding or modifying a Widget, Control Center control, Live Activity, WidgetKit extension, complication, or App Group shared between an app and its extensions.
---

# Apple App Extensions

### Widget Extensions

A widget extension is used to define Widgets, Controls, and Live Activities. It's a separate `app-extension` target bundled inside a host app target. Set the extension target's `platform` (or `supportedDestinations`) to match the platforms the host app supports.

- Put widget extension sources in a top-level `Widget Extension/` directory (parallel to `App/`), not inside `App/`.
- Name the widget extension target `<AppTargetName> Widget Extension` (e.g. `Hello World Widget Extension` when the app is `Hello World`).
- Add a widget extension target to `Project.json` with:
  - `"type": "app-extension"`
  - `"platform"` (or `"supportedDestinations"`) matching the host app's platforms (e.g. `"iOS"`, or `["iOS", "macOS"]`)
  - `"sources": [{"path": "Widget Extension"}]`
  - `"info"` with `"path": "Widget Extension/Info.plist"` and `properties` containing both `CFBundleDisplayName` (the human-readable name, e.g. `"Hello World Widget Extension"`) and `NSExtension.NSExtensionPointIdentifier = "com.apple.widgetkit-extension"`. The Info.plist file is generated from `properties` — do not write `Widget Extension/Info.plist` to disk yourself.
  - `PRODUCT_BUNDLE_IDENTIFIER` set to the host app's bundle id with `.widget-extension` appended (e.g. `com.example.myapp.widget-extension`)
  - Do not set `ASSETCATALOG_COMPILER_APPICON_NAME` or `ASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME` on the widget extension target — it has no asset catalog of its own.
- Embed the widget extension in the host app target by adding it as a dependency with `embed: true`:
  ```json
  "dependencies": [{"embed": true, "target": "Hello World Widget Extension"}]
  ```
- If the host app supports more platforms than the widget target, scope the dependency with XcodeGen's `destinationFilters` key so the extension is only embedded for platforms it supports. For example, an iOS-only widget in an iOS+macOS host app must use:
  ```json
  "dependencies": [{"embed": true, "target": "Hello World Widget", "destinationFilters": ["iOS"]}]
  ```
  Use `destinationFilters`, not `platformFilters`; `platformFilters` is a generated `.pbxproj` field and is ignored in `Project.json`.
- On macOS, both the host app and the widget extension must declare App Sandbox in their entitlements. Add an `entitlements` block to each target with `"com.apple.security.app-sandbox": true`, using the same shape as the App Groups example below (per-target paths like `App/App.entitlements` and `Widget Extension/Widget Extension.entitlements`). If a target also uses App Groups, combine both keys into the same `entitlements` block. iOS, iPadOS, and watchOS widgets do not need this.
- You must add @main to a `WidgetBundle`-conforming type. Return any Widgets, Controls, or Live Activities you define from its body.

For watchOS, follow the same shape as above with these differences:

- Set the extension target's `"platform"` to `"watchOS"`, and set its `deploymentTarget` to watchOS 9 or later.
- The extension's `PRODUCT_BUNDLE_IDENTIFIER` must be nested under the **watch** app's bundle id (e.g. `<watch-app-bundle-id>.widget-extension`), and the widget target must be embedded in the watch app target, not the iPhone target.

#### Widgets

- A widget's view must set a container background with `.containerBackground(_:for:.widget)` — widgets without one will be rejected at render time on modern iOS.
- On a `WidgetConfiguration` (e.g. the one returned from `StaticConfiguration` / `IntentConfiguration`), the modifiers to set the name and description are `.configurationDisplayName(_:)` and `.description(_:)`.
- On watchOS restrict the accessory families with `.supportedFamilies([.accessoryCircular, .accessoryRectangular, .accessoryInline, .accessoryCorner])`. `.accessoryCorner` is watchOS-only; the other three also work on the iOS Lock Screen.
- Decide the widget's update path from how its data changes, before writing the provider:
    - Data only this device changes (the app's own state, settings, date-derived values): call `WidgetCenter.shared.reloadAllTimelines()` from the app after every change. No push needed.
    - Data that can change while the app is closed — another user, a server, anything this device doesn't originate: `reloadAllTimelines()` cannot keep the widget current, because nothing is running to call it. Refresh it by push through a `WidgetPushHandler` and the extension's own `aps-environment` entitlement (iOS 26+, watchOS 26+) — load the notifications skill for the setup and the send. A widget over data like this isn't finished until a push can refresh it, so build that with the widget rather than leaving it for later.
- Check what the app already has before building a push path for the widget. If it already pushes about this same data, there is a device-token table, an auth key, and a sender in place: add widget tokens to them rather than standing up a parallel path. Working app pushes also settle the membership question below — a free team could not have sent them.
- A WidgetKit push carries no data; it only triggers a timeline reload. A push-refreshed widget must therefore fetch fresh data itself in `getTimeline`, falling back to the last stored snapshot when offline or signed out. That usually means the extension needs the app's credentials or session — see the backend's skill for how to share one. A snapshot that only the app writes stays stale no matter how many pushes arrive.
- Push of any kind requires a paid Apple Developer Program membership (see the notifications skill), and a free team has no substitute for it — `simctl push` delivers application push types only, so it cannot stand in for a widget push even in the simulator. A free team's widget can therefore only update while the app runs. Ship it anyway, and say plainly in your summary that it updates when they open the app plus on the timeline schedule. Only a free team earns that summary: never present an App Group snapshot as staying current on its own, and never describe a widget that way when push was available and you skipped it.
- After adding a widget, tell the user how to install it manually, and say when it updates:
    - On iOS/iPadOS: long-press the home screen, tap **Edit**, choose **Add Widget**, then search for the app name.
    - On macOS: control-click the desktop, choose **Edit Widgets…**, then search for the app name.
    - On watchOS: press and hold the watch face, tap **Edit**, swipe to the **Complications** screen, tap a slot, and pick the app's complication from the list.

#### Controls

- Implement a control as a `ControlWidget` and expose it from the bundle. Use `StaticControlConfiguration` for controls with no configuration, and give every control a globally unique `kind` string (reuse the app's bundle-id prefix and append a control-specific suffix). Always apply `.displayName(_:)` and `.description(_:)` so the control shows up properly in the Control Center gallery:
- Controls are only supported on iOS 18+, iPadOS 18+, macOS 26+, and watchOS 26+. Make sure `deploymentTarget` has appropriate values on both the host and the extension.
- Actions are `AppIntent`s. To make tapping the control open the host app, set `static var openAppWhenRun = true` on the intent and return `.result()` from `perform()`.
- After adding a control, tell the user how to install it: long-press Control Center to enter edit mode, tap **Add a Control** at the bottom, then search for the app name

#### Live Activities

- Implement a Live Activity by making a `Widget` whose body is an `ActivityConfiguration` in the same widget extension.
- Live Activities run on iOS 16.1+ and iPadOS 17+, so keep the extension target's `platform` as `"iOS"`. When the host device is paired with an Apple Watch running watchOS 11+ or a Mac running macOS 26+, the system automatically mirrors the activity to the Smart Stack / menu bar — you don't build a separate watchOS or macOS target for that.
- If the host app also supports macOS, embed the Live Activity dependency with `"destinationFilters": ["iOS"]`.
- Use a top-level `Shared/` directory (parallel to `App/`) for the `ActivityAttributes` definition. Include `Shared/` in the `sources` of *both* the app target and the extension target so the attributes type is in-scope on both sides — don't use `#if` fences or try to link across targets.
- On the **host app** target's Info.plist, add `"NSSupportsLiveActivities": true`. If the activity's state changes more than a few times per hour, also add `"NSSupportsLiveActivitiesFrequentUpdates": true`.
- Set `deploymentTarget` to `"17.0"` or higher on both the host and the extension. (ActivityKit itself is iOS 16.1+, but anything using `@Observable` needs 17.0, so default to 17.0.)
- When telling the user how to see the activity, mention that Live Activities appear on the Lock Screen on any supported iPhone or iPad, including in the Simulator. Only mention the device type(s) that the project actually supports.

Building the activity itself:

- `ActivityConfiguration` takes two closures, and both are required: the Lock Screen / banner view, and a `dynamicIsland:` closure returning a `DynamicIsland` with all four regions — an expanded set of `DynamicIslandExpandedRegion`s plus `compactLeading:`, `compactTrailing:`, and `minimal:`. Design the compact and minimal states as a glanceable value, not a shrunken version of the full layout.
- Apply `.supplementalActivityFamilies([.small, .medium])` to the configuration and branch on the `\.activityFamily` environment value in the view. Without it, Apple Watch and CarPlay render the *compact* presentation, and StandBy stretches the Lock Screen presentation to fill the screen — both usually the wrong shape for those surfaces. `.small` opts into a custom Watch and CarPlay layout, `.medium` into a custom StandBy one.
- Set the Lock Screen background with `.activityBackgroundTint(_:)`, and pair it with `.activitySystemActionForegroundColor(_:)`, which colors the text of the auxiliary button people use to end the activity. There is no `.containerBackground` placement for a Live Activity, so the widget rule about container backgrounds does not apply here. The Dynamic Island's background is always black and can't be changed; tint its border with `.keylineTint(_:)` instead.
- Deep-link with `.widgetURL(_:)`, which sets the default destination for the Lock Screen, compact, and minimal presentations — those are tap targets as a whole, so they can't hold individual links. Only the expanded Dynamic Island can host a `Link`, and a `Link` takes priority over the widget URL. Handle the URL with `onOpenURL`.

Managing the activity's lifecycle:

- Gate any "start" UI on `ActivityAuthorizationInfo().areActivitiesEnabled`, and follow `activityEnablementUpdates` to react when the user changes it in Settings. Requesting an activity can also fail because the device is at its limit, so always handle the throw with UI rather than swallowing it.
- Nothing ends an activity for you. Call `await activity.end(_:dismissalPolicy:)` with the final content when the underlying event finishes — `.default` keeps it on the Lock Screen for up to four hours after it ends, `.immediate` removes it at once, `.after(_:)` picks a time. An activity you never end runs for up to eight hours before the system ends it, then lingers on the Lock Screen for up to four more, and occupies one of the device's activity slots the whole time.
- Attributes and `ContentState` together cannot exceed 4 KB, and that budget covers push payloads too. Keep `ContentState` to the few values that actually change, put everything fixed in the attributes where it's set once at request time, and keep both `Codable` with plain default encoding — the state crosses process and network boundaries, and a push has to reproduce it exactly.
- A Live Activity can be started, updated, and ended remotely, which is what makes it useful for server-driven events like deliveries and games. That needs ActivityKit push tokens, which are a different mechanism from both app pushes and widget pushes — see the notifications skill.

### App Groups

An App Group lets the host app and its extensions (widgets, controls, live activities) share a `UserDefaults` suite, files, and SwiftData stores. Only add one when the extension genuinely needs data that the host writes at runtime — for read-only content, timeline-provider data, bundled resources, and date-derived values are a better fit and need no setup.

Project setup (what you do whenever adding an App Group):

- Pick an App Group identifier of the form `group.<host-bundle-id>`, using the current `PRODUCT_BUNDLE_IDENTIFIER` from `Project.json`. App Group identifiers are globally owned, so always derive new ones from the current app's generated bundle id. Use the exact same string in `Project.json` entitlements and Swift code. If the app is headed for TestFlight or the App Store and the bundle id is still a placeholder (such as Bitrig's `app.bitrig.new.<uuid>`), settle the permanent bundle ID first (see the xcodegen-project skill) so the group derives from the real bundle ID.
- Store the identifier as a Swift constant in a file under a top-level `Shared/` directory, and add `{"path": "Shared"}` to the `sources` of every target that uses the group (host + each extension). Don't duplicate the string across targets.
  ```swift
  enum AppGroup {
    static let id = "group.com.example.myapp"
  }
  ```
- In `Project.json`, add an `entitlements` block to every target that uses the group. The shape is a `path` (where the `.entitlements` file is generated) and a `properties` dict:
  ```json
  "entitlements": {
    "path": "App/App.entitlements",
    "properties": {
      "com.apple.security.application-groups": ["group.com.example.myapp"]
    }
  }
  ```
  Use a per-target path for each extension (e.g. `Widget Extension/Widget Extension.entitlements`).
- In Swift, read and write through the shared suite, not `UserDefaults.standard`:
  ```swift
  let defaults = UserDefaults(suiteName: AppGroup.id)
  ```
- For SwiftData stores or files that both sides need to see, put them inside the group's container:
  ```swift
  let url = FileManager.default
    .containerURL(forSecurityApplicationGroupIdentifier: AppGroup.id)!
    .appending(path: "Store.sqlite")
  let config = ModelConfiguration(url: url)
  ```

When you first add an App Group, simply tell the user which features now share data.
