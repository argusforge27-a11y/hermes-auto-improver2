---
name: faceless-longform-qa
description: Quality-check rendered videos.
version: 1.0.0
author: Hermes Agent
license: MIT
---
# Faceless Long-Form QA

## When to Use
A draft or final video exists (renders/draft.mp4, renders/final.mp4) and needs checking before the user sees it, or the user asks "is this video okay".

## Procedure
1. In the project folder: `./lf qa --draft` (or `./lf qa` for the final). Any ERROR means re-render after fixing it; warnings are judgement calls.
2. View the contact sheet `review/draft-sheet.jpg` (or `final-sheet.jpg`) and the frames beside it with your image tool. If you cannot view images, say so.
3. Watch the hook and each changed chapter: `./lf watch renders/draft.mp4 --start 0 --end 0:45 --max-frames 10` and view each frame.
4. Check: text fits and is not cramped; nothing important sits in the caption zone (bottom ~150 px); no long static stretch; no two neighbouring scenes identical; theme contrast readable; the hook shows motion and text in 3 s.
5. Report: PASS/FAIL, the list of exact problems with timestamps, and which chapters to re-render (`./lf render --chapters N`).

## Pitfalls
- A transcript alone is not a check; view frames.
- Never present a video that failed QA as finished.

## Verification
`renders/qa.md` says PASS and the viewed frames show no layout problem.

