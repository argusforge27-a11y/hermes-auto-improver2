#!/usr/bin/env python3
"""Compare agent verdicts with the user's.
  calibrate.py log "task" pass|fail pass|fail "what the human saw" [--dim name]   (agent verdict, then human verdict)
  calibrate.py report | list"""
import signal; signal.signal(signal.SIGPIPE, signal.SIG_DFL)
import json, os, sys, collections, time
HOME = os.environ.get("POWER_CORE_HOME", os.path.expanduser("~/.power-core")); os.makedirs(HOME, exist_ok=True); F = os.path.join(HOME, "calibration.jsonl")
def load(): return [json.loads(l) for l in open(F, encoding="utf-8") if l.strip()] if os.path.exists(F) else []
a = sys.argv[1:]; c = a[0] if a else ""
if c == "log" and len(a) >= 5 and a[2] in ("pass", "fail") and a[3] in ("pass", "fail"):
    dim = a[a.index("--dim") + 1] if "--dim" in a else ""; note = a[4] if a[4] != "--dim" else ""
    open(F, "a", encoding="utf-8").write(json.dumps({"t": time.strftime("%Y-%m-%d"), "task": a[1], "agent": a[2], "human": a[3], "note": note, "dim": dim}, ensure_ascii=False) + "\n"); print("logged")
elif c == "list":
    for e in load(): print(f"{e['t']}  {e['task']}: agent={e['agent']} human={e['human']} {e['dim']} {e['note']}")
elif c == "report":
    L = load()
    if not L: sys.exit("no data yet: log the user's verdicts with `log`")
    n = len(L); agree = sum(e["agent"] == e["human"] for e in L); fp = [e for e in L if e["agent"] == "pass" and e["human"] == "fail"]; fn = [e for e in L if e["agent"] == "fail" and e["human"] == "pass"]
    print(f"{n} judgments, agreement {100 * agree / n:.0f}%")
    print(f"false PASS (agent approved, user rejected): {len(fp)}  <- the costly error")
    print(f"false FAIL (agent rejected, user approved): {len(fn)}")
    dims = collections.Counter(e["dim"] for e in fp if e["dim"])
    if dims: print(f"dimensions most often missed: {dims.most_common(3)}")
    for e in fp[-5:]: print(f"  missed: {e['task']}: {e['note']}")
    if n >= 5 and len(fp) / n >= 0.2: print("\nACTION: too lenient. Require 2 locators for any 4-5 score, add the missed defect types to the rubric, add lessons, look at more frames.")
    elif n >= 5 and len(fn) / n >= 0.2: print("\nACTION: too strict. Mark taste-level items as optional and stop blocking on them.")
    elif n >= 5: print("\nCalibration looks healthy. Keep logging.")
    else: print("\n(need at least 5 judgments for advice)")
else: sys.exit(__doc__)
