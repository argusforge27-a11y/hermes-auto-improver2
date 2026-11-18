---
name: faceless-longform-doctor
description: Diagnose faceless-longform errors.
version: 1.0.0
author: Hermes Agent
license: MIT
---
# Faceless Long-Form Doctor

## When to Use
A faceless-longform step failed, hung, produced a silent or broken video, or the user asks "why is it not working" before or during a video project.

## Procedure
1. Find the main skill: `FL="$(bash "${HERMES_SKILL_DIR:-.}/../faceless-longform/scripts/find_skill.sh" 2>/dev/null || find ~/.hermes/skills ~/.claude/skills ~/.agents/skills -maxdepth 3 -type d -name faceless-longform 2>/dev/null | head -1)"`. If empty, tell the user the faceless-longform skill is not installed.
2. Run `bash "$FL/scripts/setup.sh" --check` (installs nothing). Fix every MISSING line with the command it prints, then re-run.
3. In the project folder run `./lf lint`, then `./lf check`. Read the first ERROR; fix that one; re-run.
4. Match the symptom:
   - "boot failed: ... lines" -> script changed after voicing: `./lf voice` + `./lf words` (or `./lf estimate`).
   - Chrome not found / did not start -> `npx playwright install chromium`, or `CHROME=/path`, or `CHROME_NO_SANDBOX=1`; install the shared libraries setup.sh names.
   - "Chrome closed the connection" -> out of memory: `./lf render --jobs 1`, close other apps; it already retries.
   - Voice fails on a sentence -> reword it, or add the word to `"pronounce"` in script.json.
   - Silent video -> `./lf cues`, `./lf mix`, render again; confirm with `./lf qa`.
   - Command hangs / terminal timeout -> run it as `./lf bg <command>` and poll `./lf status`.
   - Model download failed -> check network to GitHub/Hugging Face, re-run setup.sh; Whisper failing is not fatal.
5. Confirm with `scripts/selftest.sh` (a few minutes) if the machine itself was the problem.

## Pitfalls
- Do not edit `data/*.json` by hand; delete the file and rebuild it.
- Do not claim a render is fine without `./lf qa` and viewing its frames.

## Verification
`./lf doctor` ends with "All set", `./lf check` ends with CHECK OK, `./lf qa` says PASS.

