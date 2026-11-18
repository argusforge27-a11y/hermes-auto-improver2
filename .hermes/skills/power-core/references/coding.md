# Coding: fewer bugs, faster fixes

## Before writing
1. Understand the contract: inputs, outputs, edge cases, performance limits, environment (OS, versions).
2. Look at what exists. `ls`, `grep`, read the nearest working example. Copy its structure and conventions.
3. List every external name you will use (functions, classes, flags, endpoints). **Verify each exists**:
   grep the source or run `--help`. Invented APIs are the #1 cause of broken generated code.
4. Choose the simplest design that satisfies the criteria. No framework or abstraction without a reason.

## While writing
- Grow the program in small increments; run after each. Keep a working state at all times.
- Smallest change that moves toward the goal. Don't refactor and add features in the same step.
- Handle the boundaries: empty input, missing file, wrong type, huge input, unicode, timeouts.
- Fail loudly with a clear message; never swallow exceptions silently.
- Names say what things are. Comment *why*, not *what*.
- No magic numbers: name them. No hidden global state.
- Keep secrets out of code and logs.

## Verify (mandatory)
```
python SKILL/scripts/verify_code.py <file> [<file> ...]
```
Checks syntax (Python, JS via node, shell via bash -n, JSON), flags Python undefined names when pyflakes
is available, and flags leftover TODO / FIXME / placeholder markers. Then **run the code on real input**.
Passing syntax checks does not mean it works.

## Testing
- At minimum: one normal case, one edge case, one failure case. Test the behavior the user cares about.
- A bug fix starts with a failing test (or failing reproduction command) and ends with it passing.
- Re-run everything that previously passed. Regressions are common.

## Debugging loop
Read the error top to bottom -> locate the first line that is yours -> ONE hypothesis -> add a print/assert or
a minimal repro to test it -> change one thing -> re-run -> record. Two failures in a row means the hypothesis
is wrong; step back and re-read the code and the instructions.

## Generated-project hygiene
- Pin versions you depend on; note the install commands you actually ran.
- When a task ships a `check`/`selftest` command, run it on the unmodified example first, then after changes.
- Do not claim an output file is right until you have opened it (play the video, view the image, open the page).

## Self-review before reporting
[ ] Meets the criteria? [ ] Did I run it? [ ] Edge cases? [ ] Errors visible? [ ] Anything invented?
[ ] Anything unfinished? [ ] Is the diff minimal and readable?
