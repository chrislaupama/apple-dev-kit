---
name: apple-hig
description: Consult Apple's Human Interface Guidelines when creating a new app's user-facing interface, designing a new screen or UI component, substantially redesigning UI layout, controls, navigation, or interactions, or answering an explicit HIG guidance or review request. Not triggered by code architecture, API or data-model design, or implementation changes that preserve the UI.
---

# Apple Human Interface Guidelines

The `references/` directory contains a local Markdown snapshot of Apple's HIG. Links between bundled topics point to local Markdown files, including section anchors where available. Follow these local links when a related topic is needed. Apple's Markdown is preserved except for local HIG link destinations. Source URLs and snapshot metadata are in `references/manifest.json`. Media paths and other external references retain Apple's original syntax. This is reference material; apply it to the user's task and target OS, alongside the app's existing design.

Use this skill for user-facing interface design, including during implementation when you make new interface decisions. An explicit request for HIG guidance or review also applies without a UI change.

## What the HIG covers

Use this map to recognize relevant guidance even when the request doesn't name a HIG topic. Choose topics relevant to the current task. Topic names below map to `references/<topic>.md`; the searchable index lists the full collection.

| Design decision or concern | Topics to consider |
| --- | --- |
| Product focus, familiarity, brand, and clear language | `design-principles`, `branding`, `inclusion`, `writing` |
| Text hierarchy, contrast, appearance, and glass | `typography`, `color`, `dark-mode`, `materials` |
| Icons, symbols, artwork, and asset presentation | `icons`, `sf-symbols`, `images`, `app-icons` |
| Accessible operation, text scaling, and language direction | `accessibility`, `voiceover`, `right-to-left` |
| Adaptive layout, rows, grids, sidebars, and windows | `layout`, `lists-and-tables`, `collections`, `sidebars`, `split-views`, `windows` |
| Navigation, commands, and finding content | `tab-bars`, `toolbars`, `menus`, `the-menu-bar`, `searching`, `search-fields` |
| Forms, preferences, and choosing values | `entering-data`, `settings`, `text-fields`, `pickers`, `toggles`, `sliders`, `steppers` |
| Presentation, confirmation, waiting, and recovery | `modality`, `sheets`, `alerts`, `loading`, `progress-indicators`, `undo-and-redo` |
| Touch, keyboard, pointer, dragging, and focus | `gestures`, `keyboards`, `pointing-devices`, `drag-and-drop`, `focus-and-selection` |
| Animation, haptics, and other feedback | `motion`, `feedback`, `playing-haptics` |
| First use, permissions, accounts, and interruptions | `onboarding`, `launching`, `privacy`, `managing-accounts`, `managing-notifications` |
| Documents, sharing, media, and data visualization | `file-management`, `collaboration-and-sharing`, `playing-audio`, `playing-video`, `charting-data`, `charts` |
| Experiences outside the main app | `widgets`, `live-activities`, `app-shortcuts`, `siri`, `snippets` |

Platform overviews are `designing-for-ios`, `designing-for-ipados`, `designing-for-macos`, `designing-for-tvos`, `designing-for-visionos`, `designing-for-watchos`, and `designing-for-iphone-duo`. Specialized guidance also covers games, spatial experiences, Pencil, Digital Crown, remotes, maps, purchases, health, and generative AI; search the index for these when relevant.

Consider cross-cutting concerns before selecting references: a settings screen may need text-scaling and appearance guidance; a custom canvas may need accessible actions, focus, and gesture alternatives. Select the topics that could change the implementation, even if the user didn't explicitly mention them.

## Retrieve only what the decision needs

- Identify the design question and target platform. Search topic titles with `rg -i -m 5 'sheet|dialog' references/index.tsv` or another focused pattern. Map SwiftUI names to HIG concepts when needed (`Form` → entering data, `NavigationSplitView` → sidebars). Paths here are relative to this skill's directory.
- Inspect headings in the matching page with `rg -n '^#{1,4} ' references/sheets.md`, then read the relevant line ranges with the file-reading tool or `sed -n 'START,ENDp'`. Include applicable general guidance and platform considerations. A short page can be read in full.
- Start with one directly relevant topic. For a fresh app, also consult the target platform's `designing-for-*.md` overview. Load foundations or related topics as needed to resolve remaining design decisions. Reuse relevant material already read in this conversation.
- Preserve qualifications such as “consider,” platform differences, and OS-specific conditions. Verify Swift API availability separately when implementing the design.
- Cite the original Apple page when explaining a HIG-based decision. When an illustration matters, open the original page; Apple's Markdown may contain relative media paths.

The snapshot date is in `references/manifest.json`. For newer OS behavior, missing topics, or an explicit request for current guidance, consult Apple's live HIG and distinguish it from the snapshot. Refreshing the bundled snapshot is a separate maintenance task.
