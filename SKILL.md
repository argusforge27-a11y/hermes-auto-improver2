---
name: hermes-auto-improver
description: Auto-improves Hermes skills daily via GitHub Actions evals.
version: 1.0.0
author: Hermes Auto-Improver
license: MIT
metadata:
  hermes:
    tags: [automation, self-improvement, eval-driven, github-actions]
    related_skills: [skill-creator, power-core]
---

# Hermes Auto-Improver

## When to Use

This skill runs automatically via GitHub Actions on a daily schedule (03:00 UTC).

It should trigger when:
- You want Hermes skills to continuously improve without manual intervention
- You want health metrics (trigger accuracy, latency, hallucination rate, tool success) tracked over time
- You want degraded skills automatically fixed or flagged for review
- You want learned patterns synced to Hermes memory across sessions

**Do not invoke this skill manually** — it runs on the cloud scheduler. Use `scripts/run_health_check.py` locally for one-off checks.

A skill that runs on a cloud scheduler (GitHub Actions) to continuously improve all Hermes skills without user intervention.

## What It Does

- **Daily health checks**: Runs evals on every installed skill, measures trigger accuracy, latency, hallucination rate, tool-use success
- **Automatic improvement**: When a skill degrades, drafts fixes using skill-creator's improve_description.py + comparator/analyzer agents
- **Smart merge**: Auto-merges improvements that pass all evals; opens PR for uncertain changes
- **Memory sync**: Pushes learned patterns and lessons to local Hermes memory

## Architecture

```
GitHub Actions (daily cron)
    │
    ▼
scripts/run_health_check.py ──► collects metrics per skill
    │
    ├── all skills healthy ──► logs success, updates dashboard
    │
    └── degraded skills found ──► scripts/improve_skill.py
                                        │
                                        ▼
                                  proposes fixes
                                        │
                                        ▼
                                  runs evals on fixes
                                        │
                                        ├── passes ──► auto-commit to skill
                                        │
                                        └── uncertain ──► open PR for review
```

## Core Scripts

| Script | Purpose |
|--------|---------|
| `run_health_check.py` | Discovers all skills, runs their evals, computes metrics |
| `improve_skill.py` | Uses skill-creator agents to propose and validate fixes |
| `sync_memory.py` | Writes lessons to ~/.hermes/memory/ and skill references/ |
| `check_degraded.py` | Reads metrics JSON, outputs `degraded=N` and `skills=...` to `$GITHUB_OUTPUT` |
| `get_degraded_skills.py` | Reads metrics JSON, prints only degraded skill names (for for-loop) |
| `github_actions.yml` | Daily cron workflow definition |

## Metrics Tracked (per skill)

- **Trigger accuracy**: % of relevant prompts that correctly invoke the skill (target: ≥90%)
- **Latency**: p50/p95 response time (target: p95 < 30s)
- **Hallucination rate**: % of claims unverified by tool output (target: <5%)
- **Tool-use success**: % of tool calls that complete without error (target: ≥95%)

## Improvement Loop

For each degraded skill:
1. **Analyze**: Run comparator/analyzer on current vs. ideal outputs
2. **Draft**: Generate improved SKILL.md + reference files
3. **Validate**: Run quick_validate.py + full eval suite
4. **Decide**: If all metrics improve → auto-merge; else → open PR
5. **Record**: Write lesson to memory/references/

## Deployment

1. Push this skill's repo to GitHub
2. Enable GitHub Actions (Settings → Actions → Allow all actions)
3. Add `HERMES_TOKEN` secret (for memory sync back to local)
4. Workflow runs daily at 03:00 UTC

## Cloud Deployment Checklist

For any skill to run in GitHub Actions (or any cloud runner):

1. **No `hermes_tools` imports** — replace with subprocess calls to `hermes` CLI if needed, or pure file I/O.
2. **No `hermes-agent` pip install** — it doesn't exist on PyPI.
3. **Paths via env vars** — `HERMES_SKILLS_DIR`, `HERMES_METRICS_FILE`, `HERMES_MEMORY_FILE`, `HERMES_LESSONS_FILE`.
4. **Frontmatter parsing without PyYAML** — use regex/string splitting (see `run_health_check.py::parse_frontmatter`).
5. **Skill discovery checks repo root** — skills may live at workspace root, not in category folders.
6. **Subprocess timeouts ≥180s** — especially for eval scripts that iterate many skills.
7. **Zero or minimal deps** — prefer stdlib only; if PyYAML is used, add `pip install pyyaml` step.
8. **Workflow permissions** — `contents: write` and `pull-requests: write` for auto-merge/PR creation.
9. **Test locally first** — run with `HERMES_SKILLS_DIR=$(pwd) python scripts/run_health_check.py` to simulate CI environment.
10. **Health check exits 0 always** — let the workflow's check step read metrics and control flow via `GITHUB_OUTPUT`.
11. **Workflow runs from repo root** — no `cd` into subdirectory; scripts and SKILL.md at workspace root.
12. **`improve_skill.py` writes to actual skill dir** — validation happens in temp dir, but passing changes are written to the real SKILL.md for PR creation.

