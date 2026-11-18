"""Automatic QA of a finished render, without needing to "see" it: numbers first, pictures second.

  scripts/py scripts/qa_video.py <project> [file] [--draft] [--frames 10]     -> renders/qa.md + review/final/*.jpg + review/final-sheet.jpg
  scripts/py scripts/qa_video.py <project> --share 45                        -> renders/share.mp4 (720p, under ~45 MB) for chat delivery

Checks (one pass over the file): video + audio streams, 1920x1080, frame rate, duration vs the narration timing in data/lines.json,
black frames (other than the first and last fade), long static stretches, dead air in the soundtrack, loudness (target about -16 LUFS),
true peak, size and bitrate. Then it extracts evenly spaced frames and a contact sheet so a model with vision (or you) can look.
Exit code 1 if there is an ERROR. Standard library + ffmpeg only.
"""
import argparse, json, re, subprocess, sys
from pathlib import Path

ap = argparse.ArgumentParser(); ap.add_argument('project'); ap.add_argument('file', nargs='?'); ap.add_argument('--draft', action='store_true')
ap.add_argument('--frames', type=int, default=10); ap.add_argument('--share', type=float, help='make renders/share.mp4 of about this many MB')
a = ap.parse_args(); P = Path(a.project)
f = Path(a.file) if a.file else P / 'renders' / ('draft.mp4' if a.draft else 'final.mp4')
if not f.exists() and not a.file and a.share and (P / 'renders' / 'draft.mp4').exists(): f = P / 'renders' / 'draft.mp4'; print('note: no final.mp4 yet, using draft.mp4')
if not f.exists(): sys.exit(f'ERROR: {f} not found. Render first (./lf draft or ./lf final).')


def run(cmd): return subprocess.run(cmd, capture_output=True, text=True)


def probe():
    r = run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration,size,bit_rate:stream=codec_type,codec_name,width,height,avg_frame_rate', '-of', 'json', str(f)])
    if r.returncode: sys.exit(f'ERROR: ffprobe could not read {f}: {r.stderr.strip()[:200]}')
    return json.loads(r.stdout)


info = probe(); dur = float(info['format']['duration']); size_mb = int(info['format']['size']) / 1e6
v = next((s for s in info['streams'] if s['codec_type'] == 'video'), None); au = next((s for s in info['streams'] if s['codec_type'] == 'audio'), None)

if a.share:
    out = P / 'renders' / 'share.mp4'; abr = 96; vbr = max(200, int(a.share * 8192 / dur - abr))
    r = run(['ffmpeg', '-v', 'error', '-y', '-i', str(f), '-vf', 'scale=1280:720:flags=lanczos', '-c:v', 'libx264', '-preset', 'veryfast', '-b:v', f'{vbr}k', '-maxrate', f'{int(vbr * 1.4)}k',
             '-bufsize', f'{vbr * 2}k', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', f'{abr}k', '-movflags', '+faststart', str(out)])
    if r.returncode: sys.exit('ERROR: ffmpeg failed: ' + r.stderr[-300:])
    print(f'{out} ({out.stat().st_size / 1e6:.1f} MB, 720p, {vbr} kbps video). Chat apps cap upload size (often somewhere between 10 and 50 MB): use ./lf share 20 for a smaller file.')
    sys.exit(0)

errors, warns, notes = [], [], []
draft = a.draft or 'draft' in f.name
if not v: errors.append('no video stream')
else:
    if (v['width'], v['height']) != (1920, 1080): errors.append(f'size is {v["width"]}x{v["height"]}, expected 1920x1080')
    n, d = (int(x) for x in v['avg_frame_rate'].split('/')); fps = n / d if d else 0
    if abs(fps - (15 if draft else 30)) > 1.5 and not (24 <= fps <= 31 and not draft): warns.append(f'frame rate is {fps:.1f} fps (draft 15, final 24-30)')
    if v['codec_name'] != 'h264': warns.append(f'video codec is {v["codec_name"]}; YouTube prefers h264')
if not au: errors.append('NO AUDIO STREAM: run ./lf cues, ./lf mix, then render again (a render without data/mix.wav is silent)')
elif au['codec_name'] != 'aac': warns.append(f'audio codec is {au["codec_name"]}, expected aac')

lj = P / 'data' / 'lines.json'
if lj.exists():
    want = json.loads(lj.read_text())['duration']
    if abs(want - dur) > (0.6 if draft else 0.3): errors.append(f'duration is {dur:.2f} s but the narration timing says {want:.2f} s (the script, voice or mix changed after this render: render again)')
else: notes.append('data/lines.json not found; duration not compared with the narration')

# one pass: black frames, static stretches, silence, loudness (video analysed at a small size to stay fast)
r = run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(f), '-vf', 'scale=320:-2,blackdetect=d=0.4:pix_th=0.10,freezedetect=n=-60dB:d=15',
         '-af', 'silencedetect=n=-45dB:d=4,ebur128=peak=true', '-f', 'null', '-'])
