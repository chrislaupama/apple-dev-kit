---
name: figma-import
description: Use when importing a Figma design into a SwiftUI project, translating Figma frames into SwiftUI, or when the user shares a figma.com URL. Adds SwiftUI-project rules on top of the Figma plugin's figma-design-to-code and figma-swiftui skills, which must be loaded first.
---

# Figma Import

Load the Figma plugin's figma-design-to-code and figma-swiftui skills first for the core pattern mappings, typography, colors, and asset handling. If the Figma MCP tools are unavailable, ask the user to connect or authorize the Figma connector, then continue on their next message.

## Page and file URLs
- When the URL's node is a page, or design context reports that nothing is selected, call get_metadata and list every top-level frame in document order. If there are multiple frames, tell the user how many frames were found and ask whether to import all of them, choose a subset, or start with one.
- Then call get_design_context once per chosen frame, or once per child of a large frame as described below. Never write a screen from its frame name alone.
- An empty render or "nothing selected" is not a permission problem. Only report an access error after reading a specific frame fails.

## Large frames
- Design context is capped per response. A response carrying a truncation notice or an omitted-content marker, at its end or in the middle, is missing evidence however complete its code looks, and SF Symbol names and label text never come from the screenshot, so never write a screen from one. Split the frame instead of guessing.
- A frame that is a whole device pose, such as a Duo mockup with a bezel and pane controls, is usually too large for one response. Call get_metadata on it first, then request design context once per child in one parallel batch: each content pane, the pane controls, and any floating bar. Skip the bezel and other mockup layers, which map to nothing.
- If a child still truncates, split it again by its own children. Keep a list of repeating rows in one request, because each row's text lives only in design context.

## Decide who owns each element
Before writing a view, classify each element as system chrome to omit, a native control to substitute, an extension surface, or genuinely custom UI. Names are hints. Confirm from anatomy, position, and the screenshot. Ownership follows the nearest product-screen boundary: a map inside an app screen is a MapKit candidate, while the same map inside a phone mockup in a marketing graphic is artwork.

## Context frames are evidence, not screens
- Omit keyboards, Home Screen, Lock Screen, Control Center, Face ID, notification banners, and share sheets. The platform provides them.
- Use a drawn keyboard only to infer the focused field's keyboard type, capitalization, and submit label.
- Widget and notification frames describe an extension the app might contribute. Mention them, but do not add a target unless the user asks. Use the apple-app-extensions skill if they do.

## Additional pattern mappings
These extend the table in the figma-swiftui reference.

| Figma evidence | SwiftUI | Guardrail |
|---|---|---|
| Alert or action sheet with role-labeled actions such as Cancel or Delete | alert or confirmationDialog with button roles | Let iOS choose side-by-side versus stacked buttons |
| Menu list, context preview, or Cut/Copy/Paste bar | Menu, contextMenu, or the text system's edit menu | Never draw selection handles or clipboard commands |
| Activity view with app and action rows | ShareLink | The activity list is system-owned and personalized |
| Bottom-anchored growing field with send, mic, or attachment actions, often above a keyboard | TextField with a vertical axis, lineLimit, and safeAreaInset(edge: .bottom) | Do not bake the keyboard height into the layout |
| Email, password, phone, URL, or code field variants | TextField or SecureField with textContentType, keyboardType, autocapitalization, and submitLabel | Preserve autofill and privacy semantics |
| Grouped rows with a swipe reveal | List rows with swipeActions | Do not draw the revealed buttons |
| Sheet with a grabber, half-height variant, or inspector | sheet with presentationDetents and presentationDragIndicator, or inspector | Avoid fixed overlay heights and hand-built grabbers |
| Centered symbol, title, and subtitle on an otherwise empty screen | ContentUnavailableView | Also use for search with no results |
| Color swatch picker | ColorPicker | |
| Face ID or Touch ID prompt | LocalAuthentication request | The system draws the prompt |
| Frame named Map with pins or route geometry | Map from MapKit, only after asking | Adds live data and may need location permission |

## Capabilities need opt-in
- A map, camera view, sign-in screen, or network-backed list implies a capability the design cannot confirm. Ask before adding MapKit, camera, location, authentication, or networking. Group the question by capability with the affected frames rather than asking per layer.
- If the user accepts one that needs a purpose string, use the protected-resources skill.

## Surfaces, blur, and glass
Figma's Glass effect is a GLASS record in a node's effects. get_design_context, get_metadata, and SVG or PNG exports all drop it and show an ordinary translucent rectangle with the node's blend mode and fills. Only use_figma can see it, so check for it before mapping any surface.

After get_design_context, load the figma-use skill and run one read-only use_figma script per chosen frame that lists every visible node carrying a visible GLASS effect. Switch to the frame's page first, because a frame fetched by ID on an unloaded page has no children to search. Effect styles count, because a node's effects reflect its applied style.

```js
const frame = await figma.getNodeByIdAsync("151:546")
let page = frame
while (page.type !== 'PAGE') page = page.parent
await figma.setCurrentPageAsync(page)
const hasGlass = n => n.visible && 'effects' in n && n.effects.some(e => e.type === 'GLASS' && e.visible)
const nodes = frame.findAll(hasGlass)
if (hasGlass(frame)) nodes.unshift(frame)
return Promise.all(nodes.map(async n => {
  let instance = null
  for (let p = n; p && p.type !== 'PAGE' && !instance; p = p.parent) if (p.type === 'INSTANCE') instance = p
  const main = instance && await instance.getMainComponentAsync()
  const set = main && main.parent && main.parent.type === 'COMPONENT_SET' ? main.parent.name : null
  return { id: n.id, name: n.name, type: n.type, cornerRadius: n.cornerRadius, fills: n.fills,
    component: main ? { name: set || main.name, library: main.remote } : null }
}))
```

