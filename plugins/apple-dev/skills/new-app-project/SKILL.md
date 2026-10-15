---
name: new-app-project
description: Use when creating a new SwiftUI app project, or making the first changes to a new or mostly-new one, especially when it still has a stub target, app icon, accent color, App, or ContentView.
---

# New App Project

- Create new projects as an XcodeGen `Project.json` (see the xcodegen-project skill) with this layout: `Project.json`, `App/` (the app's Swift sources, `Assets.xcassets` with `AppIcon` and `AccentColor`), and `.gitignore` ignoring `*.xcodeproj`, `.build/` and `xcuserdata/`. A minimal spec:
  ```json
  {
    "name": "Project",
    "options": { "deploymentTarget": { "iOS": "26.0" } },
    "settings": { "CODE_SIGN_IDENTITY": "-" },
    "targets": {
      "MyApp": {
        "type": "application",
        "platform": "iOS",
        "sources": [{ "path": "App" }],
        "settings": {
          "PRODUCT_BUNDLE_IDENTIFIER": "com.example.myapp",
          "TARGETED_DEVICE_FAMILY": "1,2",
          "GENERATE_INFOPLIST_FILE": "YES",
          "ASSETCATALOG_COMPILER_APPICON_NAME": "AppIcon",
          "ASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME": "AccentColor"
        },
        "info": { "path": "App/Info.plist", "properties": { "UILaunchScreen": {} } }
      }
    }
  }
  ```
  Then run `xc build` to confirm it generates and compiles.
- Any time you are making the first change to a new project, set a suitable name for the app target. Give the app an icon: a 1024×1024 `Icon.png` in `App/Assets.xcassets/AppIcon.appiconset/` referenced from its `Contents.json`. Use an image-generation tool if the session has one; otherwise ask the user for artwork, or leave the placeholder and say so.
- The target name must not contain `:` or `/`; if the app's name does, keep the exact name in `CFBundleDisplayName` and use a version without those characters for the target
- Set a suitable custom accent color for the app when one is clearly appropriate for the app's theme or brand, but it is acceptable to keep the default blue when no better accent color stands out
- Use 2 spaces of indentation at each level for the code you write when creating and extending the project
- Use a placeholder bundle ID until a permanent one is needed; then follow the xcodegen-project skill's Bundle Identifier rules rather than choosing an identifier yourself
- Use [native-app-design](../native-app-design/SKILL.md) when designing the app's initial user-facing interface (layout, controls, navigation, and interactions), after setting up the project.
