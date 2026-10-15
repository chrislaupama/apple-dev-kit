---
name: app-store-connect
description: Use this skill when a task involves TestFlight or the App Store — uploading builds, App Store listing metadata and localizations, release notes, screenshots, pricing, age rating, in-app purchases and subscriptions, App Privacy labels, App Review details and submission, or a project's appStoreConnect/ (Bitrig) or metadata/ (asc) listing files. Uses the `asc` App Store Connect CLI.
---

# App Store Connect with `asc`

`asc` (App Store Connect CLI, `brew install asc`) talks to the App Store Connect API. It prints JSON when piped, which is what you want; add `--output table` only for showing the user. Every command has `--help` with examples, and `asc search "<what you want>"` finds commands. When the `asc` skill pack is installed (skills named `asc-*`, such as asc-release-flow, asc-metadata-sync, asc-submission-health, asc-signing-setup, asc-testflight-orchestration), load the matching one for command detail. This skill adds the project-specific rules.

## Ground rules

- **Auth is the user's job.** If `asc auth status` shows no credentials, ask the user to create a team API key (App Store Connect → Users and Access → Integrations → App Store Connect API, Admin or App Manager role), save the `.p8` to `~/.appstoreconnect/private_keys/`, and run in their own terminal:
  `asc auth login --name personal --key-id <KEY_ID> --issuer-id <ISSUER_ID> --private-key ~/.appstoreconnect/private_keys/AuthKey_<KEY_ID>.p8 --network`
  Never ask for key contents, passwords or 2FA codes in chat. Never pass `--include-sensitive`.
