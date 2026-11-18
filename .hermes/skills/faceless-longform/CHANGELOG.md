# Changelog

## 2.0.0 - tested for Hermes Agent, Watch built in

**Fixes for errors that would hit an agent host**
- Renderer moved `engine/` -> `assets/engine/`. Hermes hub installs copy only `references/ templates/ scripts/ assets/ examples/`; the old layout would have lost the renderer.
- No more `$SKILL` variable: `new_video.sh` writes `./lf` into each project with the skill path baked in (`FACELESS_SKILL` overrides; `find_skill.sh` searches Hermes, Claude, Codex and other skill folders).
- Long commands (voice, Whisper, renders) can exceed a terminal tool's timeout: `./lf bg <command>` + `./lf status` + `logs/`.
- Chrome: found in Playwright/Puppeteer downloads and headless-shell builds, `--disable-dev-shm-usage` (Docker), automatic retry without the sandbox, clear "did not start" help.
- A crashed Chrome used to hang the render forever: now detected, each chapter retried 3 times, partial files cleaned; workers sized to free RAM; disk checked before rendering.
- Model download retries and size checks (a truncated 340 MB file is re-fetched); corrupt cache files are rebuilt; the voice fails with the offending sentence, not a traceback.
- `script.json` errors name the line and column; empty lines, bad themes/moods/backdrops/captions, missing music file are caught by the lint, not mid-render.
- `mix.py`: friendly errors, in-place maths (less RAM), cached effects, missing music file falls back to the built-in bed.
- SKILL.md description shortened under the 1024-character limit; Hermes metadata (`version`, `metadata.hermes`) added; `present_files`/`view` assumptions replaced by host rules.

**New**
- `./lf doctor` (`setup.sh --check`), `./lf qa` (`qa_video.py`: streams, size, duration vs narration, black frames, static stretches, dead air, loudness, peak, frames + contact sheet), `./lf share` (chat-sized copy).
- `pronounce` map: respell hard names for the voice only; captions keep the real spelling.
- Lint additions: symbols, abbreviations, URLs, long parentheses, 45-word sentences, repeated lines, too many callouts, duplicate chapter titles.
- Watch (bradautomates/claude-video) built in: `./lf watch <url|file>` (auto-install, local engine forced, tool check) and `mini_watch.py` (ffmpeg-only viewer for our own renders, pairs frames with narration). `references/watch.md`.
- `references/lessons.md`, `references/hermes.md`; companion skills `faceless-longform-doctor`, `faceless-longform-qa`, `faceless-reference-study` (`scripts/install_companions.sh`).
- `selftest.sh` now also tests the stand-in voice, QA, viewer and background jobs, with no model download.

**Not changed:** scene library, themes, fonts, storytelling and research rules.
