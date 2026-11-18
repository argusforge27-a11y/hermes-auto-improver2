#!/bin/bash
# Copies the three companion skills (doctor, qa, reference-study) next to faceless-longform:  scripts/install_companions.sh [target-skills-folder]
SK="$(cd "$(dirname "$0")/.." && pwd)"
T="${1:-}"
[ -z "$T" ] && { [ -d "${HERMES_HOME:-$HOME/.hermes}" ] && T="${HERMES_HOME:-$HOME/.hermes}/skills/media" || T="$(dirname "$SK")"; }
mkdir -p "$T" || exit 1
for d in "$SK"/companions/*/; do n=$(basename "$d"); rm -rf "$T/$n"; cp -R "$d" "$T/$n" && echo "installed $n -> $T/$n"; done
echo "Hermes: /reload-skills or start a new session."
