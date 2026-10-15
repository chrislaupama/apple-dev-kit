---
name: ios-project
description: Use when a Project.json (XcodeGen) project requires iPhone- or iPad-specific configuration, including platform support, iOS target settings, device families, launch screens, or iPad support.
---

# iOS Project

- All iPhone and iPad app targets must include `"UILaunchScreen": {}` in their Info.plist configuration in `Project.json`. The presence of this key, even if empty, tells iOS the app supports modern screen dimensions. Without it, the app may run in a letterboxed compatibility mode
- Set `TARGETED_DEVICE_FAMILY` to `1` for iPhone, `2` for iPad, or `1,2` when the target supports both iPhone and iPad.
- Never use the `UIDeviceFamily` target setting; remove it if it exists.
- References to iOS in this plugin's project guidance usually relate to iPadOS too.
