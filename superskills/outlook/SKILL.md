---
name: outlook
description: Intelligent Outlook email management via Microsoft Graph API. Read inbox, categorize messages, draft responses, and schedule emails with AI-powered assistance.
version: 1.0.0
---

# Outlook Email Manager

> **Note**: Review [PROFILE.md](PROFILE.md) for user-specific communication preferences, signature, and mailbox management settings.
> 
> **Master Briefing**: Global brand voice at `~/.superskills/master-briefing.yaml` applies automatically.

Manage your Outlook mailbox intelligently: read emails, categorize by priority, draft responses in your voice, and schedule sends.

## Tools

**OutlookClient.py** (in src/):
- Microsoft Graph API integration
- OAuth2 authentication with MSAL
- Token caching and refresh
- Mailbox operations (read, send, draft, categorize)
- Error handling and retry logic

**EmailParser.py** (in src/):
- Parse email bodies (HTML/plain text)
- Extract attachments metadata
- Identify action items and key information
- Summarize long email threads

**OutlookConfig.py** (in src/):
- Load user profile (PROFILE.md)
- Manage communication preferences
- Signature injection
- Mailbox folder mappings

**AuthManager.py** (in src/):
- MSAL OAuth2 flow handler
- Token acquisition and refresh
- Secure token cache storage
- Credential validation

## Core Workflow

### 1. Authentication
- Load credentials from .env (CLIENT_ID, CLIENT_SECRET, TENANT_ID)
- Acquire OAuth2 token via MSAL
- Cache token for reuse (stored in ~/.superskills/tokens/)
- Auto-refresh on expiration

### 2. Read Inbox
- Query Microsoft Graph API for inbox messages
- Filter by unread, flagged, or specific sender
- Parse email metadata (from, subject, timestamp)
- Extract body content (HTML → plain text conversion)

### 3. Categorize Messages
- Analyze email content for priority signals
- Apply categories: Urgent / Action Required / FYI / Newsletter
- Flag important messages
- Optional: Move to folders based on rules

### 4. Draft Responses
- Load user communication profile
- Generate response draft matching user tone
- Inject signature from profile
- Save to Drafts folder (never auto-send)

### 5. Schedule Sends
- Queue draft for delayed sending
- Use Graph API's `SingleValueExtendedProperties` for schedule
- Confirm scheduled time with user

## Usage Examples

**Read Unread Messages:**
```python
from superskills.outlook.src import OutlookClient

client = OutlookClient()
messages = client.read_inbox(filter="unread", limit=10)

for msg in messages:
    print(f"{msg['from']}: {msg['subject']}")
```

**Draft Response:**
```python
client = OutlookClient()
draft = client.draft_reply(
    message_id="AAMkAG...",
    content="Thanks for reaching out...",
    tone="professional"
)
print(f"Draft saved: {draft['id']}")
```

**Categorize Inbox:**
```python
client = OutlookClient()
results = client.categorize_inbox(limit=20)
print(f"Urgent: {results['urgent_count']}")
print(f"Action Required: {results['action_count']}")
```

## Configuration

**Required Credentials (.env or environment):**
- `MICROSOFT_CLIENT_ID` - Azure AD App Client ID (or `MICROSOFT_APPLICATION_ID`)
- `MICROSOFT_CLIENT_SECRET` - Azure AD App Secret
- `MICROSOFT_TENANT_ID` - Azure AD Tenant ID
- `MICROSOFT_REDIRECT_URI` - OAuth redirect (default: http://localhost:8000)

**User Profile (PROFILE.md):**
- Communication tone (professional/casual/concise)
- Email signature
- Mailbox management preferences
- Auto-archive settings

## Quality Checklist

When processing user requests:
- ✓ Load user profile for tone and signature preferences
- ✓ Never auto-send emails (always save as draft)
- ✓ Validate credentials before API operations
- ✓ Handle token refresh gracefully
- ✓ Sanitize HTML content for security
- ✓ Respect rate limits and implement retry logic
- ✓ Provide clear confirmation messages
- ✓ Log operations without exposing email content

## Error Handling

- Missing credentials: Show helpful setup message
- Token expired: Auto-refresh transparently
- API rate limit: Retry with exponential backoff
- Network failure: Show clear error with retry option
- Invalid message ID: Validate before API call

## Security Notes

- Tokens stored in `~/.superskills/tokens/` with restricted permissions
- Email content never logged in full
- All drafts require explicit user confirmation before sending
- OAuth flow follows Microsoft security best practices
