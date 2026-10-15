# Building for iPhone Duo

Developer guidance for adapting an iPhone app to iPhone Duo, Apple's folding iPhone. Apple's design guidance lives in the `apple-hig` skill's `references/designing-for-iphone-duo.md`, and the `app-resizability` skill covers size classes, asymmetric safe areas, the vertical bar edge, scene lifecycle, multi-window support, and the orientation and full-screen plist checks. This file covers only what those do not.

## Start with resizability, then refine

An app that resizes well is most of the way to iPhone Duo. If the app already resizes on iPad, or in iPhone Mirroring, do that work first, because resizing, navigation, and multitasking work carries over directly. Add fold-aware refinements and hinge interactions afterward, and only where they improve the app.

Size classes on Duo: the outer display is regular height and compact width in portrait, and compact in both in landscape, like other iPhones. The inner display is regular in both, so it can show sidebars and additional columns.

Do not rely on a portrait-only orientation declaration to protect a fixed layout. The inner display does not rotate the app to honor supported interface orientations. It scales the app instead, including in Split View. Duo also honors `UIRequiresFullScreen`, but the app still resizes whenever the device opens or closes. Landscape support matters more on Duo, because people set the device down like a tent.

## SDK levels

Xcode 27.1 and the iOS 27.1 SDK are required for full support, and for the iPhone Duo simulator device. The session states which SDK the user's Xcode has. If it is older than iOS 27.1, say so before starting, and tell the user to install Xcode 27.1 and its iOS 27.1 simulator runtime (and select it with `xcode-select` if they keep several Xcodes). Until then, the app still builds and runs on other simulated iPhones, but the Duo simulator, the APIs below, and edge-to-edge layout are unavailable.

| SDK used to build | Behavior on iPhone Duo |
| --- | --- |
| Before iOS 27 | Runs. When closed, the app uses the space beside the status bar and camera. When open, it gets a familiar size and aspect ratio |
| iOS 27 | Extends beside the status bar area on the inner display |
| iOS 27.1 | Edge-to-edge screen usage and vertical placement of standard navigation and toolbar buttons |

Building with the 27.1 SDK is the starting point, not full adoption. The APIs below arrive in 27.1 and need availability checks when the app's minimum OS is older. The declarations named in this file were verified against the 27.1 SDK. The documentation search tool may not index them yet, and `ArrangementView`, `ReservedRegion`, and the hinge types are declared in the SwiftUICore module interface rather than SwiftUI's. Use `ConcentricRectangle` in SwiftUI or `UICornerConfiguration` in UIKit for custom shapes that must follow the screen's corners, because both are updated for Duo's screen shapes.

## Use native navigation so bars move for free

`NavigationStack`, `NavigationSplitView`, `TabView`, and the standard `toolbar` modifier move to the vertical edge automatically. In UIKit, set toolbar items on a view controller inside a `UINavigationController` or `UITabBarController`. Content placed in a custom bar built from `UIToolbar`, `UINavigationBar`, or `UITabBar` is not considered, so a custom bar never goes vertical. Rebuilding it on the system components is usually less work than adapting it by hand.

On the outer display, the strip that holds the status bar is the vertical bar. Toolbar and tab bar items are laid out in it beneath the status bar and Dynamic Island, so put controls there by declaring toolbar items, not through a status bar or accessory API. A full-screen layout with no navigation container shows only system items in that strip until it is wrapped in a `NavigationStack` with a `toolbar`.

Where the system puts a vertical bar:

- On the outer display in every orientation, and on the inner display in landscape. The inner display in portrait keeps horizontal bars.
- In a split view, only the detail column gets a vertical bar. Sidebar and content columns stay horizontal, and inspectors never get their own.
- Sheets on the outer display get a vertical bar by default. On the inner display sheets are centered with horizontal bars, and a sheet placed trailing with `presentationPlacement(_:)` in SwiftUI or `preferredPlacement` in UIKit gets a vertical bar. That modifier applies to sheets only, with leading and trailing values.
- The bar stays on the same physical side in right-to-left languages. Content adapts around it.
- On the inner display a tab bar can become a sidebar. Use the `sidebarAdaptable` tab view style with `defaultAdaptableTabBarPlacement(.sidebar)`, and reserve this for information-dense apps.

Extend a hero or background image under a vertical bar with `backgroundExtensionEffect()` in SwiftUI or `UIBackgroundExtensionView` in UIKit.

### Toolbar items

The HIG page covers item order, titles with symbols, and overflow. The APIs and rules behind that guidance, all iOS 27.1 unless noted:

