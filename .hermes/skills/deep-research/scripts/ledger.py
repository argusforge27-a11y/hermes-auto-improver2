#!/usr/bin/env python3
"""Claim-to-source ledger.  ledger.py add --claim C --source S [--date D] [--kind primary|secondary] [--note N] | list | check | clear"""
import argparse, json, os, re, sys
HOME = os.environ.get("POWER_CORE_HOME", os.path.expanduser("~/.power-core")); os.makedirs(HOME, exist_ok=True)
F = os.path.join(HOME, "ledger.json")
def load(): return json.load(open(F)) if os.path.exists(F) else []
def save(x): json.dump(x, open(F, "w"), indent=1, ensure_ascii=False)
p = argparse.ArgumentParser(); s = p.add_subparsers(dest="c", required=True)
x = s.add_parser("add"); x.add_argument("--claim", required=True); x.add_argument("--source", required=True)
x.add_argument("--date", default=""); x.add_argument("--kind", default="secondary", choices=["primary", "secondary"]); x.add_argument("--note", default="")
x.add_argument("--contradicts", action="store_true", help="this source disagrees with the claim")
s.add_parser("list"); s.add_parser("check"); s.add_parser("clear")
a = p.parse_args(); L = load()
norm = lambda t: re.sub(r"\W+", " ", t.lower()).strip()
if a.c == "add":
    L.append({"claim": a.claim, "source": a.source, "date": a.date, "kind": a.kind, "note": a.note, "contradicts": a.contradicts}); save(L); print(f"added ({len(L)} entries)")
elif a.c == "list":
    for i, e in enumerate(L, 1): print(f"{i}. {e['claim']}\n     {'AGAINST ' if e['contradicts'] else ''}{e['kind']} | {e['source']} | {e['date'] or 'NO DATE'}")
elif a.c == "clear": save([]); print("cleared")
else:
    claims = {}
    for e in L: claims.setdefault(norm(e["claim"]), []).append(e)
    flags = 0
    for k, es in claims.items():
        sup = [e for e in es if not e["contradicts"]]; con = [e for e in es if e["contradicts"]]
        srcs = {norm(e["source"]) for e in sup}; prim = any(e["kind"] == "primary" for e in sup)
        why = []
        if not prim and len(srcs) < 2: why.append("needs a primary source or 2 independent sources")
        if any(not e["date"] for e in sup): why.append("source date missing")
        if con: why.append(f"{len(con)} source(s) disagree: present both sides")
        if why: flags += 1; print(f"FLAG: {es[0]['claim']}\n      -> " + "; ".join(why))
    print(f"\n{len(claims)} claims, {flags} flagged." + ("" if flags else " LEDGER OK")); sys.exit(1 if flags else 0)
