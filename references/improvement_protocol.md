# Improvement Protocol

## When to Improve

A skill enters the improvement pipeline when:
- Any health metric falls below threshold (degraded in health_metrics.json)
- Or when running with `--evolve` flag to discover new capabilities

## Improvement Steps (Real Pipeline)

### 1. Run Evals to Find Failures
`improve_skill.py` runs the skill's `scripts/run_eval.py` and captures output.
If evals pass, the skill may still need evolution check for new capabilities.

### 2. Parse Failures
The eval output is parsed line-by-line to extract specific test failures:
- `[FAIL] Test Name` or `[ERROR] Test Name` markers
- The output following each failure (stdout/stderr)

### 3. Analyze Root Causes
Pattern-based analysis of failure output. Each failure pattern triggers a specific fix:

| Failure Pattern | Auto-Generated Fix |
|-----------------|-------------------|
| `ModuleNotFoundError` / `ImportError` | Add missing `import` statement |
| `AttributeError: 'X' has no attribute 'Y'` | Add missing method stub to class |
| `AssertionError` in test | Update test assertion to match actual behavior |
| `FileNotFoundError` for path | Create the missing referenced file |
| `TimeoutExpired` / timeout | Increase subprocess timeout |

### 4. Detect Missing Capabilities
If failures suggest a skill lacks a needed helper:
- File not found in standard paths → need `find_file()`
- Attribute errors on common objects → need `compute_X()`
- Validation failures → need `validate_output()`
- Slow operations → need `optimize_processing()`

### 5. A/B Experimentation (When Applicable)
For hypothesis-based improvements:

1. Create variant_a (current) and variant_b (with fix) in temp dirs
2. Run evals on both variants
3. Compare pass rates:
   - If variant_b improves by >10%: apply to real skill
   - If variant_a wins: discard variant_b
   - If tie: open PR for manual review

### 6. Generate New Functions
Generated functions have standard signatures:

```python
def find_file(filename: str, search_paths: List[str] = None) -> Optional[Path]:
    """Find a file by name in standard locations."""
    ...

def compute_metrics(eval_output: str) -> Dict[str, float]:
    """Extract metrics from eval output."""
    ...

def validate_output(output: str, expected_patterns: List[str] = None) -> Dict[str, Any]:
    """Validate output against expected patterns."""
    ...
```

Functions are appended to `run_eval.py` or `quick_validate.py` with full docstrings.

### 7. Apply Fixes
Fixes are applied as targeted string replacements in the skill's scripts:
- `old_code` must exist in the file to be replaced
- If `old_code` is empty, the fix is appended to the file
- Parent directories are created automatically if files don't exist

### 8. Validate in Temp Copy
Before writing to the real skill:
- Copy all skill files to a temp directory
- Apply fixes/new functions to the temp copy
- Run `quick_validate.py` on the temp copy
- Re-run the full eval suite on the temp copy
- Only if both pass, write changes to the real skill directory

### 9. Decide

| Condition | Action |
|-----------|--------|
| All evals pass after fix | Write changes to real skill, commit |
| Validation fails | Do NOT write changes, report failure |
| Skill already healthy + evolution check | Add new function if capabilities detected |
| A/B experiment shows variant_b better | Merge variant_b changes |
| Low confidence in fix | Open PR for manual review |

### 10. Record
- Write lesson to `references/learned_lessons.jsonl`
- Update main Hermes memory with pattern

## Auto-Merge Criteria
- Git diff shows only script and reference file changes
- All existing evals pass after fix
- No new dependencies added
- Validation in temp copy succeeded before writing
- Changes include new function OR fix applied

## PR Template

When opening PR, include:
- Skill name and degraded metrics
- Failure analysis summary
- Proposed changes (diff)
- Validation results
- Metric comparison table
- New functions added (if any)

## Evolution Check

Even healthy skills run an evolution check when `--evolve` flag is used:
1. Read skill files for context
2. Check if any missing capabilities are detected (via pattern matching)
3. Generate new function if capability needed
4. Validate and append function to appropriate script
5. Run evals to ensure nothing broke

This allows skills to grow new capabilities over time, not just maintain existing behavior.