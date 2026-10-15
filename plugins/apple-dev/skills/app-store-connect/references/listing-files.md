# App Store Listing Files

> **Note (Bitrig projects):** this reference was written for Bitrig's listing sync, which no longer runs. The layout, field shapes, limits and checklists below still describe the `appStoreConnect/` folder and what App Store Connect requires, but mentions of importing, validating, applying, refreshing and the delete opt-in refer to Bitrig tools that are gone. The accompanying SKILL.md says how to apply changes now.

An appStoreConnect/ folder at the project root mirrors the app's App Store listing as JSON and text files. The files are the desired state: edit them to describe what the listing should look like. Nothing touches App Store Connect until the changes are applied. This reference covers the files and the sync model; the accompanying SKILL.md defines the commands for the workflow steps — importing the listing, validating, and applying.

If the project has no appStoreConnect/ folder, never create it by hand: the folder must start as an import of the live listing so its files and sync state match App Store Connect. The accompanying SKILL.md names the command that runs the import.

## Layout

The file path IS the resource identity — platform, resource type, product id, and locale are all encoded in the path. There is no manifest or registry: adding a locale, an in-app purchase, or a subscription means adding files. Removing a previously-synced app-info or product localization, a placement manifest, or a whole in-app purchase, subscription, or subscription group, surfaces a warning and is left alone by default; deleting it from App Store Connect requires the explicit delete opt-in named in the accompanying SKILL.md. App Store version localizations are the exception — deleting one of those directories doesn't sync, so remove it on the App Store Connect website.

    appStoreConnect/
    ├── app.json                    bundleId, primaryLocale, contentRightsDeclaration
    ├── appInfo/
    │   ├── shared.json             primaryCategory, secondaryCategory + subcategories
    │   ├── ageRating.json          age-rating questionnaire answers
    │   └── localizations/
    │       └── {locale}.json       name, subtitle, privacyPolicyUrl
    ├── appStoreVersion/
    │   └── {platform}/             iOS, macOS, tvOS, visionOS (exact case)
    │       ├── version.json        versionString, copyright, releaseType, earliestReleaseDate
    │       ├── review/
    │       │   ├── review.json     App Review contact info and demo account
    │       │   └── notes.txt       notes for the App Review team
    │       └── localizations/
    │           └── {locale}/
    │               ├── localization.json    keywords, supportUrl, marketingUrl, promotionalText
    │               ├── description.txt
    │               ├── whatsNew.txt
    │               └── placements/          screenshots, app previews, header and search results media (see Placements)
    ├── inAppPurchases/
    │   └── {productId}/            the product id (immutable) is the directory name
    │       ├── inAppPurchase.json  name, inAppPurchaseType, familySharable
    │       ├── reviewNote.txt      note for the App Review team (optional)
    │       ├── reviewScreenshot/   screenshot required to submit the product for review (see Review screenshots)
    │       ├── pricing.json        baseTerritory, manualPrices (same shape as app pricing.json)
    │       ├── availability.json   availableInNewTerritories, availableTerritories
    │       └── localizations/
    │           └── {locale}.json   name, description
    ├── subscriptionGroups/
    │   └── {referenceName}/        the group's reference name is the directory name
    │       ├── localizations/
    │       │   └── {locale}.json   name, customAppName
    │       └── subscriptions/
    │           └── {productId}/
    │               ├── subscription.json         name, subscriptionPeriod, groupLevel, familySharable
    │               ├── reviewNote.txt            note for the App Review team (optional)
    │               ├── reviewScreenshot/         screenshot required to submit the product for review (see Review screenshots)
    │               ├── pricing.json              baseTerritory, prices: [{ territory, customerPrice }]
    │               ├── availability.json         availableInNewTerritories, availableTerritories (optional)
    │               ├── introductoryOffers.json   offers: [...]
    │               ├── promotionalOffers.json    offers: [...] (optional)
    │               ├── winBackOffers.json        offers: [...] (optional)
    │               ├── offerCodes.json           offerCodes: [...] (optional)
    │               └── localizations/
    │                   └── {locale}.json         name, description
    ├── pricing.json
    ├── availability.json
    ├── subscriptionGracePeriod.json   billing grace period settings (optional)
    ├── promotedPurchases.json         products promoted on the App Store page, in display order (optional)
    └── lock.json                   machine-managed — NEVER edit