## GitHub Actions Workflow Notes

- **Do NOT install `hermes-agent` via pip** — it does not exist on PyPI
- **No `hermes_tools` imports** — this module only exists inside Hermes runtime. Scripts must use stdlib + PyYAML only.
- **No PyYAML needed** — frontmatter can be parsed with regex (see `run_health_check.py`).
- Use environment variables for paths (`HERMES_SKILLS_DIR`, `HERMES_METRICS_FILE`, `HERMES_MEMORY_FILE`, `HERMES_LESSONS_FILE`) — never hardcode `~/.hermes` paths.
- Workflow uses `actions/checkout@v4` and runs from the checked-out repo.
- **Health check discovers skills in the workspace** (`github.workspace`), not `~/.hermes/skills`.
- **Skill discovery must check repo root** for `SKILL.md` (skills may sit at repo root, not in category subfolder).
- Install only `pyyaml` if needed; prefer zero-dependency scripts for fastest cold start.
- Set subprocess timeouts ≥180s for eval runs (47+ skills can exceed 60s default).
- **Health check always exits 0** — the `Check for Degraded Skills` step reads metrics JSON and controls downstream steps via `GITHUB_OUTPUT`. This avoids the workflow failing before the check step runs.
- **Workflow runs from repo root** — no `cd hermes-auto-improver`; scripts and SKILL.md are at workspace root.
- **`improve_skill.py` writes changes directly** to the skill's SKILL.md after validation, so the PR has a real diff to commit.

## References

- `references/health_check_spec.md` — Detailed health check protocol
- `references/improvement_protocol.md` — How fixes are proposed and validated
- `references/metrics_schema.md` — JSON schema for metrics output
- `references/github_actions_setup.md` — Deployment instructions

---

*This skill improves itself too — its own evals run daily.*

## Pitfalls

