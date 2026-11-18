#!/bin/bash
# Proves the whole toolchain works on this computer in a few minutes, with no model downloads: a stand-in narrator replaces Kokoro
# (the real voice is tested by setup.sh). Steps: new project -> lint -> stand-in voice + timing -> draw every frame -> frames + thumbnail ->
# sound mix -> draft render of the whole demo -> QA of the render -> built-in video viewer -> background-job helper.
SKILL="$(cd "$(dirname "$0")/.." && pwd)"; PY="$SKILL/scripts/py"; T="$(mktemp -d)"; ok=1
step() { printf '%-26s' "$1"; }
pass() { echo ok; }; fail() { echo "FAILED"; echo "$1"; ok=0; }
"$SKILL/scripts/new_video.sh" selftest --from demo --in "$T" >/dev/null || { echo "could not create project"; exit 1; }
D="$T/selftest"; cd "$D"
step "script lint";        "$PY" "$SKILL/scripts/check_script.py" . >/dev/null && pass || fail "check_script.py failed"
step "estimated timing";   "$PY" "$SKILL/scripts/estimate.py" . >/dev/null && pass || fail "estimate.py failed"
step "stand-in voice";     out=$(FACELESS_FAKE_TTS=1 PYTHONPATH="$SKILL/tests/fake_kokoro_onnx" "$PY" "$SKILL/scripts/voice.py" . 2>&1) && [ -s data/narration.wav ] && FACELESS_FAKE_TTS=1 PYTHONPATH="$SKILL/tests/fake_kokoro_onnx" "$PY" "$SKILL/scripts/words.py" . >/dev/null 2>&1 && pass || fail "$out"
step "draw every frame";   out=$(node tools/capture.mjs check 1 2>&1); echo "$out" | grep -q "CHECK OK" && pass || fail "$out"
step "frames + thumbnail"; node tools/capture.mjs frames review/self "5,60" >/dev/null 2>&1 && node tools/capture.mjs thumb renders/thumb.jpg >/dev/null 2>&1 && [ -s renders/thumb.jpg ] && pass || fail "capture frames/thumb failed (Chrome found? run ./lf doctor)"
step "sound cues + mix";   node tools/capture.mjs cues >/dev/null 2>&1 && "$PY" tools/mix.py . >/dev/null 2>&1 && [ -s data/mix.wav ] && pass || fail "mix failed (numpy/scipy installed? run setup.sh)"
step "draft render";       out=$(node tools/capture.mjs render --draft --jobs 2 2>&1) && [ -s renders/draft.mp4 ] && pass || fail "$out"
step "QA of the render";   "$PY" "$SKILL/scripts/qa_video.py" . --draft --frames 4 >/dev/null && pass || fail "$(cat renders/qa.md 2>/dev/null)"
step "built-in viewer";    "$PY" "$SKILL/scripts/mini_watch.py" renders/draft.mp4 --max-frames 3 --project . >/dev/null && [ -s review/watch/timeline.md ] && pass || fail "mini_watch failed"
step "background jobs";    ./lf bg lint >/dev/null 2>&1; sleep 3; ./lf status 2>&1 | grep -q "DONE" && pass || fail "./lf bg/status failed"
if [ -s renders/draft.mp4 ]; then d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 renders/draft.mp4); echo "draft video: ${d%.*} s"; fi
rm -rf "$T"
[ $ok = 1 ] && echo "Self-test passed" || { echo "Self-test found problems (see above)"; exit 1; }
