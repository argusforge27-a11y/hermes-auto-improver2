---
name: deep-research
description: Rigorous multi-source research.
version: 1.0.0
author: Hermes Agent
license: MIT
---
# Deep Research

Works WITH power-core (use its task card for the question and its lessons for past research mistakes).
`SKILL` = this folder.

## Method
1. **Frame**: one-sentence question, what would change the answer, the date today. Record it as the task-card goal.
2. **Plan 3-8 distinct queries** (different angles, not rewordings). Start broad, then narrow. Look for the primary source
   (official docs, filings, source code, original paper or data) before secondary coverage.
3. **Collect into the ledger** as you go:
   `python SKILL/scripts/ledger.py add --claim "..." --source "<url or title>" --date 2026-05 --kind primary|secondary --note "..."`
4. **Cross-check**: every important claim needs 2 independent sources, or one primary source. Different sites that copy one
   origin count as one source. Actively search for a source that disagrees.
5. **Audit**: `python SKILL/scripts/ledger.py check` flags claims with one weak source, missing dates, or conflicts.
   Fix or downgrade each flag.
6. **Write** from the ledger only. Facts, inferences and assumptions are labeled. End with confidence (high / medium / low,
   why) and what you would check next.

## Rules
- Note the date of each source; for fast-changing facts prefer the newest and say when it was published.
- Paraphrase in your own words; quote only a few words when exact wording matters; always give the source.
- If you cannot verify a claim, either leave it out or mark it "unverified". Never fill gaps from memory as if sourced.
- Present disagreement between sources honestly instead of picking one silently.
- Opinion-heavy or contested topics: report the main positions fairly and who holds them.

