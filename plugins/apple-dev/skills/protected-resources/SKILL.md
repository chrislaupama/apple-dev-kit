---
name: protected-resources
description: Use when an app accesses a protected resource or needs an Info.plist usage-description purpose string, such as for location, camera, microphone, photos, contacts, calendars, motion, or speech recognition.
---

# Protected Resources

## Purpose Strings
- When writing a purpose string (the Info.plist usage description for a protected resource), keep in mind these rules:
  - The purpose string is shorter than 4,000 bytes. Typical purpose strings are one complete sentence, but you can provide additional information to help a person make the right decision about sharing personal information.
  - The purpose string has the proper type that the corresponding key requires, typically a string.
  - The purpose string provides a description that’s accurate, meaningful, and specific about why the app needs to access the protected resource.
- Here are examples of good purpose strings:
  - Your location is used to show your position on the map, get directions, estimate travel times, and improve search results.
  - This app requires camera access to capture your site photos.