Locales use ASC locale codes like en-US, de-DE, ja. Platform directories are matched case-sensitively — iOS, not ios — so the folder stays portable to case-sensitive filesystems.

## Rules

- The folder may contain only the files in the Layout above. Never add anything else — no README, notes for the user, scratch files, or backups anywhere under appStoreConnect/. Every file maps to an App Store Connect resource, so an unrecognized file fails validation. Notes for the user belong in the conversation, not in files.
- Field names and enum values are Apple's App Store Connect API names, verbatim. If Apple calls it contentRightsDeclaration and accepts USES_THIRD_PARTY_CONTENT, that exact string goes in the file.
- The files decode strictly. A misspelled, invented, or missing required field fails the sync with an error naming the file and field. Never guess a file's shape from memory of the App Store Connect API — use the imported files and the Field shapes section below.
- Every sync — the initial import, a refresh from remote, an apply — rewrites the files in canonical form (alphabetically sorted keys, pretty-printed), so expect formatting and key order to change out from under an edit.
- Long-form fields Apple accepts line breaks in live as plain .txt files named after the exact field (description.txt, whatsNew.txt, notes.txt) next to the JSON holding the short fields. Each .txt file ends with exactly one trailing newline, which is canonical and not part of the field value — preserve it.
- Never edit lock.json. It records the App Store Connect state at the last sync and is how conflicting edits are detected; hand-editing it breaks conflict detection and can cause silent overwrites.
- A listing created before its app record exists has no lock.json and no imported files to mirror: write each file from the Field shapes section. Linking it to the record later keeps every value it sets as a pending change, except where the record already has a different value: those fields become conflicts to resolve.
- Before editing, read the existing files and mirror their shape. Don't invent fields — omitted optional fields are simply absent from the JSON.
- Respect App Store limits when writing content: name ≤ 30 characters, subtitle ≤ 30, promotionalText ≤ 170, keywords ≤ 100 (a single comma-separated string), description and whatsNew ≤ 4000.
- An app's name must be unique across the App Store. Apply sends name changes first, so a name another app already uses fails before anything else is pushed. When that happens, ask the user for a different name rather than inventing one.
- Don't create whatsNew.txt for a platform's first version. App Store Connect rejects What's New until a version has been released on that platform; add the file starting with the second version.
- Keep every locale consistent: when changing a field that exists in multiple localizations (unless asked to change just one), update all of them, translating appropriately.
- To start a new App Store version, bump versionString in version.json; the next apply creates the new version in App Store Connect. If the current remote version has not been submitted yet, changing versionString just renames it.

## Field shapes

Exact shapes for the fields a fresh import leaves empty. These lists are complete — fields not named here don't exist.

app.json — contentRightsDeclaration is DOES_NOT_USE_THIRD_PARTY_CONTENT or USES_THIRD_PARTY_CONTENT.

appStoreVersion/{platform}/version.json — releaseType is MANUAL, AFTER_APPROVAL, or SCHEDULED; SCHEDULED also needs earliestReleaseDate.

appInfo/shared.json — categories are App Store category IDs: BOOKS, BUSINESS, DEVELOPER_TOOLS, EDUCATION, ENTERTAINMENT, FINANCE, FOOD_AND_DRINK, GAMES, GRAPHICS_AND_DESIGN, HEALTH_AND_FITNESS, LIFESTYLE, MAGAZINES_AND_NEWSPAPERS, MEDICAL, MUSIC, NAVIGATION, NEWS, PHOTO_AND_VIDEO, PRODUCTIVITY, REFERENCE, SHOPPING, SOCIAL_NETWORKING, SPORTS, STICKERS, TRAVEL, UTILITIES, WEATHER.

    {
      "primaryCategory" : "FOOD_AND_DRINK",
      "secondaryCategory" : "UTILITIES"
    }

