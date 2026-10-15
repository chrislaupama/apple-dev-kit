<!--
{
  "documentType" : "article",
  "framework" : "Human Interface Guidelines",
  "identifier" : "/design/Human-Interface-Guidelines/gyro-and-accelerometer",
  "metadataVersion" : "0.1.0",
  "role" : "article",
  "title" : "Gyroscope and accelerometer"
}
-->

# Gyroscope and accelerometer

On-device gyroscopes and accelerometers can supply data about a device’s movement in the physical world.

## Discussion

![A sketch of a gyroscope, suggesting movement. The image is overlaid with rectangular and circular grid lines and is tinted purple to subtly reflect the purple in the original six-color Apple logo.](images/com.apple.HIG/inputs-gyroscope-intro@2x.png)

You can use accelerometer and gyroscope data to provide experiences based on real-time, motion-based information in apps and games that run in iOS, iPadOS, and watchOS. tvOS apps can use gyroscope data from the Siri Remote. For developer guidance, see <doc://com.apple.documentation/documentation/CoreMotion>.

## Best practices

**Use motion data only to offer a tangible benefit to people.** For example, a fitness app might use the data to provide feedback about people’s activity and general health, and a game might use the data to enhance gameplay. Avoid gathering data simply to have the data.

> Important: If your experience needs to access motion data from a device, you must provide copy that explains why. The first time your app or game tries to access this type of data, the system includes your copy in a permission request, where people can grant or deny access.

**Outside of active gameplay, avoid using accelerometers or gyroscopes for the direct manipulation of your interface.** Some motion-based gestures may be difficult to replicate precisely, may be physically challenging for some people to perform, and may affect battery usage.

## Platform considerations

*No additional considerations for iOS, iPadOS, macOS, tvOS, visionOS, or watchOS.*

## Resources

#### Related

[Feedback](feedback.md)

#### Developer documentation

<doc://com.apple.documentation/documentation/CoreMotion/getting-processed-device-motion-data> — Core Motion

#### Videos

  <doc://com.apple.documentation/videos/play/wwdc2021/10287>



---

Copyright &copy; 2026 Apple Inc. All rights reserved. | [Terms of Use](https://www.apple.com/legal/internet-services/terms/site.html) | [Privacy Policy](https://www.apple.com/privacy/privacy-policy)