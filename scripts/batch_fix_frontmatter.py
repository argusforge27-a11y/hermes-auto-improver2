#!/usr/bin/env python3
"""Batch fix frontmatter for degraded skills."""
import re
from pathlib import Path

FIXES = {
    # Add author to skills missing it
    'author': [
        'skill-author', 'debug-detective', 'data-sanity', 'writing-clarity',
        'memory-never-forget', 'deep-research', 'generate-all-content-types',
        'faceless-shorts', 'ai-video-editor', 'safe-ops', 'power-core',
        'xiaohongshu-agent', 'context-keeper', 'judgment-critic',
        'faceless-longform', 'faceless-longform-doctor', 'faceless-longform-qa',
        'faceless-reference-study'
    ],
    # Fix descriptions
    'description_fixes': {
        'media-qa': 'Quality checks for video, audio, image outputs.',
        'youtube-video-cellcog': 'YouTube video creation with CellCog AI pipelines.',
        'youtube-channel-ops': 'YouTube channel setup and management via Google APIs.'
    },
    # Skills with invalid/nested frontmatter that need rebuilding
    'rebuild_frontmatter': [
        'thinking-frameworks', 'viral-content-architect', 'ai-youtube-content-planning-assistant'
    ]
}

def fix_skill(skill_name: str, skills_root: Path):
    """Fix frontmatter for a single skill."""
    skill_paths = list(skills_root.rglob(f'{skill_name}/SKILL.md'))
    if not skill_paths:
        print(f"  {skill_name}: SKILL.md not found")
        return
    
    skill_path = skill_paths[0]
    content = skill_path.read_text()
    
    # Check if it needs rebuilding (no valid frontmatter)
    if skill_name in FIXES['rebuild_frontmatter']:
        if not content.startswith('---'):
            # Add frontmatter
            desc = FIXES['description_fixes'].get(skill_name, f'{skill_name} skill')
            new_fm = f'''---
name: {skill_name}
description: {desc}
version: 1.0.0
author: Hermes Agent
license: MIT
---
'''
            skill_path.write_text(new_fm + content.strip() + '\n')
            print(f'  {skill_name}: Rebuilt frontmatter')
            return
    
    # Check if frontmatter exists
    if not content.startswith('---'):
        print(f'  {skill_name}: No frontmatter found, skipping')
        return
    
    # Parse existing frontmatter
    parts = content.split('---', 2)
    if len(parts) < 3:
        print(f'  {skill_name}: Invalid frontmatter structure, skipping')
        return
    
    fm_text = parts[1]
    fm_lines = []
    for line in fm_text.split('\n'):
        stripped = line.strip()
        
        # Track entering nested structures
        if stripped.startswith('- ') or (stripped and not stripped[0].isalnum() and ':' not in stripped and not stripped.startswith('#')):
            continue
        
        # Handle description fix
        if stripped.startswith('description:'):
            if skill_name in FIXES['description_fixes']:
                new_desc = FIXES['description_fixes'][skill_name]
                fm_lines.append(f'description: {new_desc}')
            else:
                fm_lines.append(line)
            continue
        
        fm_lines.append(line)
    
    # Check if we need to add author
    has_author = any('author:' in l for l in fm_lines)
    if not has_author and skill_name in FIXES['author']:
        # Insert author after description or at the beginning
        inserted = False
        for i, l in enumerate(fm_lines):
            if l.strip().startswith('description:'):
                fm_lines.insert(i + 1, 'author: Hermes Agent')
                inserted = True
                break
        if not inserted:
            fm_lines.insert(1, 'author: Hermes Agent')
    
    # Check if version exists
    has_version = any('version:' in l for l in fm_lines)
    if not has_version:
        fm_lines.insert(1, 'version: 1.0.0')
    
    # Check if license exists
    has_license = any('license:' in l for l in fm_lines)
    if not has_license:
        fm_lines.insert(1, 'license: MIT')
    
    # Reconstruct frontmatter
    new_fm = '---\n' + '\n'.join(fm_lines) + '\n---\n'
    new_content = new_fm + '\n'.join(parts[2:])
    
    skill_path.write_text(new_content)
    print(f'  {skill_name}: Fixed')

def main():
    skills_root = Path.home() / '.hermes' / 'skills'
    
    print("Fixing skills...")
    for skill in FIXES['author'] + list(FIXES['description_fixes'].keys()) + FIXES['rebuild_frontmatter']:
        fix_skill(skill, skills_root)
    
    print("\nDone!")

if __name__ == '__main__':
    main()