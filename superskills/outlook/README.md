# Outlook Email Manager Skill

Intelligent Outlook email management via Microsoft Graph API. Read inbox, categorize messages, draft responses, and schedule emails with AI-powered assistance.

## Features

- **Read Inbox**: Fetch unread, flagged, or filtered messages
- **Categorize Emails**: Auto-categorize by priority (Urgent, Action Required, FYI, Newsletter)
- **Draft Responses**: Generate replies matching your communication style
- **Schedule Sends**: Queue emails for delayed sending
- **Search**: Find emails with Graph API query syntax

## Quick Start

### 1. Azure AD App Registration

Create an Azure AD app registration to enable Graph API access:

1. Navigate to [Azure Portal → App registrations](https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade)
2. Click **New registration**
3. Configure:
   - **Name**: SuperSkills Outlook Integration
   - **Supported account types**: Accounts in this organizational directory only
   - **Redirect URI**: Web → `http://localhost:8000`
4. Click **Register**

### 2. Generate Client Secret

1. In your app registration, go to **Certificates & secrets**
2. Click **New client secret**
3. Add description (e.g., "SuperSkills CLI")
4. Set expiration (recommended: 24 months)
5. Click **Add**
6. **Copy the secret value immediately** (it won't be shown again)

### 3. Configure API Permissions

1. Go to **API permissions**
2. Click **Add a permission** → **Microsoft Graph** → **Delegated permissions**
3. Add these permissions:
   - `Mail.Read` - Read user mailbox
   - `Mail.ReadWrite` - Create drafts and modify messages
   - `Mail.Send` - Send emails
   - `User.Read` - Read user profile
4. Click **Add permissions**
5. If required by your organization, click **Grant admin consent**

### 4. Copy Credentials

1. Go to **Overview** page
2. Copy these values:
   - **Application (client) ID**
   - **Directory (tenant) ID**
3. Along with the client secret from step 2

### 5. Configure SuperSkills

**Option 1: Global configuration (recommended)**

Add credentials to the root `.env` file:

```bash
cd /path/to/superskills
nano .env  # or vim, code, etc.
```

Add these lines:

```bash
MICROSOFT_CLIENT_ID=12345678-1234-1234-1234-123456789abc
MICROSOFT_CLIENT_SECRET=your_secret_value_here
MICROSOFT_TENANT_ID=87654321-4321-4321-4321-cba987654321
MICROSOFT_REDIRECT_URI=http://localhost:8000
```

**Option 2: Skill-specific configuration (advanced)**

For skill-specific overrides, create a local `.env`:

```bash
cd superskills/outlook
cp .env.template .env
nano .env
```

**Note:** The skill automatically uses credentials from the root `.env` file via the framework's credential cascade system. Skill-specific `.env` files are only needed for overrides.

### 6. Customize Profile (Optional)

Copy and customize your profile:

```bash
cp PROFILE.md.template PROFILE.md
```

Edit `PROFILE.md` to set:
- Communication tone
- Email signature
- Prioritization rules
- Auto-actions

### 7. Install Dependencies

```bash
poetry install --with outlook
```

Or with pip:

```bash
pip install msal requests beautifulsoup4 pyyaml python-dotenv
```

## Usage

### Read Unread Emails

```bash
superskills call outlook "Show me my 10 most recent unread emails"
```

### Categorize Inbox

```bash
superskills call outlook "Analyze and categorize my inbox"
```

### Draft Reply

```bash
superskills call outlook "Draft a professional reply to john@company.com confirming I can attend the meeting"
```

### Search Emails

```bash
superskills call outlook "Search for emails from client@domain.com about project alpha"
```

## Authentication Flow

The skill uses **Device Code Flow** for CLI authentication:

1. First run prompts you to visit a URL
2. Enter the provided code in your browser
3. Sign in with your Microsoft account
4. Token is cached in `~/.superskills/tokens/`
5. Subsequent runs use cached token (auto-refreshed)

## Troubleshooting

### "Credential not found" error

Ensure `.env` file exists in `superskills/outlook/` with valid credentials.

### "AADSTS7000215: Invalid client secret"

Client secret may have expired. Generate a new one in Azure Portal.

### "Insufficient privileges to complete the operation"

Ensure API permissions are configured and admin consent is granted (if required).

### Token refresh fails

Delete token cache and re-authenticate:

```bash
rm ~/.superskills/tokens/outlook_token.bin
superskills call outlook "read inbox"
```

## Architecture

```
OutlookClient (main orchestrator)
├── AuthManager (OAuth2 token handling)
├── OutlookConfig (profile & preferences)
└── EmailParser (content parsing)
    └── Microsoft Graph API
```

## Security

- Tokens stored in `~/.superskills/tokens/` with restricted permissions (600)
- Client secrets never committed to git
- Email content not logged in full
- All drafts require explicit confirmation before sending

## API Rate Limits

Microsoft Graph API limits:
- 10,000 requests per 10 minutes per app
- Automatic retry with exponential backoff implemented

## References

- [Microsoft Graph API Documentation](https://docs.microsoft.com/en-us/graph/overview)
- [MSAL Python Documentation](https://msal-python.readthedocs.io/)
- [Mail API Reference](https://docs.microsoft.com/en-us/graph/api/resources/mail-api-overview)

## Support

For issues or questions:
1. Check Azure AD app configuration
2. Verify API permissions and admin consent
3. Review credential setup in `.env`
4. Check SuperSkills logs for detailed errors
