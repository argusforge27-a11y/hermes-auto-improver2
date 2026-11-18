#!/usr/bin/env python3
"""Generate HTML report for skill description optimization results."""

import html
import json
from pathlib import Path


def generate_html(data: dict, auto_refresh: bool = False, skill_name: str = "") -> str:
    """Generate HTML report from optimization results."""
    train_queries = []
    test_queries = []

    history = data.get('history', [])
    if history:
        for r in history[0].get('train_results', []):
            train_queries.append({"query": r["query"], "should_trigger": r.get("should_trigger", True)})
        for r in history[0].get('test_results', []):
            test_queries.append({"query": r["query"], "should_trigger": r.get("should_trigger", True)})

    refresh_tag = '    <meta http-equiv="refresh" content="5">\n' if auto_refresh else ""

    title_prefix = f"{skill_name}: " if skill_name else ""

    html_parts = [
        "<!DOCTYPE html>",
        "<html lang=\"en\">",
        "<head>",
        "  <meta charset=\"UTF-8\">",
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">",
        refresh_tag,
        f"  <title>{html.escape(title_prefix)}Skill Description Optimization</title>",
        "  <style>",
        "    body { font-family: system-ui, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }",
        "    .explainer { background: #f5f5f5; padding: 15px; border-radius: 8px; margin-bottom: 20px; }",
        "    .summary { background: #fff; border: 1px solid #ddd; padding: 15px; border-radius: 8px; margin-bottom: 20px; }",
        "    .summary .best { color: green; font-weight: bold; }",
        "    table { border-collapse: collapse; width: 100%; }",
        "    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
        "    th { background: #f5f5f5; }",
        "    .positive-col { background: #e8f5e9; }",
        "    .negative-col { background: #ffebee; }",
        "    .pass { color: green; }",
        "    .fail { color: red; }",
        "    .legend { margin: 15px 0; }",
        "    .legend-item { display: inline-block; margin-right: 15px; }",
        "    .legend-swatch { display: inline-block; width: 12px; height: 12px; border-radius: 2px; margin-right: 5px; vertical-align: middle; }",
        "    .swatch-positive { background: #4caf50; }",
        "    .swatch-negative { background: #f44336; }",
        "    .swatch-train { background: #2196f3; }",
        "    .swatch-test { background: #ff9800; }",
        "  </style>",
        "</head>",
        "<body>",
        f"    <h1>{html.escape(title_prefix)}Skill Description Optimization</h1>",
        "    <div class=\"explainer\">",
        "        <strong>Optimizing your skill's description.</strong> This page updates automatically as Claude tests different versions of your skill's description. Each row is an iteration — a new description attempt.",
        "The columns show test queries: green checkmarks mean the skill triggered correctly (or correctly didn't trigger), red crosses mean it got it wrong. The \"Train\" score shows performance on queries used to improve the description; the \"Test\" score shows performance on held-out queries the optimizer hasn't seen.",
        "When it's done, Claude will apply the best-performing description to your skill.",
        "    </div>",
    ]

    # Summary section
    best_test_score = data.get('best_test_score')
    best_train_score = data.get('best_train_score')
    html_parts.append(f"""
    <div class="summary">
        <p><strong>Original:</strong>
{html.escape(data.get('original_description', 'N/A'))}</p>
        <p class="best"><strong>Best:</strong> {html.escape(data.get('best_description', 'N/A'))}</p>
        <p><strong>Best Score:</strong> {data.get('best_score', 'N/A')} {'(test)' if best_test_score else '(train)'}</p>
        <p><strong>Iterations:</strong>
{data.get('iterations_run', 0)} | <strong>Train:</strong> {data.get('train_size', '?')} | <strong>Test:</strong> {data.get('test_size', '?')}</p>
    </div>
""")

    # Legend
    html_parts.append("""
    <div class="legend">
        <span style="font-weight:600">Query columns:</span>
<span class="legend-item"><span class="legend-swatch swatch-positive"></span> Should trigger</span>
        <span class="legend-item"><span class="legend-swatch swatch-negative"></span> Should NOT trigger</span>
        <span class="legend-item"><span class="legend-swatch swatch-train"></span> Train</span>
<span class="legend-item"><span class="legend-swatch swatch-test"></span> Test</span>
    </div>
""")

    # Table header
    html_parts.append("""
    <div class="table-container">
    <table>
        <thead>
            <tr>
                <th>Iter</th>
                <th>Train</th>
                <th>Test</th>
<th class="query-col">Description</th>
""")

    # Add column headers for train queries
    for qinfo in train_queries:
        polarity = "positive-col" if qinfo["should_trigger"] else "negative-col"
        html_parts.append(f'                <th class="{polarity}">{html.escape(qinfo["query"])}</th>\n')

    # Add column headers for test queries
    for qinfo in test_queries:
        polarity = "positive-col" if qinfo["should_trigger"] else "negative-col"
        html_parts.append(f'                <th class="{polarity}">{html.escape(qinfo["query"])}</th>\n')

    html_parts.append("            </tr>\n        </thead>\n        <tbody>")

    # Data rows
    for h in history:
        iteration = h.get('iteration', 0)
        desc = h.get('description', '')
        train_passed = h.get('train_passed', 0)
        train_total = h.get('train_total', 0)
        test_passed = h.get('test_passed', 0)
        test_total = h.get('test_total', 0)
        train_results = h.get('train_results', [])
        test_results = h.get('test_results', [])

        train_score = f"{train_passed}/{train_total}" if train_total else "—"
        test_score = f"{test_passed}/{test_total}" if test_total else "—"

        html_parts.append(f"            <tr>")
        html_parts.append(f"                <td>{iteration}</td>")
        html_parts.append(f"                <td>{train_score}</td>")
        html_parts.append(f"                <td>{test_score}</td>")
        html_parts.append(f"                <td>{html.escape(desc)}</td>")

        for r in train_results:
            status = "pass" if r["pass"] else "fail"
            icon = "✓" if r["pass"] else "✗"
            html_parts.append(f"                <td class=\"{status}\">{icon} {r['triggers']}/{r['runs']}</td>")

        for r in test_results:
            status = "pass" if r["pass"] else "fail"
            icon = "✓" if r["pass"] else "✗"
            html_parts.append(f"                <td class=\"{status}\">{icon} {r['triggers']}/{r['runs']}</td>")

        html_parts.append(f"            </tr>")

    html_parts.append("        </tbody>\n    </table>\n    </div>\n</body>\n</html>")
    return "".join(html_parts)