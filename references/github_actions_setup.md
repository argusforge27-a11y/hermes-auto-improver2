# GitHub Actions Deployment

## Quick Setup

1. **Verify the repo exists on GitHub first** (critical):
   ```bash
   curl -sI https://github.com/<user>/<repo>
   ```
   If it returns 404, create the repo on GitHub (empty, no initial commit) before pushing. `git push` to a non-existent repo silently succeeds but the remote returns 404.
2. **Enable Actions BEFORE the first push** — Settings → Actions → Allow all actions. Pushing to a repo without Actions enabled triggers a failed run with 0 jobs and no useful logs.
3. **Copy this skill** to the repo:
   ```bash
   cp -r ~/.hermes/skills/productivity/hermes-auto-improver /path/to/repo/
   ```
4. **Add `.gitignore`** to exclude `references/learned_lessons.jsonl` (grows unbounded in CI, can exceed 50MB):
   ```bash
   echo "references/learned_lessons.jsonl" >> /path/to/repo/.gitignore
   ```
5. **Push to GitHub**
6. **Trigger the first run manually** — go to the Actions tab, click "Run workflow" → "Run workflow". Schedule runs only begin after the first successful manual run.
7. **Add secrets**:
   - `HERMES_TOKEN` — Personal access token for memory sync (optional, for pushing lessons back)
   - `GH_TOKEN` — Auto-provided by GitHub Actions as `GITHUB_TOKEN`

## Workflow File

Place at `.github/workflows/hermes-auto-improver.yml`:

```yaml
name: Hermes Auto-Improver

on:
  schedule:
    - cron: '0 3 * * *'  # Daily at 03:00 UTC
  workflow_dispatch:  # Manual trigger

permissions:
  contents: write
  pull-requests: write

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Run Health Check
        run: |
          python scripts/run_health_check.py
        env:
          HERMES_SKILLS_DIR: ${{ github.workspace }}
          HERMES_METRICS_FILE: ${{ github.workspace }}/health_metrics.json
      
      - name: Upload Metrics
        uses: actions/upload-artifact@v4
        with:
          name: health-metrics
          path: health_metrics.json
      
      - name: Check for Degraded Skills
        id: check
        run: |
          python scripts/check_degraded.py >> $GITHUB_OUTPUT
      
      - name: Trigger Improvements
        if: steps.check.outputs.degraded != '0'
        run: |
          SKILLS=$(python scripts/get_degraded_skills.py)
          for skill in $SKILLS; do
            echo "=== IMPROVING: $skill ==="
            python scripts/improve_skill.py --skill "$skill" --skills-root "${{ github.workspace }}"
          done
      
      - name: Sync Memory
        if: env.HERMES_TOKEN != ''
        run: |
          python scripts/sync_memory.py
        env:
          HERMES_TOKEN: ${{ secrets.HERMES_TOKEN }}
      
      - name: Create PR for Uncertain Changes
        if: steps.check.outputs.degraded != '0'
        uses: peter-evans/create-pull-request@v5
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          branch: auto-improve/${{ github.run_id }}
          title: "Auto-improve: degraded skills detected"
          body: |
            Health check found degraded skills: ${{ steps.check.outputs.skills }}
            
            See workflow run for details.
          labels: auto-improve, needs-review
```

**Key differences from earlier versions:**
- No `cd hermes-auto-improver` — workflow runs from repo root where `SKILL.md` lives
- No `pip install pyyaml` — frontmatter parsed with regex, zero external deps
- Health check exits 0 always; `Check for Degraded Skills` step reads metrics and controls downstream steps
- `improve_skill.py` writes changes directly to skill directory for PR creation

## Critical Notes

- **Do NOT run `pip install hermes-agent`** — the package does not exist on PyPI
- Scripts are designed to run **standalone** (no Hermes runtime required)
- Only dependency is `pyyaml` (stdlib + PyYAML)
- Paths are configured via environment variables, not hardcoded to `~/.hermes`
- Health check runs against skills in the GitHub workspace, not local machine

## Local Testing

```bash
# Run health check locally
python scripts/run_health_check.py

# Test improvement on one skill
python scripts/improve_skill.py --skill skill-name --dry-run

# Validate skill structure
python ~/.hermes/skills/productivity/skill-creator/scripts/quick_validate.py ~/.hermes/skills/productivity/hermes-auto-improver
```