- **Description too long**: skill_manage rejects descriptions >60 chars. Keep it trigger-first, one sentence, ends with period.
- **Missing referenced files**: Lint fails if SKILL.md references files that don't exist. Create all references/ files before linting.
- **GitHub Actions permissions**: Workflow needs `contents: write` and `pull-requests: write` permissions to auto-merge and create PRs.
- **HERMES_TOKEN secret**: Required for memory sync back to local Hermes. Without it, lessons only stay in GitHub repo.
- **Skill discovery**: Health check only finds skills under ~/.hermes/skills/**/SKILL.md. Skills installed elsewhere won't be checked.
- **Eval script dependency**: Skills without scripts/run_eval.py fall back to quick_validate only, giving limited metrics.
- **Auto-merge safety**: Only merges changes to SKILL.md and references/. Script/logic changes always open PR for review.
- **False positives**: Trigger accuracy measurement uses synthetic prompts; real-world accuracy may differ. Verify manually periodically.
- **Health check timeout**: Checking many skills (47+) can exceed default 60s timeout. Set `timeout=180` in run_eval.py subprocess calls or increase GitHub Actions job timeout.
- **Repo must exist before pushing**: `git push` to a non-existent repo silently succeeds (exit 0) but the remote returns 404. Always verify the repo exists on GitHub via `curl -sI https://github.com/<user>/<repo>` before pushing. If it doesn't exist, create it on GitHub first (empty repo, no initial commit), then push.
- **learned_lessons.jsonl grows unbounded**: The sync_memory.py appends lessons without size limit. In CI this file can reach 50MB+ and trigger GitHub's large-file warning. Add `references/learned_lessons.jsonl` to `.gitignore` or truncate it before each push.
- **Workflow runs on every push before Actions enabled**: Pushing to a repo that doesn't yet have Actions enabled triggers a failed run that shows 0 jobs. Enable Actions (Settings → Actions → Allow all actions) BEFORE the first push, or the run will fail with no useful logs.
- **Manual trigger required for first run**: Even with `workflow_dispatch:` configured, the user must click "Run workflow" in the Actions tab to start the first run. Schedule runs only begin after the first successful manual run.
- **GitHub Actions pip install hermes-agent fails**: The `hermes-agent` package does not exist on PyPI. Workflow must only install `pyyaml`. Scripts must run standalone without Hermes runtime — use environment variables for paths, not hardcoded `~/.hermes` paths.
- **Script imports from hermes_tools break in CI**: The `hermes_tools` module is only available inside Hermes runtime. Cloud runners (GitHub Actions) have no Hermes installation — all scripts must be pure Python with stdlib deps.
- **Skill discovery misses root-level skills**: If the skill repo has `SKILL.md` at the root (not in a category subfolder), discovery must check the workspace root explicitly.
- **Skill name mismatch**: If the repo directory name differs from the skill name (e.g., repo `hermes-auto-improver1` vs skill `hermes-auto-improver`), `improve_skill.py::find_skill_dir` must match by prefix (`startswith`). `run_eval.py` reads the skill name from SKILL.md frontmatter via regex, not the directory name.
- **PyYAML is optional overhead**: Frontmatter parsing can be done with simple regex/string splitting. Removing PyYAML eliminates a pip install step and speeds up CI.
- **Test locally before push**: Run `HERMES_SKILLS_DIR=$(pwd) python scripts/run_health_check.py` to simulate the CI environment. Verify health check finds the skill, metrics are written to `HERMES_METRICS_FILE`, and `improve_skill.py --skills-root $(pwd)` writes changes to the real SKILL.md.
- **Health check exits 0 always; check step controls flow**: The health check script must always exit 0. The "Check for Degraded Skills" step reads the metrics JSON and outputs `degraded=N` and `skills=...` to `GITHUB_OUTPUT`. Downstream steps (improve, PR creation) gate on `if: steps.check.outputs.degraded != '0'`. This prevents the workflow from failing before the check step runs and lets the check step decide control flow.
- **Validation in temp dir, write to real dir**: `improve_skill.py` validates fixes in a temporary directory (copies all skill files), but on success writes the improved SKILL.md directly to the actual skill directory. This ensures the PR/commit shows a real diff against the checked-out code.
- **Workflow runs from repo root**: No `cd` into subdirectory. Scripts, SKILL.md, and workflow all operate from `github.workspace`. This matches the checkout layout and avoids path confusion.
- **Debug steps are critical**: Always include "Debug - Verify workspace" (ls -la, head SKILL.md), "Debug - Show metrics" (cat metrics JSON), and "Debug - Show git diff" steps in CI workflows. They expose the exact state when things fail and are the first place to look when a run fails.
- **continue-on-error for health check**: The "Run Health Check" step uses `continue-on-error: true` so the workflow proceeds to the check step even if the health check script has issues. The check step's `GITHUB_OUTPUT` parsing is the single source of truth for downstream gating.
- **NEVER use inline Python in YAML run steps**: `python -c "..."` with embedded quotes and f-strings breaks YAML parsing in GitHub Actions — the `\"` escaping inside a `run: |` block creates invalid YAML. Instead, extract all Python logic into standalone scripts (`scripts/check_degraded.py`, `scripts/get_degraded_skills.py`) and call them from the workflow. This is the #1 cause of silent workflow failures — the run fails with a YAML parse error before any step executes, and the error is buried in the Actions log.
- **Two separate scripts for degraded skills**: `scripts/check_degraded.py` outputs `degraded=N` and `skills=...` to stdout (piped to `$GITHUB_OUTPUT`); `scripts/get_degraded_skills.py` reads the metrics JSON and prints only the skill names (used in the for-loop in the Trigger Improvements step). Keeping them separate avoids the quoting hell of doing both in one inline script.
- **Repo name ≠ skill name**: When the repo directory name differs from the skill name in SKILL.md frontmatter (e.g., repo `hermes-auto-improver2` vs skill `hermes-auto-improver`), `improve_skill.py::find_skill_dir` matches by `startswith` prefix, and `run_eval.py` reads the name from SKILL.md frontmatter via regex. Never hardcode the skill name in scripts — always derive it from the frontmatter or directory name.
- **learned_lessons.jsonl must be gitignored**: The file grows unbounded and triggers GitHub's 50MB large-file warning. Add `references/learned_lessons.jsonl` to `.gitignore` or truncate it (`> file`) before each push. The file is writable at runtime but should never be committed.


