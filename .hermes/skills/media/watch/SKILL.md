---
name: watch
description: Use when user gives video URL/file to analyze visuals.
author: Hermes Media Team
version: 1.0.0
license: MIT
allowed-tools: Bash, Read, AskUserQuestion
metadata:
  version: "0.3.2"
---

# watch — Video Analysis & Frame Extraction Skill

Watch a video (URL or local path). Downloads with `yt-dlp`, extracts auto-scaled frames with `ffmpeg`, pulls transcripts from captions (or local WhisperX / cloud Whisper / Gemini API fallback), and provides frame paths + transcript so you can answer questions grounded in visual evidence.

## Setup Preflight
```bash
python3 ~/.hermes/skills/media/watch/scripts/setup.py --json
```

## Running Watch
```bash
python3 ~/.hermes/skills/media/watch/scripts/watch.py "<URL-or-local-path>" --question "<question>"
```

### Options & Flags
- `--engine auto|gemini|local` — Default `auto`. With `GEMINI_API_KEY`, uses Google Gemini multimodal model directly. **Local engine still imports `gemini` module** — if no API key is configured, create a stub at `scripts/gemini.py` (see Troubleshooting).
- `--detail transcript|efficient|balanced|token-burner` — Default `balanced`.
- `--start T --end T` — Interval sampling (e.g. `0:30` to `2:15`).
- `--fps F` — Custom frame sampling rate.
- `--timestamps T1,T2` — Pin cue frames for visual cues ("look here" moments).
- `--whisper groq|openai|whisperx` — Fallback transcription backend.

## Troubleshooting
- **ModuleNotFoundError: No module named 'gemini'** when using `--engine local` — The watch script unconditionally imports `gemini` at module load. If no Gemini API key is configured, create a minimal stub at `~/.hermes/skills/media/watch/scripts/gemini.py` with no-op functions (`is_youtube`, `upload_file`, `ask`, `delete_file`) that raise `SystemExit` with a clear message. The local engine path never calls these, but the import must succeed.
- **Transcript unavailable: no matching API key for auto** — Local Whisper/WhisperX backends require `faster-whisper` or `whisperx` installed and configured. Run `python3 ~/.hermes/skills/media/watch/scripts/setup.py` to install dependencies. Cloud backends (Groq, OpenAI) need API keys in `~/.config/watch/.env`.
