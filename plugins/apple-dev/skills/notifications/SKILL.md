---
name: notifications
description: Use when an app shows or schedules local notifications, or sends or receives push (remote) notifications — including notification permission requests, APNs and device tokens, silent pushes, push updates for widgets and controls, starting or updating Live Activities with ActivityKit pushes, badges, or testing notifications.
---

# Notifications

## Permission

- Request permission with UNUserNotificationCenter's requestAuthorization at the moment the app first needs it (e.g. when the user enables a reminder), not at launch. There is no Info.plist purpose string for notifications — explain the benefit in your UI before asking.
- Use `.provisional` authorization for content the user hasn't explicitly asked for: notifications deliver quietly to Notification Center without a permission alert, and the user promotes or demotes them from there.
- Check `notificationSettings()` before scheduling; if denied, show UI that explains what's off rather than silently doing nothing.
- Persist user-facing notification state (e.g. a toggle for a scheduled recurring reminder) in AppStorage or UserDefaults.

## Local notifications

Local notifications (UNNotificationRequest with a time, calendar, or location trigger) need no entitlement, no paid team, and work in the simulator. Prefer them whenever the app itself knows when to notify — reminders, timers, streaks. Only reach for push when a server must initiate delivery.

## Push notifications — project setup

Push requires a paid Apple Developer Program membership. Free teams cannot enable the capability, and provisioning fails with a generic signing error — if the user has no paid membership, say so up front and offer local notifications instead.

