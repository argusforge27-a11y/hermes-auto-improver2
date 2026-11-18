"""Long-form soundtrack: narration + a chapter-by-chapter music bed + soft scene sounds, all made here with numpy. No samples, no downloads.

  python3 tools/mix.py [project=.]          -> data/mix.wav (48 kHz stereo, loudness-normalised to about -16 LUFS)

Reads data/narration.wav (voice.py or words.py --audio), data/cues.json + data/chapters.json (node tools/capture.mjs cues) and script.json:
  "music": "bed"                   the procedural score (default): a different key and feel in every chapter, crossfaded
          "none"                   voice and sound effects only
          "audio/your-track.mp3"   your own royalty-free track (looped with crossfades), ducked under the voice
  "musicLevel": -27                music loudness in dB relative to full scale RMS (default -27; the voice sits at -19)
  chapter "mood": "calm" | "tense" | "upbeat" | "epic" | "mellow"    (default calm)  picks that chapter's chords, tempo and texture
Sound rules: every effect is soft and rounded (nothing above ~5 kHz), no clicks, ticks, beeps or glitches.
Needs ~1 GB of free RAM for 20 minutes of audio.
"""
import json, subprocess, sys, tempfile, os
from pathlib import Path
import numpy as np
from scipy import signal
from scipy.io import wavfile

P = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
SR = 48000
rng = np.random.default_rng(7)
def need(f, hint):
    if not (P / f).exists(): sys.exit(f'ERROR: {f} is missing. {hint}')
    try: return json.loads((P / f).read_text())
    except json.JSONDecodeError as e: sys.exit(f'ERROR: {f} is not valid JSON ({e}). Delete it and rebuild: {hint}')
cj = need('data/cues.json', 'Run ./lf cues first (it draws the film and writes the sound cues).')
script = need('script.json', 'Run this from the project folder.')
chapters = json.loads((P / 'data/chapters.json').read_text()) if (P / 'data/chapters.json').exists() else [{'i': 0, 'start': 0, 'end': cj['duration'], 'mood': None}]
DUR = float(cj['duration']); N = int(DUR * SR) + SR // 10
F32 = np.float32


def lp(x, f, o=2): b, a = signal.butter(o, min(f, SR / 2 - 100) / (SR / 2), 'low'); return signal.lfilter(b, a, x).astype(F32)
def hp(x, f, o=2): b, a = signal.butter(o, f / (SR / 2), 'high'); return signal.lfilter(b, a, x).astype(F32)
def bp(x, f0, f1, o=2): b, a = signal.butter(o, [f0 / (SR / 2), f1 / (SR / 2)], 'band'); return signal.lfilter(b, a, x).astype(F32)
def db(x): return 10 ** (x / 20)
def tt(d): return (np.arange(int(d * SR)) / SR).astype(np.float64)
def env(n, a=0.005, r=5.0):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na); rest = n - na
    if rest > 0: e[na:] = np.exp(-np.linspace(0, r, rest))
    return e
def sweep(f0, f1, d):
    t = tt(d); f = f0 * (f1 / f0) ** (t / d); return np.sin(2 * np.pi * np.cumsum(f) / SR)
def noise(d): return rng.standard_normal(int(d * SR))
def norm(x): return x / (np.abs(x).max() + 1e-9)


# ---------- scene sounds ----------
def whoosh(**_):
    d = 0.5; n = noise(d); lo, hi = lp(n, 500), lp(n, 2400); k = np.sin(np.pi * np.linspace(0, 1, len(n))); x = (lo * (1 - k) + hi * k) * k ** 1.5; return norm(x) * 0.5
def pop(**_): x = sweep(560, 240, 0.11) * env(int(0.11 * SR), 0.002, 6); return lp(x, 3000) * 0.7
def chime(**_):
    x = np.zeros(int(1.6 * SR))
    for k, f in enumerate([784, 1047, 1319]):
        st = int(k * 0.11 * SR); n = int(1.0 * SR); t = tt(1.0); x[st:st + n] += (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)) * env(n, 0.004, 5) * 0.3
    return lp(x, 4500)
def hit(**_):
    d = 0.7; t = tt(d); x = np.sin(2 * np.pi * (55 + 70 * np.exp(-t * 22)) * t) * env(len(t), 0.002, 5); return np.tanh(1.5 * (x + lp(noise(d), 900) * env(len(t), 0.001, 9) * 0.5)) * 0.9
