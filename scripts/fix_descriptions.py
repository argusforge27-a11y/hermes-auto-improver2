#!/usr/bin/env python3
"""Batch fix long descriptions for degraded skills."""
from pathlib import Path

FIXES = {
    'skill-author': ('Write and harden skills for other agents.', 'Hermes Agent', '1.0.0', 'MIT'),
    'debug-detective': ('Debug with hypothesis logging.', 'Hermes Agent', '1.0.0', 'MIT'),
    'data-sanity': ('Check data quality before analysis.', 'Hermes Agent', '1.0.0', 'MIT'),
    'writing-clarity': ('Produce clear, audience-appropriate writing.', 'Hermes Agent', '1.0.0', 'MIT'),
    'memory-never-forget': ('Persistent memory across sessions.', 'Hermes Agent', '1.0.0', 'MIT'),
    'deep-research': ('Rigorous multi-source research.', 'Hermes Agent', '1.0.0', 'MIT'),
    'faceless-shorts': ('Create faceless YouTube Shorts.', 'Hermes Agent', '1.0.0', 'MIT'),
    'ai-video-editor': ('Edit talking-head videos for free.', 'Hermes Agent', '1.0.0', 'MIT'),
    'safe-ops': ('Protect files during risky operations.', 'Hermes Agent', '1.0.0', 'MIT'),
    'power-core': ('Upgrade how the agent learns and reads.', 'Hermes Agent', '1.0.0', 'MIT'),
    'youtube-channel-ops': ('YouTube channel setup via Google APIs.', 'Hermes Agent', '1.0.0', 'MIT'),
    'xiaohongshu-agent': ('Xiaohongshu/RED content automation.', 'Hermes Agent', '1.0.0', 'MIT'),
    'context-keeper': ('Keep long tasks on track.', 'Hermes Agent', '1.0.0', 'MIT'),
    'judgment-critic': ('Strengthen agent evaluation judgment.', 'Hermes Agent', '1.0.0', 'MIT'),
    'faceless-longform': ('Create 8-20+ min faceless videos.', 'Hermes Agent', '1.0.0', 'MIT'),
    'faceless-longform-doctor': ('Diagnose faceless-longform errors.', 'Hermes Agent', '1.0.0', 'MIT'),
    'faceless-longform-qa': ('Quality-check rendered videos.', 'Hermes Agent', '1.0.0', 'MIT'),
    'faceless-reference-study': ('Study reference video patterns.', 'Hermes Agent', '1.0.0', 'MIT'),
    'media-qa': ('Measurable quality checks for media.', 'Hermes Agent', '1.0.0', 'MIT'),
    'youtube-video-cellcog': ('YouTube video with CellCog AI.', 'Hermes Agent', '1.0.0', 'MIT'),
}

def fix_skill(skill_name, skills_root):
    skill_paths = list(skills_root.rglob(f'{skill_name}/SKILL.md'))
    if not skill_paths:
        print(f'{skill_name}: NOT FOUND')
        return
    
    skill_path = skill_paths[0]
    content = skill_path.read_text()
    
    if skill_name not in FIXES:
        print(f'{skill_name}: No fix defined')
        return
    
    desc, author, version, license = FIXES[skill_name]
    
    # Build new frontmatter
    new_fm = f'''---
name: {skill_name}
description: {desc}
version: {version}
author: {author}
license: {license}
---
'''
    
    # Find content after frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            body = parts[2]
        else:
            body = content
    else:
        body = content
    
    skill_path.write_text(new_fm + body.lstrip() + '\n')
    print(f'{skill_name}: Fixed')

if __name__ == '__main__':
    skills_root = Path.home() / '.hermes' / 'skills'
    for skill_name in FIXES:
        fix_skill(skill_name, skills_root)
    print('Done!')