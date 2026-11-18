#!/usr/bin/env python3
"""Improve a skill description based on eval results.

Takes eval results (from run_eval.py) and generates an improved description
by calling `claude -p` as a subprocess (same auth pattern as run_eval.py —
uses the session's Claude Code auth, no separate ANTHROPIC_API_KEY needed).
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

from scripts.utils import parse_skill_md


def improve_description(
    skill_name: str,
    skill_content: str,
    current_description: str,
    eval_results: dict,
    history: list,
    model: str | None = None,
    log_dir: Path | None = None,
    iteration: int | None = None,
) -> str:
    """Generate an improved description by calling claude -p."""
    # Build prompt for the improvement model
    prompt = textwrap.dedent(f"""
        You are an expert at writing skill descriptions for the Claude Code skill system.

        A "skill" is sort of like a prompt, but with progressive disclosure -- there's a title and description that Claude sees when deciding whether to use the skill, and then if it does use the skill, it reads the
        .md file which has lots more details and potentially links to other resources in the skill folder like helper files and scripts and additional documentation or examples.

        The description appears in Claude's "available_skills" list.
        When a user sends a query, Claude decides whether to invoke the skill based solely on the title and on this description. Your goal is to write a description that triggers for relevant queries, and doesn't trigger for irrelevant ones.

        Here's the current description:
        <current_description>
        "{current_description}"
        </current_description>

        Here are the eval results for the current description:
        <eval_results>
        {json.dumps(eval_results, indent=2)}
        </eval_results>

        <scores_summary>
        {len(eval_results.get('results', []))} queries evaluated
        {eval_results['summary']['passed']} passed, {eval_results['summary']['failed']} failed
        {eval_results['summary']['passed']}/{eval_results['summary']['total']} pass rate
    """)

    # Add history if any
    if history:
        prompt += "\nPrevious attempts (older first):\n"
        for h in history:
            iter_num = h.get("iteration", "?")
            passed = h.get("train_passed", 0)
            total = h.get("train_total", 0)
            desc = h.get("description", "")
            prompt += f"  Attempt {iter_num}: {passed}/{total} - {desc[:80]}"
            if h.get("note"):
                prompt += f" ({h['note']})"
            prompt += "\n"

    # Add individual query details for failures
    failed_queries = [r for r in eval_results.get("results", []) if not r["pass"]]
    if failed_queries:
        prompt += "\nFailures:\n"
        for r in failed_queries:
            status = "should trigger" if r["should_trigger"] else "should NOT trigger"
            prompt += f"  [FAIL] "{r['query']}" (triggered {r['triggers']}/{r['runs']} times) — expected: {status}\n"

    prompt += textwrap.dedent(f"""
        </scores_summary>

        Skill content (for context on what the skill does):
        <skill_content>
        {skill_content}
        </skill_content>

        Based on the failures, write a new and improved description that is more likely to trigger correctly. When I say "based on the failures", it's a bit of a tricky line to walk because we don't want to overfit to the specific cases you're seeing.
        So what I DON'T want you to do is produce an ever-expanding list of specific queries that this skill should or shouldn't trigger for. Instead, try to generalize from the failures to broader categories of user intent and situations where this skill would be useful or not useful. The reason for this is twofold:

        1. Avoid overfitting
        2.
        The list might get loooong and it's injected into ALL queries and there might be a lot of skills, so we don't want to blow too much space on any given description.

        Concretely, your description should not be more than about 100-200 words, even if that comes at the cost of accuracy.
        There is a hard limit of 1024 characters — descriptions over that will be truncated, so stay comfortably under it.

        Here are some tips that we've found to work well in writing these descriptions:
        - The skill should be phrased in the imperative -- "Use this skill for" rather than "this skill does"
        - The skill description should focus on the user's intent, what they are trying to achieve, vs. the implementation details of how the skill works.
        - The description competes with other skills for Claude's attention — make it distinctive and immediately recognizable.
        - If you're getting lots of failures after repeated attempts, change things up.
        Try different sentence structures or wordings.

        I'd encourage you to be creative and mix up the style in different iterations since you'll have multiple opportunities to try different approaches and we'll just grab the highest-scoring one at the end. 

        Please respond with only the new description text in <new_description> tags, nothing else.
        """)

    # Write prompt to temp file and run claude -p
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(prompt)
        prompt_file = f.name

    try:
        cmd = ["claude", "-p", f"@{prompt_file}"]
        if model:
            cmd.extend(["--model", model])

        # Remove CLAUDECODE env var to allow nesting claude -p inside a
        # Claude Code session. The guard is for interactive terminal conflicts;
        # programmatic subprocess usage is safe.
        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

        result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=120)

        if result.returncode != 0:
            print(f"claude -p failed: {result.stderr}", file=sys.stderr)
            sys.exit(1)

        output = result.stdout.strip()

        # Extract <new_description> from output
        import re
        match = re.search(r'<new_description>(.*?)</new_description>', output, re.DOTALL)
        if not match:
            print(f"Could not find <new_description> in output:\n{output}", file=sys.stderr)
            sys.exit(1)

        new_description = match.group(1).strip()

        # Log the improvement attempt
        if log_dir:
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / f"improve_iteration_{iteration}.log"
            with open(log_file, "w") as f:
                f.write(f"=== PROMPT ===\n{prompt}\n\n=== OUTPUT ===\n{output}\n\n=== NEW DESCRIPTION ===\n{new_description}")

        return new_description

    finally:
        try:
            os.unlink(prompt_file)
        except OSError:
            pass


def main():
    parser = argparse.ArgumentParser(description="Improve skill description from eval results")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--eval-results", required=True, help="Path to eval results JSON")
    parser.add_argument("--history", default=None, help="Path to history JSON")
    parser.add_argument("--model", required=True, help="Model for claude -p")
    parser.add_argument("--log-dir", default=None, help="Directory for logs")
    parser.add_argument("--iteration", type=int, default=None, help="Iteration number for logging")
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")
    args = parser.parse_args()

    skill_path = Path(args.skill_path)
    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    name, _, content = parse_skill_md(skill_path)
    eval_results = json.loads(Path(args.eval_results).read_text())
    history = []
    if args.history:
        history = json.loads(Path(args.history).read_text())

    current_description = eval_results["description"]

    if args.verbose:
        print(f"Current: {current_description}", file=sys.stderr)
        print(f"Score: {eval_results['summary']['passed']}/{eval_results['summary']['total']}", file=sys.stderr)

    new_description = improve_description(
        skill_name=name,
        skill_content=content,
        current_description=current_description,
        eval_results=eval_results,
        history=history,
        model=args.model,
        log_dir=Path(args.log_dir) if args.log_dir else None,
        iteration=args.iteration,
    )

    if args.verbose:
        print(f"New: {new_description}", file=sys.stderr)

    print(new_description)


if __name__ == "__main__":
    main()