def slide(**_): d = 1.0; n = lp(noise(d), 700); e = np.sin(np.pi * np.linspace(0, 1, len(n))) ** 2; return norm(n) * e * 0.35 + sweep(260, 120, d) * e * 0.08
def thud(**_): d = 0.35; t = tt(d); return np.sin(2 * np.pi * (70 + 40 * np.exp(-t * 30)) * t) * env(len(t), 0.002, 7) * 0.9
def riser(**_):
    d = 1.6; t = tt(d); n = bp(noise(d), 300, 3500) * np.linspace(0, 1, len(t)) ** 2; return norm(n) * 0.4 + sweep(120, 520, d) * np.linspace(0, 1, len(t)) ** 2 * 0.15
FX = dict(whoosh=whoosh, pop=pop, chime=chime, hit=hit, slide=slide, thud=thud, riser=riser)
LEVEL = dict(whoosh=-19, pop=-17, chime=-18, hit=-11, slide=-20, thud=-12, riser=-20)


# ---------- the music bed ----------
MOODS = {   # chord progression (semitone roots, quality), tempo (bpm), texture
    'calm':   dict(bpm=72, prog=[(0, 'maj7'), (9, 'min7'), (5, 'maj7'), (7, 'sus')], pluck=[0, 2], bass=True, pad=1.0),
    'mellow': dict(bpm=66, prog=[(5, 'maj7'), (4, 'min7'), (2, 'min7'), (0, 'maj7')], pluck=[0, 1, 2, 1], bass=True, pad=0.8),
    'upbeat': dict(bpm=104, prog=[(0, 'maj'), (7, 'maj'), (9, 'min'), (5, 'maj')], pluck=[0, 1, 2, 1, 2, 1, 0, 1], bass=True, pad=0.7),
    'tense':  dict(bpm=62, prog=[(9, 'min'), (5, 'maj'), (2, 'min'), (4, 'maj')], pluck=[2], bass=True, pad=1.1, drone=True),
    'epic':   dict(bpm=78, prog=[(2, 'min'), (10, 'maj'), (5, 'maj'), (0, 'maj')], pluck=[], bass=True, pad=1.5, drone=True),
}
QUAL = dict(maj=[0, 4, 7], min=[0, 3, 7], maj7=[0, 4, 7, 11], min7=[0, 3, 7, 10], sus=[0, 5, 7])
KEYS = [0, 2, -3, 5, -1, 3, -5, 1]            # a new key every chapter so a long video never sits in one place
ROOT = 130.81                                  # C3


def music_chapter(mood, dur, key):
    m = MOODS.get(mood or 'calm', MOODS['calm']); beat = 60 / m['bpm']; bar = beat * 4; n = int(dur * SR) + int(bar * SR); x = np.zeros(n, dtype=F32)
    nb = int(np.ceil(dur / bar)) + 1
    for b in range(nb):
        root, q = m['prog'][b % len(m['prog'])]; f0 = ROOT * 2 ** ((root + key) / 12); tones = [f0 * 2 ** (s / 12) for s in QUAL[q]]
        st = int(b * bar * SR); t = tt(bar * 1.15); L = len(t)
        e = np.minimum(1, t / (0.7 * m['pad'])) * np.minimum(1, (bar * 1.15 - t) / 0.9)
        pad = sum(np.sin(2 * np.pi * f * t + 0.4 * np.sin(2 * np.pi * 0.17 * t + k)) + 0.3 * np.sin(2 * np.pi * f * 2.003 * t) for k, f in enumerate(tones)) * e * 0.085 * m['pad']
        if m.get('bass'): pad = pad + np.sin(2 * np.pi * (f0 / 2) * t) * e * 0.16
        if m.get('drone'): pad = pad + np.sin(2 * np.pi * (f0 / 4) * t) * e * 0.12
        x[st:st + L] += pad[:max(0, min(L, n - st))].astype(F32)
        for k, idx in enumerate(m['pluck']):
            step = bar / len(m['pluck']); ps = st + int(k * step * SR); pn = int(1.1 * SR)
            if ps + pn >= n: continue
            f = tones[idx % len(tones)] * (2 if (k + b) % 3 == 0 else 1); pt = tt(1.1)
            x[ps:ps + pn] += ((np.sin(2 * np.pi * f * pt) + 0.3 * np.sin(4 * np.pi * f * pt)) * env(pn, 0.004, 6) * 0.10).astype(F32)
    return lp(x, 3000)[:int(dur * SR)]


