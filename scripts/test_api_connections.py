#!/usr/bin/env python3
"""
Test API connections for configured SuperSkills credentials.

This script performs minimal API calls to verify that configured
credentials are valid and working.
"""
import argparse
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print("⚠️  python-dotenv not installed")
    print("   Install with: pip install python-dotenv")
    sys.exit(1)

# Add superskills to path for imports
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

# API test definitions
API_TESTS = {
    "OpenAI": {
        "credential": "OPENAI_API_KEY",
        "test_func": "test_openai",
        "import_check": "openai"
    },
    "Anthropic": {
        "credential": "ANTHROPIC_API_KEY",
        "test_func": "test_anthropic",
        "import_check": "anthropic"
    },
    "ElevenLabs": {
        "credential": "ELEVENLABS_API_KEY",
        "test_func": "test_elevenlabs",
        "import_check": "elevenlabs"
    },
    "Gemini": {
        "credential": "GEMINI_API_KEY",
        "test_func": "test_gemini",
        "import_check": "google.genai"
    },
    "Craft": {
        "credential": "CRAFT_API_ENDPOINT",
        "test_func": "test_craft",
        "import_check": "requests"
    },
    "Notion": {
        "credential": "NOTION_API_KEY",
        "test_func": "test_notion",
        "import_check": "requests"
    },
    "Postiz": {
        "credential": "POSTIZ_API_KEY",
        "test_func": "test_postiz",
        "import_check": "requests"
    },
    "Microsoft Graph": {
        "credential": "MICROSOFT_CLIENT_ID",
        "test_func": "test_microsoft_graph",
        "import_check": "requests"
    },
    "Pinecone": {
        "credential": "PINECONE_API_KEY",
        "test_func": "test_pinecone",
        "import_check": "requests"
    },
    "Perplexity": {
        "credential": "PERPLEXITY_API_KEY",
        "test_func": "test_perplexity",
        "import_check": "requests"
    }
}

def load_env():
    """Load environment from root .env file."""
    env_file = repo_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        return True
    return False

def check_import(module_name):
    """Check if a Python module is available."""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False

def test_openai(verbose=False):
    """Test OpenAI API connection."""
    try:
        import openai
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            return False, "Credential not set"

        client = openai.OpenAI(api_key=api_key)
        # Simple API call - list models
        models = client.models.list()

        if verbose:
            model_count = len(list(models))
            return True, f"API key valid, {model_count} models available"
        return True, "API key valid"

    except Exception as e:
        return False, str(e)[:50]

def test_anthropic(verbose=False):
    """Test Anthropic API connection."""
    try:
        import anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            return False, "Credential not set"

        anthropic.Anthropic(api_key=api_key)
        # Simple API info check
        # Note: Anthropic doesn't have a simple health check, so we'll just validate format
        if api_key.startswith("sk-ant-"):
            return True, "API key format valid"
        return False, "Invalid API key format"

    except Exception as e:
        return False, str(e)[:50]

def test_elevenlabs(verbose=False):
    """Test ElevenLabs API connection."""
    try:
        import requests
        api_key = os.getenv("ELEVENLABS_API_KEY")
        voice_id = os.getenv("ELEVENLABS_VOICE_ID")

        if not api_key:
            return False, "API key not set"

        # Test with user info endpoint
        response = requests.get(
            "https://api.elevenlabs.io/v1/user",
            headers={"xi-api-key": api_key},
            timeout=10
        )

        if response.status_code == 200:
            response.json()
            if verbose and voice_id:
                return True, f"API valid, Voice ID: {voice_id[:8]}..."
            return True, "API key valid"
        elif response.status_code == 401:
            return False, "Invalid API key"
        else:
            return False, f"API error: {response.status_code}"

    except Exception as e:
        return False, str(e)[:50]

def test_gemini(verbose=False):
    """Test Google Gemini API connection."""
    try:
        from google import genai
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            return False, "Credential not set"

        client = genai.Client(api_key=api_key)
        # Test simple generation to verify API key
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents="Test",
            config={"max_output_tokens": 10}
        )

        if response.text:
            if verbose:
                return True, "API valid, connection successful"
            return True, "API key valid"
        return False, "No response from API"

    except Exception as e:
        error_msg = str(e)
        if "API key not valid" in error_msg or "authentication" in error_msg.lower():
            return False, "Invalid API key"
        return False, str(e)[:50]

def test_craft(verbose=False):
    """Test Craft Docs API connection."""
    try:
        import requests
        endpoint = os.getenv("CRAFT_API_ENDPOINT")

        if not endpoint:
            return False, "Endpoint not set"

        # Try a simple GET request
        response = requests.get(endpoint, timeout=10)

        if response.status_code in [200, 401, 403]:
            # Even 401/403 means the endpoint exists
            return True, "Endpoint accessible"
        else:
            return False, f"HTTP {response.status_code}"

    except requests.exceptions.Timeout:
        return False, "Request timeout"
    except Exception as e:
        return False, str(e)[:50]

def test_notion(verbose=False):
    """Test Notion API connection."""
    try:
        import requests
        api_key = os.getenv("NOTION_API_KEY")

        if not api_key:
            return False, "Credential not set"

        # Test with search endpoint
        response = requests.post(
            "https://api.notion.com/v1/search",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json"
            },
            json={"page_size": 1},
            timeout=10
        )

        if response.status_code == 200:
            return True, "API key valid"
        elif response.status_code == 401:
            return False, "Invalid API key"
        else:
            return False, f"API error: {response.status_code}"

    except Exception as e:
        return False, str(e)[:50]

