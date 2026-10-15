---
name: xcodegen-project
description: Use when creating or modifying an app project defined by Project.json (an XcodeGen spec, as Bitrig projects are), including project configuration, target names, Info.plist settings, permissions, deployment targets, bundle identifiers, or bundle resources. Use the applicable platform skills for platform-specific configuration.
---

# XcodeGen (Project.json) Project

## Project Configuration
- Projects are defined by a `Project.json` file in the project root. This uses XcodeGen's spec format serialized as JSON (not YAML). Never look for or create YAML/YML project files in a project that has `Project.json`
- The `.xcodeproj` is generated from it by `xc` (or `xcodegen generate --spec Project.json`). Never edit the generated `.xcodeproj`; changes there are overwritten. That includes changes made through Xcode's MCP tools (`AddEntitlement`, `AddInfoPlist`, `UpdateTargetBuildSetting`, `XcodeNewTarget`…) or in Xcode's UI
- To rename a user's app, set the name of the target in the Project.json definition
- Target names must not contain `:` or `/`. When the app's name contains one, use a version without it for the target and put the exact user-facing name in the target's `CFBundleDisplayName` Info.plist property, e.g. target `Sun Day UV Tracker` with `"CFBundleDisplayName": "Sun Day: UV Tracker"`
- When changes are necessary in the Xcode project or Info.plist, make them in the Project.json file
- If the user reports an App Store rejection related to missing or insufficient permissions, capabilities, or purpose strings, edit the appropriate place in the Project.json definition.
- If the user asks how to restrict their app to certain OS versions, edit the appropriate place in the Project.json definition
- Set per-platform minimum OS versions on the project, not the target: `"options": { "deploymentTarget": { "iOS": "18.0", "macOS": "15.0" } }`. A dictionary on a target with `supportedDestinations` is ignored.
- Always rebuild with `xc build` after editing Project.json.
- Keep the generated `*.xcodeproj` out of git (add it to `.gitignore`) unless the project already commits it.

### Bundle Identifier
- Projects created by Bitrig may still carry a scaffold placeholder bundle ID (`app.bitrig.new.<UUID>`). It's fine for simulator work — leave it alone until something needs a permanent identifier.
- When a permanent bundle ID is needed — the user asks for one, or a feature requires one (push, CloudKit, Sign in with Apple, App Groups, running on a device, App Store Connect) — check whether the app already has an App Store Connect record (`appStoreConnect/app.json` → `bundleId` in a Bitrig project, or `asc apps list` when the `asc` CLI is signed in) and use that ID. Otherwise ask the user once for a reverse-DNS identifier on a domain they own (e.g. `com.theirdomain.appname`); don't invent one, since App IDs are permanent once registered.
- Set it as `PRODUCT_BUNDLE_IDENTIFIER` in the target's `settings`, then update everything derived from it: extension bundle IDs (`<app id>.<suffix>`), `WKCompanionAppBundleIdentifier`, App Group and iCloud container identifiers that were derived from the placeholder, and any code that hard-codes them.

### Signing
- Set `DEVELOPMENT_TEAM` (and `CODE_SIGN_STYLE: Automatic`) in the project or target `settings` once the user has a team. Simulator builds don't need one.

### Bundle Resources
- Non-Swift files in the `App/` directory are automatically included in the app bundle as resources
- When adding data files that should ship with the app, organize them in an `App/Resources/` subdirectory
