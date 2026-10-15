#!/bin/bash
# Copies the Claude plugin that ships with the selected Xcode (skills + the `xcrun mcpbridge`
# MCP server) into plugins/xcode-integration so the chris-local marketplace can install it.
# Run again after updating Xcode, then: claude plugin marketplace update chris-local
#                                       claude plugin update xcode-integration@chris-local
set -euo pipefail

kit_root=$(cd "$(dirname "$0")/.." && pwd)
dest="$kit_root/plugins/xcode-integration"

# `xcrun agent plugin path` materializes the plugin for this Xcode build and prints its path.
src=$(xcrun agent plugin path --plugin-format claude 2>/dev/null | tail -1)
if [ -z "$src" ] || [ ! -f "$src/.claude-plugin/plugin.json" ]; then
    echo "sync-xcode-plugin: Xcode did not provide a Claude plugin (needs Xcode 27 or later)" >&2
    exit 1
fi

rsync -a --delete "$src/" "$dest/"
xcode_version=$(xcodebuild -version | tr '\n' ' ' | sed 's/ *$//')
printf 'Copied from %s\n%s\n' "$src" "$xcode_version" >"$dest/SYNCED_FROM.txt"
echo "Synced xcode-integration from $xcode_version ($(find "$dest/skills" -name SKILL.md | wc -l | tr -d ' ') skills)"