- The component field is the nearest instance enclosing the glass, which says who owns the surface. Glass inside an Apple UI kit component, such as its toolbars, tab bars, buttons, and Liquid Glass containers, belongs to a system control that draws its own glass, so map the control and add nothing. Glass with no component, or from a local component, is a custom surface.
- A custom node the script returns is glass, whatever the design context shows for it. Its shape still comes from the node type and corner radii. A solid fill on it is a tint, so pass the color to the glass style instead of drawing it underneath.
- Never export a GLASS node as an image asset. The export loses the effect, and the image would freeze a surface that has to refract whatever scrolls behind it. Build the view and export only the children that are real artwork.
- Choose by role. A floating interactive surface the system does not own gets glassEffect. One the system already draws as glass, such as a toolbar button or tab bar, gets the plain control. A passive translucent panel gets the closest single Material. A blur that is part of artwork stays a custom effect.
- A Material already includes blur and tint. Do not layer the Figma tint fill on top of it.
- A blur applied to a layer's own pixels is image blur, not glass. An opaque fill with only a drop shadow is a raised surface, not glass.
- Blur radii and the Glass effect's light, refraction, depth, dispersion, and frost values do not convert to SwiftUI. Pick the material or glass variant that looks closest and do not copy the numbers.
- Text with Plus Lighter or similar blend modes over a translucent surface is vibrancy. Use .primary or .secondary foreground styles, not the sampled white.

## Flattened SF Symbols
Design context labels a symbol with Image(systemName:) only while it is still a text glyph. Once a designer outlines or flattens one, it arrives as a vector or boolean group whose layer name is the glyph's single private-use character, U+100000 or above, which renders as a box or as nothing. That layer is still an SF Symbol, so never trace it as a path or pick a lookalike from the screenshot. List the glyphs with one read-only use_figma script per frame, then look each codepoint up in the sf-symbols-catalog skill's index:

```js
const frame = await figma.getNodeByIdAsync("151:546")
let page = frame
while (page.type !== 'PAGE') page = page.parent
await figma.setCurrentPageAsync(page)
const isGlyphName = n => /^[\u{100000}-\u{10FFFD}]$/u.test(n.name)
return frame.findAll(isGlyphName).map(n => ({
  id: n.id, type: n.type, parent: n.parent.name, codepoint: n.name.codePointAt(0).toString(16)
}))
```

- Layers that share a codepoint are the same symbol, so resolve each codepoint once.
- When the index has no row for a codepoint, follow the catalog skill's guidance, check the layer's ancestors for a dotted symbol name, and otherwise leave a labeled placeholder and tell the user which codepoint you could not resolve.

## Shapes and effects
- Keep the node type. An ellipse with equal sides is Circle, an unequal ellipse is Ellipse, and a rounded rectangle keeps its actual corner radii. Do not infer the primitive from a corner-radius value.
- Attach a shadow to the background shape and place content above it. A shadow on a whole subtree makes every image and glyph cast a halo.
- Clip only a panel's content to its rounded shape. Clipping the whole view also clips its shadow.

## Assets in a Project.json project
- Non-Swift files under App/ are copied flat into the bundle root, so two frames that both export image.png collide and break the build. Name each downloaded asset with its frame and node ID, for example Profile-151-546-avatar.png, or add it to Assets.xcassets under a unique name.
- Use monospacedDigit for counters, timers, and prices that update in place.
- Design context turns Apple UI kit glyphs into Image(systemName:) names. Verify each one exists on the app's minimum OS with the sf-symbols-catalog skill before writing the view, and use the same skill to pick a symbol for a non-Apple icon that clearly matches one.

## Apple's UI kit
Apple publishes an official iOS and iPadOS 27 UI kit for Figma at https://www.figma.com/community/file/1651309003795292092/ios-and-ipados-27. Layers that come from it are Apple components and map to system controls and colors; layers from other kits stay literal. Its 27.1 update adds iPhone Duo bezels, a keyboard, and toolbar, tab bar, and status bar components, so a Duo design built on it shows where the vertical bar and safe areas fall. Point the user at it when they want to design iPhone or iPad screens in Figma before importing them.

The kit's Pane controls instance is the Duo's vertical bar, and it is system chrome. It is a narrow column along the outer edge of a pane holding a Status bar instance with the Dynamic Island, time, and levels, and a Controls slot of round Buttons groups, sometimes with a vertical Tab Bar. iOS builds that column from the app's toolbar and tab bar in every pose that moves bars to the side, so omit the column and never draw a vertical stack of glass buttons. Read its contents as toolbar evidence instead: the top group holds the navigation and top-bar items, the bottom group holds the bottom-bar items and tabs, and each button's symbol becomes a toolbar item or Tab in the pane's NavigationStack or TabView. A horizontal bar that stays inside a pane, such as a list header with its own buttons, is that pane's own toolbar and maps the same way.

## Where this skill overrides the Figma skills
- Do not build screens the design does not contain. An add or edit affordance gets a labeled placeholder, not an invented form. Ask the user before designing a missing destination.
- Do not persist flow state such as an onboarding flag without asking. Prototype state often only drives a demo.
- Marketing artwork, mockups, and fixed-ratio compositions are not app screens. Keep their artwork layers, masks, and coordinates literal instead of converting them to native controls or materials.
- A literal color from a non-Apple kit stays literal. Map to a system background only when the layer comes from an Apple component.
- When asking about a custom font or emoji, present both options neutrally and preserve the source if the user does not answer.