def music_track(dur, f):
    """your own track, looped to the film length with 3 s crossfades at the loop points"""
    out = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(f), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    a = np.frombuffer(out, dtype=F32).copy(); a /= np.abs(a).max() + 1e-9; n = int(dur * SR); xf = min(int(3 * SR), len(a) // 4); res = np.zeros(n, dtype=F32); pos = 0
    while pos < n:
        seg = a.copy()
        if pos: seg[:xf] *= np.linspace(0, 1, xf).astype(F32)
        seg[-xf:] *= np.linspace(1, 0, xf).astype(F32)
        take = min(len(seg), n - pos); res[pos:pos + take] += seg[:take]; pos += len(a) - xf
    return res


def build_music():
    mus = script.get('music', 'bed')
    if not mus or mus == 'none': return None
    if mus != 'bed':
        if not (P / mus).exists(): print(f'WARNING: music file {mus} not found; using the built-in bed instead'); mus = 'bed'
        else: return music_track(DUR, P / mus)
    m = np.zeros(N, dtype=F32); xf = int(2.5 * SR)
    for c in chapters:
        a = max(0, int((c['start'] - 1.25) * SR)); dur = (c['end'] - c['start']) + 2.5; seg = music_chapter(c.get('mood'), dur, KEYS[c['i'] % len(KEYS)])
        f = np.ones(len(seg), dtype=F32); f[:xf] = np.linspace(0, 1, xf); f[-xf:] = np.minimum(f[-xf:], np.linspace(1, 0, xf))
        if c['i'] == 0: f[:int(2 * SR)] = np.linspace(0, 1, int(2 * SR))
        b = min(N, a + len(seg)); m[a:b] += (seg * f)[:b - a]
    fo = int(4 * SR); m[-fo:] *= np.linspace(1, 0, fo).astype(F32); return m


def load_audio(f):
    out = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(f), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(out, dtype=F32).copy()


mix = np.zeros((N, 2), dtype=F32)
voice = None; vf = P / 'data/narration.wav'
if vf.exists():
    v = load_audio(vf)[:N]; voice = np.zeros(N, dtype=F32); voice[:len(v)] = v
    act = np.abs(voice) > 0.02; rms = np.sqrt(np.mean(voice[act] ** 2) + 1e-12) if act.any() else 0.1; voice *= F32(db(-19) / rms)   # level on the speech itself, not the pauses
    mix += voice[:, None]
m = build_music()
if m is not None:
    m = m * F32(db(script.get('musicLevel', -27 if voice is not None else -20)) / (np.sqrt(np.mean(m ** 2)) + 1e-9))
    if voice is not None:                                                      # duck under the voice: 100 Hz envelope, quick attack, slow release
        hop = SR // 100; nf = N // hop; lev = np.abs(voice[:nf * hop]).reshape(nf, hop).max(1)
        e = np.zeros(nf); a_, r_ = 1 - np.exp(-1 / (0.04 * 100)), 1 - np.exp(-1 / (0.55 * 100))
        for i in range(1, nf): e[i] = e[i - 1] + ((a_ if lev[i] > e[i - 1] else r_) * (lev[i] - e[i - 1]))
        g = 1 - 0.6 * np.clip(e / (np.percentile(e, 95) + 1e-9), 0, 1); g = np.interp(np.arange(N) / hop, np.arange(nf), g).astype(F32); m *= g
    mix += m[:, None]
    del m
fx_cache = {}
for c in cj['cues']:
    fn = FX.get(c['type'])
    if not fn: print('unknown cue type, skipped:', c['type']); continue
    if c['type'] not in fx_cache: x0 = fn(); fx_cache[c['type']] = lp(x0, 5000) / (np.abs(x0).max() + 1e-9) * 0.9
    x = fx_cache[c['type']] * F32(db(LEVEL[c['type']]) * c.get('gain', 1.0))
    i = int(c['t'] * SR); n = min(len(x), N - i)
    if n > 0 and i >= 0: mix[i:i + n] += x[:n, None]
np.multiply(mix, F32(1.15), out=mix); np.tanh(mix, out=mix); np.multiply(mix, F32(1 / 1.15), out=mix)   # in place: a 20-minute mix is ~0.5 GB, so no temporary copies
np.multiply(mix, F32(db(-1) / (np.abs(mix).max() + 1e-9)), out=mix)
tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False).name
out16 = np.empty(mix.shape, dtype=np.int16)
for a_ in range(0, len(mix), SR * 30): np.multiply(mix[a_:a_ + SR * 30], F32(32767), out=mix[a_:a_ + SR * 30]); out16[a_:a_ + SR * 30] = mix[a_:a_ + SR * 30]
del mix; wavfile.write(tmp, SR, out16); del out16
r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', str(SR), '-ac', '2', str(P / 'data/mix.wav')])
if r.returncode: os.replace(tmp, P / 'data/mix.wav'); print('loudnorm failed; wrote the un-normalised mix')
else: os.unlink(tmp)
print(f"data/mix.wav: {DUR:.1f} s · voice: {'yes' if voice is not None else 'NO (captions-only)'} · music: {script.get('music', 'bed')} · {len(cj['cues'])} cues")
