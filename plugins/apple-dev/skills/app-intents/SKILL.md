---
name: app-intents
description: Use when adding or modifying App Intents, App Shortcuts, Siri actions, Spotlight actions, Action Button actions, or parameters exposed through those systems.
---

# App Intents

### App Intents and Siri Shortcuts
- Define `AppIntent` types and an `AppShortcutsProvider` in the app target — Siri Shortcuts need no extension target or App Group; the intent runs in the app's own sandbox.
- An intent does not share in-memory state with the running UI (it may run in a separate background instance of the app). Persist through one store, and have the intent read-modify-write the latest saved state by id — don't write a stale in-memory array over it.
- Make the UI observe the store for external changes, so when the intent changes data, the UI updates to show it.
- Every phrase in an `AppShortcut` must contain the `\(.applicationName)` token — it's required to build and Siri routes voice by app name. Tell the user the spoken phrase includes the app name (e.g. "Add note in MyNotesApp"); a bare phrase like "Add note" won't trigger by voice.
- Only `AppEnum`/`AppEntity` parameters can be interpolated into a phrase. A free-text `String` parameter can't — leave it out of the phrase and collect it with `@Parameter(requestValueDialog:)`.
- Siri voice invocation is unreliable in the Simulator, even though the shortcut still appears in Spotlight and the Shortcuts app there. If the user says voice doesn't trigger it, have them test on a real device — don't keep rewording the phrases.
