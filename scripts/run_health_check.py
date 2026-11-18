#!/usr/bin/env python3
"""
Health check runner for all Hermes skills.
Works standalone (no Hermes runtime, no external deps).
"""
import json
import os
import subprocess
import sys
import time
import re
from pathlib import Path
from typing import Dict, List, Any

SKILLS_DIR = Path(os.environ.get("HERMES_SKILLS_DIR", Path.home() / ".hermes" / "skills"))
METRICS_FILE = Path(os.environ.get("HERMES_METRICS_FILE", Path.home() / ".hermes" / "cache" / "health_metrics.json"))


def discover_skills() -> List[Path]:
    """Find all skill directories with SKILL.md"""
    skills = []
    if not SKILLS_DIR.exists():
        print(f"Skills directory not found: {SKILLS_DIR}")
        return skills
    
    # Check if SKILLS_DIR itself is a skill
    if (SKILLS_DIR / "SKILL.md").exists():
        skills.append(SKILLS_DIR)
    
    # Find all skill directories (both direct children and nested in categories)
    for skill_dir in SKILLS_DIR.rglob("*"):
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
            # Avoid duplicates (skills_dir itself is already added)
            if skill_dir not in skills:
                skills.append(skill_dir)
    return skills


def parse_frontmatter(content: str) -> dict | None:
    """Parse YAML frontmatter without PyYAML - only top-level fields"""
    if not content.startswith("---"):
        return None
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    
    fm_text = parts[1]
    fm = {}
    in_nested = False
    for line in fm_text.split('\n'):
        stripped = line.strip()
        
        # Skip nested content (indented lines, list items, empty lines)
        if in_nested:
            if line and not line[0].isspace():
                in_nested = False
            else:
                continue
        
        # Track entering nested structures
        if stripped.startswith('- ') or stripped.startswith('  '):
            in_nested = True
            continue
            
        if ':' in stripped and not stripped.startswith('#'):
            key, val = stripped.split(':', 1)
            key = key.strip()
            val = val.strip().strip('"\'')
            if val.startswith('[') and val.endswith(']'):
                val = [v.strip().strip('"\'') for v in val[1:-1].split(',')]
            fm[key] = val
        elif stripped == '' and in_nested:
            continue
            
    return fm


def validate_skill_frontmatter(skill_dir: Path) -> tuple[bool, str]:
    """Validate skill frontmatter"""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return False, "No SKILL.md"
    
    content = skill_md.read_text()
    fm = parse_frontmatter(content)
    if fm is None:
        return False, "Missing or invalid frontmatter"
    
    required = ["name", "description", "version", "author", "license"]
    for field in required:
        if field not in fm:
            return False, f"Missing frontmatter field: {field}"
    
    desc = fm.get("description", "")
    if len(desc) > 60:
        return False, f"Description too long: {len(desc)} chars (max 60)"
    
    return True, "Frontmatter OK"


def validate_skill_references(skill_dir: Path) -> tuple[bool, str]:
    """Check that referenced files exist"""
    skill_md = skill_dir / "SKILL.md"
    content = skill_md.read_text()
    
    refs = re.findall(r'references/([a-zA-Z0-9_][a-zA-Z0-9_.-]{0,63})', content)
    missing = []
    for ref in refs:
        if not (skill_dir / "references" / ref).exists():
            missing.append(ref)
    
    if missing:
        return False, f"Missing referenced files: {missing}"
    
    return True, "All references exist"


def run_skill_evals(skill_dir: Path) -> Dict[str, Any]:
    """Validate a single skill (frontmatter + references). Does NOT run eval scripts
    to avoid circular dependencies (eval scripts may call health check)."""
    skill_name = skill_dir.name
    start = time.time()

    eval_script = skill_dir / "scripts" / "run_eval.py"
    has_eval = eval_script.exists()

    # Always do frontmatter + reference validation
    fm_ok, fm_msg = validate_skill_frontmatter(skill_dir)
    ref_ok, ref_msg = validate_skill_references(skill_dir)
    success = fm_ok and ref_ok
    output = f"Frontmatter: {fm_msg}; References: {ref_msg}; has_eval_script={has_eval}"

    latency = time.time() - start

    return {
        "skill": skill_name,
        "eval_success": success,
        "eval_output": output[:2000],
        "latency_seconds": latency,
        "has_eval_script": has_eval
    }


def compute_trigger_accuracy(skill_dir: Path) -> float:
    """Estimate trigger accuracy (placeholder)"""
    return 0.85


def compute_hallucination_rate(skill_dir: Path) -> float:
    """Estimate hallucination rate (placeholder)"""
    return 0.03


def compute_tool_success_rate(skill_dir: Path) -> float:
    """Estimate tool-use success rate (placeholder)"""
    return 0.97


def main():
    print(f"Discovering skills in {SKILLS_DIR}...")
    skills = discover_skills()
    print(f"Found {len(skills)} skills")

    if not skills:
        print("No skills found. Exiting.")
        sys.exit(1)

    all_metrics = {
        "timestamp": time.time(),
        "skills": []
    }

    for skill_dir in skills:
        print(f"Checking {skill_dir.name}...")
        metrics = run_skill_evals(skill_dir)

        metrics["trigger_accuracy"] = compute_trigger_accuracy(skill_dir)
        metrics["hallucination_rate"] = compute_hallucination_rate(skill_dir)
        metrics["tool_success_rate"] = compute_tool_success_rate(skill_dir)

        healthy = (
            metrics["eval_success"] and  # This checks frontmatter + references
            metrics["trigger_accuracy"] >= 0.80 and  # Placeholder threshold (real impl would be higher)
            metrics["hallucination_rate"] < 0.10 and  # Placeholder threshold
            metrics["tool_success_rate"] >= 0.90 and  # Placeholder threshold
            metrics["latency_seconds"] < 30
        )
        metrics["healthy"] = healthy

        all_metrics["skills"].append(metrics)
        status = "HEALTHY" if healthy else "DEGRADED"
        print(f"  {skill_dir.name}: {status}")

    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    METRICS_FILE.write_text(json.dumps(all_metrics, indent=2))
    print(f"\nMetrics saved to {METRICS_FILE}")

    healthy_count = sum(1 for s in all_metrics["skills"] if s["healthy"])
    print(f"\nSummary: {healthy_count}/{len(all_metrics['skills'])} skills healthy")

    # Always exit 0 - let workflow check step handle degraded
    sys.exit(0)


if __name__ == "__main__":
    main()
