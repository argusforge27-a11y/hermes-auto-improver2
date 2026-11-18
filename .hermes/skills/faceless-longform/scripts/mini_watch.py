"""mini_watch: let the agent SEE a local video using only ffmpeg (no yt-dlp, no network, no API). Built for checking our own renders.

  scripts/py scripts/mini_watch.py <video> [--start 0:30] [--end 1:10] [--max-frames 24] [--mode even|scenes] [--width 640]
                                   [--project .] [--out review/watch]

Writes evenly spaced (or scene-change) frames as JPEGs and a timeline (<out>/timeline.md) that puts the narration line spoken at each
moment next to its frame, taken from data/lines.json in the project. Then YOU view the frames in order with your image tool.
For videos from a URL, or when you need a real transcript of someone else's video, use the full Watch skill: ./lf watch <url>.
"""
import argparse, json, re, subprocess, sys
from pathlib import Path


def secs(x):
    parts = [float(p) for p in str(x).split(':')]
    return sum(p * 60 ** i for i, p in enumerate(reversed(parts)))


def fmt(t): return f'{int(t // 60)}:{t % 60:04.1f}'


ap = argparse.ArgumentParser(); ap.add_argument('video'); ap.add_argument('--start', default='0'); ap.add_argument('--end')
ap.add_argument('--max-frames', type=int, default=24); ap.add_argument('--mode', choices=['even', 'scenes'], default='even'); ap.add_argument('--width', type=int, default=640)
ap.add_argument('--project', default='.'); ap.add_argument('--out'); a = ap.parse_args()
V = Path(a.video)
if not V.exists(): sys.exit(f'ERROR: {V} not found')
P = Path(a.project); out = Path(a.out) if a.out else P / 'review' / 'watch'; out.mkdir(parents=True, exist_ok=True)
for old in out.glob('w*.jpg'): old.unlink()
r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(V)], capture_output=True, text=True)
try: dur = float(r.stdout.strip())
except ValueError: sys.exit(f'ERROR: ffprobe cannot read {V} (is it a video?): {r.stderr.strip()[:200]}')
t0 = secs(a.start); t1 = min(dur, secs(a.end)) if a.end else dur
if t1 <= t0: sys.exit(f'ERROR: --start {a.start} is not before the end ({fmt(t1)})')
n = max(1, a.max_frames)
even = [t0 + (t1 - t0) * (k + 0.5) / n for k in range(n)]
if a.mode == 'scenes':
    q = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-ss', str(t0), '-to', str(t1), '-i', str(V), '-vf', "scale=320:-2,select='gt(scene,0.22)',showinfo", '-an', '-f', 'null', '-'], capture_output=True, text=True)
    cand = sorted([t0 + 0.3] + [t0 + float(m) + 0.3 for m in re.findall(r'pts_time:([\d.]+)', q.stderr)])   # +0.3 s: after the transition has settled
    times = []
    for t in cand + even:                                  # scene changes first, then even spacing to fill the gaps; never two frames closer than 1.5 s
        if all(abs(t - u) >= 1.5 for u in times): times.append(t)
        if len(times) >= n: break
    times = sorted(min(t, t1 - 0.05) for t in times)
else: times = even
lines = json.loads((P / 'data/lines.json').read_text())['lines'] if (P / 'data/lines.json').exists() else []
chs = json.loads((P / 'data/chapters.json').read_text()) if (P / 'data/chapters.json').exists() else []
rows = ['| # | time | frame | chapter | narration at that moment |', '|---|---|---|---|---|']
for k, t in enumerate(times):
    f = out / f'w{k:02d}_t{t:06.1f}.jpg'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.2f}', '-i', str(V), '-frames:v', '1', '-vf', f'scale={a.width}:-2', '-q:v', '3', str(f)])
    say = next((l['text'] for l in lines if l['start'] - 0.2 <= t <= l['end'] + 0.35), '')
    if not say: prev = [l for l in lines if l['end'] < t]; say = ('(pause) after: ' + prev[-1]['text']) if prev else ''
    ch = next((c['title'] for c in reversed(chs) if c['start'] <= t), '')
    rows.append(f'| {k} | {fmt(t)} | {f.relative_to(P) if f.is_relative_to(P.resolve()) or f.is_relative_to(P) else f} | {ch} | {say[:110]} |')
(out / 'timeline.md').write_text(f'# {V.name}: {fmt(t0)} to {fmt(t1)} ({len(times)} frames, mode {a.mode})\n\n' + '\n'.join(rows) + '\n')
print((out / 'timeline.md').read_text())
print('Now view each frame image in order (your image-viewing tool). Look for: text overflow, empty or cramped scenes, the same layout repeating, captions colliding with content, wrong theme contrast.')
