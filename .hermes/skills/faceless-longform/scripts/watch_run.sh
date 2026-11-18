#!/bin/bash
# Let the agent WATCH a video (the free, open-source Watch skill by bradautomates/claude-video, MIT), built into this skill.
#   ./lf watch <video-file-or-url> [watch.py options]   frames + timestamped transcript on this computer; $0 with the local engine
#   ./lf watch --check      is Watch installed, and are ffmpeg / yt-dlp / Deno there?
#   ./lf watch --where      print the path of Watch's watch.py
#   ./lf watch --setup      install Watch (git clone, copied into the host's skills folder) and say what else is missing
# Local engine = nothing leaves this computer. It is forced with --engine local unless you pass --engine yourself (a Gemini key in the
# environment would otherwise make Watch use Gemini). A LOCAL FILE without Watch installed falls back to the built-in mini_watch.py (ffmpeg only).
# Watch does not run in Claude Chat or Cowork (cloud sandboxes); it runs in Claude Code, Hermes, Codex and other local agents.
set -u
SK="$(cd "$(dirname "$0")/.." && pwd)"
REPO_URL="${WATCH_REPO_URL:-https://github.com/bradautomates/claude-video.git}"

locate() {
  local roots=() r f
  [ -n "${WATCH_SKILL_DIR:-}" ] && { [ -f "$WATCH_SKILL_DIR/scripts/watch.py" ] && { echo "$WATCH_SKILL_DIR/scripts/watch.py"; return 0; }; }
  roots+=("${HERMES_HOME:-$HOME/.hermes}/skills" "$HOME/.claude/skills" "$HOME/.claude/plugins/cache" "$HOME/.agents/skills" "$HOME/.codex/skills" "$HOME/.cursor/skills" "./.claude/skills" "./.agents/skills" "./.hermes/skills")
  for r in "${roots[@]}"; do
    [ -d "$r" ] || continue
    f=$(find "$r" -maxdepth 6 -path '*/watch/scripts/watch.py' 2>/dev/null | sort | tail -1)
    [ -n "$f" ] && { echo "$f"; return 0; }
  done
  return 1
}
pybin() { for p in python3 python; do command -v $p >/dev/null && $p -c "import sys; assert sys.version_info >= (3, 10)" 2>/dev/null && { echo $p; return; }; done; command -v py >/dev/null && echo "py -3"; }

tools_report() {
  command -v ffmpeg >/dev/null && echo "ffmpeg   ok" || echo "ffmpeg   MISSING (brew install ffmpeg | winget install --id Gyan.FFmpeg --exact | sudo apt install ffmpeg)"
  command -v yt-dlp >/dev/null && echo "yt-dlp   ok ($(yt-dlp --version 2>/dev/null))" || echo "yt-dlp   missing: needed for video URLs (brew install yt-dlp | winget install --id yt-dlp.yt-dlp --exact | pipx install \"yt-dlp[default,curl-cffi]\")"
  command -v deno >/dev/null && echo "deno     ok" || echo "deno     missing: needed for YouTube URLs (brew install deno | winget install --id DenoLand.Deno --exact | see docs.deno.com)"
  echo "(local video files need only ffmpeg. Keep yt-dlp on its latest release: sites break old versions.)"
}

install_watch() {
  command -v git >/dev/null || { echo "git is needed to fetch Watch (or install it yourself: npx skills add bradautomates/claude-video -g --skill watch)"; return 1; }
  local target tmp
  if [ -n "${WATCH_INSTALL_DIR:-}" ]; then target="$WATCH_INSTALL_DIR"
  elif [ -d "${HERMES_HOME:-$HOME/.hermes}" ]; then target="${HERMES_HOME:-$HOME/.hermes}/skills/media/watch"
  else target="$HOME/.agents/skills/watch"; fi
  if [ -f "$target/scripts/watch.py" ] && [ "${1:-}" != "--update" ]; then echo "Watch is already installed at $target (./lf watch --setup --update to refresh)"; return 0; fi
  tmp=$(mktemp -d); echo "fetching Watch from $REPO_URL ${WATCH_REPO_REF:+(ref $WATCH_REPO_REF)}..."
  git clone --depth 1 ${WATCH_REPO_REF:+--branch "$WATCH_REPO_REF"} -q "$REPO_URL" "$tmp/cv" 2>"$tmp/err" || { echo "could not fetch Watch: $(head -c 300 "$tmp/err")"; rm -rf "$tmp"; return 1; }
  [ -f "$tmp/cv/skills/watch/scripts/watch.py" ] || { echo "the repository layout changed (no skills/watch/scripts/watch.py); install it manually: npx skills add bradautomates/claude-video -g --skill watch"; rm -rf "$tmp"; return 1; }
  mkdir -p "$target" && cp -R "$tmp/cv/skills/watch/." "$target/" && rm -rf "$tmp"
  echo "installed Watch $(grep -m1 '^version:' "$target/SKILL.md" 2>/dev/null | tr -d '"') at $target"
  echo "Hermes: start a new session (or /reload-skills). Pin a release for repeatable installs: WATCH_REPO_REF=<tag> ./lf watch --setup --update"
}

case "${1:-}" in
  --where) locate || { echo "Watch is not installed (./lf watch --setup)"; exit 3; }; exit 0;;
  --check) w=$(locate) && echo "watch    ok ($w)" || echo "watch    NOT INSTALLED: ./lf watch --setup  (local video files still work through the built-in mini_watch)"; tools_report; exit 0;;
  --setup) shift; install_watch "$@" || exit 1; tools_report; exit 0;;
  ""|-h|--help) sed -n '2,11p' "$0" | sed 's/^# \{0,1\}//'; exit 0;;
esac

SRC="$1"; shift
WP=$(locate) || WP=""
if [ -z "$WP" ]; then
  if [ -f "$SRC" ]; then
    echo "note: the Watch skill is not installed, so using the built-in mini_watch (frames + your own narration timeline, no transcript). Install Watch with: ./lf watch --setup" >&2
    exec "$SK/scripts/py" "$SK/scripts/mini_watch.py" "$SRC" --project "${LF_PROJECT:-.}" "$@"
  fi
  echo "The Watch skill is needed for URLs and is not installed. Run:  ./lf watch --setup   (then: ./lf watch --check)" >&2; exit 3
fi
WD=$(dirname "$(dirname "$WP")"); PYB=$(pybin); [ -n "$PYB" ] || { echo "Python 3.10+ is needed to run Watch"; exit 1; }
if [ -f "$WD/scripts/setup.py" ]; then
  chk=$($PYB "$WD/scripts/setup.py" --check 2>&1) || { echo "Watch's own setup check failed:"; echo "$chk"; echo; echo "Fix what it lists (usually ffmpeg or yt-dlp), then run again. ./lf watch --check shows the tools."; exit 4; }
fi
engine=(); case " $* " in *" --engine "*|*" --engine="*) ;; *) [ -z "${WATCH_ENGINE:-}" ] && $PYB "$WP" --help 2>/dev/null | grep -q -- '--engine' && engine=(--engine local);; esac
echo "watching: $SRC  (Watch at $WD; ${engine[*]:-engine as configured})" >&2
exec $PYB "$WP" "$SRC" "${engine[@]}" "$@"
