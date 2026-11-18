"""Estimated timing with NO voice: script.json -> data/lines.json + data/words.json.

  scripts/py scripts/estimate.py <project> [--wps 2.7]

Use it to preview pacing and render a draft before the real voice exists (Kokoro for 15-20 minutes takes several minutes), or
for a captions-only video that you voice yourself. When voice.py + words.py have run, they overwrite both files.
Standard library only.
"""
import argparse, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from lf_common import load_script, flatten, words_of

ap = argparse.ArgumentParser()
ap.add_argument('project')
ap.add_argument('--wps', type=float, default=2.7, help='speaking rate, words per second (Kokoro at speed 1.0 is about 2.7)')
a = ap.parse_args()
P = Path(a.project)
S = load_script(P)
chapters, flat = flatten(S)
speed = S.get('speed', 1.0)
t = float(S.get('lead', 0.6))
lines, words = [], []
for i, ln in enumerate(flat):
    toks = [w for w in re.sub(r'\*', '', ln['text']).split() if w.strip()]
    letters = [len(re.sub(r'[^A-Za-z0-9]', '', w)) or 1 for w in toks]
    base = len(toks) / (a.wps * speed)
    unit = base / sum(l + 2.5 for l in letters)
    start = t
    for w, l in zip(toks, letters):
        d = (l + 2.5) * unit
        words.append({'w': w, 'line': i, 's': round(t, 3), 'e': round(t + d * 0.92, 3)})
        t += d
        if w.endswith(','): t += 0.16
        elif re.search(r'[.?!]$', w) and w is not toks[-1]: t += 0.32
    lines.append({'i': i, 'text': ln['text'], 'start': round(start, 3), 'end': round(t, 3)})
    gap = ln.get('gap', S.get('chapter_gap', 0.9) if (i + 1 < len(flat) and flat[i + 1]['first']) else S.get('gap', 0.35))
    if re.search(r'[.?!]["\')]*$', ln['text'].strip()): t += float(gap)
    else: t += 0.12
dur = lines[-1]['end'] + float(S.get('outro', 2.5))
(P / 'data').mkdir(exist_ok=True)
(P / 'data/lines.json').write_text(json.dumps({'duration': round(dur, 3), 'estimated': True, 'lines': lines}, indent=1))
(P / 'data/words.json').write_text(json.dumps(words, indent=1))
m, s = divmod(dur, 60)
print(f'estimated timing: {len(lines)} lines, {len(words)} words, {int(m)}:{int(s):02d} ({dur:.1f} s) -> data/lines.json, data/words.json')
