# What was tested (and what was not)

Tested in a Linux sandbox (Node 22, ffmpeg 6.1, headless Chromium, Python 3.12): full `selftest.sh` (lint, timing, stand-in voice + word timing, drawing every frame, frames, thumbnail, mix, draft render of the demo, QA, viewer, background jobs); malformed `script.json` variants; a Chrome crash during a render (retry succeeded, final video correct length); QA against deliberately broken videos (no audio, black screen, dead air, static picture, quiet audio: all caught); `watch_run.sh` locate/setup/run against a mock Watch repo; companion install; syntax checks of every script.

**Not tested here (no internet in the sandbox):** the real Kokoro voice and Whisper downloads and output, the real Watch skill and yt-dlp on a live URL, and Hermes itself. Run `scripts/setup.sh` and then `scripts/selftest.sh` on your machine; after that make a 2.5-minute project with `--from demo` and the real voice before a long video.
