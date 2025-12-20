#!/usr/bin/env python3
"""Validate credential setup for SuperSkills."""
import os
import sys
from pathlib import Path

# Add superskills to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print("⚠️  python-dotenv not installed")
    print("   Install with: pip install python-dotenv")
    print()

# Load .env if available
env_file = repo_root / ".env"
if DOTENV_AVAILABLE and env_file.exists():
    load_dotenv(env_file)
    print(f"✓ Loaded {env_file}\n")
elif not env_file.exists():
    print(f"ℹ No .env file found at {env_file}")
    print(f"  Create one by running: cp .env.template .env\n")

# Define all possible credentials by skill
CREDENTIALS = {
    "Shared (Multiple Skills)": {
        "OPENAI_API_KEY": "OpenAI (Transcriber, SummarizAIer, QuizMaker)"
    },
    "Transcriber": {
        "ASSEMBLYAI_API_KEY": "AssemblyAI (alternative to OpenAI)"
    },
    "Designer": {
        "GEMINI_API_KEY": "Google Gemini Imagen",
        "MIDJOURNEY_API_KEY": "Midjourney (alternative)"
    },
    "Narrator": {
        "ELEVENLABS_API_KEY": "ElevenLabs API",
        "ELEVENLABS_VOICE_ID": "ElevenLabs Voice ID"
    },
    "Marketer": {
        # Note: Marketer now uses Notion+n8n workflow (see superskills/marketer/SKILL.md)
        # No dedicated API credentials required - uses Notion API Key below
    },
    "Planner": {
        "MICROSOFT_CLIENT_ID": "Microsoft Azure Client ID",
        "MICROSOFT_CLIENT_SECRET": "Microsoft Azure Secret",
        "MICROSOFT_TENANT_ID": "Microsoft Azure Tenant",
        "MICROSOFT_APPLICATION_ID": "Microsoft Application ID"
    },
    "EmailCampaigner": {
        "SENDGRID_API_KEY": "SendGrid API",
        "SENDGRID_FROM_EMAIL": "Verified sender email"
    },
    "Craft": {
        "CRAFT_API_ENDPOINT": "Craft Docs endpoint",
        "CRAFT_API_KEY": "Craft API key (optional)"
    },
    "SummarizAIer": {
        "ANTHROPIC_API_KEY": "Anthropic Claude (alternative)"
    },
    "Notion": {
        "NOTION_API_KEY": "Notion API Key"
    },
    "FeedbackCollector": {
        "TYPEFORM_API_KEY": "Typeform API",
        "GOOGLE_FORMS_API_KEY": "Google Forms (alternative)"
    },
    "Invoicer": {
        "STRIPE_API_KEY": "Stripe (optional)",
        "PAYPAL_CLIENT_ID": "PayPal (optional)"
    },
    "KnowledgeBase": {
        "PINECONE_API_KEY": "Pinecone vector DB (optional)"
    }
}

print("=" * 70)
print(" SuperSkills Credential Validation")
print("=" * 70)
print()

total_found = 0
total_credentials = 0

for skill, creds in CREDENTIALS.items():
    print(f"📦 {skill}")
    print("-" * 70)
    
    # Special handling for workflow-based skills
    if not creds:
        print(f"  ℹ️  This skill uses workflow-based integration (no API keys required)")
        if skill == "Marketer":
            print(f"  📖 Uses Notion+n8n workflow - see superskills/marketer/SKILL.md")
            print(f"  🔗 Requires: Notion API Key (see 'Notion' section)")
        print()
        continue
    
    skill_found = 0
    for key, description in creds.items():
        total_credentials += 1
        value = os.getenv(key)
        
        if value:
            # Mask the value for security
            if len(value) > 12:
                masked = value[:8] + "..." + value[-4:]
            elif len(value) > 8:
                masked = value[:8] + "..."
            else:
                masked = "***"
            
            print(f"  ✓ {key:30} {masked:20} {description}")
            skill_found += 1
            total_found += 1
        else:
            print(f"  ✗ {key:30} {'NOT SET':20} {description}")
    
    if skill_found == len(creds):
        print(f"  🎉 All {skill} credentials configured!")
    elif skill_found > 0:
        print(f"  ⚠️  {len(creds) - skill_found}/{len(creds)} credentials missing")
    else:
        print(f"  ℹ️  No credentials configured (skill not in use)")
    
    print()

print("=" * 70)
print(f"Summary: {total_found}/{total_credentials} credentials configured")
print("=" * 70)
print()

if total_found == 0:
    print("🚨 No credentials found!")
    print()
    print("Quick setup:")
    print("  1. cp .env.template .env")
    print("  2. Edit .env and add your API keys")
    print("  3. Run this script again to verify")
    print()
    print("📖 See docs/CREDENTIAL_SETUP.md for detailed instructions")
    sys.exit(1)
elif total_found < total_credentials:
    print("⚠️  Some credentials are missing.")
    print()
    print("This is normal if you're not using all skills.")
    print("Only configure credentials for skills you plan to use.")
    print()
    print("📖 See docs/CREDENTIAL_SETUP.md for setup instructions")
else:
    print("🎉 All credentials configured!")
    print()
    print("You're ready to use all SuperSkills!")

print()
print("💡 Tip: You can also set credentials per-skill:")
print("   superskills/transcriber/.env")
print("   superskills/craft/.env")
print("   etc.")
print()
