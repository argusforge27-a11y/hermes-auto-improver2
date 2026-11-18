---
name: context-keeper
description: Keep long tasks on track.
version: 1.0.0
author: Hermes Agent
license: MIT
---
# Context Keeper

Works WITH power-core (the task card holds criteria; this holds the story). `SKILL` = this folder.

- Start: `python SKILL/scripts/notes.py init "<project name>" "<goal>"`
- After each verified step or key decision, update: `notes.py set decision "chose X because Y"` ·
  `notes.py set files "path - what it is"` · `notes.py set next "the next concrete action"` · `notes.py set risk "..."`
- Resume or hand off: `notes.py show` and read it fully before doing anything else; then confirm the files still exist.
- Keep entries short and factual. Record paths, commands that worked, and the reason for each decision.
- When the context is long, rewrite the notes into a clean summary and continue from it; do not rely on remembering.
- Never store secrets or passwords in notes.

