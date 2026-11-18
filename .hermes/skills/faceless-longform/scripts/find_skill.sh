#!/bin/bash
# Prints the absolute path of the faceless-longform skill folder, wherever the host installed it (Hermes, Claude Code, Codex, ...).
# Order: $FACELESS_SKILL, $HERMES_SKILL_DIR, this script's own folder, then the usual skill directories.
cands=("${FACELESS_SKILL:-}" "${HERMES_SKILL_DIR:-}" "$(cd "$(dirname "$0")/.." 2>/dev/null && pwd)")
for root in "${HERMES_HOME:-$HOME/.hermes}/skills" "$HOME/.claude/skills" "$HOME/.agents/skills" "$HOME/.codex/skills" "$HOME/.cursor/skills" "./.claude/skills" "./.agents/skills" "./.hermes/skills"; do
  [ -d "$root" ] && while IFS= read -r d; do cands+=("$d"); done < <(find "$root" -maxdepth 3 -type d -name faceless-longform 2>/dev/null)
done
for c in "${cands[@]}"; do [ -n "$c" ] && [ -x "$c/scripts/lf" -o -f "$c/scripts/lf" ] && { echo "$c"; exit 0; }; done
exit 1
