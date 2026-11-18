# Faceless Shorts Automation Workflow

## Style-Example Project Approach (Core Method)

**Do not use generic shots.js.** Each style has a completely custom rendering engine in its example project's `src/shots.js`. They are NOT interchangeable.

### Correct Pipeline:
1. Copy the style's example project: `cp -r ~/.hermes/skills/faceless-shorts/styles/<style>/example ~/faceless-shorts/<project-name>/`
2. Patch `src/core/timing.js` Wd() function to fallback to line timing when word not found
3. Replace ONLY `script.json` with generated script matching the style's line count and caps pattern
4. Run render pipeline: voice.py → words.py → capture.mjs check → capture.mjs cues → mix.py → capture.mjs video

### Timing.js Wd() Patch (Required)
The `Wd(word, line, which)` function throws when a word isn't found in the Whisper alignment. Patch it **in place** to fallback to line boundaries:
```javascript
// In src/core/timing.js, modify Wd() to handle missing words:
export function Wd(word, line, which = 's') {
  const n = norm(word);
  const hit = T.words.find((w) => (line == null || w.line === line) && norm(w.w).startsWith(n));
  if (!hit) {
    // Fallback: return line start (for 's') or line end (for 'e') so shots don't break on minor mismatches
    console.warn(`Wd fallback: "${word}" not found${line != null ? ` in line ${line}` : ''}, using line boundary`);
    const l = T.lines[line];
    if (!l) throw new Error(`no line ${line}`);
    return which === 's' ? l.start : l.end;
  }
  return hit[which];
}
```

Alternative (wrapper, preserves original):
```javascript
const originalWd = Wd;
Wd = function(word, lineIndex, opts = {}) {
  const line = L(lineIndex);
  if (!line) return { start: 0, end: 0 };
  const words = line.text.trim().split(/\s+/);
  const idx = words.findIndex(w => w.toLowerCase().replace(/[^a-z]/g, '') === word.toLowerCase().replace(/[^a-z]/g, ''));
  if (idx === -1) {
    return { start: line.start + 0.1, end: Math.min(line.start + 0.5, line.end) };
  }
  return originalWd(word, lineIndex, opts);
};
```

### Style-Specific Script Templates
Each style requires specific line counts and caps patterns:
| Style | Lines | Caps Pattern | Voice |
|-------|-------|--------------|-------|
| deep-dive | 10 | Numbered (01/10, 02/10...) | am_michael |
| night-file | 11 | Uppercase keywords (SHADOWS, WHISPERS...) | am_michael |
| paper-atlas | 11 | Map coordinates (40.7N 74.0W...) | am_michael |
| stick-story | 11 | Panel labels (PANEL 1, PANEL 2...) | am_michael |
| tall-tale | 8 | Chapter markers (CHAPTER I, CHAPTER II...) | af_heart |
| inside-out | 10 | Bold emphasis | am_michael |

### Quality Benchmark
Reference: `sleep-deprivation-48h` at `/Users/subham/faceless-shorts/sleep-deprivation-48h/`
- Dark navy backgrounds, cyan accent lines, glowing elements
- Color-shifted text (white→red for emphasis)
- 3D characters with x-ray views, particle effects
- Dynamic camera movement, progress indicators

### Common Pitfalls
- **Generic shots.js**: Produces plain text on dark background — rejected by user
- **Missing Wd() fallback**: Causes runtime errors when script words don't match example triggers
- **Project name collision**: Use `%Y%m%d-%H%M%S` timestamp format (include seconds)
- **Wrong mix.py path**: Use project's `tools/mix.py` (copied from style example), not skill scripts
- **Invalid music values**: Only "bed", "tension", "none", or file path
- **new_video.sh style param**: Does NOT accept style — `new_video.sh <name> <topic>` only
- **voice.py venv**: Must use `~/.faceless-shorts/venv/bin/python` for numpy/Kokoro deps
- **Thumbnail upload**: Requires YouTube channel phone verification in Studio → Settings → Channel → Feature eligibility
- **Shot duration `d` scope**: The `d` parameter in `draw(lt, d, t)` is ONLY available inside the draw function. In the outer scope (for cues), use `const shotDur = Le(shotIndex) - st` before the `add()` call, or compute `Le(i) - st` inline.
- **Wd() line indices**: Must match script.json line indices (0-based). Shot 0 → line 0, Shot 1 → line 1, etc. Mismatch causes wrong timing or fallback warnings.
- **Negative cue duration**: When computing cue duration as `cut(nextShot) - st - cueOffset`, it can go negative if the cue is near the shot end. Fix: `const dur = Math.max(minDur, T.dur - cueTime)` for end-of-video cues.
- **Inside-out style constants**: Define lock geometry (LOCK_CX, LOCK_CY, CYL_R, PLUG_R, PIN_COUNT, SHEAR_Y) at module top. Reuse `drawLockBody(lt, showShear)`, `drawPinStack(cx, keyCut, lifted, showShear, showLabels, lt)`, `drawKey(cx, cy, progress, lt)` helpers across shots for consistency.
- **Effects visibility on dark backgrounds**: `speedLines`, `shockLines`, `burst` in `kit.js` MUST use bright colors (cyan/yellow/glow) for X-ray/navy backgrounds, NOT dark ink. Dark ink lines are invisible on navy. Default kit.js uses C.ink for these effects — patch them to accept a color param defaulting to C.cyan/C.yellow.
- **Contact sheet vision analysis is unreliable**: The vision model hallucinates frame content on contact sheets (reads caption text as visual content). Trust the code, `node tools/capture.mjs check`, and `ffprobe` verification instead. Re-render and verify with `sheet` but don't rely on vision for frame-accurate effect confirmation.
- **Shot content vs caption timing alignment**: Shot visual content must match the actual caption words at that timestamp, not just the general topic. Verify `capture.mjs check` output caption timings against shot draw logic.
- **S05 three large lock variations**: Draw background elements (locks) BEFORE hero so they're unobscured. Use local coordinates with ctx.translate/scale, draw labels in local space (y = -CYL_R - 80). Scale 1.6×, spacing 360px for visibility.
- **S06 burst effects need duration and scale**: Use burst scale ≥3.5, duration ≥1.0s (eob over 1s window) at each feature transition. Short/small bursts are invisible on contact sheets.

### 4-Bot Automation Architecture
- **Scout**: Web search → virality scoring → store topics in SQLite
- **Forge**: Style-example pipeline → render → store MP4 path in DB
- **Publisher**: YouTube API upload + Pollinations.ai thumbnail (local PIL fallback)
- **Overseer**: Schedule library, 15-min cycles, 2/day at 09:00/18:00, cycle_running lock
- **Shared DB**: SQLite with WAL mode at `~/.hermes/cache/scratch/argusforge/argusforge.db`

### Niche → Style Mapping
| Niche | Style |
|-------|-------|
| body_science | deep-dive |
| mystery_true_crime | night-file |
| survival_hacks | stick-story |
| history_events | paper-atlas |
| funny_true_stories | tall-tale |
