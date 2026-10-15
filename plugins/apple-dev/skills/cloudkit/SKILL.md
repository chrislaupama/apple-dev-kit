---
name: cloudkit
description: Use this skill when a task involves CloudKit — adding iCloud sync or storage to an app (SwiftData, Core Data, CKSyncEngine, or direct CKDatabase), creating or changing a container schema, inspecting or editing container records, preparing a CloudKit app for TestFlight or the App Store, or debugging sync. Not needed for local-only persistence with no iCloud involvement.
---

# CloudKit

## Authorization

cktool needs tokens saved to the keychain before it runs. The user creates them in CloudKit Console (https://icloud.developer.apple.com → account menu → Manage Tokens): a management token for schema and container work, and a user token for record commands. Ask them to run `xcrun cktool save-token --type management` (and `--type user` when needed) themselves in their own terminal, where it prompts for the token — never ask for a token in chat or pass one on the command line. Once saved, cktool runs without auth flags. If a cktool command later fails with a missing-token or expired-session error, ask them to save a fresh token.

## Schema workflow

The project's schema lives in CloudKitSchema.ckdb at the project root — keep it committed as the versioned source of truth.

- `xcrun cktool export-schema --team-id <team> --container-id <container> --environment development --output-file CloudKitSchema.ckdb` writes a container's schema to the file; `xcrun cktool validate-schema --team-id <team> --container-id <container> --environment development --file CloudKitSchema.ckdb` checks the file against a container.
- To apply the file to the development environment, use cktool directly:

  ```
  xcrun cktool import-schema --team-id <team> --container-id <container> --environment development --file CloudKitSchema.ckdb
  ```

- Direct cktool commands need --team-id. List teams with `xcrun cktool get-teams` (after saving the management token) and use the team that owns the container.
- `xcrun cktool reset-schema` resets the development environment to match production and deletes all development data. Destructive — confirm with the user first.

## Environments

- Development-signed builds (including the simulator) use the development environment; TestFlight and App Store builds use production.
- Only development supports just-in-time schema creation: saving a record can create record types and fields on the fly. Production never does.
- Before a TestFlight or App Store release, deploy the schema to production in CloudKit Console — the Console is the only way to deploy; cktool's schema commands operate on development. Send the user to https://icloud.developer.apple.com/dashboard/database/teams/<team-id>/containers/<container-id>/environments/DEVELOPMENT/types and have them choose Deploy Schema Changes from the sidebar menu (undeployed changes show as Modified there). Skipping this is the classic failure where the app works in development but syncs nothing in TestFlight.
- Production schema changes are additive only: deployed record types and fields can't be deleted or renamed. Design names carefully before deploying; indexes can still be added or removed.

## Project setup

Never derive a container identifier from a placeholder bundle ID — containers are permanent once registered with a team. If PRODUCT_BUNDLE_IDENTIFIER is still a placeholder (such as Bitrig's app.bitrig.<anything>.<UUID>), follow the xcodegen-project skill's Bundle Identifier rules first (reuse the App Store Connect bundle ID if there is one, otherwise ask the user for a reverse-DNS ID they own), then update everything derived from it. Never invent a bundle ID yourself.

Each target that uses CloudKit needs these entitlements (in a Project.json project, via the target's entitlements block in Project.json, same shape as App Groups; otherwise in the target's .entitlements file):

```json
"com.apple.developer.icloud-services": ["CloudKit"],
"com.apple.developer.icloud-container-identifiers": ["iCloud.<bundle-id>"]
```

Derive the container identifier from the real PRODUCT_BUNDLE_IDENTIFIER — container identifiers are globally owned, like App Groups. Use the exact same string in code and in cktool calls. Apps that rely on push-driven sync (SwiftData/Core Data mirroring, CKSyncEngine, subscriptions) also need the aps-environment entitlement set to "development" in the same entitlements block, plus the remote-notification background mode ("UIBackgroundModes": ["remote-notification"] in the target's info properties). No APNs key is needed — CloudKit delivers its own pushes. See the notifications skill for details.

CloudKit's pushes reach the app only; they cannot drive WidgetKit push updates, which need a token the app's own server sends to. A widget backed by CloudKit data refreshes from its timeline and from WidgetCenter.reloadAllTimelines() after the app syncs, so don't add aps-environment to a widget extension for CloudKit's sake — it does nothing there.

cktool operates on containers that already exist under the team. Registering the app's capabilities with `xc provision`, as the capability-provisioning skill describes, creates a missing container under the team in the target's `DEVELOPMENT_TEAM`. Use that same team as cktool's `--team-id`.

## Choosing an API

Pick the CloudKit API based on how the app stores data, keeping its existing persistence:

- The app uses SwiftData → turn on its built-in sync by passing cloudKitDatabase to ModelConfiguration (.automatic uses the first container in the entitlements).
- The app uses Core Data → use its built-in sync, NSPersistentCloudKitContainer.
- The app has a custom local store (files, SQLite, …) that should sync → CKSyncEngine.
- The need isn't syncing a local store — public data, sharing between users, cloud-only storage → CKDatabase and CKRecord directly.

The first two mirror the app's models into CloudKit records automatically, which imposes model rules: every attribute optional or given a default, every relationship optional with an inverse, no unique constraints. A model that breaks them fails at container setup with errors that name the store, not the model. Mirrored records land in the private database in zone com.apple.coredata.cloudkit.zone as CD_<Model> record types — that's what to expect in cktool output. In development the mirrored schema is created at runtime as records are saved, so save an instance of each model (or use Core Data's initializeCloudKitSchema) before exporting; otherwise the export will be missing record types.

## Records and debugging

- Record commands (query-records, create-record, delete-record, delete-records) need the user token — request token_type "user" first.
- Queries require queryable indexes. The error "Field 'recordName' is not marked queryable" means the record type needs a queryable index on recordName — add it in the schema file and import, or in CloudKit Console.
- Private-database cktool commands operate on the private database of the account that issued the user token, not the simulator's iCloud account — you can't inspect a test account's private data unless it's the same account.
- In the simulator, the private database requires an iCloud sign-in in the simulator's Settings, and sync pushes don't arrive — relaunch or foreground the app to trigger a sync before concluding sync is broken.