- **Preview, then confirm.** Run mutating commands with `--dry-run` first and show the user the plan. Anything that publishes, submits, deletes or notifies testers (`--submit`, `--confirm`, `--allow-deletes`, `--replace`, `--notify`) needs the user's explicit go-ahead for that action in this conversation.
- **Telemetry** is off on this Mac (`asc telemetry status`). If it ever shows enabled, run `asc telemetry disable`.
- **The app ID.** Look it up with `asc apps list --bundle-id <bundle id>` (or `appId` in a Bitrig project's `appStoreConnect/lock.json`) and export `ASC_APP_ID` for the session so commands don't need `--app`.
- `asc status --app <id>` is the one-screen overview of where a release stands; start there when the user asks "where are we?".

## Bitrig projects: the appStoreConnect/ folder

Projects from Bitrig have an `appStoreConnect/` folder. It is Bitrig's own format and nothing syncs it anymore. [references/listing-files.md](references/listing-files.md) still documents it. Its field shapes, App Store limits, placement groups, first-submission checklist, review-screenshot rules and App Privacy worksheet remain good knowledge.

To move such a project onto `asc`:
1. `asc metadata pull --app <id> --dir ./metadata` (add `--platform` when the app ships on several). App Store Connect is the source of truth, so pulling is safer than converting Bitrig's files.
2. Compare the pulled text with `appStoreConnect/` and tell the user about any local edits Bitrig never pushed.
3. Ask before deleting `appStoreConnect/`. Products, pricing and screenshots now live only in App Store Connect and are managed with `asc iap`, `asc subscriptions`, `asc pricing` and `asc screenshots`.

## Listing text

Canonical files: `metadata/app-info/<locale>.json` (name, subtitle, privacyPolicyUrl…) and `metadata/version/<version>/<locale>.json` (description, keywords, promotionalText, supportUrl, marketingUrl, whatsNew).

```bash
asc metadata validate --dir ./metadata --output table
asc metadata push --app <id> --version <v> --dir ./metadata --dry-run --output table
asc metadata push --app <id> --version <v> --dir ./metadata          # after the user approves
```

Limits: name ≤ 30, subtitle ≤ 30, promotionalText ≤ 170, keywords ≤ 100 (comma-separated, one string), description and whatsNew ≤ 4000. Keep every locale consistent, translating when a shared field changes. Leave whatsNew out of a platform's first version, since App Store Connect rejects it there. Copyright: `asc versions update --version-id <id> --copyright "2026 Name"`. Categories, age rating, content rights and pricing have their own groups: `asc categories`, `asc age-rating`, `asc apps content-rights`, `asc pricing`.

A listing has one version per platform (iOS, which also covers iPad and Apple Watch; macOS; tvOS; visionOS). Name, subtitle, privacy URL, categories, age rating, price and products are shared across platforms. Ask which platform the user means when it isn't clear.

## New app record

There is no API for creating apps. Either the user creates it at appstoreconnect.apple.com → Apps → + (name, primary language, bundle ID, SKU), or they run `asc web apps create --name "…" --bundle-id … --sku …` **in their own terminal**: it signs in with their Apple Account password and 2FA, which must never pass through you. Settle the permanent bundle ID first (see the xcodegen-project skill). `asc bundle-ids create` registers it when needed.

## Builds and TestFlight

Bump `CURRENT_PROJECT_VERSION` for every upload and keep `MARKETING_VERSION` at the version being released. Set `ITSAppUsesNonExemptEncryption` (usually `false`) in Info.plist to skip the export-compliance question. Then:

```bash
xc gen                                                                  # Project.json projects
asc publish testflight --app <id> --project Project.xcodeproj --scheme <App> --version <v> --wait --output json
asc publish testflight --app <id> --build-id <BUILD_ID> --group "<Group>" --wait     # distribute an existing build
```

`publish testflight` archives, exports, uploads and waits for processing; add `--group` to distribute. Add `--notify` only on request. Use `--platform MAC_OS --pkg-path …` for Mac apps. Builds take minutes to process, so run these in the background. If upload says the app record is missing, see "New app record". Signing failures: check `DEVELOPMENT_TEAM` and that an Apple account is signed in to Xcode, or see the asc-signing-setup skill.

## Screenshots

Capture in Xcode's Simulator (see the simulator-use skill) with the status bar overridden, on the device whose screen natively produces the set:

| Set (`--device-type`) | Capture on | Needed when |
|---|---|---|
| `IPHONE_69` | newest Pro Max iPhone (1320×2868) | every iOS app |
| `IPAD_PRO_3GEN_129` | 13-inch iPad Pro (2064×2752) | the app supports iPad |
| `WATCH_ULTRA` | newest Apple Watch Ultra | the project has a watch app |
| `APPLE_TV` | Apple TV 4K | tvOS |
| `IPHONE_DUO` | iPhone Duo | only if the user wants it |

`asc screenshots sizes --all` lists every accepted size. Mac (`DESKTOP`) and Vision Pro screenshots can't be captured in the Simulator, so ask the user for them. Choose 3–5 screens that show the app at its best with realistic content, the same screens in the same order on every device, never resized; recapture on the right device instead. Then:

```bash
asc screenshots validate --path ./screenshots/en-US/iphone --device-type IPHONE_69
asc screenshots upload --app <id> --version <v> --locale en-US --path ./screenshots/en-US/iphone --device-type IPHONE_69 --dry-run
```

Replacing an existing set needs `--replace --confirm`, which deletes the old screenshots, so get the user's OK.

## In-app purchases and subscriptions

Create with `asc iap setup …` / `asc subscriptions setup …` (both reconcile complete metadata and pricing; see `--help`), then `asc iap pricing …` / `asc subscriptions pricing …`. Review screenshots: `asc iap review-screenshots …` / `asc subscriptions review screenshots create --subscription-id <id> --file review.png`. A screenshot of the app's purchase screen works.

- A product stays in Missing Metadata until localizations, pricing and the review screenshot are all present. StoreKit returns nothing for it, even in the sandbox.
- Price a subscription in a base territory and let it equalize everywhere. A single-territory price keeps it in Missing Metadata.
- The first product must be submitted together with an app version. `asc review doctor --app <id>` and `asc validate` say what's missing. The asc-submission-health skill covers multi-item submissions.
- If products still don't load once Ready to Submit, have the user check the Paid Applications agreement (`asc agreements`, or App Store Connect → Business).
- Sandbox purchases only complete on a device or in TestFlight. Local testing uses a StoreKit configuration file run from Xcode (see the purchases skill). Manage sandbox testers with `asc sandbox`.

## App Privacy label

Apple has no API for it; the user fills it in and clicks **Publish** at `https://appstoreconnect.apple.com/apps/<appId>/distribution/privacy`. Before sending them there, work out the answers from the project (backend schema, auth, linked SDKs, uploads). Give them a worksheet, one line per data type with purpose, linked-to-identity and tracking, as described in the reference's App privacy section. `asc validate --deep` reports whether it's published when a web session is cached.

## Review and submission

1. Review details: `asc review details-for-version --version-id <id>`, then `details-create` / `details-update` with contact name, email, a real phone number (`+` and country code) and `--notes`. When sign-in gates content, the reviewer needs working demo credentials or a note saying why none are needed. Offer to create the demo account when you can reach the backend.
2. `asc validate --app <id> --version <v> --strict` and fix the ordered remediation list until it's clean.
3. With the user's explicit go-ahead: `asc review submit --app <id> --version <v> --latest --wait --confirm` (run with `--dry-run` first), or `asc publish appstore … --submit --confirm` to upload and submit in one go.
4. Track with `asc review status --app <id>` / `asc status --app <id> --until review-done`.

## Anything else

TestFlight groups, testers and What to Test (`asc testflight`, `asc builds`), customer reviews (`asc reviews`), crash feedback, analytics, pricing by territory, signing assets: find the command with `asc search`, read its `--help`, and prefer read-only commands unless the user asked for a change. `asc api` makes raw API calls for anything not covered.
