---
name: xcode-project
description: Use before building or changing the project configuration of an existing Xcode project or workspace that has no Project.json. Covers .xcodeproj/.xcworkspace files, Project.json, Info.plist, entitlements, capabilities, build or target settings, bundle resources, code signing, and development teams.
---

# Existing Xcode Project

This project is an existing Xcode project or workspace, defined directly by its .xcodeproj rather than by a Project.json. The files, project configuration, and git history are theirs. Work with what's already there, and match the project's existing code style and conventions rather than imposing new ones.

### Project Configuration
- `xc` builds the folder's `.xcodeproj`/`.xcworkspace` directly with xcodebuild. When project settings, Info.plist entries, or entitlements need to change, edit the Xcode project files directly. Never create a `Project.json`.
- An `.xcodeproj` holds its definition in either `project.pbxproj` (the classic property-list format) or `project.xcproj` (the JSON format Xcode 27 introduced). Edit whichever one exists, keep the same format, and never create the other.
- Exception: if the project root already contains a `Project.json`, `xc` generates the Xcode project from it and direct `.pbxproj` or `.xcproj` edits are overwritten. Make project-level changes in `Project.json` instead.
- When an app with the Game Center entitlement (`com.apple.developer.game-center`) embeds a watch app, the watch app target needs that entitlement too, even if it doesn't use Game Center. App Store review rejects the build otherwise.
- The user may have Xcode installed, but never send them to Xcode's UI to change a setting. Make the change yourself by editing the project files, then rebuild to confirm it worked.

### Code Signing
- Simulator builds don't require a development team. Signing problems mostly surface when building for the Mac, a physical device, or distribution.
- If a build fails because signing requires a development team, fix the project directly. Prefer setting `DEVELOPMENT_TEAM` to a team the user already has (check for identities with `security find-identity -v -p codesigning`).
- If no team is available, Mac builds can fall back to ad-hoc signing (`CODE_SIGN_STYLE = Manual`, `CODE_SIGN_IDENTITY = "-"`), unless the target has entitlements that need provisioning (push notifications, iCloud, and similar). Physical devices and distribution always need a real team, so never apply ad-hoc settings for those.
- When you change signing, tell the user what you changed and that it's easy to reverse. For ad-hoc signing, note that it only covers local Mac builds: installing on a device or distributing through TestFlight or the App Store still needs a development team.
