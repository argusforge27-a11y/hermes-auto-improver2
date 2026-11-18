# Calibration: make the agent's taste match yours

Agents are usually too lenient, sometimes too harsh. Calibration measures this and corrects it.

## Log every verdict the user gives
`python SKILL/scripts/calibrate.py log "<task>" <agent pass|fail> <human pass|fail> "<what the human saw that the agent missed>" [--dim picture_logic]`

## Read the report
`python SKILL/scripts/calibrate.py report` shows agreement, the false-pass rate (agent approved, human rejected), false-fail
rate, which dimensions keep being missed, and the notes. Then act:
- **High false-pass**: raise the pass bar: require more frames viewed, score 4+ only with two locators, add the missed defect
  type to the rubric, and log it as a lesson with power-core's `lessons.py add`.
- **High false-fail**: the agent is too strict on taste; mark those items as optional.
- **One dimension keeps being missed**: add a dedicated check or script for it; look for it explicitly in the hostile pass.

## Build a small gold set
Keep 3-5 known-good outputs and 3-5 known-bad ones (with the defect noted). Before trusting a changed skill or a new model,
make the agent review them blind. It should pass the good ones and reject the bad ones. If not, fix the rubric first.

## Two-pass check
For important decisions, review twice from scratch (second time without looking at the first scores). Where the passes
disagree, look closer at that item; if still unsure, ask the user.
