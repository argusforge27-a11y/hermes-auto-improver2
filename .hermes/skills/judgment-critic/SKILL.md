---
name: judgment-critic
description: Strengthen agent evaluation judgment.
version: 1.0.0
author: Hermes Agent
license: MIT
---
# Judgment Critic

Works WITH power-core (this is the detailed form of its hostile review) and with media-qa and any vision skill
(those supply what is seen or measured; this decides what it means). `SKILL` = this folder.

## Why judgment fails
Agents tend to (1) approve their own work, (2) praise in generalities, (3) look at a sample and generalize, (4) miss what they
did not specifically look for, (5) stay confident when they should not. The fixes below target each one.

## The procedure
1. **Pick the rubric**: `references/rubrics.md` (video, image, text, code, generic). Add project-specific criteria from the
   task card and from any provided skill's QA section (extract them with power-core's `extract_rules.py`).
2. **Observe before judging.** Collect raw observations first: view every frame or page you can (not one), zoom into text and
   edges, play or measure audio, run media-qa. Write down what you SEE, not how it feels.
3. **Open a scorecard**: `python SKILL/scripts/review_sheet.py new "<name>" --rubric video`
4. **Score every dimension with evidence**:
   `review_sheet.py score <id> <dimension> <1-5> "<specific observation with a locator: time, frame, region, line>"`
   The tool rejects vague evidence ("looks good") and high scores without a locator.
5. **Hostile pass (separate mindset)**: reread the ORIGINAL request, then list defects you can find:
   `review_sheet.py defect <id> <severity 1-3> "<defect with locator>"`. Find at least 3 or record
   `review_sheet.py nodefects <id> "<exactly what you checked and how>"`.
6. **Compare** when a reference exists (a known-good output, a previous version): same dimensions, side by side. State
   what is better, worse or equal, and why it matters.
7. **Verdict**: `review_sheet.py verdict <id>` returns PASS, REVISE or REJECT by fixed thresholds. You may not override a
   REJECT or REVISE by argument; fix the defects and re-score the affected dimensions.
8. **Confidence and escalation**: if you could not view something, or two dimensions are borderline, say so and ask the user
   to look at those specific items. Honest uncertainty is part of good judgment.
9. **Calibrate** every time the user gives their own verdict: `python SKILL/scripts/calibrate.py log ...`
   then read `calibrate.py report` weekly (see `references/calibration.md`).

## Rules
- A score of 4 or 5 needs a concrete locator. "Looks good overall" is not evidence.
- Severity 3 defects (breaks the purpose, wrong content, unreadable, broken audio) mean REJECT.
- Never lower the bar to finish. If the bar is wrong, tell the user and propose a new one; do not quietly shift it.
- Judge the output against the request and audience, not against your effort.
- Separate "objectively wrong" from "a matter of taste"; flag taste items as optional and do not block on them.