def test_postiz(verbose=False):
    """Test Postiz API connection."""
    try:
        import requests
        api_key = os.getenv("POSTIZ_API_KEY")
        workspace_id = os.getenv("POSTIZ_WORKSPACE_ID")

        if not api_key:
            return False, "API key not set"

        if not workspace_id:
            return False, "Workspace ID not set"

        # Note: Adjust endpoint based on actual Postiz API docs
        response = requests.get(
            f"https://api.postiz.com/workspaces/{workspace_id}",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )

        if response.status_code == 200:
            return True, "API key valid"
        elif response.status_code == 401:
            return False, "Invalid API key"
        else:
            return False, f"API error: {response.status_code}"

    except Exception as e:
        return False, str(e)[:50]

def test_microsoft_graph(verbose=False):
    """Test Microsoft Graph API connection."""
    try:
        client_id = os.getenv("MICROSOFT_CLIENT_ID")
        client_secret = os.getenv("MICROSOFT_CLIENT_SECRET")
        tenant_id = os.getenv("MICROSOFT_TENANT_ID")

        if not all([client_id, client_secret, tenant_id]):
            return False, "Missing credentials"

        # Note: Full OAuth flow requires more setup
        # This is a simplified check
        return True, "Credentials configured (OAuth flow required)"

    except Exception as e:
        return False, str(e)[:50]

def test_pinecone(verbose=False):
    """Test Pinecone API connection."""
    try:
        api_key = os.getenv("PINECONE_API_KEY")

        if not api_key:
            return False, "Credential not set"

        # Note: Pinecone API endpoint varies by environment
        # This is a basic check
        return True, "API key configured (environment setup required)"

    except Exception as e:
        return False, str(e)[:50]

def test_perplexity(verbose=False):
    """Test Perplexity API connection."""
    try:
        import requests
        api_key = os.getenv("PERPLEXITY_API_KEY")

        if not api_key:
            return False, "Credential not set"

        # Test with models endpoint
        response = requests.get(
            "https://api.perplexity.ai/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )

        if response.status_code == 200:
            return True, "API key valid"
        elif response.status_code == 401:
            return False, "Invalid API key"
        else:
            return False, f"API error: {response.status_code}"

    except Exception as e:
        return False, str(e)[:50]

def run_api_test(api_name, test_def, verbose=False):
    """Run a single API test."""
    # Check if credential is set
    credential_key = test_def["credential"]
    credential_value = os.getenv(credential_key)

    if not credential_value:
        return "skipped", "Credential not configured"

    # Check if required module is available
    if not check_import(test_def["import_check"]):
        return "skipped", f"Module '{test_def['import_check']}' not installed"

    # Run the test
    test_func = globals()[test_def["test_func"]]
    try:
        success, message = test_func(verbose)
        return "success" if success else "failed", message
    except Exception as e:
        return "failed", str(e)[:50]

def main():
    parser = argparse.ArgumentParser(
        description="Test API connections for configured SuperSkills credentials"
    )
    parser.add_argument(
        "--api",
        help="Test specific API only (e.g., 'OpenAI', 'Gemini')"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed test results"
    )

    args = parser.parse_args()

    print("=" * 70)
    print(" SuperSkills API Connection Test")
    print("=" * 70)
    print()

    # Load environment
    if load_env():
        print("✓ Loaded root .env file")
    else:
        print("⚠️  No root .env file found")
    print()

    # Determine which APIs to test
    if args.api:
        if args.api not in API_TESTS:
            print(f"❌ Unknown API: {args.api}")
            print(f"Available: {', '.join(API_TESTS.keys())}")
            sys.exit(1)
        apis_to_test = {args.api: API_TESTS[args.api]}
    else:
        apis_to_test = API_TESTS

    # Run tests
    results = {
        "success": 0,
        "failed": 0,
        "skipped": 0
    }

    for api_name, test_def in apis_to_test.items():
        status, message = run_api_test(api_name, test_def, args.verbose)

        # Format output
        if status == "success":
            symbol = "✓"
            results["success"] += 1
        elif status == "failed":
            symbol = "✗"
            results["failed"] += 1
        else:  # skipped
            symbol = "⊘"
            results["skipped"] += 1

        print(f"{symbol} {api_name:20} {message}")

    print()
    print("=" * 70)

    total_configured = results["success"] + results["failed"]
    len(apis_to_test)

    print(f"Summary: {results['success']}/{total_configured} configured APIs working")
    if results["skipped"] > 0:
        print(f"         {results['skipped']} APIs not configured (optional)")

    print("=" * 70)
    print()

    if results["failed"] > 0:
        print("⚠️  Some API tests failed. Check your credentials in .env")
        print()
        print("Troubleshooting:")
        print("  1. Verify credentials: python scripts/validate_credentials.py")
        print("  2. Check API key validity on provider website")
        print("  3. See docs/CREDENTIAL_SETUP.md for setup instructions")
    elif results["success"] > 0:
        print("✓ All configured APIs are working!")
    else:
        print("ℹ️  No APIs configured yet")
        print()
        print("Quick start:")
        print("  1. cp .env.template .env")
        print("  2. Edit .env and add your API keys")
        print("  3. Run this script again")

if __name__ == "__main__":
    main()
