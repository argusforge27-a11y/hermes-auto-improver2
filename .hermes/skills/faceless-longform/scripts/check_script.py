"""Lint script.json BEFORE spending minutes on voice and render time.

  scripts/py scripts/check_script.py <project>

Checks structure (chapters, lines, scene types and their required fields, icon names, "at" words that must be spoken inside the
scene), length and pacing (estimated running time, chapter lengths, how long a picture stays up, how often something new
happens), and writing hygiene (digits, very long lines, missing sources). Exit code 1 if there are errors. Standard library only.
"""
import re, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from lf_common import load_script, flatten, words_of

P = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
S = load_script(P)
chapters, flat = flatten(S)
speed = S.get('speed', 1.0)
WPS = 2.7 * speed
errors, warns = [], []
err = lambda m: errors.append(m)
warn = lambda m: warns.append(m)

REQ = {'title': [], 'chapter': [], 'text': ['headline'], 'kinetic': [], 'callout': ['text'], 'quote': ['quote'], 'stat': ['value'], 'bullets': ['items'],
       'compare': ['left', 'right'], 'flow': ['steps'], 'rank': ['n', 'title'], 'icons': ['items'], 'icon': ['icon', 'headline'], 'timeline': ['events'],
       'image': ['src'], 'map': [], 'chart': [], 'outro': []}
PUNCH = {'callout', 'stat', 'image', 'map', 'chart', 'quote', 'rank', 'kinetic', 'timeline', 'compare', 'icons'}   # scenes that re-hook attention
icon_src = next((p for p in [P / 'src/core/icons.js', Path(__file__).parent.parent / 'assets/engine/src/core/icons.js'] if p.exists()), None)
ICONS = set(re.findall(r'^\s{2}(\w+): P\(', icon_src.read_text(), re.M)) if icon_src else set()

# top-level settings (typos here fail late, in the middle of a render, so catch them now)
ENG = next((p for p in [P / 'src/core', Path(__file__).parent.parent / 'assets/engine/src/core'] if p.exists()), None)
THEMES = set(re.findall(r'^\s{2}(\w+): \{', (ENG / 'themes.js').read_text(), re.M)) if ENG and (ENG / 'themes.js').exists() else {'midnight', 'daylight', 'parchment'}
BACKDROPS = {'drift', 'grid', 'dots', 'rays', 'contours', 'paper', 'stars', 'plain'}
MOODS = {'calm', 'tense', 'upbeat', 'epic', 'mellow'}
if S.get('theme', 'midnight') not in THEMES: err(f'unknown theme "{S.get("theme")}" (themes: {", ".join(sorted(THEMES))})')
if S.get('captions', 'subtitle') not in ('subtitle', 'none'): err(f'"captions" must be "subtitle" or "none", got "{S.get("captions")}"')
if not re.match(r'^[a-z]{2}_\w+$', str(S.get('voice', 'bm_george'))): warn(f'voice "{S.get("voice")}" does not look like a Kokoro voice id (try bm_george, am_michael, af_heart; ./lf voices)')
mus = S.get('music', 'bed')
if mus not in ('bed', 'none', None, False) and not (P / str(mus)).exists(): err(f'music file "{mus}" not found in the project folder (use "bed", "none" or a file such as "media/track.mp3")')
if not isinstance(S.get('pronounce', {}), dict): err('"pronounce" must be an object like {"Thames": "Temz"}')
if not isinstance(S.get('sources', []), list): err('"sources" must be a list of strings')
for ci, c in enumerate(chapters):
    if c.get('mood') and c['mood'] not in MOODS: err(f'chapter {ci}: unknown mood "{c["mood"]}" (moods: {", ".join(sorted(MOODS))})')
    if c.get('backdrop') and c['backdrop'] not in BACKDROPS: err(f'chapter {ci}: unknown backdrop "{c["backdrop"]}" (backdrops: {", ".join(sorted(BACKDROPS))})')
    if not c.get('title'): err(f'chapter {ci} has no "title" (YouTube chapter names come from it)')
tits = [str(c.get('title')) for c in chapters]
for t_ in set(tits):
    if tits.count(t_) > 1: warn(f'two chapters are both called "{t_}": give each its own title')

# line timing estimate (no audio needed)
t = float(S.get('lead', 0.6)); start = []; end = []
for i, ln in enumerate(flat):
    w = len(words_of(ln['text'])); start.append(t); t += w / WPS
    end.append(t)
    nxt_first = i + 1 < len(flat) and flat[i + 1]['first']
    t += float(ln.get('gap', S.get('chapter_gap', 0.9) if nxt_first else S.get('gap', 0.35))) if re.search(r'[.?!]["\')]*$', ln['text'].strip()) else 0.12
