# 🔐 Credential Setup Guide

Complete guide for configuring API credentials for SuperSkills.

## Table of Contents

- [Quick Start](#quick-start)
- [Understanding Credential Storage](#understanding-credential-storage)
- [Getting API Keys](#getting-api-keys)
- [Per-Skill Setup](#per-skill-setup)
- [Claude Desktop Integration](#claude-desktop-integration)
- [Security Best Practices](#security-best-practices)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Copy the Template

```bash
cd /path/to/superskills
cp .env.template .env
```

### 2. Edit `.env` File

```bash
# Use your favorite editor
nano .env
# or
code .env
# or
vim .env
```

### 3. Add Your API Keys

Find the services you want to use and replace the placeholder values:

```bash
# Example: OpenAI for Transcriber
OPENAI_API_KEY=sk-abc123...  # Replace with your actual key

# Example: ElevenLabs for Narrator
ELEVENLABS_API_KEY=your_key_here
ELEVENLABS_VOICE_ID=voice_id_here
```

### 4. Verify Setup

```bash
python3 scripts/validate_credentials.py
```

You should see:
```
✓ Loaded /path/to/superskills/.env

📦 Shared (Multiple Skills)
--------------------------------------------------------------
  ✓ OPENAI_API_KEY    sk-abc123...def456   OpenAI (Transcriber, SummarizAIer, QuizMaker)
  🎉 All Shared credentials configured!
```

### 5. Verify `.env` is Gitignored

```bash
git status  # .env should NOT appear in the list
```

✅ If `.env` doesn't show up, you're secure!  
❌ If it does appear, check your `.gitignore` file.

---

## Understanding Credential Storage

SuperSkills supports **three ways** to store credentials (in priority order):

### 1. Environment Variables (Highest Priority)

Set by your system or Claude Desktop:

```bash
export OPENAI_API_KEY=sk-abc123...
```

**Best for:** Claude Desktop users, production deployments

### 2. Global `.env` File (Recommended)

One file at the repo root: `/superskills/.env`

**Best for:** Most users, simple setup

### 3. Per-Skill `.env` Files

Individual files per skill: `/superskills/transcriber/.env`

**Best for:** Advanced users, skill-specific credentials

---

## Credential Loading Flow

```
┌─────────────────────────────────────┐
│  1. Check Environment Variables     │ ← Claude Desktop sets these
│     (highest priority)               │
└─────────────┬───────────────────────┘
              │ Not found
              ▼
┌─────────────────────────────────────┐
│  2. Load Global .env File           │ ← Most users use this
│     /superskills/.env                │
└─────────────┬───────────────────────┘
              │ Override with per-skill
              ▼
┌─────────────────────────────────────┐
│  3. Load Per-Skill .env File        │ ← Advanced: override global
│     /superskills/{skill}/.env        │
└─────────────────────────────────────┘
```

---

## Getting API Keys

### OpenAI (Transcriber, SummarizAIer, QuizMaker)

1. Go to https://platform.openai.com/api-keys
2. Click **"Create new secret key"**
3. Name it (e.g., "SuperSkills")
4. Copy the key (starts with `sk-`)
5. Add to `.env`:
   ```bash
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

**Cost:** Pay-as-you-go (transcription ~$0.006/minute)

---

### ElevenLabs (Narrator)

**API Key:**
1. Go to https://elevenlabs.io/app/settings
2. Find "API Key" section
3. Copy your key
4. Add to `.env`:
   ```bash
   ELEVENLABS_API_KEY=your-key-here
   ```

**Voice ID:**
1. Go to https://elevenlabs.io/app/voice-library
2. Click on your voice
3. Copy the Voice ID from the URL or settings
4. Add to `.env`:
   ```bash
   ELEVENLABS_VOICE_ID=your-voice-id-here
   ```

**Cost:** Free tier available, paid plans from $5/month

---

### Google Gemini (Designer)

1. Go to https://makersuite.google.com/app/apikey
2. Click **"Create API key"**
3. Copy the key
4. Add to `.env`:
   ```bash
   GEMINI_API_KEY=your-key-here
   ```

**Cost:** Free tier available with generous limits

---

### SendGrid (EmailCampaigner)

1. Go to https://app.sendgrid.com/settings/api_keys
2. Click **"Create API Key"**
3. Choose "Full Access" or customize permissions
4. Copy the key
5. Add to `.env`:
   ```bash
   SENDGRID_API_KEY=your-key-here
   SENDGRID_FROM_EMAIL=your-verified-email@domain.com
   ```

**Important:** Verify your sender email in SendGrid first!

**Cost:** Free tier (100 emails/day), paid plans from $15/month

---

### Microsoft Graph (Planner - Outlook Calendar)

**Setup is more complex:**

1. Go to https://portal.azure.com
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **"New registration"**
4. Name: "SuperSkills Planner"
5. Supported account types: "Single tenant"
6. Click **Register**

7. **Get Client ID and Tenant ID:**
   - On the Overview page, copy:
     - Application (client) ID
     - Directory (tenant) ID

8. **Create Client Secret:**
   - Go to **Certificates & secrets**
   - Click **"New client secret"**
   - Description: "SuperSkills"
   - Expires: Choose duration
   - Click **Add**
   - **IMPORTANT:** Copy the secret VALUE immediately (you can't see it again!)

9. **Add API Permissions:**
   - Go to **API permissions**
   - Click **"Add a permission"**
   - Choose **Microsoft Graph** → **Delegated permissions**
   - Add:
     - `Calendars.ReadWrite`
     - `User.Read`
   - Click **"Grant admin consent"**

10. **Add to `.env`:**
    ```bash
    MICROSOFT_CLIENT_ID=your-client-id-here
    MICROSOFT_CLIENT_SECRET=your-client-secret-here
    MICROSOFT_TENANT_ID=your-tenant-id-here
    ```

**Cost:** Free with Microsoft 365 subscription

---

### Craft Docs (Craft)

1. Open **Craft Docs** application
2. Go to the **Imagine** tab
3. Click **"Enable API"**
4. Select which documents/spaces to grant access
5. Click **"Download AI Bundle"**
6. Extract the bundle and find the endpoint URL
7. Add to `.env`:
   ```bash
   CRAFT_API_ENDPOINT=https://api.craft.do/v1/your-endpoint-here
   ```

**Note:** API key may be included in the endpoint or provided separately.

**Cost:** Included with Craft Pro subscription

---

### Postiz (Marketer)

1. Go to https://postiz.com/settings/api
2. Click **"Generate API Key"**
3. Copy the key and workspace ID
4. Add to `.env`:
   ```bash
   POSTIZ_API_KEY=your-key-here
   POSTIZ_WORKSPACE_ID=your-workspace-id
   ```

**Cost:** Free tier available, paid plans from $29/month

---

## Per-Skill Setup

Each skill has its own `.env.template` with specific instructions.

### Example: Setting up Transcriber only

```bash
# 1. Copy skill-specific template
cp superskills/transcriber/.env.template superskills/transcriber/.env

# 2. Edit and add your OpenAI key
nano superskills/transcriber/.env

# 3. Add this line:
OPENAI_API_KEY=sk-your-actual-key-here

# 4. Test it
python3 -c "from superskills.transcriber.src import Transcriber; t = Transcriber(); print('✓ Credentials loaded!')"
```

### When to use per-skill .env files:

✅ You want to isolate credentials per skill  
✅ Different team members manage different skills  
✅ You're sharing a specific skill with different credentials  
❌ You're just starting out (use global `.env` instead)

---

## Claude Desktop Integration

Claude Desktop can manage environment variables for you!

### Setup in Claude Desktop

1. Open **Claude Desktop**
2. Go to **Settings** → **Environment Variables**
3. Add your credentials:

```
OPENAI_API_KEY = sk-your-key-here
ELEVENLABS_API_KEY = your-key-here
ELEVENLABS_VOICE_ID = your-voice-id
CRAFT_API_ENDPOINT = https://api.craft.do/v1/...
```

### How it Works

- Claude Desktop sets these as environment variables
- SuperSkills automatically uses them (highest priority)
- No `.env` file needed!
- Credentials are managed by Claude Desktop

### Benefits

✅ Centralized credential management  
✅ Secure (credentials managed by Claude)  
✅ No `.env` files to manage  
✅ Works across all Claude Desktop features

---

## Security Best Practices

### ✅ DO

1. **Use `.env` files for local development**
   ```bash
   cp .env.template .env
   ```

2. **Keep `.env` files out of git**
   ```bash
   # Already in .gitignore:
   .env
   .env.*
   !.env.template
   ```

3. **Use different keys for dev/staging/prod**
   ```bash
   # Development
   OPENAI_API_KEY=sk-dev-key...
   
   # Production
   OPENAI_API_KEY=sk-prod-key...
   ```

4. **Rotate keys regularly** (every 90 days minimum)

5. **Use environment-specific service accounts**

6. **Monitor API usage** for unexpected spikes

### ❌ DON'T

1. **Never commit `.env` files to git**
   ```bash
   # Bad!
   git add .env
   ```

2. **Never hardcode credentials in code**
   ```python
   # Bad!
   api_key = "sk-abc123..."
   ```

3. **Never share `.env` files** (even privately)

4. **Never log credentials**
   ```python
   # Bad!
   print(f"Using API key: {api_key}")
   ```

5. **Never use production keys in development**

---

## Troubleshooting

### "Credential not found" Error

```
ValueError: OPENAI_API_KEY not found.
```

**Solutions:**

1. **Check `.env` file exists:**
   ```bash
   ls -la .env
   ```

2. **Verify key name in `.env`:**
   ```bash
   cat .env | grep OPENAI_API_KEY
   ```

3. **Check for typos:**
   ```bash
   # Correct:
   OPENAI_API_KEY=sk-...
   
   # Wrong (extra space):
   OPENAI_API_KEY = sk-...
   ```

4. **Ensure no spaces around `=`:**
   ```bash
   # Correct:
   OPENAI_API_KEY=value
   
   # Wrong:
   OPENAI_API_KEY = value
   ```

---

### Credentials Not Loading

1. **Verify `python-dotenv` is installed:**
   ```bash
   pip install python-dotenv
   ```

2. **Check `.env` location** (should be at repo root):
   ```bash
   /path/to/superskills/.env  # ✓ Correct
   /path/to/superskills/superskills/.env  # ✗ Wrong location
   ```

3. **Test loading manually:**
   ```python
   from dotenv import load_dotenv
   from pathlib import Path
   
   env_file = Path.cwd() / ".env"
   print(f"Loading from: {env_file}")
   load_dotenv(env_file)
   
   import os
   print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')[:8]}...")
   ```

---

### Multiple `.env` Files Conflict

**Priority order:**
1. Environment variables (highest)
2. Global `.env`
3. Per-skill `.env`

**Example:**
```bash
# Global .env
OPENAI_API_KEY=sk-global-key...

# superskills/transcriber/.env
OPENAI_API_KEY=sk-transcriber-specific-key...

# When using Transcriber:
# Uses sk-transcriber-specific-key... (per-skill overrides global)
```

**To debug:**
```python
import os
print(f"Current OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')[:8]}...")
```

---

### API Key Not Working

1. **Verify key is valid:**
   - Check expiration date
   - Ensure it hasn't been revoked
   - Check API dashboard for status

2. **Check API limits:**
   - Free tier limits reached?
   - Rate limiting?
   - Billing issues?

3. **Test key directly:**
   ```python
   # OpenAI example
   import openai
   openai.api_key = "sk-your-key"
   response = openai.ChatCompletion.create(
       model="gpt-3.5-turbo",
       messages=[{"role": "user", "content": "Hi"}]
   )
   print(response)  # Should work if key is valid
   ```

---

### Permission Denied Errors

**Microsoft Graph (Planner):**
```
Error: insufficient permissions
```

**Solution:**
1. Go to Azure Portal → Your App → API permissions
2. Ensure `Calendars.ReadWrite` is added
3. Click **"Grant admin consent"**
4. Wait 5-10 minutes for propagation

---

### Git Shows `.env` File

```bash
$ git status
Changes not staged for commit:
  modified:   .env  # ❌ This should NOT appear!
```

**Solution:**

1. **Check `.gitignore`:**
   ```bash
   cat .gitignore | grep .env
   ```
   Should show:
   ```
   .env
   .env.*
   !.env.template
   ```

2. **If `.gitignore` is correct but still showing:**
   ```bash
   # Remove from git cache
   git rm --cached .env
   git commit -m "Remove .env from tracking"
   ```

3. **Verify:**
   ```bash
   git status  # .env should no longer appear
   ```

---

## Advanced Topics

### Using `.env` Files in Production

**Don't do this!** Use:
- Cloud secret managers (AWS Secrets Manager, Azure Key Vault)
- Environment variables set by hosting platform
- Kubernetes secrets
- CI/CD secret management

### Credential Rotation Script

```bash
#!/bin/bash
# rotate_keys.sh

echo "Rotating API keys..."

# Backup old .env
cp .env .env.backup.$(date +%Y%m%d)

# Update .env with new keys
# (You'd fetch new keys from your secret manager here)

echo "✓ Keys rotated. Backup saved to .env.backup.*"
```

### Monitoring Credential Usage

```python
# Add to your skill:
import logging

logger = logging.getLogger(__name__)

def __init__(self):
    self.api_key = get_credential("OPENAI_API_KEY")
    logger.info("API key loaded successfully")
    # Later, log API usage
    logger.info(f"API call made, tokens used: {tokens}")
```

---

## Support

### Need Help?

1. **Run validation script:**
   ```bash
   python3 scripts/validate_credentials.py
   ```

2. **Check skill README:**
   - `superskills/transcriber/README.md`
   - `superskills/craft/README.md`
   - etc.

3. **Review this guide:** `docs/CREDENTIAL_SETUP.md`

4. **Check API provider docs:**
   - OpenAI: https://platform.openai.com/docs
   - ElevenLabs: https://elevenlabs.io/docs
   - etc.

---

## Quick Reference

| Skill | Required Credentials | Where to Get |
|-------|---------------------|--------------|
| **Transcriber** | `OPENAI_API_KEY` or `ASSEMBLYAI_API_KEY` | https://platform.openai.com/api-keys |
| **Designer** | `GEMINI_API_KEY` or `MIDJOURNEY_API_KEY` | https://makersuite.google.com/app/apikey |
| **Narrator** | `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID` | https://elevenlabs.io/app/settings |
| **Marketer** | `POSTIZ_API_KEY`, `POSTIZ_WORKSPACE_ID` | https://postiz.com/settings/api |
| **Planner** | `MICROSOFT_CLIENT_ID`, `MICROSOFT_CLIENT_SECRET`, `MICROSOFT_TENANT_ID` | https://portal.azure.com |
| **EmailCampaigner** | `SENDGRID_API_KEY`, `SENDGRID_FROM_EMAIL` | https://app.sendgrid.com/settings/api_keys |
| **Craft** | `CRAFT_API_ENDPOINT` | Craft Docs → Imagine tab |
| **SummarizAIer** | `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` | https://platform.openai.com/api-keys |

---

**Last Updated:** 2024-12-07  
**Version:** 1.0.0
