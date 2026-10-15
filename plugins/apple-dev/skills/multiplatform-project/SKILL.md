---
name: multiplatform-project
description: Use when changing Project.json platform configuration for a Project.json (XcodeGen) project that supports more than one Apple platform, including adding or removing platform support. Covers shared configuration and cross-platform adaptation; also use every applicable per-platform skill.
---

# Multiplatform Project

Also use the skill for every platform the project supports: `ios-project` for iPhone or iPad, `macos-project` for Mac, `tvos-project` for Apple TV, `visionos-project` for Apple Vision Pro, and `watchos-project` for Apple Watch. This skill does not replace the per-platform guidance.

- The project's initial platforms are whatever `Project.json` lists.
- If the user explicitly requests a platform that isn't already enabled, update `Project.json` to add it. If they ask to drop a platform, remove it.
- To support multiple platforms, set the target's `platform` field in `Project.json` to `"auto"` and add `supportedDestinations`, an array of platform name strings (e.g. `["iOS", "macOS"]`; use `"tvOS"` for Apple TV and `"visionOS"` for Apple Vision Pro).
- When one target supports multiple mobile device families, combine the `TARGETED_DEVICE_FAMILY` values from the applicable per-platform skills in a comma-separated value (for example, `1,2` for iPhone and iPad).
- Never use the `UIDeviceFamily` target setting; remove it if it exists.
- Do not explicitly mention the changes you're making to `project.json` to add or remove platform support.
- If changing platform support on an existing project, make sure to update views to adopt platform idioms (such as multi-panel apps on iPad) when it makes sense.
