---
name: capability-provisioning
description: Use after adding or changing a capability Apple's servers check against the app, such as iCloud or CloudKit, push notifications, Sign in with Apple or WeatherKit, and when one of these doesn't work in the Simulator.
---

# Registering capabilities with Apple

Services Apple's servers check against the app, such as iCloud and CloudKit containers, push notifications, Sign in with Apple and WeatherKit, work only once the app's App ID has them registered in the developer portal. Simulator builds never register anything, so these fail in the Simulator until something does.

```
xc provision -platform iOS
```

builds the app for a generic device with `-allowProvisioningUpdates`. Xcode's automatic signing then registers each target's App ID, capabilities and containers with the team in `DEVELOPMENT_TEAM`. It is a full device build, so it takes as long as a normal build, and the result isn't installed anywhere.

- Run it after you add or change one of these capabilities' entitlements, on any target, and when one of them doesn't work in the Simulator. Ordinary code changes don't need it; what it registers stays registered.
- Name the platforms the app runs on. Mac builds register what they need when built with a team, so `-platform macOS` is only needed for a Mac-only app.
- The app needs its permanent bundle ID first (see the xcodegen-project skill): registering creates App IDs and containers in the user's account under the bundle ID the app has, and they can't be renamed afterwards.
- The target needs `DEVELOPMENT_TEAM` (in Project.json `settings`, or the Xcode project) and `CODE_SIGN_STYLE: Automatic`. Find the user's teams with `security find-identity -v -p codesigning`, or ask them for their Team ID.
- When it fails, the log says why, such as no Apple account signed in to Xcode (Xcode → Settings → Accounts) or no team set; tell the user what they need to do. Free Personal Teams can't register push notifications, iCloud or Sign in with Apple at all, so say so plainly.
