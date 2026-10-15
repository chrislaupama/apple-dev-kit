---
name: visionos-project
description: Use when a Project.json (XcodeGen) project requires Apple Vision Pro-specific configuration, including visionOS platform support, target settings, or device-family settings.
---

# visionOS Project

- For a single-platform Apple Vision Pro app, set the target's `platform` to `"visionOS"`.
- Set `TARGETED_DEVICE_FAMILY` to `7` for Apple Vision Pro.
- Never use the `UIDeviceFamily` target setting; remove it if it exists.
