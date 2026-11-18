"""Narration for $0 on this computer: Kokoro-82M text-to-speech (Apache-2.0) via kokoro-onnx. No account, no API.

  scripts/py scripts/voice.py <project>          script.json -> data/narration.wav + data/lines.json (exact line times)
  scripts/py scripts/voice.py --list             voices that narrate well
  scripts/py scripts/voice.py --download         only fetch the model files (~340 MB, once)

Built for 15-20 minute scripts:
  * every sentence is cached in data/cache/ (keyed by voice + speed + text), so a re-run only speaks what you changed and a
    run that was interrupted resumes where it stopped. Editing one chapter never re-voices the others.
  * one line = one on-screen beat. Lines are grouped into whole sentences; each sentence is spoken in ONE pass (natural
    intonation) and the cuts between its lines are placed at the nearest pause in the audio.
  * pauses: "gap" on a line = pause after it (default script "gap" 0.35 s); the last line of a chapter pauses "chapter_gap" (0.9 s).
script.json: { "voice": "bm_george", "speed": 1.0, "lead": 0.6, "outro": 2.5, "gap": 0.35, "chapter_gap": 0.9, "chapters": [ { "title": "...", "lines": [ { "text": "..." } ] } ] }
Write numbers the way they are SAID ("eighteen fifty-eight", "three hundred million"). Then run words.py for word timings.
"""
import argparse, hashlib, json, os, re, sys, time, urllib.request
from pathlib import Path
import numpy as np
from scipy.io import wavfile
sys.path.insert(0, str(Path(__file__).parent))
from lf_common import load_script, flatten, speakable, die

HOME = Path(os.environ.get('FACELESS_HOME', Path.home() / '.faceless-shorts'))
KDIR = HOME / 'kokoro'
FILES = {
    'kokoro-v1.0.onnx': 'https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx',
    'voices-v1.0.bin': 'https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin',
}
GOOD = {
    'bm_george': 'UK male, documentary (best for long history / science narration)', 'bm_fable': 'UK male, storyteller',
    'am_michael': 'US male, steady explainer', 'am_fenrir': 'US male, deeper', 'am_onyx': 'US male, low', 'am_puck': 'US male, lively',
    'af_heart': 'US female, warm (best overall female)', 'af_nicole': 'US female, soft and close', 'af_bella': 'US female, bright',
    'bf_emma': 'UK female, calm',
}
SR = 24000


MIN_BYTES = {'kokoro-v1.0.onnx': 200_000_000, 'voices-v1.0.bin': 10_000_000}   # a truncated download is smaller than this


def ensure_models():
    if os.environ.get('FACELESS_FAKE_TTS'): return          # tests: a stand-in narrator needs no model files
    KDIR.mkdir(parents=True, exist_ok=True)
    for name, url in FILES.items():
        p = KDIR / name
        if p.exists() and p.stat().st_size >= MIN_BYTES[name]: continue
        if p.exists(): p.unlink()                           # truncated or corrupt from an earlier failed download
        err = None
        for attempt in range(1, 4):
            print(f'downloading {name} (once; attempt {attempt}/3)...', flush=True)
            tmp = p.with_suffix('.part')
            try:
                urllib.request.urlretrieve(url, tmp)
                if tmp.stat().st_size < MIN_BYTES[name]: raise IOError(f'download too small ({tmp.stat().st_size} bytes)')
                tmp.rename(p); err = None; break
            except Exception as e:
                err = e; time.sleep(2 * attempt)
        if err: die(f'could not download {name}: {err}. Check the internet connection (GitHub must be reachable) and run again, or copy the file by hand to {KDIR}/.', 3)


def trim(x, thr=0.008):
    """cut leading/trailing silence so line start/end times are exact"""
    idx = np.where(np.abs(x) > thr)[0]
    if not len(idx): return x
    a = max(0, idx[0] - int(0.01 * SR)); b = min(len(x), idx[-1] + int(0.03 * SR)); return x[a:b]


def silences(x, thr=0.012, min_len=0.06):
    """pauses inside speech: [(start_s, end_s)] where the 10 ms RMS stays under thr for >= min_len"""
    hop = int(0.01 * SR); n = len(x) // hop
    if n < 2: return []
    rms = np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, axis=1)); quiet = rms < thr * np.abs(x).max()
    out, st = [], None
    for f, q in enumerate(quiet):
        if q and st is None: st = f
        if (not q or f == n - 1) and st is not None:
            if (f - st) * 0.01 >= min_len: out.append((st * 0.01, f * 0.01))
            st = None
    return out


