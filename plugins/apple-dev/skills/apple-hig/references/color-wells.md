<!--
{
  "documentType" : "article",
  "framework" : "Human Interface Guidelines",
  "identifier" : "/design/Human-Interface-Guidelines/color-wells",
  "metadataVersion" : "0.1.0",
  "role" : "article",
  "title" : "Color wells"
}
-->

# Color wells

A color well lets people adjust the color of text, shapes, guides, and other onscreen elements.

## Discussion

![A stylized representation of a color-selection popover extending down from an expanded button. The image is tinted red to subtly reflect the red in the original six-color Apple logo.](images/com.apple.HIG/components-color-well-intro~dark@2x.png)

A color well displays a color picker when people tap or click it. This color picker can be the system-provided one or a custom interface that you design.

## Best practices

**Consider the system-provided color picker for a familiar experience.** Using the built-in color picker provides a consistent experience, in addition to letting people save a set of colors they can access from any app. The system-defined color picker can also help provide a familiar experience when developing apps across iOS, iPadOS, and macOS.

## Platform considerations

*No additional considerations for iOS, iPadOS, or visionOS. Not supported in tvOS or watchOS.*

### macOS

When people click a color well, it receives a highlight to provide visual confirmation that it’s active. It then opens a color picker so people can choose a color. After they make a selection, the color well updates to show the new color.

Color wells also support drag and drop, so people can drag colors from one color well to another, and from the color picker to a color well.

## Resources

#### Related

[Color](color.md)

#### Developer documentation

<doc://com.apple.documentation/documentation/UIKit/UIColorWell> — UIKit

<doc://com.apple.documentation/documentation/UIKit/UIColorPickerViewController> — UIKit

<doc://com.apple.documentation/documentation/AppKit/NSColorWell> — AppKit

[Color Programming Topics](https://developer.apple.com/library/content/documentation/Cocoa/Conceptual/DrawColor/DrawColor.html)

---

Copyright &copy; 2026 Apple Inc. All rights reserved. | [Terms of Use](https://www.apple.com/legal/internet-services/terms/site.html) | [Privacy Policy](https://www.apple.com/privacy/privacy-policy)