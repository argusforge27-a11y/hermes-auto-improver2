#!/bin/bash
# One-time setup and health check. Safe to re-run. Prints "All set" when everything works.
#   scripts/setup.sh           check, then install what is missing (Python env, voice model, Whisper model; ~0.9 GB, all free)
#   scripts/setup.sh --check   only check (installs nothing; fast; what `./lf doctor` runs)
# Checks Node.js 22+, ffmpeg (+ x264/AAC), Chrome/Chromium (also Playwright/Puppeteer downloads), Python env, voice models, disk, RAM.
# Optional (only for the Watch feature): yt-dlp, Deno. Shared Python env: ~/.faceless-shorts/venv (also used by faceless-shorts).
set -u
CHECK_ONLY=0; [ "${1:-}" = "--check" ] && CHECK_ONLY=1
ok=1; say() { printf '%-12s %s\n' "$1" "$2"; }; bad() { say "$1" "$2"; ok=0; }
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
SKILL="$(cd "$(dirname "$0")/.." && pwd)"; FH="${FACELESS_HOME:-$HOME/.faceless-shorts}"; VENV="$FH/venv"
OS="$(uname -s 2>/dev/null)"

# --- Node.js
NODE_V=$(node -v 2>/dev/null | sed 's/v//' | cut -d. -f1)
if [ -n "$NODE_V" ] && [ "$NODE_V" -ge 22 ]; then say node "ok ($(node -v))"
else bad node "MISSING or too old (found: ${NODE_V:-none}); need Node.js 22+. Install: brew install node · winget install OpenJS.NodeJS.LTS · Linux: curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - && sudo apt install -y nodejs (or nvm install 22)"; fi

# --- ffmpeg
if command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null; then
  enc=$(ffmpeg -hide_banner -encoders 2>/dev/null)
  if echo "$enc" | grep -q libx264 && echo "$enc" | grep -qw aac; then say ffmpeg "ok ($(ffmpeg -version 2>/dev/null | head -1 | cut -d' ' -f3))"
  else bad ffmpeg "found, but it lacks the libx264 or aac encoder (a minimal build). Install the full build: brew install ffmpeg · winget install Gyan.FFmpeg · sudo apt install ffmpeg"; fi
else bad ffmpeg "MISSING (brew install ffmpeg · winget install Gyan.FFmpeg · sudo apt install ffmpeg)"; fi

# --- Chrome / Chromium (a Playwright or Puppeteer download works too)
CH=""
for p in "${CHROME:-}" "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" "/Applications/Chromium.app/Contents/MacOS/Chromium" "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" /usr/bin/google-chrome /usr/bin/google-chrome-stable /usr/bin/chromium /usr/bin/chromium-browser /snap/bin/chromium /usr/bin/microsoft-edge "/c/Program Files/Google/Chrome/Application/chrome.exe" "/c/Program Files (x86)/Google/Chrome/Application/chrome.exe"; do
  [ -n "$p" ] && [ -x "$p" ] && CH="$p" && break
done
if [ -z "$CH" ]; then
  for r in "${PLAYWRIGHT_BROWSERS_PATH:-}" "$HOME/.cache/ms-playwright" "$HOME/Library/Caches/ms-playwright" /opt/pw-browsers /ms-playwright "$HOME/.cache/puppeteer"; do
    [ -n "$r" ] && [ -d "$r" ] && CH=$(find "$r" -maxdepth 5 -type f \( -name chrome -o -name chrome-headless-shell -o -name headless_shell \) 2>/dev/null | head -1) && [ -n "$CH" ] && break
  done
fi
if [ -n "$CH" ]; then say chrome "ok ($CH)"
else bad chrome "MISSING. Install Google Chrome (google.com/chrome) or Chromium, or run: npx playwright install chromium   (then it is found automatically); or set CHROME=/path/to/chrome"; fi
if [ -n "$CH" ] && [ "$OS" = "Linux" ] && command -v ldd >/dev/null; then
  miss=$(ldd "$CH" 2>/dev/null | grep "not found" | head -3 | awk '{print $1}' | tr '\n' ' ')
  [ -n "$miss" ] && bad chrome-libs "Chrome is missing shared libraries: $miss  (Debian/Ubuntu: sudo apt install -y libnss3 libatk-bridge2.0-0 libgbm1 libasound2 libxkbcommon0)"
fi

