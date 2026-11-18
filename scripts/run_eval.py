#!/usr/bin/env python3
"""
Eval script for hermes-auto-improver skill.
Runs health check and validates improvement logic.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent


def test_health_check_runs():
    """Test that health check script runs without error"""
    result = subprocess.run(
        [sys.executable, str(SKILL_DIR / "scripts" / "run_health_check.py")],
        capture_output=True, text=True, timeout=180
    )
    return result.returncode in (0, 1), result.stdout


def test_improve_skill_dry_run():
    """Test improve_skill.py dry run on a known skill (without triggering evals)"""
    # Read skill name from SKILL.md frontmatter
    import re
    skill_md = (SKILL_DIR / "SKILL.md").read_text()
    m = re.search(r'name:\s*["\']?([^"\'\n]+)', skill_md)
    skill_name = m.group(1).strip() if m else SKILL_DIR.name
    
    # Test with --dry-run and a different skills-root to avoid circular eval
    with tempfile.TemporaryDirectory() as tmp:
        # Create skill in productivity/ subdir (first place find_skill_dir looks)
        prod_dir = Path(tmp) / "productivity"
        prod_dir.mkdir()
        tmp_skill = prod_dir / skill_name
        tmp_skill.mkdir()
        (tmp_skill / "SKILL.md").write_text(skill_md)
        (tmp_skill / "scripts").mkdir()
        (tmp_skill / "scripts" / "quick_validate.py").write_text("import sys; sys.exit(0)\n")
        
        result = subprocess.run(
            [sys.executable, str(SKILL_DIR / "scripts" / "improve_skill.py"), "--skill", skill_name, "--dry-run", "--skills-root", tmp],
            capture_output=True, text=True, timeout=60
        )
    return result.returncode == 0, result.stdout


def test_sync_memory():
    """Test sync_memory.py runs"""
    # Set env vars to temp files
    with tempfile.TemporaryDirectory() as tmp:
        env = os.environ.copy()
        env["HERMES_METRICS_FILE"] = str(Path(tmp) / "metrics.json")
        env["HERMES_MEMORY_FILE"] = str(Path(tmp) / "memory.json")
        env["HERMES_LESSONS_FILE"] = str(Path(tmp) / "lessons.jsonl")
        
        # Create minimal metrics
        metrics = {"timestamp": 0, "skills": []}
        Path(env["HERMES_METRICS_FILE"]).write_text(json.dumps(metrics))
        
        result = subprocess.run(
            [sys.executable, str(SKILL_DIR / "scripts" / "sync_memory.py")],
            capture_output=True, text=True, timeout=30,
            env=env
        )
    return result.returncode == 0, result.stdout


def test_quick_validate():
    """Test quick_validate.py passes on this skill"""
    result = subprocess.run(
        [sys.executable, str(SKILL_DIR / "scripts" / "quick_validate.py")],
        capture_output=True, text=True, timeout=30
    )
    return result.returncode == 0, result.stdout


def main():
    tests = [
        ("Health check runs", test_health_check_runs),
        ("Improve skill dry run", test_improve_skill_dry_run),
        ("Sync memory runs", test_sync_memory),
        ("Quick validate passes", test_quick_validate),
    ]
    
    all_pass = True
    for name, test_fn in tests:
        try:
            passed, output = test_fn()
            status = "PASS" if passed else "FAIL"
            print(f"[{status}] {name}")
            if not passed:
                print(f"  Output: {output[:200]}")
                all_pass = False
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
            all_pass = False
    
    if all_pass:
        print("\nAll evals passed!")
        return 0
    else:
        print("\nSome evals failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())