# Learning loop: make experience compound

A skill file cannot change model weights. What it CAN do is give the agent a durable, searchable memory of
rules learned from real failures, and force the habit of using it. That is how an agent improves week over week.

## Capture (every time)
Triggers: an error, a user correction, a retry that worked, a surprising behavior, a tool quirk, the review step
catching something, or a shortcut you discovered.
```
python SKILL/scripts/lessons.py add --tags "python,paths" \
  --symptom "script could not find model files" \
  --cause "ran from the wrong working directory" \
  --rule "cd into the project folder before running its scripts, or use absolute paths"
```
Good lesson: specific, causal, an instruction, checkable. Bad lesson: "be careful".

## Retrieve (every time)
`python SKILL/scripts/lessons.py search "keyword keyword"` at the start of a task and again when a step fails.
Tags help: use tool names, file types, domains.

## Consolidate (end of task, or weekly)
`python SKILL/scripts/lessons.py review` shows probable duplicates and the most-used lessons. Then:
- Merge near-duplicates into one sharper rule (`add` the merged one, `retire <id>` the old ones).
- Promote rules hit 3+ times into your task-card habits for that kind of work.
- Retire rules that proved wrong, and record why in a new lesson.

## Learn from success too
When something works unusually well, record the method (symptom can be "n/a"; fill cause and rule).
Successful recipes are as valuable as failure rules.

## Study a better example
When you have a reference that worked (a prior good output, another agent's result, a worked example):
1. Diff it against your result along concrete dimensions: structure, steps taken, checks run, outputs.
2. For each difference that matters, write a lesson.
3. Redo the task and compare again. The gap should shrink. If not, the lesson is wrong or too vague.

## Transfer
Generalize each lesson one level up ("this ffmpeg flag broke" -> "verify flags with --help before use") and tag
both. Specific lessons catch exact repeats; general ones catch new situations.

## Hygiene
~3 lines per lesson. Keep the library to a few hundred entries; retire stale ones.
Never store secrets, personal data or credentials in lessons.
