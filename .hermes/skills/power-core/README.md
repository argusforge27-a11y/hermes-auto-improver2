# Power Core: a skill that upgrades how an agent works

**What it is:** a meta-skill for Hermes Agent (or any agent that reads `SKILL.md` skills). It adds a disciplined loop:
RECALL -> GRASP -> COMMIT -> PLAN -> EXECUTE -> GATE -> LEARN, backed by small scripts that enforce it.

**What it is NOT:** it cannot change the model's weights or raise its raw intelligence. It improves *process*: reading
instructions fully, not inventing APIs, proving results, and remembering lessons. In practice that is where most
agent failures come from.

## Install
1. Copy this folder into Hermes' skills directory (commonly `~/.hermes/skills/power-core/`; check your Hermes docs).
2. Start a new session. Because the description says to use it at the start of every non-trivial task, Hermes should
   load it automatically. If not, say: "Use the power-core skill for this task."
3. Needs only Python 3.8+. No internet, no API keys. State is stored in `~/.power-core/`.
4. If your agent can't load skills, paste the contents of `SKILL.md` into its system prompt or memory, and keep the
   `scripts/` folder somewhere it can run them.

## What's inside
| file | purpose |
|---|---|
| `SKILL.md` | the 7-step loop and the non-negotiables |
| `scripts/lessons.py` | searchable memory of lessons learned (add, search, review, retire) |
| `scripts/taskcard.py` | acceptance criteria + evidence; `gate` blocks "done" until every criterion is proven |
| `scripts/extract_rules.py` | lists every MUST/NEVER/ALWAYS line of a document so nothing is skimmed |
| `scripts/verify_code.py` | syntax checks (py, js, sh, json) and leftover-placeholder detection |
| `references/` | comprehension, analysis, coding, learning-loop, verification, skills-and-tools, measure |
| `assets/seed_lessons.jsonl` | 12 starter lessons (incl. those from the faceless-shorts failure) |

## Try it on the failing task first
Ask Hermes: "Using power-core, make the faceless-shorts video about <topic>." Then compare with its earlier bad result.
See `references/measure.md` to A/B test properly.

## Make it learn over time
After every mistake or correction, Hermes logs a lesson with `lessons.py add`. At the start of each task it runs
`lessons.py search`. Lessons compound, which is the closest a skill can get to "learning".
