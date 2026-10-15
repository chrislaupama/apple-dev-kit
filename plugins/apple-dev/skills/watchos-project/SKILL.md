---
name: watchos-project
description: Use when a Project.json (XcodeGen) project requires Apple Watch-specific configuration, including platform support, standalone or companion targets, bundle identifiers, shared sources, or watch app icons.
---

# watchOS Project

XcodeGen supports standalone watchOS apps and iPhone apps with a watch companion.

- For watchOS-only apps, remove `TARGETED_DEVICE_FAMILY` entirely. Never use the `UIDeviceFamily` target setting; remove it if it exists.
- For standalone watchOS apps, use a single `application` target with `platform: "watchOS"` and set `"WKWatchOnly": true` and `"WKApplication": true` in `info.properties`.
- For watch companion apps, keep the iPhone and watch targets as separate `application` targets (`platform: "iOS"` and `platform: "watchOS"`). Set `"WKApplication": true` and `"WKCompanionAppBundleIdentifier"` (matching the iPhone target's `PRODUCT_BUNDLE_IDENTIFIER`) on the watch target. Do not set `"WKWatchOnly"` on a companion. Do not use `supportedDestinations: ["watchOS"]` on the iPhone target — the watch app must be its own watchOS target.
- When the iPhone target has the Game Center entitlement (`com.apple.developer.game-center`), give the companion watch target the same entitlement, even if the watch app doesn't use Game Center. App Store review rejects the build otherwise.
- The watch companion target must build the iPhone target's asset catalog so it can resolve `AppIcon`. Add `{"path": "App/Assets.xcassets"}` to the watch target's `sources` (alongside the watch's own source directory), for example: `"sources": [{"path": "Watch App"}, {"path": "App/Assets.xcassets"}]`. The catalog is where `AppIcon` lives; a watch target that lists only its own source directory builds no asset catalog.
- Make sure `App/Assets.xcassets/AppIcon.appiconset/Contents.json` has a watch app icon entry. Add a watchOS 1024×1024 icon entry referencing the same `Icon.png`, for example:
  ```json
  {"filename":"Icon.png","idiom":"universal","platform":"watchos","size":"1024x1024"}
  ```
- If the app icon set only contains iOS or macOS entries, the watchOS build can fail because `AppIcon` has no applicable watch content.