- Never set up push against a placeholder bundle ID (such as Bitrig's app.bitrig.<anything>.<UUID>): follow the xcodegen-project skill's Bundle Identifier rules first (reuse the App Store Connect bundle ID if there is one, otherwise ask the user for a reverse-DNS ID they own), then update everything derived from it. Never invent a bundle ID yourself. Creating the App Store Connect app record is not required for push; it's only needed when publishing.
- Each target that receives pushes needs the aps-environment entitlement (in a Project.json project, via the target's entitlements block in Project.json, same shape as App Groups; otherwise in the target's .entitlements file):

  ```json
  "entitlements": {
    "path": "App/App.entitlements",
    "properties": {
      "aps-environment": "development"
    }
  }
  ```

  Always write "development". Distribution signing switches the app to the production APNs environment automatically; the value in the project stays "development".
- Apps that receive silent (content-available) pushes also need the remote-notification background mode in the target's `info` `properties`:

  ```json
  "UIBackgroundModes": ["remote-notification"]
  ```

  Alert-only pushes don't need it.
- The Push Notifications capability is registered on the App ID automatically the first time the app builds with a real team — if running for the simulator, you can use `xc provision` to register the app (see the capability-provisioning skill). Simulator builds alone don't register it.

## Receiving pushes in the app

- Call `UIApplication.shared.registerForRemoteNotifications()` after authorization is granted (and on every launch once granted — the token can change).
- The device token arrives through UIApplicationDelegate, so a SwiftUI app needs an @UIApplicationDelegateAdaptor delegate implementing `application(_:didRegisterForRemoteNotificationsWithDeviceToken:)`. Hex-encode the token for storage: `token.map { String(format: "%02x", $0) }.joined()`.
- Implement UNUserNotificationCenterDelegate to choose foreground presentation (`willPresent`) and handle taps (`didReceive`). Set the delegate at launch, before any notification can arrive.

## Refreshing widgets and watch complications with push (iOS 26+, watchOS 26+)

A widget can be refreshed by a push sent straight to the widget extension, without waking the app. It uses its own token and its own topic, and the User Notifications framework plays no part — registerForRemoteNotifications never yields a widget token, and a push sent to the app's topic never reaches the widget. Use it alongside timeline updates, not instead of them: the system budgets these pushes and delivers them opportunistically.

A watchOS complication is a WidgetKit widget, so everything below applies to it unchanged, including the widgets push type. Don't reach for the older ClockKit complication push type (the h.complication topic) — that's the pre-WidgetKit mechanism and doesn't refresh these.

- Add the aps-environment entitlement to the widget extension target as well as the app that hosts it, each in its own entitlements block with its own path (e.g. "Widget Extension/Widget Extension.entitlements"). Both App IDs pick the capability up on the first build with a real team. For a complication, the host is the watch app target, so the pair to entitle is the watch app and the watch widget extension — not the iPhone app.
- Conform a type to WidgetPushHandler, implement pushTokenDidChange(_:widgets:), and register it with .pushHandler(_:) on each widget's configuration.

  ```swift
  struct CaffeinePushHandler: WidgetPushHandler {
    func pushTokenDidChange(_ pushInfo: WidgetPushInfo, widgets: [WidgetInfo]) {
      // Upload pushInfo.token, plus the kind and family of each widget, to the backend.
    }
  }
  ```

- The system calls the handler with the first token and with every later change, including when the user adds or removes a widget, so treat each call as the current truth: replace the stored token and the stored widget list together, and stop sending when the list comes back empty.
- pushInfo.token is Data — hex-encode it the same way as a device token. It is a different token from the app's, so store it in its own row or column and never send one to the other's topic. The app can also read the current token at any time with WidgetCenter.shared.currentPushInfo, which is the simplest way to re-upload one at launch; it is nil until a token exists and when no widget is configured for push.
- Guard the handler and the modifier with #available / @available for iOS 26, macOS 26, watchOS 26, and visionOS 26, matching the platforms the extension targets. The API is unavailable on tvOS.
- The send is an ordinary APNs request with widget-specific headers: apns-push-type widgets, apns-topic "<host app bundle ID>.push-type.widgets", and a body of {"aps": {"content-changed": true}}. Broadcast (channel) pushes cannot update widgets.
- The topic is built from the bundle ID of the app that contains the extension, never the extension's own — so for a complication vended by a watch app's widget extension it's the watch app's bundle ID, not the iPhone app's. An app with both an iPhone widget and a watch complication therefore has two tokens on two topics, so store the topic on the token row rather than deriving one topic for the whole project.
- On watchOS the same token also covers relevance refreshes, so a complication using RelevanceConfiguration and a RelevanceEntriesProvider needs no separate registration.
- Controls have a parallel but different API, available since iOS 18 (macOS 26, watchOS 26; unavailable on visionOS): ControlPushHandler requires pushTokensDidChange(controls:) — plural, no push-info parameter — and each ControlInfo carries its own optional pushInfo.token. Register it with .pushHandler(_:) on the ControlWidgetConfiguration and send with push type controls and the .push-type.controls topic suffix.

## Starting, updating, and ending Live Activities with push

A Live Activity is driven by ActivityKit tokens, not by User Notifications. registerForRemoteNotifications never yields one, the app's device token cannot update an activity, and neither can the widget token — even though the activity is rendered by the widget extension. See the apple-app-extensions skill for the extension and ActivityAttributes setup this builds on.

- The aps-environment entitlement goes on the **host app** target only. The widget extension renders the activity but does not receive the push, so it needs the entitlement only if it also has push-updated widgets of its own.
- There are two tokens, and an app that both starts and updates remotely needs both:
  - An **update token**, one per activity, from starting it with pushType .token. Send it to the backend and keep it keyed to that activity.
  - A **push-to-start token**, one per app install, from Activity<Attributes>.pushToStartTokenUpdates (iOS 17.2+). It is available without any activity running, so read it at launch, and it is what lets the backend start an activity the user hasn't opened the app for.
- Read both as async sequences from a Task, never synchronously. activity.pushToken is nil for a while after request(attributes:content:pushType:) returns, and the update token rotates during the activity's life:

  ```swift
  let activity = try Activity.request(
    attributes: attributes,
    content: .init(state: initialState, staleDate: nil),
    pushType: .token
  )
  Task {
    for await token in activity.pushTokenUpdates {
      await upload(token.map { String(format: "%02x", $0) }.joined(), for: activity.id)
    }
  }
  ```

- Every rotation invalidates the previous token, so upsert on the activity id rather than inserting, and delete the row when the activity ends. A stale update token is the usual reason a working activity stops updating.
- Send with apns-push-type liveactivity and apns-topic "<host app bundle ID>.push-type.liveactivity" — the app's bundle ID, not the extension's. Push-to-start sends go to the push-to-start token on the same topic and push type.
- apns-priority 10 delivers immediately and counts against an hourly budget; 5 doesn't count and is the right default for routine updates. Mix the two rather than sending everything at 10. Apps that genuinely need more (live sports, turn-by-turn) add NSSupportsLiveActivitiesFrequentUpdates to the host app's Info.plist, then check ActivityAuthorizationInfo().frequentPushesEnabled — the user can switch it off in Settings — and observe frequentPushEnablementUpdates to adjust what the backend sends.
- The payload's aps dictionary needs a timestamp (seconds since 1970, so the system can always show the most recent update), an event of update, end, or start, and a content-state matching the ContentState type exactly. **The system decodes content-state with JSONDecoder's default strategies** — a backend that snake_cases keys, applies a custom date strategy, or sends a number as a string produces an update that APNs accepts and the system then fails to apply. An end event should carry the final content-state, and may carry a dismissal-date; an update may carry a stale-date to mark the activity outdated, and an alert to light up the screen for something urgent.
- A start payload additionally requires attributes-type (the ActivityAttributes type's plain name) and attributes, and Apple documents an alert as required too — starting an activity the user didn't ask for should never be silent. To get an update token back for the activity it just started, include "input-push-token": 1.

  ```json
  {
    "aps": {
      "timestamp": 1685952000,
      "event": "start",
      "attributes-type": "DeliveryAttributes",
      "attributes": { "orderNumber": "1234" },
      "content-state": { "status": "preparing", "etaMinutes": 25 },
      "input-push-token": 1,
      "alert": { "title": "Order confirmed", "body": "We're preparing your order." }
    }
  }
  ```

- Pushes are a supplement, not the only path: a device can be offline, and the system drops an update that arrives after the activity ended. Keep updating from the app when it's running, and set a stale date so a stalled activity shows as outdated rather than as wrong.
- Channel (broadcast) updates via pushType .channel(id) and the apns-channel-id header exist for large audiences, but the broadcast capability can only be enabled on developer.apple.com, not through Xcode or this plugin's tooling, and channels cannot start an activity. Don't reach for them by default.

## Sending pushes

Sending needs an APNs auth key (a .p8 with its key ID and team ID): the sender signs an ES256 JWT with it and POSTs each notification to APNs over HTTP/2 with the apns-topic header set to the bundle ID. How the key is provisioned and where the sender runs depend on the app's backend — the backend's skill covers that setup; some backends deliver their own pushes and need no key at all.

- Development-signed builds (simulator and device runs) register sandbox tokens served by api.sandbox.push.apple.com; TestFlight and App Store builds use api.push.apple.com. A BadDeviceToken response usually means a token was sent to the wrong one.
- Store device tokens in the backend keyed by user, upserted on the token with the token's APNs environment and an updated timestamp. Derive the environment at runtime, never from build configuration: `#if targetEnvironment(simulator)` is always sandbox — simulators embed no provisioning profile, so a profile-only check misreads them as production and their sends fail with BadDeviceToken; on device, no embedded.mobileprovision in the bundle means an App Store build (production); otherwise use the profile's aps-environment value. A DEBUG check misroutes development-signed Release builds — including Xcode's device installs — whose tokens are still sandbox.
- An app that pushes to itself, to its widgets, and to its Live Activities needs to tell the kinds of token apart — a kind column on the token row is enough — because the topic, the payload, and the push type all differ. One auth key signs them all. Live Activity update tokens are the exception to keying by user: they belong to a single activity, so store them with the activity id and delete them when it ends, while the push-to-start token is per install and keyed like a device token.
- Delete a stored token when APNs returns 410 Unregistered.

## Testing

- Quick payload testing needs no server: `xcrun simctl push booted <bundle-id> payload.apns` delivers a JSON payload (top-level `aps` dictionary) to the booted simulator.
- Simulators on Apple silicon receive real APNs sandbox pushes: registerForRemoteNotifications returns a working sandbox token, so the full send path is testable without a device.
- Development-signed builds (simulator and device runs) use the sandbox APNs environment; TestFlight and App Store builds use production. Test the production path via TestFlight before release.
- simctl push delivers application push types only — `xcrun simctl help push` lists what it does and doesn't support — so widget refreshes and Live Activity updates have to be tested with a real sandbox send to their own topic rather than a payload file.
- Live Activity pushes are testable end to end in the built-in simulator on Apple silicon: the activity's token is a working sandbox token, so log it and curl it to api.sandbox.push.apple.com with the liveactivity headers. When a send returns 200 but nothing changes on screen, the cause is almost always a content-state that doesn't decode; the Console app's liveactivitiesd, apsd, and chronod processes carry the real error.
- Silent pushes are throttled and deferred by the system — treat them as hints, not a delivery guarantee, and don't debug "missing" background pushes as failures.
