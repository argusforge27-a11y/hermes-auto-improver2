# Analysis: think in structure, decide with evidence

## 1. Frame the question
- Write the decision or question in one sentence. Write what would change your answer.
- Separate **facts** (observed), **inferences** (derived), **assumptions** (unverified). Label them.

## 2. Investigate before concluding
- Gather evidence from at least two independent sources or methods when stakes are not trivial
  (read the code AND run it; read the docs AND check the changelog date).
- Prefer primary sources (source code, official docs, raw data, logs) over summaries and blog posts.
- Check recency: software versions, prices, laws and APIs change. Note the date of every source.
- Look for the disconfirming case on purpose: "what would I expect to see if I'm wrong?" Then look for it.

## 3. Root-cause analysis (failures and bugs)
1. Reproduce reliably. If you cannot reproduce, you cannot confirm a fix.
2. Write the exact symptom (error text, wrong value, expected vs actual).
3. Bisect: shrink the input or the code until the smallest failing case remains.
4. Ask "why?" until you reach something you can change (stop at the actionable cause).
5. Change one thing, re-run the reproduction, record the result. Do not fix by accumulation.
6. After the fix, ask "where else could this same cause bite?" and check those places.
7. Log a lesson (symptom, cause, rule).

## 4. Comparing options
Make a table: options x criteria that matter for this user. Weigh by importance. State what the winner
sacrifices. Give a recommendation, not just a list. Mention what would flip it.

## 5. Quantitative sanity checks
- Order-of-magnitude check every number. Units. Off-by-one. Percent vs percentage points.
- Re-derive one key figure a second way. If the two disagree, find out why before reporting.
- Show the calculation, not just the result, when the user may want to audit it.

## 6. Calibrated conclusions
End with: **answer**, **confidence** (high/medium/low and why), **what I'd check next** if confidence is not high.
Never present an inference as a fact.

## 7. Research tasks
Plan 3-8 distinct queries first, collect, cross-check, then write. Keep a running list of claim -> source.
Drop any claim you cannot source. Paraphrase rather than quote.
