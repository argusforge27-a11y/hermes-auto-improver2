---
name: safe-ops
description: Protect files during risky operations.
version: 1.0.0
author: Hermes Agent
license: MIT
---
# Safe Ops

Works WITH power-core non-negotiable 6 (stay in scope; ask before risky or costly actions). `SKILL` = this folder.

## Before the action
1. **Classify**: read-only, reversible (easy to undo), or irreversible / external (delete, publish, send, spend, overwrite).
2. **Reversible but valuable files**: snapshot first. `python SKILL/scripts/snapshot.py save <path> --note "why"`
3. **Dry run** whenever the tool offers one (`--dry-run`, `-n`, `git diff`, listing the files a glob matches).
4. **Irreversible / external**: show the user exactly what will happen and the target, then wait for a clear yes
   unless the task already gave explicit permission for that exact action.
5. Use the narrowest scope: exact paths, never a wildcard you have not listed; never run as admin unless required.

## During and after
- Do the action in small batches; verify after the first batch before continuing.
- Verify the result (list the folder, diff the file, run the check).
- To undo: `python SKILL/scripts/snapshot.py list` then `snapshot.py restore <id>`.
- Never put secrets in logs, commits or messages. Never disable a safety check to make something pass; report the block.

