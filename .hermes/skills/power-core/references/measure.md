# Measure: prove the upgrade helps

1. Pick 5-10 representative tasks, including ones the agent failed before (e.g. a skill-driven video build).
2. Run each WITHOUT power-core and record: pass/fail against the criteria, errors the user found, time, retries.
3. Run each WITH power-core, same tasks, fresh session. Record the same numbers.
4. Compare. Keep what raises the success rate. If a step adds time but no quality, shorten it.
5. After 2-3 weeks, run `lessons.py review`: are repeated lessons dropping? That is the learning curve.

Tip: keep one "golden" task and re-run it after every edit to this skill so regressions show up immediately.
