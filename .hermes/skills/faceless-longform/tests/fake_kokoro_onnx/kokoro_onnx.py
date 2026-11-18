"""A stand-in for kokoro_onnx used ONLY by selftest (PYTHONPATH + FACELESS_FAKE_TTS=1). It "speaks" a soft tone burst per word with a
short pause at commas and a longer one at full stops, so voice.py's sentence grouping, pause detection, caching and timing can be tested
without the 340 MB model. It never replaces the real voice: the real package is untouched."""
import re
import numpy as np


class Kokoro:
    def __init__(self, *a, **k): pass
    def get_voices(self): return ['bm_george', 'am_michael', 'af_heart']

    def create(self, text, voice='bm_george', speed=1.0, lang='en-us'):
        if not text.strip(): raise ValueError('empty text')
        sr = 24000; out = []
        for w in text.split():
            n = int(sr * (0.05 + 0.028 * len(re.sub(r'\W', '', w))) / speed); t = np.arange(n) / sr
            f = 140 + (hash(w) % 60); env = np.minimum(1, np.minimum(t / 0.02, (n / sr - t) / 0.02))
            out.append((0.35 * np.sin(2 * np.pi * f * t) * env).astype(np.float32))
            out.append(np.zeros(int(sr * (0.30 if w[-1] in '.?!' else 0.14 if w[-1] == ',' else 0.02)), dtype=np.float32))
        return np.concatenate(out), sr
