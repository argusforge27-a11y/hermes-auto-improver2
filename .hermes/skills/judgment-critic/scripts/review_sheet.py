#!/usr/bin/env python3
"""Evidence-required scorecard.
  review_sheet.py new "name" --rubric video|image|text|code|generic
  review_sheet.py score <id> <dimension> <1-5> "evidence with a locator"
  review_sheet.py defect <id> <1-3> "defect with locator"     review_sheet.py nodefects <id> "what you checked"
  review_sheet.py show <id>     review_sheet.py verdict <id>  (exit 0 PASS, 1 REVISE, 2 REJECT, 3 incomplete)"""
import signal; signal.signal(signal.SIGPIPE, signal.SIG_DFL)
import json, os, re, sys, time
HOME = os.environ.get("POWER_CORE_HOME", os.path.expanduser("~/.power-core")); D = os.path.join(HOME, "reviews"); os.makedirs(D, exist_ok=True)
RUB = {"video": ["content_accuracy", "story_flow", "picture_logic", "text_and_captions", "timing_sync", "audio", "polish"],
       "image": ["purpose_fit", "composition", "legibility", "consistency", "technical"],
       "text": ["accuracy", "clarity", "audience_fit", "structure", "originality_and_rights"],
       "code": ["correctness", "robustness", "simplicity", "readability", "safety"],
       "generic": ["meets_request", "correctness", "completeness", "quality", "risk"]}
VAGUE = re.compile(r"^(looks?|seems?|is|was)?\s*(good|fine|ok|okay|great|nice|correct|right|perfect|works?|done|clean)\b[ .!]*$", re.I)
LOC = re.compile(r"(\d|frame|second|\bat\b|\bline\b|top|bottom|left|right|center|centre|corner|caption|title|intro|outro|first|last|paragraph|function|section|page)", re.I)
P = lambda i: os.path.join(D, f"{i}.json")
def load(i):
    if not os.path.exists(P(i)): sys.exit(f"no such review: {i}")
    return json.load(open(P(i), encoding="utf-8"))
def save(r): json.dump(r, open(P(r["id"]), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
def show(r):
    print(f"REVIEW {r['id']}: {r['name']}  [{r['rubric']}]")
    for d in r["dims"]:
        s = r["scores"].get(d); print(f"  {d:24} " + (f"{s['score']}  {s['evidence']}" if s else "NOT SCORED"))
    for x in r["defects"]: print(f"  DEFECT sev{x['sev']}: {x['text']}")
    if r.get("nodefects"): print(f"  NO DEFECTS FOUND, checked: {r['nodefects']}")
a = sys.argv[1:]; c = a[0] if a else ""
if c == "new":
    rub = a[a.index("--rubric") + 1] if "--rubric" in a else "generic"
    if rub not in RUB: sys.exit(f"rubric must be one of {list(RUB)}")
    rid = time.strftime("%m%d-%H%M%S"); n = 0
    while os.path.exists(P(rid)): n += 1; rid = time.strftime("%m%d-%H%M%S") + f"-{n}"
    r = {"id": rid, "name": a[1], "rubric": rub, "dims": RUB[rub], "scores": {}, "defects": [], "nodefects": ""}; save(r); print(rid); show(r)
elif c == "score" and len(a) >= 5:
    r = load(a[1]); dim = a[2]
    if dim not in r["dims"]: sys.exit(f"unknown dimension; use one of {r['dims']}")
    try: sc = int(a[3]); assert 1 <= sc <= 5
    except Exception: sys.exit("score must be an integer 1-5")
    ev = " ".join(a[4:]).strip()
    if len(ev) < 12 or VAGUE.match(ev): sys.exit("REJECTED: evidence is too vague. State what you observed and where.")
    if sc >= 4 and not LOC.search(ev): sys.exit("REJECTED: a score of 4-5 needs a locator (time, frame, region, line, section) in the evidence.")
    r["scores"][dim] = {"score": sc, "evidence": ev}; save(r); print(f"scored {dim} = {sc}")
elif c == "defect" and len(a) >= 4:
    r = load(a[1]); sev = int(a[2]); assert sev in (1, 2, 3); r["defects"].append({"sev": sev, "text": " ".join(a[3:])}); save(r); print(f"defect logged ({len(r['defects'])})")
elif c == "nodefects" and len(a) >= 3:
    r = load(a[1]); t = " ".join(a[2:])
    if len(t) < 25: sys.exit("REJECTED: say exactly what you checked and how (at least a sentence).")
    r["nodefects"] = t; save(r); print("recorded")
elif c == "show": show(load(a[1]))
elif c == "verdict":
    r = load(a[1]); show(r); miss = [d for d in r["dims"] if d not in r["scores"]]
    if miss: print(f"\nINCOMPLETE: score {miss} first."); sys.exit(3)
    if len(r["defects"]) < 3 and not r["nodefects"]: print("\nINCOMPLETE: hostile pass not done. Log 3+ defects, or `nodefects` with what you checked."); sys.exit(3)
    sc = [v["score"] for v in r["scores"].values()]; avg = sum(sc) / len(sc); low = [d for d, v in r["scores"].items() if v["score"] <= 2]
    blockers = [x for x in r["defects"] if x["sev"] == 3]; serious = [x for x in r["defects"] if x["sev"] == 2]
    print(f"\naverage {avg:.2f}, lowest {min(sc)}, blockers {len(blockers)}, serious {len(serious)}")
    if blockers or low: print(f"VERDICT: REJECT  (blockers or dimensions <= 2: {low}). Fix, re-score the affected dimensions, run verdict again."); sys.exit(2)
    if avg < 4.0 or serious or min(sc) < 3: print("VERDICT: REVISE  (avg < 4.0, a serious defect, or a dimension below 3). Fix the listed defects and re-score."); sys.exit(1)
    print("VERDICT: PASS  (report honestly what you could not check, and any taste-level notes as optional)"); sys.exit(0)
else: sys.exit(__doc__)