Only GAMES and STICKERS have subcategories (GAMES_PUZZLE, GAMES_CASUAL, …), given as primarySubcategoryOne, primarySubcategoryTwo, secondarySubcategoryOne, secondarySubcategoryTwo.

pricing.json — every manualPrices entry needs territory and customerPrice. customerPrice is a string and must exactly match one of Apple's price points for that territory (0, 0.99, 1.99, …). A free app:

    {
      "baseTerritory" : "USA",
      "manualPrices" : [
        {
          "customerPrice" : "0",
          "territory" : "USA"
        }
      ]
    }

Entries may also carry startDate and endDate for scheduled price changes. Apple derives all other territories' prices from the base price; those appear under derived in lock.json and are never written by hand.

availability.json — the app-level file. territories is a map keyed by territory code whose entries may carry available, releaseDate, and preOrderEnabled — it is NOT the availableTerritories list used by in-app purchase availability files. availableInNewTerritories true with an empty territories object means available everywhere:

    {
      "availableInNewTerritories" : true,
      "territories" : { }
    }

The file is authoritative only while the app has no availability yet: apply creates it from the file as written. Once availability exists in App Store Connect, the API can't change it (the territory endpoints reject the update), so apply treats any local edit to availability.json as a blocking issue. Make territory changes on the App Store Connect website, then refresh to pull them into the file.

appInfo/ageRating.json — App Store Connect validates the questionnaire as a whole, so answer every field. A benign utility app:

    {
      "advertising" : false,
      "ageAssurance" : false,
      "ageRatingOverrideV2" : "NONE",
      "alcoholTobaccoOrDrugUseOrReferences" : "NONE",
      "contests" : "NONE",
      "gambling" : false,
      "gamblingSimulated" : "NONE",
      "gunsOrOtherWeapons" : "NONE",
      "healthOrWellnessTopics" : false,
      "horrorOrFearThemes" : "NONE",
      "koreaAgeRatingOverride" : "NONE",
      "lootBox" : false,
      "matureOrSuggestiveThemes" : "NONE",
      "medicalOrTreatmentInformation" : "NONE",
      "messagingAndChat" : false,
      "parentalControls" : false,
      "profanityOrCrudeHumor" : "NONE",
      "sexualContentGraphicAndNudity" : "NONE",
      "sexualContentOrNudity" : "NONE",
      "unrestrictedWebAccess" : false,
      "userGeneratedContent" : false,
      "violenceCartoonOrFantasy" : "NONE",
      "violenceRealistic" : "NONE",
      "violenceRealisticProlongedGraphicOrSadistic" : "NONE"
    }

The string descriptor fields take NONE, INFREQUENT, or FREQUENT. ageRatingOverrideV2 takes NONE, NINE_PLUS, THIRTEEN_PLUS, SIXTEEN_PLUS, EIGHTEEN_PLUS, or UNRATED; koreaAgeRatingOverride takes NONE, FIFTEEN_PLUS, or NINETEEN_PLUS. Two more fields exist only for Kids-category apps: kidsAgeBand and developerAgeRatingInfoUrl. Do not write the deprecated ageRatingOverride field.

inAppPurchases/{productId}/inAppPurchase.json — the directory name is the productId (immutable once created). inAppPurchaseType is CONSUMABLE, NON_CONSUMABLE, or NON_RENEWING_SUBSCRIPTION and can't change after creation. familySharable is a bool. A long-form reviewNote, if present, lives in reviewNote.txt beside this file, not inline. A screenshot for the App Review team, if present, lives in a reviewScreenshot/ directory beside this file (see Review screenshots).

    {
      "familySharable" : false,
      "inAppPurchaseType" : "NON_CONSUMABLE",
      "name" : "Pro Upgrade"
    }

