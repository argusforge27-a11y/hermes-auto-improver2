#!/usr/bin/env python3
"""Task card with evidence gate. Stdlib only.
  taskcard.py new "goal" "criterion 1" "criterion 2" ...   -> prints card id
  taskcard.py show <id>        taskcard.py prove <id> <n> "evidence"
  taskcard.py add <id> "extra criterion"      taskcard.py gate <id>   (exit 1 if unproven)
  taskcard.py list"""
import json, os, sys, time
HOME = os.environ.get("POWER_CORE_HOME", os.path.expanduser("~/.power-core")); D = os.path.join(HOME, "cards")
os.makedirs(D, exist_ok=True)
def path(i): return os.path.join(D, f"{i}.json")
def load(i):
    if not os.path.exists(path(i)): sys.exit(f"no such card: {i}")
    return json.load(open(path(i), encoding="utf-8"))
def save(c): json.dump(c, open(path(c["id"]), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
def show(c):
    print(f"CARD {c['id']}: {c['goal']}")
    for n, k in enumerate(c["criteria"], 1):
        mark = "x" if k.get("evidence") else " "
        print(f" [{mark}] {n}. {k['text']}" + (f"\n        evidence: {k['evidence']}" if k.get("evidence") else ""))
def main():
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    cmd = a[0]
    if cmd == "new":
        if len(a) < 3: sys.exit("need a goal and at least one criterion")
        cid = time.strftime("%m%d-%H%M%S"); c = {"id": cid, "goal": a[1], "criteria": [{"text": t, "evidence": ""} for t in a[2:]]}
        save(c); print(cid); show(c)
    elif cmd == "show": show(load(a[1]))
    elif cmd == "list":
        for f in sorted(os.listdir(D)):
            c = load(f[:-5]); done = sum(1 for k in c["criteria"] if k["evidence"]); print(f"{c['id']}  {done}/{len(c['criteria'])}  {c['goal']}")
    elif cmd == "add": c = load(a[1]); c["criteria"].append({"text": a[2], "evidence": ""}); save(c); show(c)
    elif cmd == "prove":
        c = load(a[1]); n = int(a[2]); ev = " ".join(a[3:]).strip()
        if len(ev) < 8: sys.exit("evidence too thin: say what you ran/opened and what you saw")
        if not 1 <= n <= len(c["criteria"]): sys.exit("bad criterion number")
        c["criteria"][n - 1]["evidence"] = ev; save(c); show(c)
    elif cmd == "gate":
        c = load(a[1]); show(c); open_ = [n for n, k in enumerate(c["criteria"], 1) if not k["evidence"]]
        if open_: print(f"\nGATE FAILED: no evidence for criteria {open_}. Do not report done."); sys.exit(1)
        print("\nGATE PASSED. Now do the hostile review (references/verification.md), then report honestly.")
    else: sys.exit(__doc__)
main()