# --- Python env
PYBIN=""; for p in python3.12 python3.11 python3.10 python3 python "py -3"; do $p -c "import sys; assert sys.version_info >= (3, 10)" >/dev/null 2>&1 && PYBIN=$p && break; done
PY="$VENV/bin/python"; [ -x "$PY" ] || PY="$VENV/Scripts/python.exe"
CHECK="import numpy, scipy, kokoro_onnx, faster_whisper"
if [ $CHECK_ONLY = 0 ]; then
  mkdir -p "$FH"
  if [ ! -x "$VENV/bin/python" ] && [ ! -x "$VENV/Scripts/python.exe" ]; then
    echo "building the Python env in $VENV (a few minutes)..."
    if command -v uv >/dev/null; then uv venv --python 3.11 "$VENV" >/dev/null 2>&1 || uv venv "$VENV" >/dev/null 2>&1
    elif [ -n "$PYBIN" ]; then $PYBIN -m venv "$VENV" 2>/tmp/lf-venv.err || { say python-env "venv failed: $(head -c 300 /tmp/lf-venv.err). On Debian/Ubuntu: sudo apt install -y python3-venv python3-pip"; }; fi
    PY="$VENV/bin/python"; [ -x "$PY" ] || PY="$VENV/Scripts/python.exe"
  fi
  if [ -x "$PY" ] && ! "$PY" -c "$CHECK" 2>/dev/null; then
    for try in 1 2; do
      if command -v uv >/dev/null; then uv pip install --python "$PY" -q numpy scipy kokoro-onnx faster-whisper >/dev/null 2>&1
      else "$PY" -m pip install -q --upgrade pip >/dev/null 2>&1; "$PY" -m pip install -q numpy scipy kokoro-onnx faster-whisper >/dev/null 2>&1; fi
      "$PY" -c "$CHECK" 2>/dev/null && break
    done
  fi
fi
if [ -x "$PY" ]; then
  if "$PY" -c "$CHECK" 2>/dev/null; then say python-env "ok ($VENV)"
  else bad python-env "BROKEN or incomplete: run  $PY -m pip install numpy scipy kokoro-onnx faster-whisper   (Python 3.10-3.12 works best; 3.13+ may lack wheels: use uv or python3.12)"; fi
elif command -v python3 >/dev/null && python3 -c "import numpy, scipy" 2>/dev/null; then
  say python-env "no private env yet (system python has numpy+scipy; voice models still need: scripts/setup.sh)"; ok=0
else bad python-env "MISSING: install Python 3.10+ (python.org, or: brew install python · sudo apt install python3 python3-venv) or uv (docs.astral.sh/uv), then run scripts/setup.sh"; fi

# --- voice + Whisper models
KM="$FH/kokoro/kokoro-v1.0.onnx"; KV="$FH/kokoro/voices-v1.0.bin"
if [ -x "$PY" ] && "$PY" -c "$CHECK" 2>/dev/null; then
  if [ $CHECK_ONLY = 0 ]; then
    if FACELESS_HOME="$FH" "$PY" "$SKILL/scripts/voice.py" --download >/dev/null 2>&1; then say voice "ok (Kokoro, $FH/kokoro)"; else bad voice "model download FAILED (GitHub must be reachable; re-run, or download kokoro-v1.0.onnx and voices-v1.0.bin by hand into $FH/kokoro)"; fi
    if "$PY" -c "from faster_whisper import WhisperModel; WhisperModel('small.en', device='cpu', compute_type='int8')" >/dev/null 2>&1; then say whisper "ok (small.en)"; else say whisper "NOT AVAILABLE (model download failed). Not fatal: word timing falls back to exact line timing (about 0.1-0.2 s)."; fi
  else
    if [ -s "$KM" ] && [ -s "$KV" ] && [ "$(wc -c < "$KM")" -gt 200000000 ]; then say voice "ok (Kokoro, $FH/kokoro)"; else bad voice "model files missing: run scripts/setup.sh to download them (~340 MB)"; fi
    if ls "$HOME"/.cache/huggingface/hub/models--Systran--faster-whisper-small.en >/dev/null 2>&1; then say whisper "ok (small.en cached)"; else say whisper "not cached yet (downloads on first use; if offline, word timing falls back to line timing)"; fi
  fi
fi

# --- disk and RAM
free_gb=$(df -Pk "${HOME}" 2>/dev/null | awk 'NR==2 {printf "%.0f", $4/1048576}')
[ -n "$free_gb" ] && { [ "$free_gb" -ge 6 ] && say disk "ok (${free_gb} GB free)" || say disk "LOW: ${free_gb} GB free; a 20-minute video needs about 2-3 GB while rendering (models 0.9 GB once)"; }
mem_gb=""; [ -r /proc/meminfo ] && mem_gb=$(awk '/MemAvailable/ {printf "%.1f", $2/1048576}' /proc/meminfo)
[ -z "$mem_gb" ] && [ "$OS" = "Darwin" ] && mem_gb=$(sysctl -n hw.memsize 2>/dev/null | awk '{printf "%.1f", $1/1073741824}')
[ -n "$mem_gb" ] && { awk "BEGIN{exit !($mem_gb >= 2.5)}" && say ram "ok (${mem_gb} GB)" || say ram "LOW (${mem_gb} GB): the audio mix needs about 1.5 GB for 20 minutes and each Chrome worker 0.7 GB. Add swap or close other apps; renders then use 1 worker."; }

# --- optional: Watch (only needed for ./lf watch)
w=""; command -v yt-dlp >/dev/null && w="yt-dlp " ; command -v deno >/dev/null && w="${w}deno"
say watch-tools "optional, for ./lf watch: ${w:-none found}  (yt-dlp is needed for URLs; Deno for YouTube; local files need neither). ./lf watch --setup"

chmod +x "$SKILL"/scripts/*.sh "$SKILL"/scripts/py "$SKILL"/scripts/lf "$SKILL"/scripts/*.py 2>/dev/null
if [ $ok = 1 ]; then echo "All set"; else echo "Fix the items above, then run scripts/setup.sh again (./lf doctor re-checks without installing)."; exit 1; fi
