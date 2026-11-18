# Verification: prove it, don't assume it

## The evidence ladder (strongest first)
1. You ran it on real input and inspected the real output.
2. You ran an automated check that fails when wrong.
3. You read the code/diff carefully.
4. You reasoned it should work.   <- never enough alone

Report which rung each claim sits on.

## Hostile review (before "done")
Pretend you are an unhappy user and a strict reviewer. Re-read the ORIGINAL request, not your plan.
1. Open the actual deliverable (file, page, video, image, report). Look at all of it, not a sample.
2. Walk the requirement list item by item; point to evidence for each.
3. Hunt for three defects: something missing, something wrong, something sloppy. Finding none means look harder.
4. Check the seams: where two parts meet (audio vs picture, data vs chart, code vs docs, units, names).
5. Check for regressions: did fixing X break Y?
6. If the instructions list "Never..." items, confirm you did none of them.

## Visual and media output
- View frames/pages at the size the user will see them. Check legibility, overlap, cut-off, wrong colors.
- Video: sample a frame every 0.5-1 s plus first and last; measure audio level; check duration; check that
  on-screen text matches the narration.
- If you cannot actually see images or hear audio, SAY SO. Rely on measurable checks (frame differences,
  text-overlap math, loudness, duration) and ask the user to review. Never pretend to have looked.

## Honest report template
- **Done**: what works, with evidence.
- **Not done / limits**: anything skipped or uncertain, plainly.
- **Caught and fixed**: what your review found.
- **Next**: what you'd do, or what you need from the user.
Short and concrete. Do not bury problems mid-paragraph.

## When verification fails
Do not argue with the failure. It is the most reliable information you have. Fix, re-run the gate, log a lesson.
