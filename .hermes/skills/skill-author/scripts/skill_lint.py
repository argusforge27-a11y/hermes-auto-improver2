#!/usr/bin/env python3
"""Lint a skill folder.  skill_lint.py <skill-folder>"""
import os, re, sys
d = sys.argv[1] if len(sys.argv) > 1 else sys.exit(__doc__); bad = 0
def r(level, msg):
    global bad; bad += level == "FAIL"; print(f"{level:4} {msg}")
f = os.path.join(d, "SKILL.md")
if not os.path.exists(f): sys.exit("FAIL no SKILL.md")
t = open(f, encoding="utf-8").read(); lines = t.splitlines()
m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
if not m: r("FAIL", "missing YAML frontmatter")
else:
    fm = m.group(1); nm = re.search(r"^name:\s*(.+)$", fm, re.M); ds = re.search(r"^description:\s*(.+)$", fm, re.M)
    r("ok" if nm else "FAIL", "name present"); 
    if nm and not re.fullmatch(r"[a-z0-9-]+", nm.group(1).strip()): r("WARN", "name should be lowercase letters, digits and hyphens")
    if not ds: r("FAIL", "description missing")
    else:
        desc = ds.group(1).strip()
        n = len(desc.split())
        r("ok" if n >= 25 else "WARN", f"description is {n} words" + ("" if n >= 25 else " (add what it does AND when to trigger it)"))
        if len(desc) > 60:
            r("FAIL", f"description is {len(desc)} chars (must be ≤60; trigger-first, ends with period)")
        if not re.search(r"\b(use|when|whenever)\b", desc, re.I): r("WARN", "description does not say when to use the skill")
r("ok" if len(lines) <= 500 else "WARN", f"SKILL.md is {len(lines)} lines (aim <= 500; move detail to references/)")
refs = set(re.findall(r"`((?:SKILL/)?(?:scripts|references|assets)/[\w./-]+)`", t)) | set(re.findall(r"\b((?:scripts|references|assets)/[\w.-]+\.\w+)", t))
for x in sorted(refs):
    x2 = x.replace("SKILL/", "")
    if not os.path.exists(os.path.join(d, x2)): r("FAIL", f"referenced file missing: {x2}")
if refs: r("ok", f"{len(refs)} referenced file(s) checked")
steps = [l for l in lines if re.match(r"^\s*(\d+\.|#{2,3}\s*\d)", l)]
gates = re.findall(r"must (print|say|pass|exit)|PASS|exit(s)? (non-zero|1)|done when|check", t, re.I)
r("ok" if (not steps or gates) else "WARN", "steps have a verifiable gate" if (not steps or gates) else "numbered steps but no gate/check command; add 'done when' or a pass phrase")
vague = re.findall(r"\b(make it good|be careful|do your best|try to|as appropriate|etc\.)", t, re.I)
if vague: r("WARN", f"vague wording found: {sorted(set(v.lower() for v in vague))}; make it checkable")
if not re.search(r"pitfall|never|mistake|gotcha", t, re.I): r("WARN", "no pitfalls/never section")
if not os.path.isdir(os.path.join(d, "scripts")) and not os.path.isdir(os.path.join(d, "references")): r("WARN", "no scripts/ or references/ (fine for tiny skills)")
print("\nLINT FAILED" if bad else "\nLINT OK"); sys.exit(1 if bad else 0)
