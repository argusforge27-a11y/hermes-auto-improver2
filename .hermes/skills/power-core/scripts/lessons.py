#!/usr/bin/env python3
"""Searchable lesson memory. Stdlib only.
  lessons.py add --tags a,b --symptom S --cause C --rule R
  lessons.py search "kw kw"      lessons.py list      lessons.py review
  lessons.py retire <id>         lessons.py export
Storage: $POWER_CORE_HOME or ~/.power-core/lessons.jsonl (seeded from assets/seed_lessons.jsonl on first use)."""
import argparse, json, os, re, sys, time, shutil
HOME = os.environ.get("POWER_CORE_HOME", os.path.expanduser("~/.power-core"))
DB = os.path.join(HOME, "lessons.jsonl")
SEED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "seed_lessons.jsonl")

def ensure():
    os.makedirs(HOME, exist_ok=True)
    if not os.path.exists(DB):
        if os.path.exists(SEED): shutil.copy(SEED, DB)
        else: open(DB, "w").close()

def load():
    ensure(); out = []
    with open(DB, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try: out.append(json.loads(line))
                except ValueError: pass
    return out

def save(items):
    with open(DB, "w", encoding="utf-8") as f:
        for it in items: f.write(json.dumps(it, ensure_ascii=False) + "\n")

def words(s): return set(re.findall(r"[a-z0-9]{3,}", s.lower()))
def text(it): return " ".join([" ".join(it.get("tags", [])), it.get("symptom", ""), it.get("cause", ""), it.get("rule", "")])

def show(it, score=None):
    s = f"  (score {score})" if score is not None else ""
    print(f"[{it['id']}] tags: {', '.join(it.get('tags', []))}  hits: {it.get('hits', 0)}{s}")
    if it.get("symptom"): print(f"    symptom: {it['symptom']}")
    if it.get("cause"):   print(f"    cause:   {it['cause']}")
    print(f"    RULE:    {it['rule']}")

def cmd_add(a):
    items = load(); nid = max([i["id"] for i in items] + [0]) + 1
    it = {"id": nid, "ts": int(time.time()), "tags": [t.strip().lower() for t in a.tags.split(",") if t.strip()],
          "symptom": a.symptom, "cause": a.cause, "rule": a.rule, "hits": 0, "active": True}
    near = [i for i in items if i.get("active", True) and len(words(text(i)) & words(text(it))) >= 0.7 * max(1, len(words(text(it))))]
    items.append(it); save(items)
    print(f"saved lesson {nid}")
    if near: print("note: similar lessons exist, consider merging:", ", ".join(str(i["id"]) for i in near))

def cmd_search(a):
    q = words(" ".join(a.query)); items = load(); scored = []
    for it in items:
        if not it.get("active", True): continue
        tw = words(text(it)); tagw = set(t for t in it.get("tags", []))
        score = len(q & tw) + 2 * len(q & tagw)
        if score: scored.append((score, it))
    scored.sort(key=lambda x: (-x[0], -x[1].get("hits", 0)))
    if not scored: print("no matching lessons (try broader keywords, or `lessons.py list`)"); return
    for score, it in scored[: a.n]:
        it["hits"] = it.get("hits", 0) + 1; show(it, score)
    save(items)

def cmd_list(a):
    for it in load():
        if it.get("active", True): show(it)

def cmd_retire(a):
    items = load()
    for it in items:
        if it["id"] == a.id: it["active"] = False; print(f"retired {a.id}")
    save(items)

def cmd_review(a):
    items = [i for i in load() if i.get("active", True)]
    print(f"{len(items)} active lessons\n\nMost used:")
    for it in sorted(items, key=lambda i: -i.get("hits", 0))[:5]: show(it)
    print("\nPossible duplicates (merge with add + retire):")
    found = False
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            wa, wb = words(text(items[i])), words(text(items[j]))
            if wa and wb and len(wa & wb) / min(len(wa), len(wb)) >= 0.6:
                print(f"  {items[i]['id']} ~ {items[j]['id']}"); found = True
    if not found: print("  none")

def cmd_export(a):
    for it in load():
        if it.get("active", True): print(f"- ({', '.join(it.get('tags', []))}) {it['rule']}")

p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
x = sub.add_parser("add"); x.add_argument("--tags", default=""); x.add_argument("--symptom", default="")
x.add_argument("--cause", default=""); x.add_argument("--rule", required=True); x.set_defaults(f=cmd_add)
x = sub.add_parser("search"); x.add_argument("query", nargs="+"); x.add_argument("-n", type=int, default=8); x.set_defaults(f=cmd_search)
sub.add_parser("list").set_defaults(f=cmd_list); sub.add_parser("review").set_defaults(f=cmd_review)
sub.add_parser("export").set_defaults(f=cmd_export)
x = sub.add_parser("retire"); x.add_argument("id", type=int); x.set_defaults(f=cmd_retire)
a = p.parse_args(); a.f(a)
