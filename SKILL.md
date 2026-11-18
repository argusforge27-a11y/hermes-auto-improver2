---
name: hermes-auto-improver
description: Auto-improves Hermes skills daily via GitHub Actions evals.
version: 1.1.0
author: Hermes Auto-Improver
license: MIT
metadata:
  hermes:
    tags: [automation, self-improvement, eval-driven, github-actions, skill-evolution]
    related_skills: [skill-creator, power-core]
---

# Hermes Auto-Improver

## When to Use

This skill runs automatically via GitHub Actions on a daily schedule (03:00 UTC).

It triggers when:
- You want Hermes skills to continuously improve without manual intervention
- You want health metrics (trigger accuracy, latency, hallucination rate, tool success) tracked over time
- You want degraded skills automatically fixed or flagged for review
- You want learned patterns synced to Hermes memory across sessions
- You want skills to evolve by discovering and adding missing capabilities

**Do not invoke this skill manually** — it runs on the cloud scheduler. Use `scripts/run_health_check.py` locally for one-off checks.

A skill that runs on a cloud scheduler (GitHub Actions) to continuously improve all Hermes skills without user intervention, including discovering and implementing new capabilities.

## What It Does

- **Daily health checks**: Runs evals on every installed skill, measures trigger accuracy, latency, hallucination rate, tool-use success
- **Automatic improvement**: When a skill degrades, runs evals → parses failures → analyzes root causes → applies targeted code fixes → re-validates → commits if metrics improve
- **A/B experimentation**: Creates variant_a/b copies to test hypothesis modifications before applying to real skill
- **New function generation**: Detects missing capabilities from failures and generates complete function implementations
- **Smart merge**: Auto-commits improvements that pass all evals; opens PR for uncertain changes
- **Memory sync**: Pushes learned patterns and lessons to local Hermes memory

## Architecture

```
GitHub Actions (daily cron at 03:00 UTC)
    │
    ▼
scripts/run_health_check.py ──► discovers ALL skills → computes metrics
    │
    ├── all skills healthy ──► runs evolution check
    │                           │
    │                           ▼
    │                    detect_missing_capability()
    │                           │
    │                           ▼
    │                    generate_new_function()
    │                           │
    │                           ▼
    │                    adds function to run_eval.py
    │
    └── degraded skills found ──► scripts/improve_skill.py
                                        │
                                        ▼
                                  runs evals to find failures
                                        │
                                        ▼
                                  parses failure output
                                        │
                                        ▼
                                  analyze_failures_locally()
                                        │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
              fixes found      experiments needed   new function
                  │                 │                 needed
                  ▼                 ▼                 ▼
          apply_fixes()    run_experiment()   generate_new_function()
              │                 │                 │
              ▼                 ▼                 ▼
    validate in temp dir ──► compare variants ──► append to scripts
              │                 │                 │
              ▼                 ▼                 ▼
    validates improvement  picks winner A/B   validates new function
              │                 │                 │
              ▼                 ▼                 ▼
    writes to real skill ──► merge if better ─► writes to real skill
              │                                 │
              ▼                                 ▼
          git commit ────────────────────────► git commit
              │                                 │
              ▼                                 ▼
      git push + PR ────────────────────────► git push + PR
```

## Core Scripts

| Script | Purpose |
|--------|---------|
| `run_health_check.py` | Discovers all skills, runs their evals, computes metrics, detects missing capabilities |
| `improve_skill.py` | Runs evals → parses failures → analyzes root causes → runs A/B experiments if needed → generates new functions → validates before commit |
| `sync_memory.py` | Writes lessons to ~/.hermes/memory/ and skill references/ |
| `check_degraded.py` | Reads metrics JSON, outputs `degraded=N` and `skills=...` to `$GITHUB_OUTPUT` |
| `get_degraded_skills.py` | Reads metrics JSON, prints only degraded skill names (for for-loop) |
| `run_eval.py` | 4 tests: health check runs, improve_skill dry run, sync_memory runs, quick_validate passes |

## Failure Pattern → Fix Mapping

| Failure Pattern | Auto-Generated Fix |
|-----------------|-------------------|
| `ModuleNotFoundError: No module named 'X'` | Add `import X` |
| `AttributeError: 'Y' object has no attribute 'Z'` | Add `def Z(self): pass` method |
| `AssertionError` in test | Update test assertion |
| `FileNotFoundError` | Create missing referenced file |
| `TimeoutExpired` | Increase subprocess timeout |
| Degraded but no evals | Generate new helper function |

## New Function Generation

When a skill fails with patterns indicating missing capabilities, the engine can generate:

- `find_file()` - Search for files by name in standard locations
- `find_skill()` - Find skill directories by name
- `compute_metrics()` - Extract metrics from eval output
- `validate_output()` - Validate output against expected patterns
- `optimize_processing()` - Add timeout/retry decorators
- `handle_type_conversion()` - Safe type coercion functions

## Improvement Loop (Enhanced)

For each degraded skill:

1. **Run evals**: Execute `scripts/run_eval.py` on the skill
2. **If evals pass**: Skill is healthy, run evolution check for new capabilities
3. **Parse failures**: Extract `[FAIL]` or `[ERROR]` lines and output from eval
4. **Analyze root causes**: Pattern-match failure output to determine fix type
5. **Detect missing capabilities**: Check if failures indicate new function needed
6. **Generate fixes/experiments/new functions**: Create appropriate code changes
7. **Run A/B experiments** (if applicable): Test variant_b vs variant_a in temp dir
8. **Apply in temp copy**: Apply fixes/new functions to temporary skill copy
9. **Validate**: Run `quick_validate.py` and full evals on temp copy
10. **If validation passes**: Write changes to real skill directory
11. **Commit**: Changes are committed and pushed
12. **Record**: Write lesson to memory/references/

## Metrics Tracked (per skill)

- **Trigger accuracy**: % of relevant prompts that correctly invoke the skill (target: ≥90%)
- **Latency**: p50/p95 response time (target: p95 < 30s)
- **Hallucination rate**: % of claims unverified by tool output (target: <5%)
- **Tool-use success**: % of tool calls that complete without error (target: ≥95%)

## References

- `references/improvement_protocol.md` - Detailed improvement and evolution protocol
- `references/metrics_schema.md` - JSON schema for metrics output

## Pitfalls

- **Description too long**: skill_manage rejects descriptions >60 chars. Keep it trigger-first, one sentence, ends with period.
- **Never use inline Python in YAML**: `python -c "..."` with embedded quotes breaks GitHub Actions YAML parsing. Always use standalone scripts in `scripts/`.
- **Circular dependency trap**: `run_health_check.py` must NOT call `run_eval.py`. Health check validates frontmatter+references directly to avoid infinite recursion and timeout.
- **Repo name mismatch**: If repo name differs from skill name, `find_skill_dir` matches by prefix, and skill name is read from SKILL.md frontmatter via regex.
- **Learned lessons file**: `references/learned_lessons.jsonl` grows unbounded. Should be gitignored or truncated before pushes.
- **Memory sync requires HERMES_TOKEN**: Without the secret, lessons only stay in GitHub repo, not synced to local Hermes memory.