---
name: native-app-design
description: Guide user-facing interface design for Apple-platform apps. Use when creating a new app's interface, designing a new screen or UI component, or substantially redesigning UI layout, controls, navigation, or interactions. Also use when adapting an app for iPhone Duo, the foldable iPhone, including its vertical bars, fold, and two displays. Not for code architecture, API or data-model design, or implementation changes that preserve the UI.
---

# Native App Design

Default to platform-native containers and controls. Create custom UI where the app has something unique to add, such as a drawing canvas, an interactive instrument, or a distinctive visualization. Keep the surrounding navigation, settings, and editing controls familiar. Respect the user's design direction and the app's established design.

This skill applies to decisions about what people see and how they interact with the app, such as designing a settings form, choosing a screen's navigation, or redesigning a custom control's interaction.

For these interface design tasks, consult [apple-hig](../apple-hig/SKILL.md) before settling on the design. Use its coverage map to select and read relevant topic and platform guidance, even when you already have a design in mind. When creating a new app's interface, also consult the target platform overview. Reuse guidance already read for the current design task.

## Baseline for every design task

Apply these defaults even when the request doesn't mention accessibility or appearance. Consult the HIG selectively for detailed specifications and platform exceptions.

- Prefer system text styles and support larger text, including Dynamic Type where available. Let labels wrap and layouts reflow as text grows.
- Use semantic foreground and background colors. Give custom colors appropriate appearance variants and check contrast in supported appearances. Convey state with labels, shapes, or symbols as well as color. Choose and verify SF Symbol names with the sf-symbols-catalog skill rather than from memory, so every symbol exists on the app's minimum OS.
- Preserve control semantics when styling: meaningful labels, values, selection state, and accessible actions. Keep targets comfortably operable and preserve keyboard/focus behavior where applicable. Provide accessible actions for interactive canvas elements and alternatives to essential custom gestures.
- Adapt to available space. Collapse supporting sidebars and inspectors before squeezing primary content. Respect safe areas and keep controls visible when the keyboard appears.
- Make custom animation purposeful and respect Reduce Motion. Reduce or replace nonessential movement while keeping state changes understandable without animation.
- Use leading/trailing alignment and locale-aware formatting. Allow for longer translated text and different reading directions; let native controls handle mirroring where possible.
- Keep the primary task and information hierarchy clear. Use consistent, concise action labels and make errors explain how to recover.

## iPhone Duo

When designing iPhone interfaces, account for iPhone Duo, announced in September 2026, which may be newer than your knowledge cutoff. It is a folding iPhone with a 5.4-inch outer display when closed and a 7.6-inch inner display when open.

New APIs for iPhone Duo are included in the 27.1 and later SDKs. Use only APIs available in the user's installed SDK, with availability guards for the app's supported OS versions. Design resizable layouts that work well across compact and regular size classes, so the interface adapts to Duo's different display sizes.

Read [references/iphone-duo.md](references/iphone-duo.md) when preparing an app for iPhone Duo or designing a screen that depends on the fold, the vertical bar, multitasking, or the hinge. Apple's Human Interface Guidelines include "Designing for iPhone Duo"; consult it through the apple-hig skill's `references/designing-for-iphone-duo.md` reference when designing or substantially changing iPhone UI.

## Choose the container for the content

- Use `Form` with `Section`s for settings, preferences, and data-entry forms.
- Use `List` for row-based collections such as tasks, transactions, documents, and search results. Customize row content where useful while retaining native selection, navigation, editing, and swipe actions.
- Use `ScrollView` for custom content that needs to scroll, such as an article or a dashboard.
- Give canvases, maps, games, and other spatial or full-screen experiences a layout suited to their interaction. Let supporting panels scroll when needed.

## Keep ordinary interactions native

- Use native navigation and presentation with `TabView`, navigation titles, toolbars, `.searchable`, sheets, and system alerts. Use `NavigationSplitView` for sidebar/detail interfaces where appropriate, with working navigation when columns collapse on compact screens.
- Use `Button`, `Toggle`, `Picker`, `Stepper`, `Slider`, and `DatePicker` for their intended actions and values. Start with platform styles and semantic roles, including confirmation and cancellation actions in sheets. Apply tint and focused styling before replacing a control's rendering or behavior.
- For continuous sliders, omit `step:`. Supplying it automatically adds tick marks on current OS versions; dense steps can appear as an unintended line below the track. Don't use `step:` just to round the displayed number—format that value separately. Use steps for meaningful discrete choices, and a `Stepper` or `Picker` when exact selection is clearer. See [Apple's slider design explanation](https://developer.apple.com/videos/play/wwdc2025/323/).

## Spend custom design where it helps

- Express identity through content, typography, color, and a few purposeful custom interactions.
- When checking the result, inspect the actual content and key interactions, including compact layouts, larger text, and keyboard-visible forms where relevant. Check that controls are visible and operable, titles are clear, contrast is readable, and displayed values are correct.