total = end[-1] + float(S.get('outro', 2.5))
wc = sum(len(words_of(l['text'])) for l in flat)

# scenes
scenes = []   # (i0, spec)
for i, ln in enumerate(flat):
    sp = ln.get('scene')
    if sp: scenes.append((i, sp))
    elif i == 0 or ln['first']: scenes.append((i, {'type': 'title' if i == 0 or (ln['ch'] == 0 and chapters[0].get('hook', True)) else 'chapter', 'auto': True}))
ranges = [(i0, (scenes[k + 1][0] - 1 if k + 1 < len(scenes) else len(flat) - 1), sp) for k, (i0, sp) in enumerate(scenes)]
for i0, i1, sp in ranges:
    ty = sp.get('type'); where = f'line {i0} ("{flat[i0]["text"][:40]}...")'
    if ty not in REQ: err(f'{where}: unknown scene type "{ty}" (types: {", ".join(sorted(REQ))})'); continue
    for k in REQ[ty]:
        if k not in sp: err(f'{where}: {ty} scene needs "{k}"')
    if ty == 'chart':
        if 'labels' not in sp or not ('values' in sp or 'series' in sp): err(f'{where}: chart needs "labels" and "values" (or "series")')
        elif 'values' in sp and len(sp['values']) != len(sp['labels']): err(f'{where}: chart has {len(sp["labels"])} labels but {len(sp["values"])} values')
    if ty == 'map' and 'focus' not in sp: warn(f'{where}: map without "focus" shows the whole world')
    if ty == 'compare':
        for side in ('left', 'right'):
            if side in sp and 'points' not in sp[side]: err(f'{where}: compare.{side} needs "points"')
    if ty == 'image' and 'src' in sp and not (P / sp['src']).exists(): err(f'{where}: image file {sp["src"]} not found in the project folder')
    icons_used = [sp.get('icon')] + [it.get('icon') for k in ('items', 'steps') for it in sp.get(k, []) if isinstance(it, dict)] + [sp.get(s, {}).get('icon') for s in ('left', 'right')]
    for ic in filter(None, icons_used):
        if ICONS and ic not in ICONS: err(f'{where}: unknown icon "{ic}" (available: {", ".join(sorted(ICONS))})')
    # "at" words must be spoken inside this scene's lines
    spoken = [re.sub(r'[^a-z0-9\']+', '', w.lower()) for j in range(i0, i1 + 1) for w in words_of(flat[j]['text'])]
    ats = [it.get('at') for k in ('items', 'steps', 'events') for it in sp.get(k, []) if isinstance(it, dict)] + [sp.get('at')] + list(sp.get('at', []) if isinstance(sp.get('at'), list) else [])
    for a in filter(lambda x: isinstance(x, str), ats):
        n = re.sub(r'[^a-z0-9\']+', '', a.lower())
        if not any(w.startswith(n) for w in spoken): err(f'{where}: "at": "{a}" is not spoken in this scene (lines {i0}-{i1})')
    if ty == 'bullets' and len(sp.get('items', [])) > 6: warn(f'{where}: {len(sp["items"])} bullets is a lot; split into two scenes')
    if ty == 'timeline' and len(sp.get('events', [])) > 8: warn(f'{where}: {len(sp["events"])} timeline events; consider two timelines')

# pacing
durs = [(start[i1 + 1] if i1 + 1 < len(flat) else total) - start[i0] for i0, i1, _ in ranges]
for (i0, i1, sp), d in zip(ranges, durs):
    if d > 16: warn(f'line {i0} ({sp.get("type")}): one scene lasts about {d:.0f} s; split it so the picture changes (aim for 4-12 s)')
    if d < 1.8 and sp.get('type') != 'callout': warn(f'line {i0} ({sp.get("type")}): scene is only about {d:.1f} s')
types = [sp.get('type') for _, _, sp in ranges]
for k in range(2, len(types)):
    if types[k] == types[k - 1] == types[k - 2] and types[k] not in ('title',): warn(f'three "{types[k]}" scenes in a row around line {ranges[k][0]}: vary the visuals')
last_punch = 0.0
for (i0, _, sp), d in zip(ranges, durs):
    if sp.get('type') in PUNCH:
        if start[i0] - last_punch > 80: warn(f'about {start[i0] - last_punch:.0f} s without a stat/chart/map/callout/quote before line {i0}: add a re-hook')
        last_punch = start[i0]
if total - last_punch > 120: warn(f'the last {total - last_punch:.0f} s have no re-hook scene')

# chapters
ch_times = []
for ci, c in enumerate(chapters):
    idx = [i for i, l in enumerate(flat) if l['ch'] == ci]; ch_times.append((start[idx[0]], end[idx[-1]]))