log = r.stderr
for m in re.finditer(r'black_start:([\d.]+) black_end:([\d.]+) black_duration:([\d.]+)', log):
    s, e, d = float(m[1]), float(m[2]), float(m[3])
    if s < 0.7 or e > dur - 0.2 and s > dur - 2.5: continue          # the planned fade from and to black
    (errors if d > 1.5 else warns).append(f'black screen for {d:.1f} s at {s:.1f} s (a scene failed to draw? run ./lf check, then look at that time with ./lf frames)')
fs = re.findall(r'freeze_start: ([\d.]+)', log); fd = re.findall(r'freeze_duration: ([\d.]+)', log)
for k, s in enumerate(fs):                                            # a freeze that lasts to the end of the file has no duration line
    d = float(fd[k]) if k < len(fd) else max(0.0, dur - float(s))
    warns.append(f'picture almost static for {d:.0f} s from {float(s):.1f} s: add a scene change or a re-hook')
sil = re.findall(r'silence_start: ([\d.]+)', log); sild = re.findall(r'silence_duration: ([\d.]+)', log)
for s, d in zip(sil, sild):
    if float(s) > dur - 4.5: continue                               # the planned outro tail
    warns.append(f'no sound for {float(d):.0f} s from {float(s):.1f} s (the voice or music stopped; check data/mix.wav and the narration there)')
summ = log[log.rfind('Summary:'):] if 'Summary:' in log else ''
lu = re.search(r'I:\s+(-?[\d.]+) LUFS', summ); tp = re.search(r'Peak:\s+(-?[\d.]+) dBFS', summ)
if lu:
    L = float(lu[1])
    if L < -19 or L > -13: warns.append(f'integrated loudness {L:.1f} LUFS (target about -16; re-run ./lf mix)')
    else: notes.append(f'loudness {L:.1f} LUFS')
elif au: warns.append('could not measure loudness')
if tp and float(tp[1]) > -0.5: warns.append(f'true peak {tp[1]} dBFS is hot (may clip after YouTube re-encodes); re-run ./lf mix')
br = size_mb * 8 / dur
notes.append(f'{dur / 60:.1f} min, {size_mb:.0f} MB, {br:.1f} Mbps')
if not draft and (br < 0.4 or br > 14): warns.append(f'bitrate {br:.1f} Mbps is unusual for flat motion graphics (usually 2-5)')

# frames to look at
rv = P / 'review' / ('draft' if draft else 'final'); rv.mkdir(parents=True, exist_ok=True)
for old in rv.glob('*.jpg'): old.unlink()
for k in range(a.frames):
    t = dur * (k + 0.5) / a.frames
    run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.2f}', '-i', str(f), '-frames:v', '1', '-vf', 'scale=960:-2', '-q:v', '3', str(rv / f'f{k:02d}_t{t:06.1f}.jpg')])
frames = sorted(rv.glob('f*.jpg'))
if frames:
    cols = 4; rows = -(-len(frames) // cols); sheet = P / 'review' / (('draft' if draft else 'final') + '-sheet.jpg')
    run(['ffmpeg', '-v', 'error', '-y', '-framerate', '1', '-pattern_type', 'glob', '-i', str(rv / 'f*.jpg'), '-vf', f'scale=480:-2,tile={cols}x{rows}:padding=4:color=black', '-frames:v', '1', '-q:v', '3', str(sheet)])
else: warns.append('could not extract frames for review')

lines = [f'# QA: {f.name}', '', f'Result: **{"FAIL" if errors else "PASS"}** ({len(errors)} error(s), {len(warns)} warning(s))', '']
lines += [f'- ERROR: {m}' for m in errors] + [f'- warning: {m}' for m in warns] + [f'- {m}' for m in notes]
lines += ['', f'Look at: review/{"draft" if draft else "final"}-sheet.jpg (contact sheet) and the {len(frames)} frames in review/{"draft" if draft else "final"}/. Check text fits, nothing important sits below the caption line, captions are readable, no two neighbours look identical.']
(P / 'renders').mkdir(exist_ok=True); (P / 'renders' / 'qa.md').write_text('\n'.join(lines) + '\n')
print('\n'.join(lines)); sys.exit(1 if errors else 0)
