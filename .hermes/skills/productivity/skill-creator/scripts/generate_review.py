#!/usr/bin/env python3
"""Generate HTML review page from eval comparison results.

Reads a benchmark.json (from aggregate_benchmark.py) and generates
a side-by-side comparison viewer.
"""

import argparse
import json
import sys
from pathlib import Path


def generate_review_html(benchmark: dict) -> str:
    """Generate HTML review page from benchmark data."""
    metadata = benchmark.get("metadata", {})
    runs = benchmark.get("runs", [])
    run_summary = benchmark.get("run_summary", {})

    from collections import defaultdict
    runs_by_eval = defaultdict(list)
    for run in runs:
        runs_by_eval[run["eval_id"]].append(run)

    configs = list(set(r["configuration"] for r in runs))
    configs.sort()

    html = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "  <meta charset=\"UTF-8\">",
        "  <title>Skill Benchmark Review</title>",
        "  <style>",
        "    body { font-family: system-ui, sans-serif; max-width: 1400px; margin: 0 auto; padding: 20px; }",
        "    .header { margin-bottom: 30px; }",
        "    .eval-section { margin-bottom: 40px; border: 1px solid #ddd; border-radius: 8px; overflow: hidden; }",
        "    .eval-header { background: #f5f5f5; padding: 15px; border-bottom: 1px solid #ddd; }",
        "    .config-row { display: flex; }",
        "    .config-col { flex: 1; border-right: 1px solid #ddd; }",
        "    .config-col:last-child { border-right: none; }",
        "    .config-header { background: #e8e8e8; padding: 10px; font-weight: bold; text-align: center; }",
        "    .run { padding: 15px; }",
        "    .expectation { margin: 10px 0; padding: 10px; border-radius: 4px; }",
        "    .pass { background: #e8f5e9; border-left: 4px solid #4caf50; }",
        "    .fail { background: #ffebee; border-left: 4px solid #f44336; }",
        "    .metric { display: inline-block; margin-right: 20px; }",
        "    .notes { background: #fff3e0; padding: 15px; margin: 20px; border-radius: 4px; }",
        "  </style>",
        "</head>",
        "<body>",
        f"  <div class=\"header\">",
        f"    <h1>Skill Benchmark: {metadata.get('skill_name', 'Unknown')}</h1>",
        f"    <p>Model: {metadata.get('executor_model', 'Unknown')} | Date: {metadata.get('timestamp', 'Unknown')}</p>",
        f"  </div>",
    ]

    html.append("  <div class=\"header\">")
    html.append("    <h2>Summary</h2>")
    html.append("    <table style=\"width:100%; border-collapse:collapse;\">")
    html.append("      <tr><th>Config</th><th>Pass Rate</th><th>Avg Time</th><th>Avg Tokens</th></tr>")
    for config in configs:
        summary = run_summary.get(config, {})
        pr = summary.get("pass_rate", {}).get("mean", 0)
        time_mean = summary.get("time_seconds", {}).get("mean", 0)
        tokens_mean = summary.get("tokens", {}).get("mean", 0)
        html.append(f"      <tr><td>{config}</td><td>{pr*100:.1f}%</td><td>{time_mean:.1f}s</td><td>{tokens_mean:.0f}</td></tr>")
    if "delta" in run_summary:
        delta = run_summary["delta"]
        html.append(f"      <tr><td><strong>Delta</strong></td><td><strong>{delta.get('pass_rate', '—')}</strong></td><td>{delta.get('time_seconds', '—')}s</td><td>{delta.get('tokens', '—')}</td></tr>")
    html.append("    </table>")
    html.append("  </div>")

    for eval_id in sorted(runs_by_eval.keys()):
        eval_runs = runs_by_eval[eval_id]
        html.append(f"  <div class=\"eval-section\">")
        html.append(f"    <div class=\"eval-header\">Eval {eval_id}</div>")
        html.append(f"    <div class=\"config-row\">")
        for config in configs:
            config_runs = [r for r in eval_runs if r["configuration"] == config]
            html.append(f"      <div class=\"config-col\">")
            html.append(f"        <div class=\"config-header\">{config}</div>")
            for run in config_runs:
                html.append(f"        <div class=\"run\">")
                html.append(f"          <div class=\"metric\">Run {run['run_number']}</div>")
                html.append(f"          <div class=\"metric\">Pass Rate: {run['result']['pass_rate']*100:.0f}%</div>")
                html.append(f"          <div class=\"metric\">Time: {run['result']['time_seconds']:.1f}s</div>")
                html.append(f"          <div class=\"metric\">Tokens: {run['result']['tokens']}</div>")
                for exp in run.get("expectations", []):
                    passed = exp.get("passed", False)
                    cls = "pass" if passed else "fail"
                    text = exp.get("text", "")
                    evidence = exp.get("evidence", "")
                    html.append(f"          <div class=\"expectation {cls}\">")
                    html.append(f"            <strong>{'PASS' if passed else 'FAIL'}</strong>: {text}")
                    if evidence:
                        html.append(f"            <div style=\"margin-top:5px; font-size:0.9em; color:#666;\">Evidence: {evidence}</div>")
                    html.append(f"          </div>")
                if run.get("notes"):
                    html.append(f"          <div class=\"notes\">")
                    html.append(f"            <strong>Notes:</strong>")
                    for note in run["notes"]:
                        html.append(f"            <div>{note}</div>")
                    html.append(f"          </div>")
                html.append(f"        </div>")
            html.append(f"      </div>")
        html.append(f"    </div>")
        html.append(f"  </div>")

    if benchmark.get("notes"):
        html.append("  <div class=\"header\">")
        html.append("    <h2>Analyzer Notes</h2>")
        for note in benchmark["notes"]:
            html.append(f"    <div class=\"notes\">{note}</div>")
        html.append("  </div>")

    html.append("</body>")
    html.append("</html>")
    return "\n".join(html)


def main():
    parser = argparse.ArgumentParser(description="Generate HTML review from benchmark.json")
    parser.add_argument("benchmark", type=Path, help="Path to benchmark.json")
    parser.add_argument("--output", "-o", type=Path, help="Output HTML file (default: stdout)")
    args = parser.parse_args()

    with open(args.benchmark) as f:
        benchmark = json.load(f)

    html = generate_review_html(benchmark)

    if args.output:
        args.output.write_text(html)
        print(f"Generated: {args.output}", file=sys.stderr)
    else:
        print(html)


if __name__ == "__main__":
    main()