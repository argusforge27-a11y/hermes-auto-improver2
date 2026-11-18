#!/usr/bin/env python3
"""Quick validation for the skill."""
import re
from pathlib import Path

def validate():
    skill_root = Path(__file__).parent.parent
    skill_md = skill_root / "SKILL.md"
    if not skill_md.exists():
        return False
    content = skill_md.read_text()
    required = ['name:', 'description:']
    for field in required:
        if field not in content:
            return False
    return True

if __name__ == "__main__":
    if validate():
        print("[PASS] Quick validation")
        exit(0)
    else:
        print("[FAIL] Quick validation")
        exit(1)
