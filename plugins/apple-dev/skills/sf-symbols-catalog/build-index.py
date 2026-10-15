#!/usr/bin/python3 -I
"""Rebuild index.tsv from the SF Symbols catalog installed with macOS.

Usage: build-index.py [output]   (default: index.tsv beside this script)
Run it again after a macOS update to pick up new symbols.
"""
import csv
import plistlib
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = Path("/System/Library/PrivateFrameworks/SFSymbols.framework/Versions/A/Resources/CoreGlyphs.bundle/Contents/Resources")
PLATFORMS = ["iOS", "macOS", "watchOS", "tvOS", "visionOS"]
# Localized glyph variants (0.circle.ar, character.ja, …) are chosen by the system, not by name.
LOCALE_SUFFIX = re.compile(r"\.(ar|he|hi|ja|ko|th|zh|zh\.traditional|my|km|bn|gu|kn|ml|mr|or|pa|ta|te|si|sat|mni|el|ru|rtl)$")


def load(name):
    return plistlib.loads((SOURCE / name).read_bytes())


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "index.tsv"
    availability = load("name_availability.plist")
    releases = availability["year_to_release"]
    categories = load("symbol_categories.plist")
    keywords = load("symbol_search.plist")
    restrictions = load("symbol_restrictions.strings")
    aliases = load("name_aliases.strings")
    codepoints = {}
    codepoint_file = HERE / "codepoints.tsv"
    if codepoint_file.exists():
        for line in codepoint_file.read_text().splitlines():
            parts = line.split("\t")
            if len(parts) == 2:
                codepoints[parts[0]] = parts[1]

    rows = []
    for name, release in availability["symbols"].items():
        if LOCALE_SUFFIX.search(name):
            continue
        if name in aliases:
            # Old names still resolve, but new code should use the current name.
            rows.append([name, "", "", "", "", "", "", "", "", aliases[name], ""])
            continue
        versions = releases.get(release, {})
        rows.append([
            name,
            *[versions.get(p, "") for p in PLATFORMS],
            ",".join(categories.get(name, [])),
            ",".join(keywords.get(name, [])),
            restrictions.get(name, ""),
            "",
            codepoints.get(name, ""),
        ])
    known = {r[0] for r in rows}
    for old, new in aliases.items():
        if old not in known and not LOCALE_SUFFIX.search(old):
            rows.append([old, "", "", "", "", "", "", "", "", new, ""])
    rows.sort(key=lambda r: r[0])

    with out.open("w", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_NONE, escapechar="\\")
        writer.writerow(["name", *PLATFORMS, "categories", "keywords", "restriction", "renamed_to", "codepoint"])
        writer.writerows(rows)
    print(f"wrote {len(rows)} symbols to {out}")


if __name__ == "__main__":
    main()
