---

name: generate-all-content-types
title: Higgsfield Generate All Content Types
description: >-
author: Hermes Agent
license: MIT
version: 1.0.0
  Generate every content type on higgsfield.ai (Image, Video, Audio, plus
  Effects/Cinema/3D/Canvas) from a signed-in account: compose a prompt, pick a
  model, and click Generate. Documents the compose -> Generate -> auth-gate ->
  credit-cost pattern shared across all generators.
website: higgsfield.ai
category: ai-content-generation
tags:
source: 'browserbase: agent-runtime 2026-09-22'
updated: '2026-09-22'
recommended_method: browser
alternative_methods:
    rationale: >-
      Higgsfield exposes an official developer API (console.higgsfield.ai /
      open.higgsfield.ai) for programmatic generation with an account API key.
      This is the more robust path for headless generation with a real account,
      but it was NOT exercised in this run (no account/API key was available in
      the sandbox), so it is listed as unverified.
    rationale: >-
      Higgsfield ships an MCP server (higgsfield.ai/mcp) that lets an agent
      trigger generations via tools instead of driving the DOM. Unverified in
      this run for the same reason.
verified: true
proxies: true

---

# Higgsfield Generate All Content Types

## Purpose

Drive higgsfield.ai — an AI-native creative suite — to generate every content type it offers from a **signed-in account**: still Images (Higgsfield Soul), Videos, and Audio (voiceover / voice-change), plus the secondary generators (Effects, Cinema Studio, 3D Jutsu, Canvas, Edit/Layers, Marketing Studio). Every generator shares the same shape: **compose a prompt → pick a model/settings → click `Generate`**. This skill documents that workflow, the credit cost of each generator, and — critically — the account/login gate that anonymous sessions hit. It is **write / credit-consuming** (each `Generate` spends account credits), so it requires real account credentials to complete end-to-end.

## When to Use

- "Generate an image / video / voiceover on Higgsfield with our account."
- "Run one generation through each Higgsfield content type to smoke-test our subscription."
- A pipeline that produces marketing creative (image + video + audio) from prompts on Higgsfield.
- You need to know the credit cost and model options for each Higgsfield generator before committing an account's credits.

## Workflow

> **Prerequisite — account credentials.** Every generator requires being logged in; anonymous users can compose but cannot see or download output. Supply the account's login (Google / Apple / Microsoft OAuth, or email) via your credential store. **No credentials were available in the run that produced this skill, so the post-login generation + download steps below are documented from the UI structure but were NOT executed end-to-end.** Do not fabricate output — if login fails, stop and report the auth failure.

### 1. Open a stealth remote session

```bash
sid=$(browse cloud sessions create --keep-alive --verified --proxies \
  | node -e "let s='';process.stdin.on('data',c=>s+=c).on('end',()=>process.stdout.write(JSON.parse(s).id))")
export BROWSE_SESSION="$sid"
```

Both `--verified` and `--proxies` are required — higgsfield.ai fronts with Cloudflare + Cloudflare WAF + DataDome. A bare session risks a challenge/block.

### 2. Sign in first (do this once, before composing)

```bash
browse open "https://higgsfield.ai/ai/image?model=gpt_image_2" --remote
browse wait load --remote
# Dismiss the cookie banner: click "Accept All Cookies"
# Click the header "Login" (or "Sign in") button to open the auth dialog.
```

The auth dialog ("Welcome to Higgsfield") offers **Continue with Google / Apple / Microsoft / Email**. Complete whichever matches the stored account. New business-email signups are advertised 50 free credits. After login, the header shows the account avatar/credit balance instead of Login/Sign up — verify this before generating.

### 3. Generate — Image (`/ai/image`)

```bash
browse open "https://higgsfield.ai/ai/image?model=gpt_image_2" --remote
browse wait load --remote
# Type the prompt into the "Describe the scene you imagine" textbox.
browse fill "textarea" "a serene mountain lake at sunrise, cinematic"
# Optional: change model (GPT Image 2 / Nano Banana Pro / Seedream…),
#   quality (High / 2K), and image count (1–4) via the settings row.
# Click the "Generate 8.5 6.5" button (8.5 = full credit cost, 6.5 = discounted).
browse click "@Generate"
browse wait timeout 8000 --remote   # generation is async; poll the result grid
browse screenshot --remote --path result-image.png
```

Select the model by setting the `model=` URL query param (e.g. `?model=gpt_image_2`, `?model=nano_banana_pro`) or clicking the model button in the settings row.

### 4. Generate — Video (`/ai/video`)

```bash
browse open "https://higgsfield.ai/ai/video" --remote
browse wait load --remote
# Optional: "Add references Image, Video or Audio" to condition the video.
browse fill "textarea" "slow dolly-in on a neon-lit Tokyo alley at night"
# Pick a model via the "Model" button (Genjutsu, Seedance, etc.);
#   Genjutsu is also reachable via /ai/video?model=genjutsu.
# Click "Generate 80 60" (video costs far more — ~80 credits full / 60 discounted).
browse click "@Generate"
browse wait timeout 15000 --remote   # video renders take longer than images
```

### 5. Generate — Audio (`/audio`)

```bash
browse open "https://higgsfield.ai/audio" --remote
browse wait load --remote
# Choose a mode tab: "Text to Speech" or "Voice Change".
# For TTS: type the script into "Write exactly what the voice will read out loud",
#   optionally describe the voice in the "Voice details" box, pick model (Seed Audio 1.0).
# For Voice Change: "Upload media" (up to 3 voices/audios or an image) first.
browse fill "textarea" "Welcome to Higgsfield. This is a generated voiceover."
browse click "@Generate"
browse wait timeout 10000 --remote
```

