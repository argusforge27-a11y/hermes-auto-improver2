#!/usr/bin/env python3
"""Readability check.  readability.py <file> [--spoken] [--max-words 20]"""
import argparse, collections, re, sys
p = argparse.ArgumentParser(); p.add_argument("file"); p.add_argument("--spoken", action="store_true"); p.add_argument("--max-words", type=int, default=None); a = p.parse_args()
t = open(a.file, encoding="utf-8", errors="replace").read(); mx = a.max_words or (20 if a.spoken else 30)
sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n{2,}", t) if len(s.split()) > 0]; wl = [len(s.split()) for s in sents]
print(f"{len(t.split())} words, {len(sents)} sentences, average {sum(wl) / max(1, len(wl)):.1f} words per sentence")
long = [(n, s) for n, s in zip(wl, sents) if n > mx]
print(f"\nSentences over {mx} words: {len(long)}")
for n, s in long[:6]: print(f"  ({n}) {s[:110]}...")
if a.spoken:
    frag = [s for n, s in zip(wl, sents) if n <= 3]
    if len(frag) > 0.4 * len(sents) and len(sents) >= 5: print(f"\nWARN: {len(frag)}/{len(sents)} sentences are 1-3 words; reads like a list, not speech. Join them into natural sentences.")
filler = re.findall(r"\b(very|really|basically|actually|just|in order to|it is important to note|needless to say|at the end of the day)\b", t, re.I)
if filler: print(f"\nFiller words: {dict(collections.Counter(f.lower() for f in filler).most_common(6))}")
passive = re.findall(r"\b(?:is|are|was|were|been|being|be)\s+\w+ed\b(?:\s+by)?", t, re.I)
if passive: print(f"Possible passive voice: {len(passive)} (e.g. {passive[:3]})")
stop = set("the a an and or but of to in on for with is are was were be it that this as at by from not you your we our they their i he she his her have has had will would can could should do does did so if then than there".split())
cnt = collections.Counter(w for w in re.findall(r"[a-z']{4,}", t.lower()) if w not in stop)
rep = [(w, c) for w, c in cnt.most_common(5) if c >= 4]
if rep: print(f"Most repeated words: {rep} (vary them or cut)")
print("\nREADABILITY: " + ("review the flags above" if long or filler else "looks clean") + "  (a tool cannot judge meaning: re-read it once as the audience)")
