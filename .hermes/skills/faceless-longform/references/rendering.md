# Rendering long videos: speed, resume, troubleshooting

## How it works

The film is drawn frame by frame in headless Chrome (canvas 2D, 1920x1080) and piped to ffmpeg. A 20-minute video at 30 fps is 36,000 frames, so
`render` splits the film into **chapter segments** (`renders/segments/chNN.mp4`), renders several at once, then joins them with the audio (`renders/final.mp4`) without re-encoding.

- **Parallel:** `--jobs N` Chrome workers (default: half your CPU cores, max 4). Each uses about 300-500 MB of RAM. More jobs help until the CPU is full.
- **Resumable:** a finished chapter is cached with a fingerprint of its script lines, timing, scene code and images. Re-running `render` only redraws chapters that changed. If it is interrupted, finished chapters are kept.
- **Draft:** `render --draft` is 15 fps, lower quality and the fastest encoder, about 3x quicker, and writes `renders/draft.mp4` (cached separately). Use it to check pacing and sync; upload the final.
- **Partial:** `render --chapters 3,4` redraws only those chapters (then run `render` once more to join).
- **Force:** `render --force` ignores the cache.

## Time and disk expectations

| Machine | Speed | 18-minute film, final |
|---|---|---|
| Modern laptop, 8 cores, 4 jobs | about 60-100 fps total | about 6-10 min |
| Typical laptop, 4 cores, 2 jobs | about 30-50 fps total | about 12-20 min |
| Weak machine / 1-2 cores | about 12-20 fps | 30-50 min |

Plus: voice (Kokoro) about 1-2x real time for the narration on a laptop (a 16-minute narration takes roughly 8-20 minutes the first time; cached after),
Whisper word timing about 3-8 minutes, audio mix about 1-2 minutes.
Disk: segments + final about 0.5-1.5 GB for 20 minutes at crf 18; `renders/segments/` can be deleted after the final is verified. RAM: about 1 GB free for `mix.py`.

Tell the user these numbers before starting Stage 5 so a long render is not a surprise. Run long commands in the background or with a generous timeout and report progress per chapter.

## Quality settings

Final: x264 `veryfast`, crf 18, `-tune animation`, 30 fps, AAC 192k, +faststart. Flat motion graphics compress very well (usually 2-5 Mbps). For a smaller file use `FPS=24` (20% fewer frames) before `render`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Chrome not found` | install Google Chrome or set `CHROME=/path/to/chrome` |
| `boot failed: ... lines` mismatch | the script changed after voicing: re-run `./lf voice` + `./lf words` (or `./lf estimate`) |
| `word "xyz" not found in lines ...` | an `at` word is not spoken in that scene; fix the word or the scene boundary (`./lf lint` finds these) |
| `unknown scene type` / `unknown icon` | the message lists valid names |
| `image not found: media/x.jpg` | put the file in the project's `media/` folder |
| Text overflows or looks cramped | shorten the text; headlines under 8 words, bullet text under 10 |
| Blank or black frames in a chapter | `./lf check` prints the error and time; fix the scene it names |
| Render very slow | lower `--jobs` if RAM is tight, or raise it if CPU is idle; use `--draft`; close other apps; try `SOFTWARE_GL=1` if Chrome's GPU path is unstable |
| Segments will not join | all segments must come from the same FPS and draft/final mode; `render --force` |
| Audio out of sync | re-run `./lf cues`, `./lf mix`, then `./lf render` (audio is joined last; the picture is exact to the narration clock) |
| Voice mispronounces a word | add it to `"pronounce"` in script.json (`{"Thames": "Temz"}`: the voice says the respelling, captions keep the spelling), run `./lf voice` again (only that sentence is re-spoken) |
| Voice sounds flat in one sentence | split it into two sentences, or add a comma |
| `mix.py` out of memory | close other apps; it needs about 1.5 GB for 20 minutes (add swap on a small VPS) |
| `Chrome closed the connection` | out of memory; the renderer retries each chapter 3 times and sizes workers to free RAM; use `--jobs 1` if it persists |
| `Chrome did not start` | `CHROME_NO_SANDBOX=1`, install Chrome's shared libraries (setup.sh names them), or `npx playwright install chromium` |
| Command hangs or the terminal times out | run it as `./lf bg <command>` and poll `./lf status`; logs are in `logs/` |
| Render finished but silent | `./lf cues`, `./lf mix`, render again; `./lf qa` flags a missing audio stream |
| `not enough free disk space` | free space (old `renders/segments/`), run again; finished chapters are kept |
