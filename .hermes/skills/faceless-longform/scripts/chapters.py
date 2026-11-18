"""YouTube chapter list + source/credits block from the finished timing.

  scripts/py scripts/chapters.py <project> [--hook-title "Intro"]   -> renders/chapters.txt and renders/description-blocks.md

Needs data/chapters.json (node tools/capture.mjs cues). YouTube rules this respects: the list starts at 0:00, has at least 3
chapters, each at least 10 seconds long. The hook chapter is renamed (default "Intro") because "The Hook" is not a viewer-friendly name.
"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from lf_common import load_script

ap = argparse.ArgumentParser(); ap.add_argument('project'); ap.add_argument('--hook-title', default='Intro'); a = ap.parse_args()
P = Path(a.project); S = load_script(P); ch = json.loads((P / 'data/chapters.json').read_text())
fmt = lambda s: f'{int(s // 3600)}:{int(s % 3600 // 60):02d}:{int(s % 60):02d}' if s >= 3600 else f'{int(s // 60)}:{int(s % 60):02d}'
hook = S.get('chapters', [{}])[0].get('hook') is True or (S.get('chapters', [{}])[0].get('hook') is None and len(ch) > 1 and any(w in ch[0]['title'].lower() for w in ('hook', 'cold open', 'intro')))
rows = []
for c in ch:
    title = a.hook_title if (c['i'] == 0 and hook) else c['title']
    rows.append((0 if c['i'] == 0 else c['start'], title))
problems = []
if len(rows) < 3: problems.append('YouTube needs at least 3 chapters for the list to appear')
for (s0, t0), (s1, _) in zip(rows, rows[1:] + [(ch[-1]['end'], '')]):
    if s1 - s0 < 10: problems.append(f'chapter "{t0}" is shorter than 10 s')
(P / 'renders').mkdir(exist_ok=True)
txt = '\n'.join(f'{fmt(s)} {t}' for s, t in rows)
(P / 'renders/chapters.txt').write_text(txt + '\n')
src = '\n'.join(f'- {s}' for s in S.get('sources', []))
cred = '\n'.join(f'- {s}' for s in S.get('credits', []))
(P / 'renders/description-blocks.md').write_text(f'## Chapters (paste into the description)\n{txt}\n\n## Sources\n{src or "- (none listed)"}\n\n## Image and music credits\n{cred or "- (none)"}\n')
print(txt)
for p in problems: print('warning:', p)
print('-> renders/chapters.txt, renders/description-blocks.md')
