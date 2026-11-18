# Concat MCP Tools Reference

From `docs/MCP.md` — tools exposed by `concat --mcp`.

## Projects
| Tool | Description |
|------|-------------|
| `project_list` | List recent projects |
| `project_create` | Create new project (`name`) |
| `project_open` | Open existing project (`path`) |
| `project_save` | Save project to disk (`path`) |
| `project_close` | Close project (`path`) |
| `project_set_video` | Set project video settings (`path`, `width`, `height`, `fps`) |

## Reading
| Tool | Description |
|------|-------------|
| `timeline_read` | Compact timeline: lanes, clips in time order, media, ids (`path`) |
| `project_get` | Full project JSON (`path`) |
| `concat_version` | Version + MCP mode (`headless`/`window`) |

## Media
| Tool | Description |
|------|-------------|
| `media_probe` | Probe media file (`file`) → duration, streams, codecs |
| `media_import` | Import media into project (`path`, `file`) |

## Editing — Clips
| Tool | Description |
|------|-------------|
| `clip_add` | Add single clip (`path`, `lane`, `media_id`, `start`, `end`) |
| `clips_add_sequence` | Add all imported media to lane in order (`path`, `lane`) |
| `clip_trim` | Trim clip (`path`, `clip_id`, `start`, `end`) |
| `clips_split` | Split clip at time (`path`, `clip_id`, `time`) |
| `clips_move` | Move clip(s) (`path`, `clip_ids`, `lane`, `time`) |
| `clips_remove` | Remove clip(s) (`path`, `clip_ids`) |
| `clip_update` | Update clip properties (`path`, `clip_id`, fields) |
| `clip_transform` | Transform (position, scale, rotation) (`path`, `clip_id`, `transform`) |
| `clip_speed` | Speed ramp (`path`, `clip_id`, `speed`) |
| `clip_frame` | Set clip source frame (`path`, `clip_id`, `frame`) |
| `track_add` | Add lane/track (`path`, `index`) |

## Titles & Captions
| Tool | Description |
|------|-------------|
| `title_add` | Add title (`path`, `lane`, `start`, `duration`, `text`, `position`, `size`, `color`) |
| `title_style_words` | Style specific words (`path`, `title_id`, `styles`: `[{word, color, weight, size}]`) |
| `title_clear_word_styles` | Clear word styles (`path`, `title_id`) |
| `captions_add` | Auto-captions with local Whisper (`path`, `lane`, `model`) |

## Keyframes & Effects
| Tool | Description |
|------|-------------|
| `keyframe_set` | Set keyframe (`path`, `clip_id`, `property`, `position` 0-1, `value`, `easing`) |
| `keyframe_clear` | Clear keyframes (`path`, `clip_id`, `property`) |
| `effects_list` | List available effects |
| `effect_layer_add` | Add effect layer (`path`, `lane`, `effect_id`, `start`, `duration`) |
| `effect_key_set` | Keyframe effect parameter (`path`, `layer_id`, `param`, `position`, `value`) |

## Batch Edits
| Tool | Description |
|------|-------------|
| `edit_apply` | Any edit command or batch as one undo step (`path`, `command` or `commands`) |
| `edit_undo` | Undo (`path`) |
| `edit_redo` | Redo (`path`) |

## Templates
| Tool | Description |
|------|-------------|
| `template_list` | List templates |
| `template_instantiate` | Instantiate template (`path`, `template_id`, `replacements`) |

## Export
| Tool | Description |
|------|-------------|
| `export_start` | Start export (`path`, `output`, `preset`, `range?`) → `{id}` |
| `export_status` | Check export status (`path`, `id`) |
| `export_wait` | Wait for export with progress (`path`, `id`) → `{output}` |
| `export_cancel` | Cancel export (`path`, `id`) |

## Preview
| Tool | Description |
|------|-------------|
| `preview_frame` | Get composited frame at time (`path`, `time`) → image data |

---

## Example Workflows

### 1. Short from clips with captions
```python
with ConcatMCPClient() as c:
    p = c.call("project_create", {"name": "Short"})
    for f in glob.glob("~/Videos/clips/*.mp4"):
        c.call("media_import", {"path": p["path"], "file": f})
    c.call("clips_add_sequence", {"path": p["path"], "lane": 0})
    c.call("captions_add", {"path": p["path"], "lane": 1})
    e = c.call("export_start", {"path": p["path"], "output": "short.mp4", "preset": "1080p"})
    result = c.call("export_wait", {"path": p["path"], "id": e["id"]})
```

### 2. Zoom punch-in at 5s
```python
tl = c.call("timeline_read", {"path": p["path"]})
clip = next(c for c in tl["clips"] if c["start"] <= 5 < c["end"])
rel = (5 - clip["start"]) / (clip["end"] - clip["start"])
c.call("keyframe_set", {"path": p["path"], "clip_id": clip["id"], "property": "scale", "position": rel, "value": 1.5})
c.call("keyframe_set", {"path": p["path"], "clip_id": clip["id"], "property": "scale", "position": rel+0.1, "value": 1.0})
```

### 3. Add callout title
```python
c.call("title_add", {
    "path": p["path"],
    "lane": 1,
    "start": 12.5,
    "duration": 3.0,
    "text": "Click here →",
    "position": [0.7, 0.3],
    "size": 0.06,
    "color": "#ffff00",
})
```
