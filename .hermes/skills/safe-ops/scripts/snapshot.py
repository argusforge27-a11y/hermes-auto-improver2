#!/usr/bin/env python3
"""Backup before risky edits.  snapshot.py save <path> [--note N] | list | restore <id>"""
import argparse, json, os, shutil, sys, time
HOME = os.environ.get("POWER_CORE_HOME", os.path.expanduser("~/.power-core")); D = os.path.join(HOME, "snapshots"); os.makedirs(D, exist_ok=True)
IDX = os.path.join(D, "index.json")
def load(): return json.load(open(IDX)) if os.path.exists(IDX) else []
p = argparse.ArgumentParser(); s = p.add_subparsers(dest="c", required=True)
x = s.add_parser("save"); x.add_argument("path"); x.add_argument("--note", default="")
s.add_parser("list"); x = s.add_parser("restore"); x.add_argument("id")
a = p.parse_args(); L = load()
if a.c == "save":
    src = os.path.abspath(a.path)
    if not os.path.exists(src): sys.exit(f"not found: {src}")
    sid = time.strftime("%Y%m%d-%H%M%S") + f"-{len(L) + 1}"; dst = os.path.join(D, sid)
    shutil.copytree(src, dst) if os.path.isdir(src) else shutil.copy2(src, dst)
    L.append({"id": sid, "src": src, "dir": os.path.isdir(src), "note": a.note}); json.dump(L, open(IDX, "w"), indent=1); print(f"saved snapshot {sid} of {src}")
elif a.c == "list":
    for e in L: print(f"{e['id']}  {e['src']}  {e['note']}")
    if not L: print("no snapshots")
else:
    e = next((e for e in L if e["id"] == a.id), None)
    if not e: sys.exit("unknown id (run `list`)")
    src = os.path.join(D, e["id"])
    if e["dir"]:
        if os.path.exists(e["src"]): shutil.rmtree(e["src"])
        shutil.copytree(src, e["src"])
    else: shutil.copy2(src, e["src"])
    print(f"restored {e['src']} from {e['id']}")
