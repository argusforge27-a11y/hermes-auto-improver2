---
name: skill-author
description: Write and harden skills for other agents.
version: 1.0.0
author: Hermes Agent
license: MIT
---
# Skill Author

Works WITH power-core. `SKILL` = this folder.

## Principles for instructions other agents must follow
1. **Frontmatter**: `name` and a pushy `description` stating what it does AND the situations that should trigger it. **Description must be ≤60 characters, trigger-first, ends with a period.** The skill index clips anything longer; this is enforced by `skill_manage` at create time. **Frontmatter must also include**: `version`, `author`, `license`, and `metadata.hermes.tags` + `metadata.hermes.related_skills` — lint warns if missing.
2. **Order and gates**: numbered steps, each with a done-when and a command whose output proves it ("must print PASS").
3. **Make quality checkable**: replace "make it good" with measurable checks or scripts; judgment steps get a checklist.
4. **Worked example**: ship a small example that is known to work, and tell the agent to run it unchanged first.
5. **Constrain creativity**: give templates and recipes to fill in rather than blank-page generation where mistakes are costly.
6. **Short body, deep references**: keep SKILL.md under ~500 lines; push detail into `references/` and say when to read each file.
7. **State dependencies**: tools, versions, network, and which agent-specific features are assumed. Give a fallback.
8. **Explain why** for each important rule; agents follow rules better when they know the failure it prevents.
9. **Pitfalls section** listing the real mistakes seen, with the symptom and the fix.
10. **When to Use section**: Required near top of SKILL.md. Explicit trigger conditions. `skill_lint.py` FAILs if missing.
11. Never include anything surprising or unsafe; a skill must do what its description says.

## Pitfalls
- **Description too long**: `skill_manage` rejects descriptions >60 chars at create time. Write trigger-first, end with period, ≤60 chars. The skill index clips longer text. Test with `skill_manage` create before committing body.
- **Missing frontmatter fields**: Lint warns for missing `version`, `author`, `license`, `metadata.hermes.tags`, `metadata.hermes.related_skills`. Include all at create time.
- **Missing When to Use section**: Lint FAILs without `## When to Use` with explicit trigger conditions. Add before linting.
- **Missing referenced files**: Lint FAILs if SKILL.md references files that don't exist. Create all references/, scripts/, assets/ files before running lint.
- **YAML frontmatter parse errors**: Use `|` for multiline description. Avoid unescaped colons. Validate with `skill_manage` create first.
- **Operations array format**: `skill_manage` requires `operations` as JSON array, not stringified JSON. Pass proper array in tool calls.

## Check it
`python SKILL/scripts/skill_lint.py <skill-folder>` reports missing frontmatter, weak descriptions, missing referenced files,
oversized bodies, and steps without a verifiable gate. Fix every FAIL; consider every WARN.

## Port to another agent
List each tool the skill names, map it to the target agent's equivalent (or state it is missing), simplify steps the
target cannot do, and test with a fresh session on the example task.

