# Contributing to SuperSkills

Thank you for contributing to SuperSkills!

## Development Setup

```bash
git clone https://github.com/CoachSteff/superskills.git
cd superskills
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"
cp .env.template .env  # Add your API keys
```

## Project Structure

- `/superskills/` - All skill definitions (40 skills: 29 Claude Skills + 11 Python implementations)
- `/docs/` - Documentation
- `/tests/` - Test suite
- `/template/` - Skill creation template

## Adding a New Skill

### Prompt-Only Skill
```bash
mkdir superskills/my-skill
cp template/SKILL.md superskills/my-skill/SKILL.md
cp template/PROFILE.md.template superskills/my-skill/PROFILE.md.template
# Edit SKILL.md with YAML frontmatter + instructions
```

### Python-Powered Skill
Use `superskills/narrator/` or `superskills/designer/` as reference. Required files:
- README.md, SKILL.md, PROFILE.md.template
- src/, tests/, requirements.txt, .env.template

**Example structure:**
```
superskills/narrator/
├── SKILL.md
├── PROFILE.md.template
├── README.md
├── src/
│   ├── VoiceConfig.py
│   ├── Voiceover.py
│   └── Podcast.py
├── voice_profiles.json
├── tests/
├── requirements.txt
└── .env.template
```

## Personal Profile Files

**CRITICAL SECURITY RULES:**
- ✅ Commit `PROFILE.md.template` (templates for others)
- ❌ NEVER commit `PROFILE.md` files (contain personal info)
- Already gitignored - your profiles stay local

**Template Structure:**
```markdown
# User Profile
## [Role Name]
**Name**: [Your Name/Brand]
**Role**: [Your Professional Role]
## Voice Characteristics
- [Trait]: [Description]
## Expertise Areas
- [Area 1]
```

## Credential Management

**Security First:**
- ✅ Use `.env.template` for placeholders
- ❌ NEVER commit `.env` files
- Test with `python scripts/validate_credentials.py`

## Testing

SuperSkills includes a comprehensive test suite. You can run tests in several ways:

### Quick Test (Recommended)
```bash
superskills test
```

This runs the full test suite with verbose output.

### Fast Tests Only
Skip slow integration tests for quick validation:
```bash
superskills test --quick
```

### Specific Test File
Run a single test file:
```bash
superskills test --file test_narrator.py
```

### With Coverage
Generate a coverage report:
```bash
superskills test --coverage
```

After running, open the HTML report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Traditional pytest
If you prefer using pytest directly:
```bash
pytest tests/ -v
```

### Writing Tests

All external APIs must be mocked:
```python
def test_api_call(mocker):
    mock_api = mocker.patch('requests.post')
    mock_api.return_value.json.return_value = {'success': True}
    result = my_function()
    assert result.success == True
```

### Test Requirements
- All tests must pass before submitting a PR
- New features must include corresponding tests
- Aim for >80% code coverage for new code

Run the full test suite before submitting:
```bash
superskills test --coverage
```

## Pull Request Process

1. Create feature branch
2. Write tests first (TDD)
3. Update documentation
4. Pass all tests: `superskills test`
5. Format code: `black . --line-length 100`
6. Submit PR with clear description

## Code Review Checklist
- ✅ Tests pass (`superskills test`)
- ✅ Documentation updated
- ✅ No credentials committed
- ✅ PROFILE.md files not committed
- ✅ Code formatted (black)

## Questions?

- **Bugs**: [GitHub Issues](https://github.com/CoachSteff/superskills/issues)
- **Discussions**: [GitHub Discussions](https://github.com/CoachSteff/superskills/discussions)
- **Security**: info@cs-workx.be

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
