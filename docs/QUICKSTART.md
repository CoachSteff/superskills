# SuperSkills Quick Start

Get started with SuperSkills in 5 minutes.

## Prerequisites

- Python 3.9+
- Claude Desktop App
- Git

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/CoachSteff/superskills.git
cd superskills
```

### 2. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
```

### 3. Configure Credentials
```bash
cp .env.template .env
# Edit .env and add your API keys
```

**Minimum required:**
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. Set Up Personal Profiles (Optional)
```bash
# For each skill you plan to use:
cp superskills/author/PROFILE.md.template superskills/author/PROFILE.md
# Edit with your brand voice and expertise
```

### 5. Verify Installation
```bash
python scripts/validate_credentials.py
pytest tests/ -v
```

## Using Your First Skill

### Example 1: Author Skill
In Claude Desktop, ask:
> "Using the author skill, write a 500-word blog post about AI adoption"

### Example 2: Transcriber Skill
In Claude Desktop, ask:
> "Transcribe audio.mp3 using Whisper and create a summary"

### Example 3: Designer Skill
In Claude Desktop, ask:
> "Generate a professional image of a sunset using the designer skill"

## Next Steps

- **Explore Skills**: Browse `/superskills/` and `/new-skills/`
- **Configure More**: Add API keys in `.env` (see [CREDENTIAL_SETUP.md](CREDENTIAL_SETUP.md))
- **Customize**: Create PROFILE.md files for personalization
- **Create Custom Skills**: Read [SKILL_DEVELOPMENT.md](SKILL_DEVELOPMENT.md)

## Common Issues

### "Module not found"
```bash
pip install -e .
```

### "API Key not found"
```bash
# Check .env exists
cat .env
# Verify key is set
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OK' if os.getenv('OPENAI_API_KEY') else 'NOT SET')"
```

### Tests Failing
```bash
pip install -e ".[dev]"
pytest tests/test_designer.py -v
```

## Resources

- [Full Documentation](../README.md)
- [Credential Setup](CREDENTIAL_SETUP.md)
- [Architecture](../ARCHITECTURE.md)
- [Contributing](../CONTRIBUTING.md)
