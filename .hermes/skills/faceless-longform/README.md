# Faceless Long-Form

Turn a topic into a finished **8-20 minute faceless YouTube video**: researched script, AI narration, animated motion graphics,
captions, music, thumbnail, title, description and chapter timestamps. Runs on your own computer, costs $0, needs no API keys.

Built from the faceless-shorts skill, rebuilt for length.

## What you give it

| Input | Default | Notes |
|---|---|---|
| Topic (+ angle) | required | or ask for 3 ideas |
| Length | 15 min | 8-20 supported |
| Look | `midnight` | `daylight` (light, finance/how-to), `parchment` (history, serif) |
| Voice | AI `bm_george` | other voices: `am_michael`, `af_heart`, ...; or your own recording |
| Music | built-in, changes per chapter | none, or your own licensed track |
| Images | none | your own or openly licensed ones, shown with a slow camera move |
| Channel name / call to action | none | end card |
| Upload help | no | you upload in YouTube Studio |

## What you get

`final.mp4` (1920x1080) · `thumbnail.jpg` · 3 title options · description with chapters, sources and credits · tags · the project folder, so any chapter can be edited and re-rendered alone.

## How it works

1. **Research and outline** (you approve)
2. **Script and scene plan** (you approve)
3. Voice and word timing
4. Build, review every chapter's contact sheet, **draft render** (you approve)
5. Final render (parallel and resumable) and QA
6. Packaging

Visuals are generated motion graphics: 18 scene types (title, text, kinetic type, callout, stat counter, bar/line/donut charts, bullets, compare, flow, timeline,
world and regional maps with pins and routes, quote, countdown rank, icon grids, image, outro), 36 built-in icons, 3 themes, 8 animated backdrops. No stock footage, no AI-generated images.
The narrator is a synthetic voice.

## What is new in 2.0 (Hermes-ready)
Renderer moved to `assets/engine/` (hub installs copy only `references/ templates/ scripts/ assets/ examples/`) · `./lf` launcher in every project (no `$SKILL` variable) ·
`./lf bg` / `./lf status` for long jobs · `./lf doctor` health check · automatic render QA (`./lf qa`) · Chrome crash retry, RAM/disk-aware renders, Playwright/Puppeteer Chrome discovery ·
stronger lint (symbols, abbreviations, bad settings, long sentences) · `pronounce` map · built-in video viewer + the Watch skill (`./lf watch`) ·
lessons, Hermes notes and three companion skills. Details: CHANGELOG.md.

## Setup (once)

Needs Node.js 22+, ffmpeg, Google Chrome, Python 3.10+. Then:

```
scripts/setup.sh        # builds the Python env and downloads the voice models (~0.9 GB; shared with faceless-shorts)
scripts/selftest.sh     # optional: proves everything works in a few minutes (no model download needed)
scripts/setup.sh --check   # health check only (also ./lf doctor)
scripts/install_companions.sh   # optional: doctor, qa and reference-study skills
scripts/new_video.sh my-video --from demo     # or --from gallery / blank; then cd into it and use ./lf help
```

## Try it

Ask Claude: *"Make a 15-minute video about how the Great Stink led to London's sewers."* or *"Make a 12-minute explainer on why bridges are shaped like that. Daylight theme, female voice."*

## Folder map

`SKILL.md` the workflow Claude follows · `references/` storytelling, scene catalog, research and rights, packaging, rendering · `scripts/` setup, voice, words, estimate, lint, chapters ·
`assets/engine/` the renderer, scene library, fonts, map data and the demo script (copied into every new project) · `examples/scene-gallery/` one of every scene.

## Credits and licences

Fonts: Inter (SIL OFL 1.1) and Caladea (open-source licence). Map outlines: Natural Earth (public domain). Voice: Kokoro-82M via kokoro-onnx (Apache-2.0). Word timing: faster-whisper (MIT).