def weight(text):
    """relative spoken length of a line (letters + a little for each word and for commas), to place cuts inside a sentence"""
    ws = re.sub(r'\*', '', text).split()
    return sum(len(re.sub(r'[^A-Za-z0-9]', '', w)) + 2.5 + (2.5 if w.endswith(',') else 0) for w in ws) or 1.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('project', nargs='?'); ap.add_argument('--list', action='store_true'); ap.add_argument('--download', action='store_true')
    ap.add_argument('--voice'); ap.add_argument('--speed', type=float); ap.add_argument('--fresh', action='store_true', help='ignore the sentence cache')
    a = ap.parse_args()
    if a.list:
        for k, v in GOOD.items(): print(f'{k:12s} {v}')
        return
    ensure_models()
    if a.download: return
    if not a.project: ap.error('project folder missing')
    try:
        from kokoro_onnx import Kokoro
    except ImportError:
        die('kokoro_onnx is not installed in this Python. Run scripts/setup.sh (it builds the private environment), and call this script through scripts/py or ./lf voice.', 3)
    P = Path(a.project); S = load_script(P); chapters, flat = flatten(S)
    voice = a.voice or S.get('voice', 'bm_george'); speed = a.speed or S.get('speed', 1.0); lang = 'en-gb' if voice.startswith('b') else 'en-us'
    k = Kokoro(str(KDIR / 'kokoro-v1.0.onnx'), str(KDIR / 'voices-v1.0.bin'))
    try:
        known = set(k.get_voices())
        if known and voice not in known: die(f'voice "{voice}" does not exist. Try one of: {", ".join(sorted(GOOD))} (./lf voices).')
    except AttributeError: pass
    pron = S.get('pronounce', {})
    cache = P / 'data/cache'; cache.mkdir(parents=True, exist_ok=True)
    stats = {'new': 0, 'cached': 0}

    def say(text):
        spoken = speakable(text, pron)
        key = hashlib.sha1(f'{voice}|{speed}|{lang}|{spoken}'.encode()).hexdigest()[:20]; f = cache / f'{key}.npy'
        if f.exists() and not a.fresh:
            try: stats['cached'] += 1; return np.load(f)
            except Exception: stats['cached'] -= 1; f.unlink()          # a half-written cache file from an interrupted run
        last = None
        for attempt in (spoken, re.sub(r'[\"()\[\]:;]', ' ', spoken)):  # second try: the same words without the punctuation that trips the phonemizer
            try:
                x = trim(np.asarray(k.create(attempt, voice=voice, speed=speed, lang=lang)[0], dtype=np.float32))
                if len(x) < SR * 0.15: raise ValueError('the voice produced almost no audio')
                np.save(f, x); stats['new'] += 1; return x
            except Exception as e: last = e
        die(f'the voice failed on this sentence: "{spoken[:90]}" ({type(last).__name__}: {last}). Reword it (shorter, fewer symbols) or add the hard word to "pronounce" in script.json.', 4)

    # group the lines into whole sentences (a line ending in . ? ! closes one; "break": true forces a close; a chapter end always closes)
    groups, cur = [], []
    for i, ln in enumerate(flat):
        cur.append(i)
        last_of_chapter = i == len(flat) - 1 or flat[i + 1]['first']
        if re.search(r'[.?!]["\')]*$', ln['text'].strip()) or ln.get('break') or last_of_chapter: groups.append(cur); cur = []
    out = [np.zeros(int(S.get('lead', 0.6) * SR), dtype=np.float32)]; t = len(out[0]) / SR; lines = [None] * len(flat); t0 = time.time()
    for gi, g in enumerate(groups):
        x = say(' '.join(flat[i]['text'] for i in g)); cuts = [0.0]
        if len(g) > 1:                                    # find each cut inside the sentence
            lens = np.array([weight(flat[i]['text']) for i in g]); pauses = silences(x)
            for c in np.cumsum(lens)[:-1] / lens.sum() * len(x) / SR:
                near = [p for p in pauses if abs((p[0] + p[1]) / 2 - c) < 0.4]
                if near: p = min(near, key=lambda p: abs((p[0] + p[1]) / 2 - c)); cuts.append((p[0], p[1]))
                else: cuts.append((c, c))
        n = len(x) / SR
        for j, i in enumerate(g):
            s = 0.0 if j == 0 else cuts[j][1]; e = n if j == len(g) - 1 else cuts[j + 1][0]
            lines[i] = {'i': i, 'text': flat[i]['text'], 'start': round(t + s, 3), 'end': round(t + e, 3)}
        last = flat[g[-1]]; end_of_ch = g[-1] == len(flat) - 1 or flat[g[-1] + 1]['first']
        gap = np.zeros(int(float(last.get('gap', S.get('chapter_gap', 0.9) if end_of_ch else S.get('gap', 0.35))) * SR), dtype=np.float32)
        out += [x, gap]; t += (len(x) + len(gap)) / SR
        if gi % 10 == 0 or gi == len(groups) - 1:
            el = time.time() - t0; print(f'  sentence {gi + 1}/{len(groups)} · {t / 60:4.1f} min of audio · {stats["new"]} spoken, {stats["cached"]} from cache · {el:.0f} s', flush=True)
    out.append(np.zeros(int(float(S.get('outro', 2.5)) * SR), dtype=np.float32))
    y = np.concatenate(out); y = y / (np.abs(y).max() + 1e-9) * 0.9
    (P / 'data').mkdir(exist_ok=True)
    wavfile.write(P / 'data/narration.wav', SR, (y * 32767).astype(np.int16))
    dur = len(y) / SR
    (P / 'data/lines.json').write_text(json.dumps({'duration': round(dur, 3), 'voice': voice, 'speed': speed, 'lines': lines}, indent=1))
    m, s = divmod(dur, 60)
    print(f'data/narration.wav ({int(m)}:{int(s):02d}, {voice} x{speed}) + data/lines.json. Next: words.py')


if __name__ == '__main__':
    main()
