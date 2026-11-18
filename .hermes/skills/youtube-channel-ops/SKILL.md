---
name: youtube-channel-ops
description: YouTube channel setup via Google APIs.
version: 1.0.0
author: Hermes Agent
license: MIT
---
# YouTube Channel Setup & Operations

## Overview
Full workflow to take a user from a new Gmail account and Google Cloud project to a fully connected YouTube channel via the YouTube Data API v3. Also covers channel asset generation and upload where the API permits.

## When to Use
- Creating a brand-new YouTube channel from scratch
- Connecting a new YouTube channel to programmatic management
- Setting up channel description/branding via Google API
- Debugging OAuth or API permission issues on a YouTube channel

## Procedure

### Step 1: Gmail Account
- Create new Gmail address matching desired channel persona (e.g., `argusforge27@gmail.com`).
- Verify availability; if taken, append numeric handles (e.g., `argusforge27`).

### Step 2: Google Cloud Project
- Create new project (e.g., `ArgusForgeYT`).
- Enable YouTube Data API v3 via console link: `https://console.developers.google.com/apis/api/youtube.googleapis.com/overview?project=<PROJECT_ID>`.
- Create OAuth 2.0 Client ID (type: Desktop app).

### Step 3: OAuth Consent Screen
- Set app name and support email.
- Set Audience appropriately.
- Add user as a Test user under Audience section: `+ ADD USERS` → enter the Gmail address.
- Save and continue through remaining steps.

### Step 4: Authentication
- Use `InstalledAppFlow` with scopes `[https://www.googleapis.com/auth/youtube, https://www.googleapis.com/auth/youtube.upload, https://www.googleapis.com/auth/youtube.force-ssl]`.
- **CRITICAL**: If changing scopes, delete existing token file before re-running.
- Token file path: `~/.hermes/cache/scratch/youtube_token.pickle`

### Step 5: Verify Connection
- Run channel info lookup: `service.channels().list(part='snippet,statistics', mine=True).execute()`.
- Expect success: connected to channel with `snippet.title`, `snippet.customUrl`, `statistics.subscriberCount`, etc.

### Step 6: Update Channel Description
- Use `channels().update(part='brandingSettings', body={'id': ..., 'brandingSettings': {'channel': {'description': ...}}})`.
- **Pitfall**: `description` lives under `brandingSettings.channel`, NOT `snippet`.

### Step 7: Upload Banner
- Generate banner via image API (e.g., Pollinations.ai) at **2560x1440** JPEG/RGB.
- Convert PNG→JPEG via Pillow if needed (`img.convert('RGB').save(..., quality=90)`).
- Upload via `channelBanners().insert(media_body=MediaFileUpload(path, mimetype='image/jpeg')).execute()`.
- Apply via `channels().update(part='brandingSettings', ...)` with returned `url`.

### Step 7: Logo
- YouTube Data API does **not** support logo/profile-picture updates directly. Use YouTube Studio manual upload under Customization → Branding → Picture.

### Step 8: Custom Thumbnails (Required for Faceless Shorts Automation)
- Channel must be verified for custom thumbnails:
  YouTube Studio → Settings → Channel → Feature eligibility → **Verify phone number**.
- Without verification, `thumbnails.set` returns 403 `forbidden` — videos upload but use auto-generated thumbnails.
- This is a one-time manual step; after verification, API thumbnail uploads work automatically.

## Pitfalls

- **Testing mode gates access**: User must be added as a Test user to the OAuth consent screen before Google blocks authorization (error 403 `access_denied`).
- **Scope drift invalidates tokens**: Adding/revoking OAuth scopes requires deleting the stored token file before re-authenticating; otherwise old token is reused and returns `insufficientPermissions` / `accessNotConfigured`.
- **Field name differences**: For channel description updates, use `brandingSettings.channel.description`, not `snippet.description`.
- **Banner MIME type**: API rejects PNG banners (`bannerValidationError`); use `image/jpeg` with RGB conversion.
- **Image generation rate limits**: Pollinations.ai free tier allows ~1 image per 45s per IP; use `flux` model for quality, `sana` default for speed.
- **Google API enablement**: Enable YouTube Data API v3 in the target project or calls fail with `accessNotConfigured`.
- **Custom thumbnails require channel verification**: Phone verification in YouTube Studio is mandatory before `thumbnails.set` works.

## References
- `faceless-shorts` → `references/automation-workflow.md` (4-bot pipeline, style-example approach, thumbnail upload)
