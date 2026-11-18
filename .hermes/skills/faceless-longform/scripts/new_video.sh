#!/bin/bash
# Start a video project:  scripts/new_video.sh <name> [--from demo|gallery|blank] [--in <folder>]
# Creates <folder>/<name> (default folder: ~/faceless-longform) holding the engine, fonts, map data, a starter script.json and
# an `lf` launcher that already knows where this skill lives (so commands never depend on a $SKILL variable).
#   demo     "The Great Stink", a 2.5-minute worked example (history theme)
#   gallery  one example of every scene type, for choosing visuals (dark theme)
#   blank    an empty three-chapter skeleton (default)
set -e
SKILL="$(cd "$(dirname "$0")/.." && pwd)"
NAME="${1:?usage: new_video.sh <name> [--from demo|gallery|blank] [--in <folder>]}"; shift || true
FROM=blank; BASE="${FACELESS_PROJECTS:-$HOME/faceless-longform}"
while [ $# -gt 0 ]; do case "$1" in --from) FROM="${2:?--from needs demo|gallery|blank}"; shift 2;; --in) BASE="${2:?--in needs a folder}"; shift 2;; *) echo "unknown option $1"; exit 1;; esac; done
case "$NAME" in */*|.*|"") echo "project name must be a plain folder name (letters, digits, - _), got: $NAME"; exit 1;; esac
DEST="$BASE/$NAME"
[ -e "$DEST" ] && { echo "$DEST already exists (pick another name, or delete it first)"; exit 1; }
[ -d "$SKILL/assets/engine" ] || { echo "engine not found at $SKILL/assets/engine: the skill folder is incomplete (re-install it)"; exit 1; }
mkdir -p "$DEST"
cp -R "$SKILL/assets/engine/." "$DEST/"
rm -rf "$DEST/data/cache" "$DEST/renders" "$DEST/review"; mkdir -p "$DEST/data" "$DEST/media" "$DEST/renders" "$DEST/review" "$DEST/logs"
case "$FROM" in
  demo) ;;   # assets/engine/script.json is the demo
  gallery) cp "$SKILL/examples/scene-gallery/script.json" "$DEST/script.json"; cp "$SKILL/examples/scene-gallery/media/"* "$DEST/media/" 2>/dev/null || true;;
  blank) cat > "$DEST/script.json" <<'JSON'
{
  "title": "Your Video Title",
  "theme": "midnight",
  "voice": "bm_george",
  "speed": 1.0,
  "music": "bed",
  "captions": "subtitle",
  "targetMinutes": 15,
  "pronounce": {},
  "sources": [],
  "credits": [],
  "thumbnail": { "text": "YOUR *TITLE*", "sub": "subtitle", "icon": "bulb" },
  "chapters": [
    { "title": "The Hook", "hook": true, "mood": "tense", "lines": [
      { "text": "Write the opening line here.", "scene": { "type": "title", "title": "Your *Title*", "kicker": "Topic", "sub": "Promise" } }
    ] },
    { "title": "First Chapter", "mood": "calm", "lines": [
      { "text": "Write a line of narration here." }
    ] },
    { "title": "Last Chapter", "mood": "mellow", "lines": [
      { "text": "Write the closing line here." }
    ] }
  ]
}
JSON
  ;;
  *) rm -rf "$DEST"; echo "unknown template $FROM (demo | gallery | blank)"; exit 1;;
esac
# the project launcher: ./lf <command>   (see ./lf help)
cat > "$DEST/lf" <<LAUNCH
#!/bin/bash
# Project launcher. The skill folder is remembered here; if it moved, set FACELESS_SKILL=/new/path.
S="\${FACELESS_SKILL:-$SKILL}"
[ -x "\$S/scripts/lf" ] || S="\$("\$(dirname "\$0")/.skill-finder.sh" 2>/dev/null)"
[ -x "\$S/scripts/lf" ] || { echo "faceless-longform skill folder not found (set FACELESS_SKILL=/path/to/faceless-longform)"; exit 1; }
LF_PROJECT="\$(cd "\$(dirname "\$0")" && pwd)" exec "\$S/scripts/lf" "\$@"
LAUNCH
cp "$SKILL/scripts/find_skill.sh" "$DEST/.skill-finder.sh"
chmod +x "$DEST/lf" "$DEST/.skill-finder.sh"
echo "created $DEST (from $FROM)"
echo "next: cd $DEST && ./lf lint     (then ./lf voice, ./lf words  or  ./lf estimate for a quick draft; ./lf help lists everything)"