for ci, (c, (a, b)) in enumerate(zip(chapters, ch_times)):
    d = b - a; label = f'chapter {ci} "{c.get("title")}"'
    if d < 25 and ci not in (0, len(chapters) - 1): warn(f'{label} is only {d:.0f} s')
    if d > 200: warn(f'{label} is {d:.0f} s; split it (YouTube chapters work best at 1-3 minutes)')
    if ci == 0 and d > 60: warn(f'the opening ({label}) is {d:.0f} s; the hook should pay off its promise within about 30-45 s')
    if not c.get('lines'): err(f'{label} has no lines')

# writing hygiene
for i, ln in enumerate(flat):
    n = len(words_of(ln['text']))
    if n > 30: warn(f'line {i} has {n} words; one line is one beat, so split it ("{ln["text"][:50]}...")')
    if re.search(r'\d', ln['text']): warn(f'line {i}: digits in the narration ("{re.search(r".{0,15}\d+.{0,10}", ln["text"]).group(0)}"): write numbers as they are said ("nineteen ninety-four", "three million")')
    if re.search(r'[A-Z]{3,}', re.sub(r'\b(UK|USA|NASA|FBI|CIA|NATO|GDP|CEO|AI|TV|EU|UN|DNA|NHS|BBC|CNN|FAQ|PhD)\b', '', ln['text'])): warn(f'line {i}: ALL-CAPS word in the narration; TTS may spell it out')
for i, ln in enumerate(flat):
    tx = ln['text']
    if re.search(r'[%$&@#+=<>/\\]', re.sub(r'https?://\S+', '', tx)): warn(f'line {i}: a symbol (% $ & @ # + = < > /) in the narration: write it as it is said ("percent", "dollars", "and"), or add it to "pronounce"')
    if re.search(r'https?://|www\.', tx): warn(f'line {i}: a web address in the narration; the voice will spell it badly. Say it in words and put the link in the description')
    if re.search(r'\b(e\.g\.|i\.e\.|etc\.|vs\.|approx\.)', tx, re.I): warn(f'line {i}: abbreviation (e.g. / i.e. / etc. / vs.) is read badly by the voice; write "for example", "that is", "and so on", "versus"')
    if re.search(r'\b(Mr|Mrs|Ms|Dr|St|Prof|Jr|Sr)\.', tx): warn(f'line {i}: a title abbreviation with a full stop (Dr., St.) can split the sentence; write "Doctor", "Saint", or use "pronounce"')
    if re.search(r'\([^)]{20,}\)', tx): warn(f'line {i}: a long parenthesis is awkward to hear; make it its own sentence')
for gi, g in enumerate(re.split(r'(?<=[.?!])["\')]*\s+', ' '.join(l['text'] for l in flat))):
    if len(words_of(g)) > 45: warn(f'a single sentence has {len(words_of(g))} words ("{g[:60]}..."); the voice runs out of breath. Split it')
for i in range(1, len(flat)):
    if flat[i]['text'].strip().lower() == flat[i - 1]['text'].strip().lower(): warn(f'line {i} repeats line {i - 1} word for word')
ncall = sum(1 for _, _, sp in ranges if sp.get('type') == 'callout')
if ncall > 8: warn(f'{ncall} callouts; they are seasoning (3-6 in a 15-minute video)')
if not S.get('sources'): warn('no "sources" in script.json: list the real sources behind your facts (they go in the description)')
tm = S.get('targetMinutes')
mins = total / 60
if tm and abs(mins - tm) > max(1.5, tm * 0.12): warn(f'estimated {mins:.1f} min vs targetMinutes {tm}')
elif not tm and not (8 <= mins <= 24): warn(f'estimated {mins:.1f} min (this skill is tuned for 8-24 minute videos)')

print(f'{S.get("title")}: {len(chapters)} chapters, {len(flat)} lines, {wc} words, estimated {int(mins)}:{int(total % 60):02d} at {WPS:.1f} words/s')
print(f'scenes: {len(ranges)} (one every {total / max(1, len(ranges)):.1f} s on average; longest ~{max(durs):.0f} s)')
for ci, (c, (a, b)) in enumerate(zip(chapters, ch_times)):
    print(f'  {ci:2d} {int(a // 60)}:{int(a % 60):02d}  {b - a:4.0f} s  {len([r for r in ranges if flat[r[0]]["ch"] == ci]):2d} scenes  {c.get("title")}')
for m in warns: print('  warning:', m)
for m in errors: print('  ERROR:', m)
print('SCRIPT OK' if not errors else f'{len(errors)} error(s): fix before voicing')
sys.exit(1 if errors else 0)
