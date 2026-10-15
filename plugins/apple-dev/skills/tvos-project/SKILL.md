---
name: tvos-project
description: Use when a Project.json (XcodeGen) project requires Apple TV-specific configuration, including tvOS platform support, target settings, or device-family settings.
---

# tvOS Project

- For a single-platform Apple TV app, set the target's `platform` to `"tvOS"`.
- Set `TARGETED_DEVICE_FAMILY` to `3` for Apple TV.
- Never use the `UIDeviceFamily` target setting; remove it if it exists.
