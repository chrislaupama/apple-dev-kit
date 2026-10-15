# apple-dev-kit (private)

A personal Claude Code plugin for building SwiftUI apps without Bitrig. It is adapted from the skills and system prompt bundled in Bitrig 0.29.0. **For personal use only; don't publish or share it.**

## What's inside (`plugins/apple-dev/`)

| Path | What it is |
|---|---|
| `context/swiftui-guidelines.md` | Bitrig's system prompt, adapted. A SessionStart hook injects it, only in Apple-platform projects. |
| `bin/xc` | Replaces the `bitrig` CLI: `xc preview / build / test / provision / logs / sims / list / gen`. Uses XcodeGen + xcodebuild + simctl. |
| `skills/` | 25 skills. Guidance skills are copied as-is; build, project, simulator, provisioning, CloudKit, Supabase, push and App Store Connect skills are rewritten to drop Bitrig's tools. |
| `skills/sf-symbols-catalog/build-index.py` | Rebuilds the SF Symbols index from macOS's own catalog (run after macOS updates). |
| `reference/bitrig-system-prompt.original.md` | The unmodified Bitrig prompt, for comparison. |
| `bin/apple-api` | Looks up APIs and their availability in the installed SDK's Swift interfaces (`apple-api SwiftUI 'func glassEffect'`, `apple-api SwiftUI --new 27`). Answers "does this exist in my SDK?" offline; Xcode's `DocumentationSearch` covers the prose docs. |

`plugins/xcode-integration/` is Apple's own Claude plugin from Xcode 27. It provides the Xcode MCP server (`xcrun mcpbridge`) with 52 tools and 15 Apple-authored skills. `scripts/sync-xcode-plugin.sh` copies it from Xcode; run that again after every Xcode update. Its tools need Xcode running with the project open.

Dropped: `bitrig-product-support`, `bitrig-github-project`, `selected-ui-elements` (Bitrig-only features).

## Install

```bash
claude plugin marketplace add /path/to/apple-dev-kit
claude plugin install apple-dev@chris-local
claude plugin install xcode-integration@chris-local
```

Needs Xcode, XcodeGen (`brew install xcodegen`) and, for TestFlight and the App Store, the `asc` CLI (`brew install asc`, then `asc telemetry disable` and `asc auth login …` with an App Store Connect API key).

Recommended alongside: the asc skill pack (MIT), which has command-level skills that the app-store-connect skill defers to:

```bash
claude plugin marketplace add rorkai/app-store-connect-cli-skills
claude plugin install asc@rorkai
```

Also install the third-party plugins Bitrig bundled from their upstream sources: RevenueCat (`github.com/RevenueCat/ai-toolkit`) and Supabase agent skills (`npx skills add supabase/agent-skills`).

## Gaps compared with Bitrig

- App Store Connect goes through `asc` instead of Bitrig's sync. Bitrig's `appStoreConnect/` folder is replaced by asc's `metadata/` folder (`asc metadata pull`). Creating the app record and publishing the App Privacy label still need the website (or `asc web apps create`, run by you).
- No CloudKit token helper: the user saves cktool tokens themselves (`xcrun cktool save-token`).
- No Supabase secret sheet: the user pastes secrets in the Supabase dashboard.
- Simulator control comes from Xcode's device-interaction tools (Xcode must be open); there's no click-to-select element context.
- No simulator camera shim and no app-icon generator. Docs come from Xcode's `DocumentationSearch` tool (needs Xcode running), Apple's what's-new skills and `apple-api`.
