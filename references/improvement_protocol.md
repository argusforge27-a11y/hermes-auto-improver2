# Improvement Protocol

## When to Improve
A skill enters the improvement pipeline when any health metric falls below threshold.

## Improvement Steps (Real Pipeline)

### 1. Run Evals to Find Failures
`improve_skill.py` runs the skill's `scripts/run_eval.py` and captures output.
If evals pass, the skill is healthy and no improvement is needed.

### 2. Parse Failures
The eval output is parsed line-by-line to extract specific test failures:
- `[FAIL] Test Name` or `[ERROR] Test Name` markers
- The output following each failure (stdout/stderr)

### 3. Analyze Root Causes
Pattern-based analysis of failure output. Each failure pattern triggers a specific fix:

| Failure Pattern | Fix Applied |
|---|---|
| `ModuleNotFoundError` / `ImportError` | Add missing `import` statement |
| `AttributeError: 'X' has no attribute 'Y'` | Add missing method to class |
| `AssertionError` in test | Update test assertion to match actual behavior |
| `FileNotFoundError` for path | Create the missing referenced file |
| `TimeoutExpired` / timeout | Increase subprocess timeout |

Analysis is done locally (no LLM dependency) — `analyze_failures_locally()` in `improve_skill.py`.

### 4. Apply Fixes
Fixes are applied as targeted string replacements in the skill's scripts:
- `old_code` must exist in the file to be replaced
- If `old_code` is empty, the fix is appended to the file
- Parent directories are created automatically if files don't exist

### 5. Validate in Temp Copy
Before writing to the real skill:
- Copy all skill files to a temp directory
- Apply fixes to the temp copy
- Run `quick_validate.py` on the temp copy
- Re-run the full eval suite on the temp copy
- Only if both pass, write changes to the real skill directory

### 6. Decide
| Condition | Action |
|-----------|--------|
| All evals pass after fix | Write changes to real skill, commit |
| Validation fails | Do NOT write changes, report failure |
| Skill already healthy | Exit 0, no changes |

### 7. Record
- Write lesson to `references/learned_lessons.jsonl`
- Update main Hermes memory with pattern

## Auto-Merge Criteria
- Git diff shows only script and reference file changes
- All existing evals pass after fix
- No new dependencies added
- Validation in temp copy succeeded before writing

## PR Template
When opening PR, include:
- Skill name and degraded metrics
- Failure analysis summary
- Proposed changes (diff)
- Validation results
- Metric comparison table