### 6. Other content types (same compose → Generate pattern)

| Content type | URL | Notes |
|---|---|---|
| Effects (free) | `/effects/use` | Pre-baked visual effects applied to an uploaded image/video |
| Cinema Studio | `/generate` | Multi-shot cinematic scene builder |
| 3D Jutsu | `/3d-jutsu` | 3D asset / scene generation |
| Canvas | `/canvas` | Free-form editing canvas |
| Edit / Layers | `/layers` | Layer-based image editing |
| Marketing Studio | `/marketing-studio` | Ad/marketing creative generator |

### 7. Collect output and release

After each `Generate`, the finished asset appears in the result area / the account's project history. Read the CDN URL from the rendered `<img>`/`<video>` (`cdn.higgsfield.ai/...`) or download via the UI. Then:

```bash
browse cloud sessions update "$sid" --status REQUEST_RELEASE
```

## Site-Specific Gotchas

- **Account login is mandatory to see any output.** Anonymous users CAN type a prompt and click `Generate`, but instead of an image they get a blurred "Generated preview" with an overlay: *"Create an account to see generated image — Sign up and generate for free."* The task cannot be completed without real account credentials. This was the terminal state in the run that built this skill (no credentials were provided).
- **`Generate` spends credits — this is a write action.** The button label doubles as the price tag: Image `Generate 8.5 6.5`, Video `Generate 80 60` (first number = full cost, second = current-promo discounted cost). Do not loop generations blindly; each one bills the account. Video is ~10× the cost of an image.
- **Anti-bot: Cloudflare + Cloudflare WAF + DataDome.** `--verified --proxies` got through cleanly in testing (homepage, /ai/image, /ai/video, /audio all rendered). A bare session is not safe. If you hit a challenge, recreate the session rather than retrying in place.
- **`browse type` broke on multi-word input** in testing (`Error: Unexpected arguments`) — the space-delimited args were mis-parsed. Use `browse fill "textarea" "<full prompt>"` (quoted) instead; the page has a single primary `textarea` per generator so the `textarea` selector is reliable.
- **`browse fill` did NOT auto-submit** here (`pressedEnter: false`), which is what you want — pressing Enter mid-prompt is not required and the `Generate` button is the only submit path.
- **Cookie consent dialog overlays the UI on first load.** Click "Accept All Cookies" (or "Reject Advertising Cookies") before interacting, or clicks land on the banner.
- **Model selection via URL query param.** Many generators accept `?model=<id>` (e.g. `/ai/image?model=gpt_image_2`, `/ai/video?model=genjutsu`) — faster and more deterministic than clicking the model dropdown.
- **SPA rendering is progressive.** After `browse wait load`, add `browse wait timeout 2000-3000` before snapshotting — the compose form and settings row hydrate a beat after `load`.
- **Generation is asynchronous.** `Generate` does not block; the asset streams into the result grid seconds (image) to tens of seconds (video) later. Poll with `wait timeout` + re-snapshot rather than expecting an immediate result.
- **Prefer the API/MCP for headless account generation.** Higgsfield ships an official developer API (`console.higgsfield.ai` / `open.higgsfield.ai`) and an MCP server (`/mcp`). With an API key these are more robust than driving the DOM. Neither was verified in this run (no key available) — treat as unconfirmed leads, not guaranteed paths.
- **Auth methods offered:** Continue with Google, Apple, Microsoft, or Email. There is no visible username/password form until you pick "Continue with Email".

## Expected Output

```json
// Per-generation success shape (requires a logged-in account)
{
  "site": "higgsfield.ai",
  "logged_in": true,
  "content_type": "image",            // image | video | audio | effect | cinema | 3d | canvas | edit | marketing
  "url": "https://higgsfield.ai/ai/image?model=gpt_image_2",
  "model": "gpt_image_2",
  "prompt": "a serene mountain lake at sunrise, cinematic",
  "credits_charged": 8.5,
  "status": "completed",
  "assets": [
    "https://cdn.higgsfield.ai/card/<uuid>.webp"
  ]
}
```

```json
// Terminal state actually observed in this run (no account credentials available)
{
  "site": "higgsfield.ai",
  "logged_in": false,
  "content_types_available": [
    { "type": "image", "url": "/ai/image", "generate_credits": "8.5 / 6.5", "auth_required": true },
    { "type": "video", "url": "/ai/video", "generate_credits": "80 / 60", "auth_required": true },
    { "type": "audio", "url": "/audio", "modes": ["text_to_speech", "voice_change"], "auth_required": true },
    { "type": "effects", "url": "/effects/use", "auth_required": true },
    { "type": "cinema_studio", "url": "/generate", "auth_required": true },
    { "type": "3d_jutsu", "url": "/3d-jutsu", "auth_required": true },
    { "type": "canvas", "url": "/canvas", "auth_required": true },
    { "type": "edit_layers", "url": "/layers", "auth_required": true },
    { "type": "marketing_studio", "url": "/marketing-studio", "auth_required": true }
  ],
  "auth_gate": "Clicking Generate while anonymous shows a blurred preview with 'Create an account to see generated image / Sign up and generate for free'.",
  "auth_methods": ["google", "apple", "microsoft", "email"],
  "status": "blocked_needs_account",
  "note": "Compose + Generate UI reachable anonymously; output and download require login + credits. No credentials were supplied to this run."
}
```