inAppPurchases/{productId}/localizations/{locale}.json — name (≤ 30) and description (≤ 45).

inAppPurchases/{productId}/pricing.json — same shape as the app pricing.json above (baseTerritory plus manualPrices whose customerPrice matches a price point); Apple derives the other territories from the base, and they appear under derived in lock.json.

inAppPurchases/{productId}/availability.json — availableInNewTerritories is a bool; availableTerritories is an explicit list of territory codes, and the product can only be bought in the listed territories. The file is optional: omit it for a new product to leave it available in every territory (Apple's default), which is what a worldwide app usually wants. Write it only to deliberately restrict the product — this example limits sales to the United States:

    {
      "availableInNewTerritories" : true,
      "availableTerritories" : [ "USA" ]
    }

subscriptions live under subscriptionGroups/{referenceName}/subscriptions/{productId}/. The group's reference name is its directory name; the subscription's productId is its directory name (immutable).

subscription.json — subscriptionPeriod is ONE_WEEK, ONE_MONTH, TWO_MONTHS, THREE_MONTHS, SIX_MONTHS, or ONE_YEAR. groupLevel is an integer of at least 1 — the subscription's rank within its group (level 1 is the top tier). familySharable is a bool. A long-form reviewNote lives in reviewNote.txt beside it, and a screenshot for the App Review team, if present, in a reviewScreenshot/ directory beside it (see Review screenshots).

    {
      "familySharable" : false,
      "groupLevel" : 1,
      "name" : "Pro Monthly",
      "subscriptionPeriod" : "ONE_MONTH"
    }

subscriptionGroups/{referenceName}/localizations/{locale}.json — name and an optional customAppName (the app name shown on the subscription's management screen).

subscriptions/{productId}/localizations/{locale}.json — name and description.

subscriptions/{productId}/pricing.json — baseTerritory plus prices, a list of { territory, customerPrice }. Each customerPrice must match a subscription price point for that territory. With a baseTerritory, the entry for that territory is the baseline and every other territory the subscription is available in is priced by equalizing it, exactly as setting one price on the website does; entries for other territories override the equalized price for those territories. That is what almost every subscription wants — one price, sold everywhere the app is. An entry may also carry a future startDate to schedule a price change, and preserveCurrentPrice true to keep existing subscribers at their current price when it takes effect (preserveCurrentPrice is write-only and won't round-trip). Scheduled entries are not equalized: give a startDate row for each territory it applies to.

    {
      "baseTerritory" : "USA",
      "prices" : [
        {
          "customerPrice" : "1.99",
          "territory" : "USA"
        }
      ]
    }

Omitting baseTerritory means the opposite: the subscription sells only in the territories the file prices, and every one of them needs its own entry. Apple derives nothing server-side for subscriptions, so a file without a baseTerritory that lists one territory is a subscription sold in one territory.

subscriptions/{productId}/availability.json — availableInNewTerritories is a bool; availableTerritories is an explicit list of territory codes. The file is optional and rarely needed: leave it out and availability follows pricing, which for a baseTerritory means every territory the app sells in, and otherwise means the territories priced. Write it only to deliberately sell the subscription somewhere narrower than the app, and keep a price for every territory listed — a subscription is not purchasable in a territory with no price, and App Store Connect reports it as missing metadata.

    {
      "availableInNewTerritories" : false,
      "availableTerritories" : [ "USA" ]
    }

subscriptions/{productId}/introductoryOffers.json — offers is a list. Each offer needs duration (THREE_DAYS, ONE_WEEK, TWO_WEEKS, ONE_MONTH, TWO_MONTHS, THREE_MONTHS, SIX_MONTHS, or ONE_YEAR), numberOfPeriods (integer), offerMode, and territory — every offer is scoped to one territory (at most one offer per territory), and the subscription must already have a price there. offerMode is FREE_TRIAL, PAY_AS_YOU_GO, or PAY_UP_FRONT. A FREE_TRIAL offer must not have a customerPrice; the paid modes require one, and it must match a subscription price point for that territory.

    {
      "offers" : [
        {
          "duration" : "ONE_WEEK",
          "numberOfPeriods" : 1,
          "offerMode" : "FREE_TRIAL",
          "territory" : "USA"
        }
      ]
    }

subscriptions/{productId}/promotionalOffers.json — offers for existing or previous subscribers, redeemed in-app. Each offer needs name, offerCode (its immutable identifier), duration, numberOfPeriods, offerMode (FREE_TRIAL, PAY_AS_YOU_GO, or PAY_UP_FRONT), and prices — at least one { territory, customerPrice } entry. For FREE_TRIAL the entries carry only the territory, no customerPrice.

    {
      "offers" : [
        {
          "duration" : "ONE_MONTH",
          "name" : "Come Back Deal",
          "numberOfPeriods" : 1,
          "offerCode" : "comeback1",
          "offerMode" : "PAY_UP_FRONT",
          "prices" : [ { "customerPrice" : "0.99", "territory" : "USA" } ]
        }
      ]
    }

subscriptions/{productId}/winBackOffers.json — App Store-surfaced offers for lapsed subscribers. Each offer needs referenceName, offerId (immutable), duration, periodCount, offerMode, priority (HIGH or NORMAL), startDate, customerEligibilityPaidSubscriptionDurationInMonths, customerEligibilityTimeSinceLastSubscribedInMonths ({ minimum, maximum }), and prices; optional endDate, customerEligibilityWaitBetweenOffersInMonths, and promotionIntent (NOT_PROMOTED or USE_AUTO_GENERATED_ASSETS).

subscriptions/{productId}/offerCodes.json — offerCodes is a list. Each entry needs name (immutable), customerEligibilities (any of NEW, EXISTING, EXPIRED), offerEligibility (STACK_WITH_INTRO_OFFERS or REPLACE_INTRO_OFFERS), duration, numberOfPeriods, offerMode, prices (same rules as promotional offer prices: at least one entry, territory-only for FREE_TRIAL), and customCodes — a list of { customCode, numberOfCodes } with optional expirationDate. An existing offer code's terms can't be changed (only new custom codes added); removing one from the file deactivates it permanently, and a deactivated code's name can't be reused.

subscriptionGracePeriod.json — one per app, created by App Store Connect with the first subscription, only ever updated. duration is THREE_DAYS, SIXTEEN_DAYS, or TWENTY_EIGHT_DAYS; optIn and sandboxOptIn are bools; renewalType is ALL_RENEWALS or PAID_TO_PAID_ONLY.

promotedPurchases.json — promotedPurchases is a list of { productId, visibleForAllUsers, enabled }, one per promoted in-app purchase or subscription. The array order is the display order on the App Store product page.

## Preparing for first submission

A freshly imported listing has only the basics filled in: app name, bundleId, primaryLocale, versionString, and releaseType. Everything else App Review requires starts empty. To get a listing submission-ready, fill in:

App-level:

- app.json — contentRightsDeclaration
- appInfo/shared.json — primaryCategory (the file itself may not exist yet); secondaryCategory optional
- appInfo/localizations/{locale}.json — privacyPolicyUrl (required, must be a live page); subtitle optional
- appInfo/ageRating.json — the full questionnaire. It starts with only override fields; every field in the Field shapes example needs an answer.
- pricing.json — at least one manualPrice for the base territory (shape above); even a free app needs an explicit price of 0
- availability.json — does not exist until created; availableInNewTerritories true with an empty territories object means available everywhere

Version-level, per platform:

- version.json — copyright
- localizations/{locale}/description.txt — required
- localizations/{locale}/localization.json — keywords and supportUrl required; marketingUrl and promotionalText optional
- review/review.json — contactFirstName, contactLastName, contactEmail, contactPhone (must start with + and a country code, like +44 844 209 0611; App Store Connect verifies it is a plausible real number and rejects fictional 555 numbers), demoAccountRequired (plus demoAccountName and demoAccountPassword when true)
- review/notes.txt — optional, but a short note explaining the app, and how the reviewer signs in or that no sign-in is needed, helps review go smoothly

Check whether sign-in gates any of the app's content before filling in review.json — missing or non-working demo credentials are a common rejection. If it does, set demoAccountRequired with a working account the reviewer can use; if the only sign-in is Sign in with Apple or anonymous, the reviewer needs no account, so say that in notes.txt. Don't leave this for the user to raise: offer to create the account when the app's backend is one you can reach (a Supabase project, say), and otherwise ask them for credentials while assembling the rest of the listing.

Ask the user for values that can't be derived from the project (support and privacy policy URLs, review contact details, price); reasonable listing copy can be drafted from knowledge of the app and confirmed with the user. Never fill those external values with invented placeholders: a fictional 555 phone number or an example.com URL fails validation, and anything that slips past is rejected by App Store Connect partway through an apply, leaving the push half-done. Leave a field out until the user supplies the real value.

If asked to write the privacy policy itself (or any similar legal document, like terms of service), drafting one is fine — but present it clearly as a draft, not legal advice. Tell the user to verify it accurately reflects what the app actually does with data (including any third-party SDKs). Always tell them to have a legal professional review it before publishing it at the privacyPolicyUrl — state this every time as something they need to do.

Beyond these files, a submission also needs screenshots and a published App Privacy label (see the sections below), a build uploaded and attached to the version, and an export compliance answer (given per build, or preempted with the ITSAppUsesNonExemptEncryption Info.plist key). These files manage only the listing — the accompanying SKILL.md says how builds are uploaded and submitted.

## Placements

Screenshots, app previews, and the media App Store Connect shows atop the product page and in search results are placements: each places one image or video from the app's asset library on an App Store version localization. They live at appStoreVersion/{platform}/localizations/{locale}/placements/{placementType}/{placementGroup}/ — one directory per placement group, beside the localization.json they belong to. Both directory names are Apple's values lowercased with underscores as hyphens: APP_SCREENSHOT is app-screenshot, IPHONE_DYNAMIC_ISLAND_LARGE_PROFILE is iphone-dynamic-island-large-profile. Each directory holds a manifest.json listing its placements in display order, plus an assets/ subdirectory with the files:

    {
      "placements": [
        { "fileName": "home.png" },
        { "fileName": "tour.mp4", "previewFrameTimeCode": "00:00:05:00" }
      ]
    }

Each fileName is a file within that directory's assets/ subdirectory. previewFrameTimeCode, for videos only, is the frame shown before the video plays, as HH:MM:SS:FF; leave it out to keep App Store Connect's choice. A file may appear in several placement groups; it uploads once. App Store Connect doesn't serve videos back for download, so imports and refreshes can't fetch them: an entry whose video file is missing stands for the video already placed under that name, unchanged, and validation warns rather than fails. Its previewFrameTimeCode can still be edited while App Review hasn't seen the video and no other placement shares it; otherwise a new frame means uploading the video again, which needs the file. To replace such a video, add the new file.

The placement types an App Store version takes:

- app-screenshot — up to 10 screenshots per group; images (.png, .jpg, .jpeg) only.
- imessage-app-screenshot — up to 10 screenshots of the iMessage app per group, in the iMessage groups (the iPhone and iPad group names prefixed with imessage-, like imessage-iphone-dynamic-island-large-profile); images only.
- app-preview — up to 3 app preview videos per group; videos (.mov, .mp4, .m4v) only, 15 to 30 seconds with an audio track, at the group's exact preview size.
- product-page-header-asset — the header above the icon and screenshots on iOS 27 and iPadOS 27 product pages: one image or video in default-profile. Images are PNG at 3840×1646 (21:9); videos are 3840×1646, 5 to 30 seconds, and play muted until tapped.
- app-store-search-results-asset — shown in place of screenshots in iOS 27 and iPadOS 27 search results: one image or video in default-profile, from 1920×1280 to 3840×2560 (3:2); videos run 5 to 30 seconds and always play muted.

A 5244×2950 PNG (16:9) is valid as both the header and the search results asset, so the same file can fill both. Header and search results images can't have transparency.

Screenshot and preview groups are device families. App Store Connect adds groups as devices ship, so planning checks each group, and how many placements it holds, against App Store Connect's current list. The app-screenshot groups as of October 2026:

- iPhone: iphone-dynamic-island-large-profile (6.9- and 6.7-inch iPhones with the Dynamic Island), iphone-duo-profile, iphone-face-id-large-profile (6.5-inch), iphone-dynamic-island-medium-profile (6.3- and 6.1-inch with the Dynamic Island), iphone-face-id-medium-profile (6.1-, 5.8-, and 5.4-inch with a notch), iphone-home-button-large-profile (5.5-inch), iphone-home-button-medium-profile (4.7-inch), iphone-home-button-40-profile, iphone-home-button-35-profile
- iPad: ipad-13-profile (13-inch, and 12.9-inch iPad Pro from the 3rd generation), ipad-129-profile (12.9-inch iPad Pro, 2nd generation), ipad-11-profile, ipad-105-profile, ipad-97-profile
- Apple Watch: watch-ultra-profile, watch-series-10-profile, watch-series-7-profile, watch-series-4-profile, watch-series-3-profile
- Mac: mac-profile; Apple TV: tv-profile; Apple Vision Pro: vision-pro-profile

app-preview uses the same groups except the Apple Watch groups and iphone-home-button-35-profile. Screenshot and preview dimensions are exact, per Apple's screenshot and app preview specifications; iPhone Duo's two displays share iphone-duo-profile, at 1398×2034 (outer) or 2007×2853 (inner), in either orientation.

Every screenshot must be exactly one of the pixel sizes App Store Connect accepts for its group. Any other size is rejected partway through an apply, and validation doesn't check sizes. Capture each group on a device whose screen natively produces one of its sizes; never resize or crop another device's capture to fit. iPhone and iPad sizes are given in portrait, and a landscape screenshot swaps them. The screenshot groups a submission needs:

- iPhone (required for an iOS app): iphone-dynamic-island-large-profile at 1320×2868, 1290×2796, or 1260×2736. App Store Connect scales it for every smaller iPhone, so the smaller iPhone groups are optional.
- iPad (required when the iOS app supports iPad): ipad-13-profile at 2064×2752 or 2048×2732.
- iPhone Duo (optional): iphone-duo-profile at the sizes above.
- Apple Watch (required when the app includes a watch app): one group, either watch-ultra-profile at 422×514 or 410×502, or watch-series-10-profile at 416×496 or 374×446. Watch screenshots belong to the iOS version, under appStoreVersion/iOS/; there is no watchOS platform directory.
- Apple TV: tv-profile at 1920×1080 or 3840×2160.
- Mac: mac-profile at 1280×800, 1440×900, 2560×1600, or 2880×1800.
- Apple Vision Pro: vision-pro-profile at 3840×2160.

A locale without screenshots of its own shows the primary locale's, so screenshots go under the primaryLocale from app.json unless localized ones are wanted.

App Store Connect only takes placement changes while a version is being prepared: in Prepare for Submission or after a rejection. Once it's submitted, its placements are fixed; to change them, bump versionString in version.json to start a new version, which App Store Connect seeds with the current placements. The exception is a live version's header and search results asset, which can switch to an asset App Review has already approved — for instance one submitted for review in App Store Connect's Asset Library. New uploads take App Store Connect a while to process; until they finish, planning reports the group as still processing and leaves it alone.

## Review screenshots

Each in-app purchase and subscription takes one review screenshot — shown to the App Review team, not on the App Store — in a reviewScreenshot/ directory beside the product's JSON: inAppPurchases/{productId}/reviewScreenshot/ or subscriptionGroups/{referenceName}/subscriptions/{productId}/reviewScreenshot/. The directory holds a manifest.json naming the single image file in its assets/ subdirectory:

    {
      "screenshot": "review.png"
    }

The product can exist and sync without one, but App Store Connect keeps it in Missing Metadata until the screenshot is uploaded, so it can't be submitted for review.

Ascot writes appStoreConnect/.gitignore once so assets/ directories stay out of git while manifests are committed; delete that file to commit images and videos instead — the decision is recorded in lock.json, so the file is never recreated. On a fresh clone with manifests but no images, an assets-only refresh re-downloads them from App Store Connect without touching any authored file; a full refresh also restores them but overwrites the authored files with remote state. Videos can't be re-downloaded (see Placements), but a clone without them still plans and applies cleanly. Before submission, every platform being submitted needs its required screenshot groups from the list in Placements. The accompanying SKILL.md says how to capture them.

## App privacy (nutrition label)

The App Privacy data-collection disclosures cannot be managed through these files — Apple has no API for them. Only privacyPolicyUrl in appInfo/localizations/{locale}.json is handled here; the rest the user fills out on the App Store Connect website, and it must be published before the app's first submission for review.

Work out the answers before sending the user to the page, and don't ask them what data leaves the device. Read it off the project: the backend the app talks to and what its schema stores, the auth method and what it returns, every third-party SDK linked into the app (analytics, crash reporting, advertising, purchases), and anything the app uploads. Innocuous subject matter doesn't make the answer "collects nothing" — accounts and their tables still count.

Give the user a worksheet, one line per data type, in the order the questionnaire asks: Apple's category and type (Contact Info → Email Address, Identifiers → User ID, User Content → Other User Content, and so on), the purpose (App Functionality for anything a feature needs to work; Analytics, Product Personalization, or Advertising only when something genuinely does that), whether it's linked to the user's identity, and whether it's used for tracking. Rows stored under a user's account are linked. Tracking means sharing with data brokers or combining with third-party data for advertising — decide it rather than leaving the user to interpret the term. Data that never leaves the device is not collected and does not belong on the label.

Give the page alongside the worksheet: read the numeric appId from lock.json (reading it is fine, just never edit it) and link them to https://appstoreconnect.apple.com/apps/{appId}/distribution/privacy. Ask them to confirm each line matches their app, and make sure the label agrees with the privacy policy at privacyPolicyUrl.

Saving answers is not enough. Tell the user explicitly to click Publish on that page — until they do, the label is a draft and the app can't be submitted. Answers can be revised and republished any time without a new app version.

## Validating edits

After editing listing files, always run the validation step. Validation checks the files locally — decoding, character limits, URL, email, and phone formats (placeholder values are errors), product id uniqueness across in-app purchases and subscriptions, subscription groupLevel (≥ 1), the introductory offer rules (a required territory, at most one offer per territory, customerPrice required for paid modes and forbidden for FREE_TRIAL), and that every placement and review screenshot manifest entry resolves to a file in its assets/ directory that its placement type can show — without touching App Store Connect, and reports diagnostics naming the file and field. Fix every reported error and validate again before telling the user the edits are ready or applying them. Validation does not detect conflicts with remote changes; those surface when applying.

## Applying changes

Editing files changes nothing remotely; applying pushes the pending changes to App Store Connect. Apply only when the user has asked for the listing to be updated or confirms they want the edits pushed; if they only asked for edits, stop after validating and point them at the review-and-apply surface named in the accompanying SKILL.md. Apply is guarded: it re-runs validation and refuses on errors, and refuses while there are unresolved conflicts, so nothing is pushed in those cases. It also never deletes anything removed locally — a localization, a placement group, or a whole product — without the explicit delete opt-in (see Layout). A conflict means a field changed both locally and in App Store Connect since the last sync; it is reported rather than silently overwritten, and is resolved by choosing the local or the App Store Connect values (the accompanying SKILL.md says how) — never by editing lock.json. After a successful apply the remote state is re-fetched, lock.json is updated, and the files are rewritten in canonical form — commit the result.
