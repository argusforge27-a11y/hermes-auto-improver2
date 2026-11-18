#!/usr/bin/env python3
"""Hypothesis log.  hypo.py new "symptom" | try "hypothesis" "change" | result ok|fail "obs" | show | close "cause" "verified how" """
import json, os, sys, time
HOME = os.environ.get("POWER_CORE_HOME", os.path.expanduser("~/.power-core")); os.makedirs(HOME, exist_ok=True)
F = os.path.join(HOME, "debug.json")
def load(): return json.load(open(F)) if os.path.exists(F) else None
def save(d): json.dump(d, open(F, "w"), indent=1, ensure_ascii=False)
def show(d):
    print(f"SYMPTOM: {d['symptom']}")
    for i, t in enumerate(d["tries"], 1): print(f" {i}. [{t.get('result', '...')}] {t['hyp']} | change: {t['change']}" + (f" | saw: {t['obs']}" if t.get("obs") else ""))
    if d.get("closed"): print(f"CLOSED: cause={d['closed']['cause']} verified={d['closed']['how']}")
a = sys.argv[1:]; c = a[0] if a else ""
if c == "new" and len(a) >= 2: save({"symptom": a[1], "tries": [], "t": time.time()}); print("new debug session. Next: reproduce, shrink, then `try`.")
else:
    d = load()
    if not d: sys.exit("no active session: run `new \"symptom\"` first")
    if c == "try" and len(a) >= 3:
        if d["tries"] and "result" not in d["tries"][-1]: sys.exit("previous try has no result yet: run `result ok|fail \"what you observed\"` first")
        fails = 0
        for t in reversed(d["tries"]):
            if t.get("result") == "fail": fails += 1
            else: break
        if fails >= 2: print("STOP: two failed hypotheses in a row. Re-read the exact error and the instructions, shrink the repro, and choose a DIFFERENT line of attack before trying again.\n")
        d["tries"].append({"hyp": a[1], "change": a[2]}); save(d); print(f"try #{len(d['tries'])} logged. Make exactly ONE change, re-run the repro.")
    elif c == "result" and len(a) >= 2 and a[1] in ("ok", "fail"):
        if not d["tries"] or "result" in d["tries"][-1]: sys.exit("no open try")
        d["tries"][-1]["result"] = a[1]; d["tries"][-1]["obs"] = " ".join(a[2:]); save(d); print("logged." + (" If the symptom is gone, run `close`." if a[1] == "ok" else " Hypothesis rejected: that is information, use it."))
    elif c == "show": show(d)
    elif c == "close" and len(a) >= 3: d["closed"] = {"cause": a[1], "how": a[2]}; save(d); show(d); print("\nNow: log a lesson with power-core lessons.py, and check where else this cause could occur.")
    else: sys.exit(__doc__)
