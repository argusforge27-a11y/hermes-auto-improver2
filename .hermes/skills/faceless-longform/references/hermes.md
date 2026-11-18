# Running this skill in Hermes Agent (and other hosts)

Facts about Hermes (from its Skills docs): skills live in `~/.hermes/skills/<category>/<name>/`; every skill becomes a slash command; hub/URL/GitHub installs copy `SKILL.md` plus files under `references/ templates/ scripts/ assets/ examples/` only (that is why the renderer lives in `assets/engine/`); `${HERMES_SKILL_DIR}` resolves to the skill folder; a bare absolute path to a media file in a reply is delivered natively to the chat (Telegram, Discord, ...), and `[[as_document]]` sends it as a file instead of a compressed preview.

## Install
- Copy the folder: `cp -r faceless-longform ~/.hermes/skills/media/` then `/reload-skills` or a new session. Or keep it elsewhere and add that folder under `skills.external_dirs` in `~/.hermes/config.yaml`.
- Run `scripts/setup.sh` once (Hermes terminal, not in the chat prompt); `scripts/selftest.sh` proves it works (a few minutes).
- Hub installs run a security scan. This skill downloads model files and runs ffmpeg/Chrome, so a "caution" finding is expected: review, then `--force` (a "dangerous" verdict can never be forced).
- Companion skills (doctor, qa, reference-study): `scripts/install_companions.sh` copies them next to this one.

## Finding the skill folder
Never rely on a `$SKILL` variable. Use `${HERMES_SKILL_DIR}` or `scripts/find_skill.sh`; after `new_video.sh` every command is `./lf <command>` inside the project, which remembers the path.

## Long commands (the usual source of "it hung" errors)
Voice (10-25 min), Whisper, draft and final renders (5-50 min) can exceed a terminal tool's timeout. Run them as `./lf bg voice`, `./lf bg draft`, `./lf bg final`; check with `./lf status` every minute or two and report per-chapter progress; the log is `logs/<name>.log`. Resumable: voice caches per sentence, render caches per chapter, so a re-run after any interruption continues where it stopped.

## Seeing images
The "look at every contact sheet" rule needs an image-capable tool. Use the host's vision/image tool on `review/chNN.jpg` and `review/final-sheet.jpg`. If the model has no vision, rely on `./lf check`, `./lf lint`, `./lf qa` (numbers) and ask the user to open `review/*.jpg`; say plainly that frames were not inspected.

## Delivering files
- Chat gateways: put the bare absolute path on its own line: `/home/you/faceless-longform/<name>/renders/share.mp4`. Make a chat-sized copy first (`./lf share 45`); chat apps cap uploads. Thumbnail: path plus `[[as_document]]` keeps full quality. Give the full 1080p `final.mp4` path as text for the user to copy or download.
- Claude Code / Claude desktop: `present_files` if available.
- Any host: print absolute paths and sizes.

## Windows
Scripts are bash. Use WSL2 (recommended) or Git Bash. Install: `winget install OpenJS.NodeJS.LTS`, `winget install Gyan.FFmpeg`, Chrome. Inside WSL use Linux paths and install Chrome there or `npx playwright install chromium`.

## Docker, servers, small VPS
Chrome needs shared libraries on bare servers (setup.sh names them); the renderer already uses `--disable-dev-shm-usage` and `--no-sandbox` where needed. RAM: about 0.7 GB per render worker and about 1.5 GB for the audio mix of a 20-minute video; the renderer reduces workers to fit free RAM. Disk: 2-3 GB per 20 minutes; it stops with a clear message if short.
