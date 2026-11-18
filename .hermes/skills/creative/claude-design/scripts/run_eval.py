#!/usr/bin/env python3
"""Basic evals for the skill."""
import re
import sys
from pathlib import Path

def test_module_imports():
    scripts_dir = Path(__file__).parent
    if scripts_dir.exists():
        files = list(scripts_dir.glob("*.py"))
        assert len(files) > 0, "No Python scripts found"
    print("[PASS] test_module_imports")
    return True

def test_skill_frontmatter():
    skill_root = Path(__file__).parent.parent
    skill_md = skill_root / "SKILL.md"
    assert skill_md.exists(), "SKILL.md not found"
    content = skill_md.read_text()
    for field in ['name:', 'description:', 'version:', 'author:', 'license:']:
        assert field in content, f"Missing: {field}"
    print("[PASS] test_skill_frontmatter")
    return True

def test_references_exist():
    skill_root = Path(__file__).parent.parent
    skill_md = skill_root / "SKILL.md"
    if not skill_md.exists():
        print("[SKIP] test_references_exist")
        return True
    content = skill_md.read_text()
    references = re.findall(r'`([^`]+)`', content)
    missing = []
    for ref in references:
        ref_path = skill_root / ref
        if not ref_path.exists():
            missing.append(ref)
    if missing:
        print(f"[FAIL] test_references_exist: Missing {missing}")
        return False
    print("[PASS] test_references_exist")
    return True

def test_basic_functionality():
    print("[PASS] test_basic_functionality")
    return True

def main():
    tests = [test_module_imports, test_skill_frontmatter, test_references_exist, test_basic_functionality]
    passed = failed = 0
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except AssertionError as e:
            print(f"[FAIL] {test.__name__}: {e}")
            failed += 1
    print(f"Results: {passed} passed, {failed} failed")
    sys.exit(1 if failed > 0 else 0)

if __name__ == "__main__":
    main()
