---
name: macos-project
description: Use when a Project.json (XcodeGen) project requires macOS-specific configuration, including platform support, target settings, App Store icons, app category, sandbox entitlements, or Catalyst.
---

# macOS Project

- For Mac-only apps, remove `TARGETED_DEVICE_FAMILY` entirely. Never use the `UIDeviceFamily` target setting; remove it if it exists.
- Do not make Mac Catalyst apps unless specifically asked to.
- When adding macOS support to a project, ensure `App/Assets.xcassets/AppIcon.appiconset/Contents.json` has both an iOS and a macOS image entry referencing the same `Icon.png`:
  ```json
  {"filename":"Icon.png","idiom":"universal","platform":"ios","size":"1024x1024"},
  {"filename":"Icon.png","idiom":"mac","scale":"2x","size":"512x512"}
  ```
  The iOS entry uses `"idiom":"universal"` with `"platform":"ios"`; the macOS entry uses `"idiom":"mac"` with `"scale":"2x"`. Both point to the same 1024x1024 source image
- When adding macOS support, set `LSApplicationCategoryType` in the project's Info.plist settings (e.g. `"LSApplicationCategoryType": "public.app-category.utilities"`). Choose the category that best fits the app. See Apple's documentation for the full list of category values.
- For macOS App Store distribution, the host app target must declare App Sandbox in its entitlements. Add an `entitlements` block to the target with `"com.apple.security.app-sandbox": true` (and `"com.apple.security.network.client": true` if the app makes outbound network requests), using a target-specific path such as `App/App.entitlements` and placing those keys in its `properties` dictionary.
