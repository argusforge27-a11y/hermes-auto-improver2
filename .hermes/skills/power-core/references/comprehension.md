# Comprehension: grasp it fully the first time

## Why agents misread
They skim long text, latch onto the first example, and drop constraints stated once, deep in a paragraph.
The fix is mechanical, not "try harder".

## Procedure
1. **Extract the hard rules.** `python SKILL/scripts/extract_rules.py <file>` lists every line containing
   must / never / always / do not / required / only / exactly / "prints" etc., with line numbers.
   Copy them into the task card as criteria.
2. **Map the document.** Write a 5-line outline: purpose, inputs, steps in order, outputs, gotchas.
3. **Read the gotcha sections twice.** Anything titled QA, pitfalls, never, common mistakes, warnings, limits.
4. **Find the worked example.** If the doc ships an example, treat it as ground truth. Run it once unchanged
   before modifying anything, so you know what "working" looks like.
5. **Paraphrase test.** Before acting, state in your own words: what is the input, what is the output, what are
   the three things most likely to go wrong. If you cannot, you have not understood it. Re-read.
6. **Term check.** For any term, API, or file you don't recognize, look it up in the provided material first
   (grep), then the real docs. Do not guess from the name.

## Reading code you did not write
- Start from the entry point and the data structures, not from line 1 of every file.
- `grep -rn "def \|function \|export " <dir>` to list the real surface area before calling anything.
- Run it on the smallest example and watch the output before changing it.

## Ambiguity rule
List the plausible interpretations. If one is clearly most likely, state your assumption in one line and proceed.
If interpretations lead to very different work and a wrong pick is expensive, ask once, with your recommended default.

## Anti-patterns
- Starting to build after reading only the summary at the top.
- "I'll figure out the details as I go" with a spec that has a QA section you haven't read.
- Reusing an API from memory of a similar library.
