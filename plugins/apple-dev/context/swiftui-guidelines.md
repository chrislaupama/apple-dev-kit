# Apple-platform app development
This project is an app for Apple platforms (iPhone, iPad, Apple Watch, Apple TV, Apple Vision Pro or Mac). Always use Swift and SwiftUI as the default unless you see or are told otherwise. These guidelines come from the apple-dev plugin; the project's own CLAUDE.md and existing code style take precedence where they differ.

## Environment
- The user may range from an experienced software engineer to a completely nontechnical user. Do not assume they understand the codebase or development terminology, but adapt your responses to their apparent technical level.
- iPhone Duo is Apple's foldable iPhone, announced September 2026, which may be beyond your knowledge cutoff; consult the `iphone-duo` skill for details.
- Whenever you finish changes that affect the app, show them to the user with `xc preview -platform <platform>` (repeat `-platform` for every platform your changes affect), run from the project directory. It regenerates the Xcode project from Project.json when there is one, builds, installs and launches the app in the Simulator, or opens the Mac app. Nothing rebuilds automatically when you change code. Use `xc build` only to check that code compiles, and `xc test` for tests. See the `xcode-build` skill. A failing build is not a reason to switch to raw xcodebuild: fix the errors and run `xc` again.
- In a project defined by `Project.json` (XcodeGen), make project changes there, never in the generated `.xcodeproj`. See the `xcodegen-project` skill.
- Don't assume Xcode's Simulator has a camera (Bitrig's simulator added one with its own shim). Request camera permission normally, include `NSCameraUsageDescription`, handle a missing camera gracefully, and tell the user to test camera features on a device.
- When Xcode is open with the project and the `xcode-integration` tools are connected, use them to see and operate the running app, read its console and debug it (see the `simulator-use` and `xcode-build` skills). Prefer `xc` for routine builds.
- Complete tasks directly with your tools rather than sending the user to Xcode to make changes, except for things only Xcode can do (signing in to an Apple account, local StoreKit testing, running on a physical device).

## Tool Use
- When calling the Bash tool, always set the `description` field to a short, human-readable description of what the command does.
- If a tool call fails with the same error three times in a row, stop retrying and tell the user what's wrong instead of continuing.

## UI Design
- Use the `native-app-design` skill when creating the user-facing interface of a new app, designing a new screen or UI component, or substantially redesigning existing UI (layout, controls, navigation, or interactions). Code architecture, API or data-model design, and implementation changes that preserve the UI do not trigger this skill.
- Make the design of any UI you create Apple-like. Use clean typography and consistent padding/spacing
- Prefer SF Symbols over emoji
- In UI elements, use real ellipsis "…", not a series of dots "..."

## SwiftUI and Apple APIs

### State and Data Flow
- Use clean separation of concerns, and keep as much logic as possible in the model layer, not the view layer
- Never use @AppStorage outside of a View - in those cases read from UserDefaults directly instead
- AppStorage and UserDefaults can store values of type Bool, Float, Double, Int, String, URL, Date, Array, and Dictionary. Array elements and Dictionary keys and values can be any type that is otherwise valid to store
- Be proactive about storing state in AppStorage or UserDefaults that makes sense to persist across app launches. For example, proactively store in AppStorage or UserDefaults the state of a toggle tracking whether a user has scheduled a recurring system user notification
- Don't store an @Observed object in the @State of a view
- When creating Environment, Preference, etc keys, use the @Entry macro whenever possible
- Prefer using @Observable over ObservableObject when a model class is needed
- To create bindings from properties in an @Observable class, use the @Bindable property wrapper

### Styling
- To use the accent color of the app, use `.tint` on `ShapeStyle`
- `.tint`, `.primary`, `.secondary`, etc. are different `ShapeStyle` types. They cannot be mixed in a ternary expression. Use `AnyShapeStyle` to erase the type: `.foregroundStyle(condition ? AnyShapeStyle(.tint) : AnyShapeStyle(.primary))`

### Layout and Navigation
- Use NavigationStack for navigation, not NavigationView
  - Choose the content container for the task: Form for forms, List for lists, ScrollView for custom scrolling content, or a non-scrolling layout when appropriate.
- When you create a view that can scroll (i.e. it is in a ScrollView), make sure that it is horizontally flexible so that it takes up the full width of the screen
- When there are multiple items in a grid, they should usually all be the same size as each other

### Controls and Toolbars
- Choose control types based on semantics, then style visually as needed
  - Use `Toggle` with `.toggleStyle(.button)` when reflecting persistent state (e.g., a filter that IS set to "Unread")
  - Use `Button` with alternating labels when triggering an action that changes something (e.g., "Show Details" / "Hide Details")
  - Use `Picker` with `.pickerStyle(.menu)` when selecting one option from many, not a `Menu` of `Button`s
  - Apply `.buttonStyle()` to controls styled as buttons (`Toggle`, `Picker`, `Menu`, etc.) to customize their button appearance
- Most controls that take a string label can also take an optional systemImage argument to specify a symbol (i.e. `Button("Play", systemImage: "play") {}`) - use that instead of a trailing closure with a Label
- Give each Slider a meaningful label. Add minimumValueLabel and maximumValueLabel when they help explain the range, using content builder closures. For continuous values, omit `step:`: it automatically adds tick marks on current OS versions. Use it for meaningful discrete choices, not just to format the displayed number
- Any time you show a button that has a rounded rectangle button, make sure the background is part of the label so it is also tappable
- For toolbar items, prefer symbols over text where possible
  - Avoid using SF Symbols that end in ".circle" in toolbar items, since they already have a platter background
  - Group related toolbar items with ToolbarItemGroup
  - Text toolbar items should not be grouped with other toolbar items

### Accessibility
- Ensure that all apps and UIs you create have good and complete accessibility support. This is important for users who need it, and to make the elements on the screen selectable.
- Ensure controls have proper accessibility labels, even when displaying only an icon
  - Use `Label` or provide both title and image parameters
  - Apply `.labelStyle(.iconOnly)` or `.labelsHidden()` to hide text visually

### Animation and Feedback
- When creating animations, use spring animations unless instructed otherwise
  - To make spring animations, prefer the presets `Animation.smooth`, `Animation.snappy`, or `Animation.bouncy`
  - If a custom spring is needed, use `Animation.spring(duration:bounce:)`
- To add haptic feedback, use the SwiftUI sensoryFeedback view modifier, like `.sensoryFeedback(.impact(weight: .heavy, intensity: 1), trigger: counter)`

### File and Media
- If you are accessing a file URL, make sure to start and stop accessing the security-scoped resource
- When playing an audio file, use AVAudioEngine with an AVAudioFile

### OS 27 APIs
- New APIs introduced in the 27 releases can be used, but MUST have their availability guarded for every platform you target, using the matching version for each. For example `@available(iOS 27.0, macOS 27.0, watchOS 27.0, tvOS 27.0, visionOS 27.0, *)` or `if #available(iOS 27.0, *) { ... }`
- Only use an API if it is available in the SDK the user has
- For details on new APIs, don't rely on prior knowledge:
  - Load the `xcode-integration:swiftui-whats-new-27` or `xcode-integration:app-intents-whats-new-27` skill for what changed in the 27 releases, and `xcode-integration:swiftui-specialist` for Apple's current SwiftUI best practices.
  - Check exact signatures and availability in the user's SDK with `apple-api <Framework> '<regex>'` (or `apple-api <Framework> --new 27` for everything new). It reads the installed SDK's Swift interfaces, including SwiftUICore and the `_X_SwiftUI` overlays. If it finds nothing, the API isn't in this SDK.
  - For prose documentation, fetch Apple's documentation JSON with your web tools, for example `https://developer.apple.com/tutorials/data/documentation/swiftui/view.json`.

## Swift Code Style
- Prefer `var` for stored properties in structs; reserve `let` for preserving invariants
- Always try to use strong types to encode guarantees at compile time
  - For example, make String-backed enums for string values that have a fixed set of values
- Never name any types with a name that is used by a framework type, for example do NOT create views with names like ProgressView or Button since those type names are already used in SwiftUI
- Put the primary type for a file at the top, with supporting types after it in the file
- Create one file per type unless there's a compelling reason to group them (e.g. a small private helper type used only by the file's primary type)
- Prefer using trailing closures (including multiple trailing closures) unless there's a strong reason not to
- Never include PreviewProvider or #Preview
