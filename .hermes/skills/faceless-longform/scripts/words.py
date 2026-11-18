"""Word timings with local Whisper (faster-whisper small.en, MIT) -> data/words.json [{w, line, s, e}].

  scripts/py scripts/words.py <project>                       after voice.py (uses data/narration.wav + data/lines.json)
  scripts/py scripts/words.py <project> --audio my_vo.m4a      YOUR OWN recording: becomes data/narration.wav, and the
                                                               line times (data/lines.json) are rebuilt from what you said

After voice.py the line times are exact, so Whisper runs chapter by chapter on just that chapter's audio (a mishearing can
never drift the rest of the film). The words keep the SCRIPT's spelling with the times Whisper heard; words it heard
differently ("7" vs "seven") or missed share the time between their matched neighbours, by length.

No Whisper (not installed, or its model can't download)? After voice.py the line times are exact anyway, so each line's
words are spread inside it by length, with pauses at commas and full stops (within ~0.1-0.2 s of the speech).
"""
import argparse, json, re, subprocess, sys
from difflib import SequenceMatcher
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from lf_common import load_script, flatten

norm = lambda w: re.sub(r'[^a-z0-9]+', '', w.lower())


def align(script_words, heard, t0, t1):
    """script_words: [str]; heard: [(word, s, e)] -> [(s, e)] per script word, inside [t0, t1]"""
    a = [norm(w) for w in script_words]; b = [norm(h[0]) for h in heard]
    times = [None] * len(a)
    for blk in SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size): times[blk.a + k] = (heard[blk.b + k][1], heard[blk.b + k][2])
    i = 0
    while i < len(a):
        if times[i] is not None: i += 1; continue
        j = i
        while j < len(a) and times[j] is None: j += 1
        lo = times[i - 1][1] if i > 0 else t0; hi = times[j][0] if j < len(a) else t1
        if hi <= lo: hi = lo + 0.05 * (j - i)
        L = [max(1, len(a[k])) for k in range(i, j)]; tot = sum(L); c = lo
        for k, l in zip(range(i, j), L): d = (hi - lo) * l / tot; times[k] = (c, c + d * 0.9); c += d
        i = j
    return times


def inline_fallback(P, flat):
    L = json.loads((P / 'data/lines.json').read_text())['lines']; words = []
    for i, ln in enumerate(flat):
        toks = [w for w in re.sub(r'\*', '', ln['text']).split() if norm(w)]
        wts = [len(norm(w)) + 2.5 + (2.5 if w.endswith(',') else 4.5 if re.search(r'[.?!]$', w) and k < len(toks) - 1 else 0) for k, w in enumerate(toks)]
        lo, hi = L[i]['start'], L[i]['end']; c = lo; tot = sum(wts)
        for w, wt in zip(toks, wts):
            d = (hi - lo) * wt / tot; speak = d - (hi - lo) * (wt - len(norm(w)) - 2.5) / tot
            words.append({'w': w, 'line': i, 's': round(c, 3), 'e': round(c + speak * 0.92, 3)}); c += d
    write(P, words); print(f'data/words.json: {len(words)} words (spread inside the voice line times)')


def write(P, words):
    (P / 'data/words.json').write_text(json.dumps(words, indent=1))
    (P / 'data/words.txt').write_text('\n'.join(f"{w['s']:8.2f} {w['e']:8.2f}  L{w['line']:<3d} {w['w']}" for w in words))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('project'); ap.add_argument('--audio'); a = ap.parse_args()
    P = Path(a.project); S = load_script(P); chapters, flat = flatten(S)
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel('small.en', device='cpu', compute_type='int8')
    except Exception as e:
        if a.audio or not (P / 'data/lines.json').exists():
            raise SystemExit(f'Whisper is needed for your own recording and could not load: {e}')
        print(f'Whisper unavailable ({type(e).__name__}); spreading words inside the exact line times instead')
        return inline_fallback(P, flat)
    if a.audio:
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', a.audio, '-ac', '1', '-ar', '24000', str(P / 'data/narration.wav')], check=True)
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(P / 'data/narration.wav'), '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    pcm = np.frombuffer(raw, dtype=np.float32); dur_audio = len(pcm) / 16000
    toks = [(w, i) for i, ln in enumerate(flat) for w in re.sub(r'\*', '', ln['text']).split() if norm(w)]
    have_lines = (P / 'data/lines.json').exists() and not a.audio
    try:
        words = []
        if have_lines:      # exact line windows: transcribe + align one chapter at a time
            L = json.loads((P / 'data/lines.json').read_text())['lines']; heard_total = 0
            for ci in range(len(chapters)):
                idx = [i for i, ln in enumerate(flat) if ln['ch'] == ci]; lo, hi = max(0.0, L[idx[0]]['start'] - 0.4), min(dur_audio, L[idx[-1]]['end'] + 0.4)
                segs, _ = model.transcribe(pcm[int(lo * 16000):int(hi * 16000)], word_timestamps=True, vad_filter=False)
                heard = [(w.word.strip(), lo + w.start + 0.04, lo + w.end) for s in segs for w in s.words]; heard_total += len(heard)
                ct = [(w, i) for (w, i) in toks if i in set(idx)]; times = align([w for w, _ in ct], heard, L[idx[0]]['start'], L[idx[-1]]['end'])
                for (w, i), (s, e) in zip(ct, times):
                    l0, l1 = L[i]['start'], L[i]['end']; s = min(max(s, l0), l1); e = min(max(e, s), l1)   # keep every word inside its line's exact window
                    words.append({'w': w, 'line': i, 's': round(s, 3), 'e': round(e, 3)})
                print(f'  chapter {ci + 1}/{len(chapters)}: {len(ct)} words, Whisper heard {len(heard)}', flush=True)
            note = f'Whisper heard {heard_total}'
        else:               # your own recording: one pass over the whole file
            segs, _ = model.transcribe(pcm, word_timestamps=True, vad_filter=False)
            heard = [(w.word.strip(), w.start + 0.04, w.end) for s in segs for w in s.words]
            times = align([w for w, _ in toks], heard, 0.0, dur_audio)
            words = [{'w': w, 'line': i, 's': round(s, 3), 'e': round(e, 3)} for (w, i), (s, e) in zip(toks, times)]
            lines = []
            for i, ln in enumerate(flat):
                ws = [w for w in words if w['line'] == i]; lines.append({'i': i, 'text': ln['text'], 'start': ws[0]['s'], 'end': ws[-1]['e']})
            (P / 'data/lines.json').write_text(json.dumps({'duration': round(dur_audio, 3), 'lines': lines}, indent=1)); note = f'Whisper heard {len(heard)}'
    except Exception as e:
        if not have_lines: raise SystemExit(f'Whisper could not transcribe the recording: {e}')
        print(f'Whisper failed ({type(e).__name__}: {e}); spreading words inside the exact line times instead')
        return inline_fallback(P, flat)
    write(P, words); print(f'data/words.json: {len(words)} words ({note})')


if __name__ == '__main__':
    main()
