#!/usr/bin/env python3
"""Profile a CSV with the standard library.  profile_csv.py <file> [--delimiter ,] [--max-cols 60]"""
import argparse, csv, statistics as S, sys
p = argparse.ArgumentParser(); p.add_argument("file"); p.add_argument("--delimiter", default=","); p.add_argument("--max-cols", type=int, default=60); a = p.parse_args()
with open(a.file, newline="", encoding="utf-8-sig", errors="replace") as f: rows = list(csv.reader(f, delimiter=a.delimiter))
if not rows: sys.exit("empty file")
hdr, data = rows[0], rows[1:]
print(f"{len(data)} rows x {len(hdr)} columns")
dups = len(data) - len({tuple(r) for r in data}); print(f"duplicate rows: {dups}")
ragged = sum(1 for r in data if len(r) != len(hdr)); 
if ragged: print(f"WARNING: {ragged} rows have a different number of fields than the header (check delimiter/quotes)")
def num(x):
    try: return float(x.replace(",", "").replace("$", "").replace("%", "").strip())
    except ValueError: return None
for i, name in enumerate(hdr[: a.max_cols]):
    col = [r[i].strip() for r in data if i < len(r)]; miss = sum(1 for x in col if x == "" or x.lower() in ("na", "n/a", "null", "none", "nan"))
    vals = [x for x in col if x != ""]; nums = [num(x) for x in vals]; isnum = vals and sum(n is not None for n in nums) >= 0.9 * len(vals)
    line = f"- {name!r}: {'numeric' if isnum else 'text'}, missing {miss} ({100 * miss / max(1, len(col)):.0f}%), distinct {len(set(vals))}"
    if isnum:
        ns = sorted(n for n in nums if n is not None)
        if ns:
            line += f", min {ns[0]:g}, max {ns[-1]:g}, mean {S.mean(ns):.4g}, median {S.median(ns):.4g}"
            if len(ns) >= 8:
                q = S.quantiles(ns, n=4); iqr = q[2] - q[0]; o = [x for x in ns if x < q[0] - 1.5 * iqr or x > q[2] + 1.5 * iqr]
                if o: line += f"  | outliers (IQR): {len(o)}, e.g. {o[:3]}"
    else:
        low = {}
        for x in vals: low.setdefault(x.lower(), set()).add(x)
        mixed = [v for v in low.values() if len(v) > 1]
        if mixed: line += f"  | inconsistent spelling/case: {[sorted(v) for v in mixed[:2]]}"
    print(line)
if len(hdr) > a.max_cols: print(f"... {len(hdr) - a.max_cols} more columns not shown")