- Never make an item image-only. Any item that shows a symbol should also carry a title, through the title-and-systemImage initializers or `Label`, because the system can only show what it knows and an image-only item has no title for the overflow menu. A deliberately text-only item such as Done or the system Edit button is fine. It simply stays in the horizontal bar, so keep those to a minimum.
- Use semantic placements. `cancellationAction` places a custom Back or Close at the top, and `topBarPinnedTrailing` in SwiftUI or `pinnedTrailingGroup` in UIKit places a prominent action such as Done next. A navigation controller adds Back automatically. Remaining items keep their original grouping, with a spacer separating former top and bottom items.
- Representation rules: an item shown vertically uses its icon. An item shown horizontally uses its icon or title, preferring the icon. An item in the overflow menu uses both. A title-only item, or an item with a custom view, never goes vertical unless it opts in.
- `axisBehavior(_:)` on an item sets `ToolbarItemAxisBehavior`. Use `.horizontalOnly` for an item that switches between a symbol and text, such as a custom Select button, so related items stay on one axis. Use `.verticalPreferred` for a custom view that has a vertically adapted layout and fits the bar's fixed width. The system Edit button already stays horizontal.
- Prefer symbol-only items. Move supplementary text such as a count into a badge, with the `badge` modifier on the item's content in SwiftUI or `UIBarButtonItemBadge` in UIKit, so the item can go vertical. Keep an item horizontal only when its text carries standalone information, such as a cart total.
- Keyboard accessory bars stay attached to the keyboard and never move to the vertical axis. Flexible spacers are zero size in a vertical bar, and fixed spacers keep their minimum size, so do not add spacing of your own.
- A vertical bar has no scroll edge effect, but it gains a background when Reduce Transparency is on. Keep custom item content legible in both cases.
- Items overflow from the bottom of the bar up. `visibilityPriority(_:)` with `ToolbarItemVisibilityPriority` (iOS 27) sets which items overflow first. Prioritize groups, then items within a group. Overflow also happens when the keyboard appears or when Picture in Picture is pinned in open portrait.
- `ToolbarOverflowMenu` (iOS 27) in SwiftUI or `additionalOverflowItems` in UIKit puts custom overflow actions in the system menu.
- `toolbarVerticalCompressionBehavior(_:)` decides which bar gives way when the toolbar and tab bar compete for the vertical edge. The default, `.automatic`, sends toolbar items to overflow first so primary destinations stay reachable, which suits navigation-focused screens, and `.prefersTabBar` requests that explicitly. `.prefersToolbarItems` minimizes the tab bar instead, for task-focused screens.
- `toolbarVerticalBehavior(.disabled)` in SwiftUI or `preferredVerticalBarBehavior` in UIKit opts a view out of vertical bars. Reserve it for a single-page, bottom-heavy layout such as Calculator, or a sheet whose only item is a Close button. A sheet with the vertical bar disabled stops short of the outer camera, and the status bar repositions itself. A `NavigationStack` resolves the behavior from its topmost view, a `TabView` from its selected tab, a `NavigationSplitView` from its trailing-most column, and a sheet at the presentation. Treat it as a stable choice rather than toggling it from a view's state, and use `toolbarVisibility` when the goal is hiding bars rather than changing their layout.

## Reserved regions

The HIG page describes the three reserved regions. The API exposes two kinds:

- `ReservedRegion.Kind.division` is the fold. It is active only while the device is partially folded, and it has zero width when the device is flat.
- `ReservedRegion.Kind.occlusion` is a camera obstruction. The outer camera is always present. The inner camera region is active only while that camera is active.

System components handle both, so only custom layouts need the API. A `GeometryProxy`, from `GeometryReader` or `onGeometryChange`, exposes `reservedRegions(kind:)`, and each `ReservedRegion` reports a `frame`, `margins`, and `isActive`. Only active regions are returned by default. Pass the `.includeInactive` query option to see inactive ones, which lets a layout make high-level choices from a region's presence alone, such as preferring an even number of grid columns whenever a division region exists. Region frames are mirrored for right-to-left layouts by default, so a custom `Layout` can test intersections without accounting for direction; pass `.fixed` for the layout direction behavior to get physical frames. In UIKit the equivalent is `UIViewReservedRegion` on `UIView`.

### Displacement

Apple calls the pattern of moving an element out of a reserved region displacement. Continuously scrolling content such as an article, a feed, a document, or a list does not displace, because scrolling already handles it. Backgrounds do not displace either; they span the fold so nothing shows through. Controls and containers are what move.

- Let purpose choose the region. In the book pose, alerts move to the trailing side, closer to where they will appear when the device closes. In the table pose, the top region suits content viewed at a distance and the bottom region suits touch controls. When several regions fit, keep the element contextual, such as a search field staying over the view it searches.
- Move related elements together so their relationship survives, and do not move an element far from its source.
- Size can adapt as well as position. A split view rebalances to an even 50/50 split, and a grid can widen the spacing around the hinge while keeping its outer margins.
- Sheets, alerts, menus, popovers, and toolbar buttons displace automatically. Use them to get the behavior for free, and adopt reserved regions for the highest-priority manually laid-out controls.

## Arrangement views

`ArrangementView` is the SwiftUI type behind the HIG's arrangement views. It holds a primary and a secondary view and lays them out from the size classes, the aspect ratio, and the active division regions. The default style, `.automatic`, resolves to split:

    ArrangementView {
        controls
    } secondary: {
        canvas
    }
    .arrangementViewStyle(.split)

