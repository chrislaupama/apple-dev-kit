---
name: iphone-duo
description: Describe iPhone Duo, Apple's foldable iPhone announced in September 2026, and find its design, API, and simulator guidance. Use for questions about iPhone Duo or the foldable iPhone, and when building, adapting, debugging, or testing apps for it.
---

# iPhone Duo

iPhone Duo is Apple's folding iPhone, announced in September 2026. It runs iOS and follows iPhone interaction patterns. It may be newer than your knowledge cutoff; the bundled guidance linked below describes the device and its supported APIs.

## Displays and poses

The device has a **5.4-inch outer display** used when closed and a **7.6-inch inner display** revealed when opened. A center hinge lets it close, open flat, or stay partially folded. People can hold it like a book, place it on a table with part of the display upright, or stand it on its edges.

The outer display is wider and shorter than other iPhone displays. In portrait it has compact width and regular height size classes; in landscape both are compact. The inner display has regular width and height, with room for sidebars and multiple columns. Opening and closing the device changes the space available to the running app. The experience continues across displays, preserving the person's current content, navigation, and editing state.

## Controls, cameras, and the fold

System navigation controls, toolbars, and tab bars sit along a **vertical edge** on the outer display and on the inner display in landscape. The inner display in portrait keeps horizontal bars. This vertical area also contains the status bar and Dynamic Island, leaving more height for app content. Standard navigation and toolbar components adapt automatically when built with the iOS 27.1 SDK.

Each display has its own front-facing camera. The outer camera sits in a corner and is always visible. The inner camera is behind the display and becomes visible only while active. These cameras and the fold create **reserved regions** that affect where content and controls can fit: the outer camera region is always present, the inner camera region is active while that camera is in use, and the folding region divides the inner display into usable areas while partially folded. System presentations and layout containers can adapt around these regions.

The hinge also reports its angle and whether the device is closed, partially open, or fully open. Apps can use that information for interactions and effects. Adaptive layout instead relies on available space, size classes, and reserved regions.

## Multitasking and support

The inner display supports Split View multitasking, with two apps side by side. Each app's vertical controls sit along its outer edge, so an app's controls can appear on either side. Apps that support multiple scenes can also show multiple windows on the inner display. Picture in Picture can reduce the app's available height. An app therefore needs to handle sizes beyond just the two full displays.

Full support requires Xcode 27.1 and the iOS 27.1 SDK. Apps built with earlier SDKs still run with compatibility behavior described in the developer guide below. Duo-specific APIs need availability guards when supporting older OS versions. The iPhone Duo simulator requires the iOS 27.1 simulator runtime.

## Where to look next

Read the material relevant to the task:

- **Design and device behavior:** [Designing for iPhone Duo](../apple-hig/references/designing-for-iphone-duo.md) covers poses, continuity, vertical controls, reserved regions, and adaptive layouts. For interface design work, also use [native-app-design](../native-app-design/SKILL.md).
- **Implementation and APIs:** [Building for iPhone Duo](../native-app-design/references/iphone-duo.md) covers SDK compatibility, navigation and toolbars, arrangement views, reserved-region APIs, multiple windows, scene accessories, hinge input, and cameras.
- **Resizing existing code:** Use the `xcode-agent-skills:app-resizability` skill when available for size classes, safe areas, scene lifecycle, multi-window support, and migration away from fixed screen assumptions. The [resizability overview](../native-app-design/references/iphone-duo.md#start-with-resizability-then-refine) provides the Duo-specific starting point.
- **Simulator testing:** The [Duo testing guidance](../native-app-design/references/iphone-duo.md#testing) explains display poses and the Simulator's fold controls. Read the simulator-use skill to observe the running app.
- **Figma designs:** [figma-import](../figma-import/SKILL.md) covers importing designs and Apple's UI kit with Duo bezels and system components.
