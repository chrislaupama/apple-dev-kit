---
name: sf-symbols-catalog
description: Use when choosing an SF Symbol for a control, toolbar item, tab, or icon, verifying that a symbol name exists and is available on the app's minimum OS version, searching symbols by keyword or category, resolving a renamed symbol, identifying a symbol from a private-use codepoint or a pasted glyph, or checking a symbol's usage restrictions. Not for rendering symbols, custom symbol design, or general HIG questions about symbols.
---

# SF Symbols Catalog

`index.tsv` beside this file lists every SF Symbol with its availability. Paths here are relative to this skill's directory. If `index.tsv` is missing, or after a macOS update, rebuild it from the catalog installed on this Mac with `/usr/bin/python3 -I build-index.py` (run from this skill's directory). Use the index instead of recalling names from memory: a symbol that is missing on the app's minimum OS still builds, then renders as nothing at runtime.

The newest iOS release the index covers is `cut -f2 index.tsv | sort -n | tail -1`. Symbols added after it are absent rather than nonexistent, so say so when a lookup fails for a symbol the user expects to exist.

## Index columns

`name`, `iOS`, `macOS`, `watchOS`, `tvOS`, `visionOS`, `categories`, `keywords`, `restriction`, `renamed_to`, `codepoint`. Version columns hold the OS version that introduced the symbol. `codepoint` is the hex scalar of the symbol's private-use character, blank when the symbol is newer than the bundled table.

## Search

- **Exact name:** `rg '^car\.fill\t' index.tsv`. No match means the name does not exist in this catalog.
- **Keyword or name part:** `rg -i 'trash' index.tsv | cut -f1,2,10 | head -20`. Names are dotted components, so search by component and try synonyms; `arrow.*up` matches names with both parts. When a keyword search finds nothing, browse a category.
- **Category:** `awk -F'\t' '$7 ~ /transportation/' index.tsv | cut -f1,2`. List the keys with `cut -f7 index.tsv | tr ',' '\n' | sort -u`.
- **Available on the minimum OS:** `rg -i 'share' index.tsv | awk -F'\t' '$2 && $2 <= 17' | cut -f1,2`. Use column 3 for macOS, 4 for watchOS, 5 for tvOS, 6 for visionOS.
- **Renamed symbol:** a row whose `renamed_to` is set is an old name. Use the current name in new code.
- **Codepoint:** `rg -i '\t1006e8$' index.tsv | cut -f1`. A flattened glyph in a Figma import or a character copied from the SF Symbols app is a private-use scalar from U+100000 up. No match means the symbol is newer than the bundled table, not that it does not exist.

## Apply the result

- Read the app's minimum OS versions and check every platform the app supports. Choose a symbol available on each minimum, or guard a newer one with a fallback to an older symbol.
- Verify symbol names that arrive from outside, such as a Figma import or a name the user supplies, the same way before writing them into code.
- A symbol with `restriction` text may only depict the Apple product or service it names and may not be modified. Choose another symbol when the design uses one for anything else, and tell the user why.
- To confirm what a symbol looks like, build and run the app or view it in the SF Symbols app.