- `.split` divides the space between the two views, horizontally when wider than tall and vertically when taller than wide. Chain `.axes(_:)` on the style to limit it. If it cannot split on its primary axis, it shows only the primary view. Use it for a main-and-detail relationship where neither view may be obscured, or wherever an `HStack` or `VStack` already does the job.
- `.overlay` layers the primary view over the secondary one when no division region is active. When the device is partially folded, the primary view moves to the trailing or bottom region and the secondary to the leading or top. Use it for a foreground-and-background relationship, or wherever a `ZStack` already does the job. Read the `overlayArrangementZIndex` environment value to switch a view between a collapsed and an expanded form as the device folds.
- The arrangement view spans the whole area, fold included, and insets the primary and secondary views from an active division region and its margins. If you add a background, add it on the arrangement view or behind it, never on the primary or secondary views alone, or the gap at the fold shows the window background.
- Keep navigation outside. Never put a `NavigationSplitView` inside an arrangement view, and never put an arrangement view inside a `NavigationSplitView`, a `List`, a `ScrollView`, or any other container that could leave part of it unreachable.
- When the deployment target is below 27.1, give the availability fallback the same primary and secondary order as the arrangement view.

The UIKit counterpart is `UIArrangementViewController` with `UISplitArrangement` and `UIOverlayArrangement`. Read the z index from `state(for:)` on the controller.

## Multitasking and multiple windows

Every app participates in Split View on Duo. A person drags the home indicator to either side to create an even split, so test the app at half width on both sides, because the vertical bar lands on the outer edge of whichever side the app is on. Picture in Picture can pin to the top of the screen, and the app resizes vertically underneath it.

The inner display hosts multiple windows of the same app when the app supports them. An iPad app that already supports multiple scenes gets this on Duo.

- Only the inner display can create new windows. Handle errors when requesting a scene, and use `UIWindowSceneActivationAction`, which hides itself when new windows are unavailable.
- Consider whether people would open two documents or compare two pieces of content, and support multiple windows if so.
- Support dragging content into and out of the app where it fits, so a neighboring app's text or images arrive without a copy, switch, and paste round trip.

## Scene accessories

Scene accessories show additional content on another display while the main UI stays put. They are enabled by default, and the system toggles availability at any time, so respond to changes with observation tracking. On Duo, `CameraCaptureAccessory` added with the `sceneAccessory` modifier shows UI on the outer display while a camera app is full screen on the inner display with an active session, such as a teleprompter or a preview for the person being photographed. Register it on the same view as the camera UI, and use `onAvailabilityChange` to disable related controls when the device is closed.

## The hinge as an input

Hinge data is for interactions and effects, not layout. Layout uses size classes, arrangement views, and reserved regions.

- SwiftUI: `onHingeChange(isEnabled:_:)` receives the old and new `DeviceHingeContext`. Its `hinge` is nil on a device without a hinge. Otherwise it carries a `status` of `.closed`, `.partiallyOpen`, or `.fullyOpen`, and a continuous `angle`. Reset any derived state when the status leaves `.partiallyOpen`.
- UIKit: add a `UIHingeInteraction` with an update handler, and read `status` and `angle` from the delivered `UIHinge`.

Many apps do not need a hinge feature. Get the adaptive experience right first.

## Camera apps

Duo has two square-sensor ultrawide front cameras. Discovering a front camera returns a virtual front camera that switches between them as the device opens and closes, limited to the features both share: 1080p at 60 fps and no depth. The virtual camera reports `isVirtualDevice`, and its `activePrimaryConstituent` names the physical camera streaming. The `builtInInnerUltraWideCamera` and `builtInOuterUltraWideCamera` device types give full capability, and an app using them switches cameras itself with `AVCaptureDeviceDirectionCoordinator` from AVKit. A front camera can face away from the person on Duo, so the coordinator reports which cameras face forward relative to a specific view and calls back when that changes. Reconfigure the session, reconsider preview mirroring, and update UI in that handler. Adopt the rotation coordinator so the preview stays upright when the app moves between displays, and disable sensor orientation compensation afterward. Use `dynamicAspectRatio` to fill the inner display from the square sensor.

## Sheets and presentations

Sheets, alerts, popovers, and context menus adapt to every pose, and sheets slide off the fold when the device is partially folded.

## Design resources

Apple's iOS and iPadOS 27 UI kit for Figma, at https://www.figma.com/community/file/1651309003795292092/ios-and-ipados-27, includes iPhone Duo bezels, a keyboard, and toolbar, tab bar, and status bar components as of its 27.1 update. Use it to mock up either display and to read the exact bezel and safe area geometry.

## Testing

Test in Xcode's Simulator. Switch it to iPhone Duo when that device is available in the device list, which requires the iOS 27.1 simulator runtime from Xcode 27.1. The device starts closed, so everything observed after switching is the outer display and its compact layout. Use the Simulator app's fold controls to switch between Closed, Partially Open, and Fully Open, and its rotate control to turn the device, so every pose the HIG describes is reachable without a physical device. See the simulator-use skill for observing the running app. Dragging the home indicator to either side enters Split View on the inner display, and the vertical bar lands on the outer edge of whichever side the app is on.
