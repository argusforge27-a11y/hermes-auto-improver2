#!/usr/bin/env python3
"""Project notes that survive context loss.  notes.py init "name" "goal" | set decision|files|next|risk|done "text" | show"""
import json, os, sys, time
HOME = os.environ.get("POWER_CORE_HOME", os.path.expanduser("~/.power-core")); os.makedirs(HOME, exist_ok=True)
F = os.path.join(HOME, "notes.json"); KEYS = ("decision", "files", "next", "risk", "done")
def load(): return json.load(open(F)) if os.path.exists(F) else None
a = sys.argv[1:]; c = a[0] if a else ""
if c == "init" and len(a) >= 3: json.dump({"name": a[1], "goal": a[2], "decision": [], "files": [], "next": [], "risk": [], "done": [], "t": time.ctime()}, open(F, "w"), indent=1); print("notes started")
else:
    d = load()
    if not d: sys.exit("no notes yet: notes.py init \"name\" \"goal\"")
    if c == "set" and len(a) >= 3 and a[1] in KEYS:
        if a[1] == "next": d["next"] = [" ".join(a[2:])]
        else: d[a[1]].append(" ".join(a[2:]))
        d["t"] = time.ctime(); json.dump(d, open(F, "w"), indent=1, ensure_ascii=False); print("saved")
    elif c == "show":
        print(f"PROJECT: {d['name']}   (updated {d['t']})\nGOAL: {d['goal']}")
        for k in KEYS:
            print(f"{k.upper()}:" + ("  (none)" if not d[k] else ""))
            for x in d[k]: print(f"  - {x}")
        print("\nResume: confirm listed files still exist, then do NEXT.")
    else: sys.exit(__doc__)
