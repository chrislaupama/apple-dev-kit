#!/bin/bash
# Injects the SwiftUI guidelines and puts `xc` on PATH, but only in Apple-platform projects.
set -u

plugin_root="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
project_dir="${CLAUDE_PROJECT_DIR:-$PWD}"

is_apple_project() {
    local dir="$1"
    [ -f "$dir/Project.json" ] || [ -f "$dir/project.yml" ] && return 0
    compgen -G "$dir/*.xcodeproj" >/dev/null || compgen -G "$dir/*.xcworkspace" >/dev/null && return 0
    [ -f "$dir/Package.swift" ] && grep -qE '\.(iOS|macOS|watchOS|tvOS|visionOS)\(' "$dir/Package.swift" && return 0
    return 1
}

is_apple_project "$project_dir" || exit 0

if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
    printf 'export PATH="%s/bin:$PATH"\n' "$plugin_root" >>"$CLAUDE_ENV_FILE"
fi

cat "$plugin_root/context/swiftui-guidelines.md"
printf '\nThe `xc` build tool and `apple-api` lookup are in `%s/bin/` (also on PATH).\n' "$plugin_root"
