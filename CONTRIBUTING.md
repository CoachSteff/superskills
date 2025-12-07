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

- `/superskills/` - Claude skill definitions (.skill files + PROFILE.md.template)
- `/new-skills/` - Python-powered skills (production pattern)
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
Use `/new-skills/designer/` as reference. Required files:
- README.md, SKILL.md, PROFILE.md.template
- src/, tests/, requirements.txt, .env.template

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

All external APIs must be mocked:
```python
def test_api_call(mocker):
    mock_api = mocker.patch('requests.post')
    mock_api.return_value.json.return_value = {'success': True}
    result = my_function()
    assert result.success == True
```

Run tests: `pytest tests/ -v`

## Pull Request Process

1. Create feature branch
2. Write tests first (TDD)
3. Update documentation
4. Pass all tests: `pytest tests/ -v`
5. Format code: `black . --line-length 100`
6. Submit PR with clear description

## Code Review Checklist
- ✅ Tests pass
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
