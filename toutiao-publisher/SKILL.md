---
name: toutiao-publisher
description: Publish articles to Toutiao (Today's Headlines). Handles persistent authentication (login once) and session management. Supports both desktop and Linux headless environments.
---

# Toutiao Publisher Skill

Manage Toutiao (Today's Headlines) account, maintain persistent login session, and publish articles.

## When to Use This Skill

Trigger when user:
- Asks to publish to Toutiao/Today's Headlines
- Wants to manage Toutiao login
- Mentions "toutiao" or "头条号"

## Core Workflow

### Step 1: Authentication (One-Time Setup)

The skill requires a one-time login. The session is persisted for subsequent uses.

#### Option A: Interactive Login (Desktop with Display)

```bash
# Browser will open for manual login (scan QR code)
python scripts/run.py auth_manager.py setup
```

**Instructions:**
1.  Run the setup command.
2.  A browser window will open loading the Toutiao login page.
3.  Log in manually (e.g., scan QR code).
4.  Once logged in (redirected to dashboard), the script will save the session and close.

#### Option B: Import Cookies (Linux/Headless/Remote Server)

If you have cookies from a browser export, you can import them directly:

```bash
# Import cookies from JSON file
python scripts/run.py import_cookies.py --cookies cookies.json
```

**Cookie Format:** Standard browser cookie export in JSON format with fields: `name`, `value`, `domain`, `path`, `secure`, `httpOnly`, `sameSite`, `expirationDate`, etc.

### Step 2: Publish Article

```bash
# Desktop: Opens browser with authenticated session at publish page
python scripts/run.py publisher.py

# Linux/Server: Use headless mode with pre-imported cookies
python scripts/run.py publisher.py --headless --title "Article Title" --content "article.md"
```

**Desktop Instructions:**
1.  Run the publisher command.
2.  Browser opens directly to the "Publish Article" page.
3.  Write and publish the article manually.
4.  Press `Ctrl+C` in the terminal when done.

**Linux/Server Instructions:**
- Ensure cookies are imported first (see Option B above)
- Use `--headless` flag
- Provide `--title` and `--content` arguments
- Browser runs without GUI

> **Note:** Toutiao requires titles to be **2-30 characters**. This tool automatically optimizes titles to fit this constraint (truncating if >30, padding if <2).

#### Automated Publishing

You can fully automate the publishing process by providing arguments:

```bash
# Publish with title, content file, and cover image
python scripts/run.py publisher.py --title "AI Trends 2025" --content "article.md" --cover "assets/cover.jpg" --headless

# Dry run (fill fields but don't publish)
python scripts/run.py publisher.py --title "Test" --content "test.md" --dry-run --headless
```

### Management

```bash
# Check authentication status
python scripts/run.py auth_manager.py status

# Validate authentication (test if cookies work)
python scripts/run.py auth_manager.py validate

# Clear authentication data (logout)
python scripts/run.py auth_manager.py clear
```

## Linux Headless Environment Support

### Requirements

1. **Python 3.8+** with pip
2. **Chromium browser** - Install via:
   ```bash
   # Using patchright (recommended)
   python -m patchright install chromium

   # Or using system package manager
   sudo apt install chromium  # Debian/Ubuntu
   sudo yum install chromium  # CentOS/RHEL
   ```
3. **Pre-imported cookies** - Since headless mode cannot perform interactive login

### Usage on Linux Server

```bash
# 1. First, import cookies (from a trusted machine with active session)
python scripts/run.py import_cookies.py --cookies cookies.json

# 2. Validate cookies work
python scripts/run.py auth_manager.py validate

# 3. Publish in headless mode
python scripts/run.py publisher.py --headless --title "Server Post" --content "article.md"
```

### Browser Support

The skill automatically detects and uses available browsers in this order:
1. Google Chrome
2. Microsoft Edge
3. Chromium (fallback)

On Linux, if Chrome/Edge are not available, install Chromium:
```bash
pip install patchright
python -m patchright install chromium
```

## Technical Details

- **Persistent Auth**: Uses `patchright` to launch a persistent browser context. Cookies and storage state are saved to `data/browser_state/state.json`.
- **Anti-Detection**: Uses `patchright`'s stealth features to avoid bot detection.
- **Environment**: Automatically manages a virtual environment (`.venv`) with required dependencies.
- **Cookie Import**: Supports standard browser cookie JSON format, auto-fixes `sameSite` field compatibility issues.

## Script Reference

- `scripts/auth_manager.py`: Handles login, session validation, and state persistence.
- `scripts/publisher.py`: Launches authenticated browser for publishing.
- `scripts/import_cookies.py`: Import cookies from browser export JSON.
- `scripts/run.py`: Wrapper ensuring execution in the correct virtual environment.
