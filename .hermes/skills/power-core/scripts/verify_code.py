#!/usr/bin/env python3
"""Fast static checks. Passing is necessary, NOT sufficient: also run the code.  verify_code.py <file>..."""
import json, os, re, shutil, subprocess, sys
bad = 0
def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True); return r.returncode, (r.stdout + r.stderr).strip()
for p in sys.argv[1:] or sys.exit(__doc__):
    ext = os.path.splitext(p)[1].lower(); res = []
    if not os.path.exists(p): print(f"FAIL {p}: not found"); bad += 1; continue
    if ext == ".py":
        rc, out = run([sys.executable, "-m", "py_compile", p]); res.append(("syntax", rc, out))
        rc, out = run([sys.executable, "-m", "pyflakes", p])
        if "No module named pyflakes" not in out: res.append(("pyflakes (undefined names, unused)", rc, out))
    elif ext in (".js", ".mjs", ".cjs"):
        if shutil.which("node"): rc, out = run(["node", "--check", p]); res.append(("node --check", rc, out))
        else: print(f"skip {p}: node not installed")
    elif ext in (".sh", ".bash"):
        rc, out = run(["bash", "-n", p]); res.append(("bash -n", rc, out))
    elif ext == ".json":
        try: json.load(open(p, encoding="utf-8")); res.append(("json", 0, ""))
        except Exception as e: res.append(("json", 1, str(e)))
    else: print(f"skip {p}: no checker for '{ext}'")
    text = open(p, encoding="utf-8", errors="replace").read()
    marks = [f"line {i}: {l.strip()[:80]}" for i, l in enumerate(text.splitlines(), 1) if re.search(r"\b(TODO|FIXME|XXX|PLACEHOLDER|lorem ipsum)\b", l)]
    if marks: res.append(("leftover markers", 1, "\n".join(marks[:10])))
    for name, rc, out in res:
        if rc: bad += 1; print(f"FAIL {p} [{name}]\n{out}")
        else: print(f"ok   {p} [{name}]")
print("\nVERIFY OK (now run it on real input)" if not bad else f"\nVERIFY FAILED: {bad} problem(s)"); sys.exit(1 if bad else 0)
