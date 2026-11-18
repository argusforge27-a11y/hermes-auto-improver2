#!/usr/bin/env python3
"""Install judgment-critic and import its lessons (safe to re-run).  install.py [--skills-dir ~/.hermes/skills]"""
import argparse, json, os, shutil, time
here = os.path.dirname(os.path.abspath(__file__))
p = argparse.ArgumentParser(); p.add_argument("--skills-dir", default=os.path.expanduser("~/.hermes/skills")); a = p.parse_args()
os.makedirs(a.skills_dir, exist_ok=True); dst = os.path.join(a.skills_dir, "judgment-critic")
if os.path.exists(dst): shutil.rmtree(dst)
shutil.copytree(here, dst, ignore=shutil.ignore_patterns("__pycache__", "install.py", "judgment_lessons.jsonl")); print(f"installed skill: judgment-critic -> {dst}")
home = os.environ.get("POWER_CORE_HOME", os.path.expanduser("~/.power-core")); os.makedirs(home, exist_ok=True); db = os.path.join(home, "lessons.jsonl"); items = []
if os.path.exists(db):
    for l in open(db, encoding="utf-8"):
        if l.strip():
            try: items.append(json.loads(l))
            except ValueError: pass
have = {i.get("rule", "").strip().lower() for i in items}; nid = max([i.get("id", 0) for i in items] + [0]); added = 0
for l in open(os.path.join(here, "judgment_lessons.jsonl"), encoding="utf-8"):
    e = json.loads(l)
    if e["rule"].strip().lower() in have: continue
    nid += 1; added += 1; items.append({"id": nid, "ts": int(time.time()), "tags": e["tags"], "symptom": e["symptom"], "cause": e["cause"], "rule": e["rule"], "hits": 0, "active": True})
with open(db, "w", encoding="utf-8") as f:
    for i in items: f.write(json.dumps(i, ensure_ascii=False) + "\n")
print(f"lessons: added {added}, library now {len(items)}")
