---
name: debug-detective
description: Debug with hypothesis logging.
version: 1.0.0
author: Hermes Agent
license: MIT
---
# Debug Detective

Works WITH power-core and its coding reference; this adds a log that stops flailing. `SKILL` = this folder.

## Loop
1. `python SKILL/scripts/hypo.py new "<exact symptom: error text, expected vs actual>"`
2. Reproduce it with ONE command you can re-run. Write that command in the symptom or notes. No reproduction, no fix.
3. Shrink: remove input, code and config until the smallest failing case remains.
4. `python SKILL/scripts/hypo.py try "<hypothesis>" "<the single change or probe>"`
5. Make that one change or probe, re-run the reproduction.
6. `python SKILL/scripts/hypo.py result ok|fail "<what you observed>"`
   (The tool refuses a new `try` while the previous one has no result.)
7. After 2 failed hypotheses in a row it tells you to STOP: re-read the error, the instructions and the docs, and pick a
   different line of attack (different layer, different tool, simpler repro).
8. When fixed: `hypo.py close "<root cause>" "<how verified>"`, then log a lesson with power-core's `lessons.py add`,
   then ask where else the same cause could occur.

## Where bugs usually hide (check in order)
Wrong working directory or path -> wrong version or environment -> bad input data -> assumption about an API that is false ->
state left over from a previous run -> timing or ordering -> your own recent change (diff it).
Read the FIRST error in the output, not the last; later errors are often consequences.

