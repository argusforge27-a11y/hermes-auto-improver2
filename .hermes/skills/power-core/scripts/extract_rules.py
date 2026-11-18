#!/usr/bin/env python3
"""Print every hard-rule line of a document so none is skipped.  extract_rules.py <file> [more files]"""
import re, sys
PAT = re.compile(r"\b(must|never|always|do not|don't|dont|required|only|exactly|ask before|before you|"
                 r"is mandatory|forbidden|prints?|should not|shouldn't|at most|at least|no more than|default)\b", re.I)
HEAD = re.compile(r"^\s*#{1,6}\s*(.*(QA|pitfall|never|gotcha|warning|limit|common mistake|caution).*)$", re.I)
for p in sys.argv[1:] or sys.exit(__doc__):
    try: lines = open(p, encoding="utf-8", errors="replace").read().splitlines()
    except OSError as e: print(f"{p}: {e}"); continue
    print(f"=== {p} ({len(lines)} lines) ===")
    n = 0
    for i, l in enumerate(lines, 1):
        if HEAD.match(l): print(f"{i:5}  >>> SECTION TO READ TWICE: {l.strip()}"); continue
        if PAT.search(l) and l.strip():
            n += 1; print(f"{i:5}  {l.strip()[:220]}")
    print(f"--- {n} rule lines. Turn each into a checklist item or criterion. ---")
