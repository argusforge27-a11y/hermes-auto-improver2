---
name: concat-ai-agent
version: 0.1.0
author: Argus
license: AGPL-3.0-or-later
description: Drive Concat video editor via MCP from natural language.
category: media
---

## When to Use
- User says "edit video", "create short", "add captions", "zoom at timestamp", "split podcast", "tutorial with callouts"
- Any natural language video editing instruction
- Batch/automated video processing via Concat's MCP

## Related Skills
- faceless-shorts (for full Shorts pipeline)
- ai-video-editor (for talking-head editing)
# Concat AI Agent Skill

Drive Concat's built-in MCP server (`concat --mcp headless`) from Hermes using natural language.

## Prerequisites
- Concat installed (macOS: `/Applications/Concat.app/Contents/MacOS/concat` or the DMG mount)
- Rust not required — uses the shipped binary

## Usage
```
# In Hermes chat:
"Create a 30s Short from ~/Videos/clips/*.mp4 with auto-captions, punch-in at 5s, export 1080p"
"Split podcast.mp4 into 60s chapters, add titles, export each"
"Take screen_recording.mov, zoom 2x at timestamp 12.5, add callout text 'Click here', export"
```

## MCP Tools Exposed
The skill wraps Concat's 40+ MCP tools into high-level workflows:
- `project_create` / `project_open` / `project_save`
- `media_import` (glob support)
- `clips_add_sequence` (auto-timeline)
- `captions_add` (local Whisper)
- `title_add` / `title_style_words`
- `keyframe_set` (zoom, position, opacity)
- `effect_layer_add` (color, blur, etc.)
- `export_start` / `export_wait`
- `preview_frame`

## Configuration
Set `CONCAT_BINARY` env var if not in standard location.

## Binary Detection
The skill auto-detects the Concat binary in this order:
1. `CONCAT_BINARY` env var
2. DMG mount: `/Volumes/Concat/Concat.app/Contents/MacOS/concat` (preferred — always matches the tested version)
3. Installed app: `/Applications/Concat.app/Contents/MacOS/concat`

## Pitfalls & Fixes
- **Import errors in scripts/** — Use relative imports within `scripts/` (e.g., `from .concat_mcp_client import ConcatMCPClient`), not `from scripts.concat_mcp_client`. The skill's `__init__.py` runs from the skill root with `scripts/` on `sys.path`.
- **MCP initialize handshake timeout** — Capture `req_id` *before* sending the initialize request, then wait on that specific ID. The server replies with the same `id`; waiting on a counter that increments after send misses the reply.
- **Project path handling** — `project_create` returns a project object with `path`; subsequent calls (`title_add`, `media_import`, etc.) require that exact path. Store it after creation.
- **Installed vs DMG binary** — The installed `/Applications/Concat.app` binary may have different MCP behavior (tested: initialize times out). Prefer the DMG mount at `/Volumes/Concat/...` which is verified working.
