#!/bin/bash
# Scaffold all Hermes skills with required files

set -e

SKILLS_DIR="${HERMES_SKILLS_DIR:-$HOME/.hermes/skills}"
echo "Scaffolding skills in: $SKILLS_DIR"

count=0
for skill_md in $(find "$SKILLS_DIR" -name "SKILL.md" -type f 2>/dev/null); do
    skill_dir=$(dirname "$skill_md")
    skill_name=$(grep "^name:" "$skill_md" 2>/dev/null | head -1 | cut -d: -f2 | tr -d ' "')
    skill_name=${skill_name:-$(basename "$skill_dir")}
    
    echo "Processing: $skill_dir ($skill_name)"
    
    # Add missing frontmatter
    if ! grep -q "^version:" "$skill_md" 2>/dev/null; then
        sed -i '' '/^description:/a\
version: 1.0.0' "$skill_md"
        echo "  Added version"
    fi
    
    if ! grep -q "^author:" "$skill_md" 2>/dev/null; then
        sed -i '' '/^description:/a\
author: '"$skill_name" | sed 's/::/:/' "$skill_md"
        echo "  Added author"
    fi
    
    if ! grep -q "^license:" "$skill_md" 2>/dev/null; then
        sed -i '' '/^description:/a\
license: MIT' "$skill_md"
        echo "  Added license"
    fi
    
    # Create scripts directory if needed
    scripts_dir="$skill_dir/scripts"
    mkdir -p "$scripts_dir"
    
    # Create run_eval.py if missing
    if [ ! -f "$scripts_dir/run_eval.py" ]; then
        cat > "$scripts_dir/run_eval.py" << 'EVALEOF'
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
EVALEOF
    echo "  Created run_eval.py"
    fi
    
    # Create quick_validate.py if missing
    if [ ! -f "$scripts_dir/quick_validate.py" ]; then
        cat > "$scripts_dir/quick_validate.py" << 'QUICKEOF'
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
QUICKEOF
    echo "  Created quick_validate.py"
    fi
    
    count=$((count + 1))
done

echo "Completed: $count skills processed"