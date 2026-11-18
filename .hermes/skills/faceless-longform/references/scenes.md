# Scene catalog

A scene is one picture that stays up for one or more narration lines. In `script.json`, a line that has `"scene": {...}` **starts** a scene;
lines without `scene` continue the previous one. The first line of a chapter with no scene gets an automatic card (`title` for the hook, `chapter` for the rest).
Every `type` below can also take: `"in": "fade" | "push" | "zoom" | "cut"` (how it arrives, default fade), `"backdrop": "drift|grid|dots|rays|contours|paper|stars|plain"`,
`"source": "Name, year"` (small credit bottom-left), `"zoom": 0.035` (slow push-in; 0 disables), `"quiet": true` (no whoosh).

**Rich text:** in any headline, title, label or text field, `*words between stars*` are drawn in the accent colour.

**Syncing to speech:** anything that appears one at a time (bullets, steps, events, pins, bars) accepts `"at": "word"`, the first spoken word, matched by prefix inside the scene's own lines,
at which that item appears. Items without `at` are spread evenly between the ones that have it. `./lf lint` fails if an `at` word is not spoken in the scene.

**Colours** are theme names: `accent`, `accent2`, `accent3`, `danger`, `good`, `muted`, `text`; any CSS colour also works.

| type | use it for | fields |
|---|---|---|
| `title` | opening card, big reveals | `title`, `kicker`, `sub`, `backdrop` |
| `chapter` | a full-screen chapter break (otherwise a slim banner appears automatically) | `n`, `title`, `sub`, `kicker` |
| `text` | one idea stated plainly | `headline`, `sub`, `kicker`, `icon`, `align` ("center" / "left"), `color`, `hi` |
| `kinetic` | the key sentence, words landing as they are spoken | `text` (defaults to the spoken lines), `size`, `hi` |
| `callout` | pattern interrupt: full-colour slam, 2-4 s | `text`, `sub`, `color`, `size` |
| `stat` | a number that counts up | `value` (number or text like "1 in 3"), `prefix`, `suffix`, `decimals`, `from`, `label`, `sub`, `icon`, `color`, `at`, `ring` (percent drawn as a ring, with `max`) |
| `chart` | data | `kind`: `bar` `hbar` `line` `donut`; `labels`, `values` (or `series: [{name, values}]` for line), `unit`, `prefix`, `decimals`, `max`, `highlight` (index or list), `title`, `at: [words]`, `center`/`centerLabel` (donut) |
| `bullets` | 3-6 points | `title`, `items`: strings or `{text, sub, at}`, `numbered` (false for dots) |
| `compare` | two sides | `title`, `left`/`right`: `{title, icon, points: [...]}` (points are strings or `{text, at}`) |
| `flow` | steps and processes | `title`, `steps`: `{label, sub, icon, at}`, `dir`: "h" (2-5 steps) or "v" (3-6 steps) |
| `timeline` | events in order (scrolls past 5) | `title`, `events`: `{date, label, at}` |
| `map` | places, regions, journeys | `focus`: a region name (`world europe asia africa north-america south-america middle-east india uk oceania east-asia`), ISO-3 country codes `["FRA","DEU"]`, or `[lonMin, latMin, lonMax, latMax]`; `highlight`: country codes; `pins`: `{name, lon, lat, at, color}`; `routes`: `{from:[lon,lat], to:[lon,lat], label, at}`; `labels`; `zoom` (false = no zoom-in) |
| `quote` | a short quotation (a line or two; cite the speaker) | `quote`, `who`, `role` |
| `rank` | countdown entries | `n`, `total`, `title`, `sub`, `stat`, `statLabel`, `kicker` |
| `icons` | 2-4 related ideas side by side | `title`, `items`: `{icon, label, sub, at}` |
| `icon` | one icon + one statement (introduce a person, place, concept) | `icon`, `headline`, `sub`, `kicker`, `side` ("left"/"right"), `color` |
| `image` | the user's own photo or an openly licensed image (`media/...`) with a slow camera move | `src`, `caption`, `credit`, `fit` ("cover"/"contain"), `motion` ("in" "out" "left" "right" "up" "none") |
| `outro` | closing card | `title`, `sub`, `items`: button labels |

**Icons** (all drawn in code): person people building home coin dollar chartup chartdown globe clock warning bulb lock key rocket book flask gear heart fire drop cloud sun star check cross question magnifier shield flag mountain bolt chat factory ship.

**Maps** use Natural Earth 110m country outlines (public domain): fine for countries and regions, not for city streets. Pin cities by `lon`/`lat`.
The map zooms in over 1.8 s from a wider view; `highlight` fills countries in the accent colour with their names.

## Visual pacing rules

- A new scene every **4-12 s** (average 6-8 s). Fewer than that feels static, more feels frantic. `./lf lint` and `./lf check` report anything over 14 s.
- Vary the type: never three identical scene types in a row; use at least 3-4 different types per chapter.
- Put a **re-hook** (stat, chart, map, callout, quote, rank, kinetic) at least every 80 s.
- Do not repeat information the voice is already saying word for word in a long `bullets` list; scenes show the *shape* (the number, the sequence, the contrast), the voice gives the detail.
- Callouts are seasoning: 3-6 in a 15-minute video, each 2-4 s, on a real turn ("but", "the twist", a surprising number). Not on every chapter.
- Use `in: "push"` for moving forward in time or sequence, `zoom` for emphasis, `cut` for a sharp contrast; fade is right 80% of the time.
- Keep text short: headlines under about 8 words, labels under 6, bullet text under 10. Captions already show the words.
- Keep important content inside the safe area: nothing important below y = 930 (captions sit there) unless the video has `"captions": "none"`.

## Themes

`"theme"` in script.json: `midnight` (dark, teal and amber; tech, business, science, mystery), `daylight` (light, indigo and orange; finance, health, how-to), `parchment` (warm paper and serif headings; history, culture, biography).
Chapter `"backdrop"` overrides the theme's default background; give different chapters different backdrops (`drift`, `grid`, `contours`, `rays`, `stars`, `dots`, `paper`) to keep a long video from feeling uniform.
A new theme is ~20 lines in `src/core/themes.js` (copy one, change the colours).

## Captions

`"captions": "subtitle"` (default) shows the narration as calm 1-2 line subtitles with the spoken word highlighted; `"none"` hides them.
A line can opt out with `"nocaps": true`. Captions help silent viewers and accessibility; leave them on unless the visuals already carry every word.

## Custom scenes

Need something the library does not have? Add a function to `src/core/scenes.js`: `SCENES.mything = (spec, S) => (lt, d, t) => { ...draw... }` using the helpers in `lib.js`
(`txt`, `card`, `rr`, `circle`, `fitRich`, `drawLayout`, `rgba`, `TH` colours) and `drawIcon`. Everything must be a pure function of `lt` (seconds since the scene started).
Then use `{"type": "mything"}` in the script and run `./lf check`.
