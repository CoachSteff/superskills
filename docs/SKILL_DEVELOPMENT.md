# Skill Development Guide

Learn how to create custom SuperSkills.

## Skill Types

### 1. Prompt-Only Skill
**When:** Instructions/workflows without external APIs
- Fast iteration, no dependencies
- SKILL.md + PROFILE.md.template

### 2. Python-Powered Skill
**When:** API integrations, complex logic
- Full infrastructure (src/, tests/, requirements.txt)
- Testable with mocked APIs

## Creating a Prompt-Only Skill

### Quick Start
```bash
mkdir superskills/my-skill
cp template/SKILL.md superskills/my-skill/SKILL.md
cp template/PROFILE.md.template superskills/my-skill/PROFILE.md.template
```

### Edit SKILL.md
```yaml
---
name: my-skill
description: Clear description of what this skill does and when to use it
license: MIT
---

# My Skill

## Purpose
This skill helps you [objective].

## Instructions
1. [Action 1]
2. [Action 2]

## Examples
### Example 1
**Input:** [Request]
**Output:** [Expected result]
```

## Creating a Python-Powered Skill

### Reference Example
Use `/superskills/designer/` or `/superskills/narrator/` as template

### Required Files
- README.md - User documentation
- SKILL.md - Claude skill definition
- PROFILE.md.template - Profile template
- src/ - Python implementation
- tests/ - Unit tests
- requirements.txt - Dependencies
- .env.template - Credential template

### Python Implementation
```python
from dataclasses import dataclass

@dataclass
class SkillResult:
    success: bool
    data: dict
    message: str

class MySkill:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('API_KEY')
        
    def do_something(self, param: str) -> SkillResult:
        # Implementation
        return SkillResult(success=True, data={}, message="Done")
```

### Testing
```python
def test_skill(mocker):
    mock_api = mocker.patch('requests.post')
    mock_api.return_value.json.return_value = {'success': True}
    
    result = skill.do_something("test")
    assert result.success == True
```

## Best Practices

### SKILL.md
- Clear, specific description
- Concrete examples
- Quality standards
- Edge cases addressed

### PROFILE.md.template
- Role-specific placeholders
- Clear `[Your Name]` format
- Comprehensive examples

### Python Skills
- Dataclass results
- Error handling
- Type hints
- Docstrings
- Mocked tests (80%+ coverage)

## Common Patterns

### API Wrapper
```python
class APIWrapper:
    def call_api(self, endpoint, data):
        response = requests.post(
            f"{self.base_url}/{endpoint}",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=data
        )
        return response.json()
```

### Credential Loading
```python
api_key = os.getenv('API_KEY')
if not api_key:
    load_dotenv()
    api_key = os.getenv('API_KEY')
if not api_key:
    raise ValueError("API_KEY not found")
```

## Troubleshooting

### Skill Not Loading
- Check YAML syntax
- Verify `name` matches directory
- Restart Claude Desktop

### Tests Failing
- Install: `pip install pytest pytest-mock`
- Check mocks match actual API calls
- Run single test: `pytest tests/test_myskill.py::test_name -v`

## Resources

- Template: `/template/SKILL.md`
- Examples: `/superskills/designer/`, `/superskills/narrator/`, `/superskills/marketer/`
- Architecture: `/dev/ARCHITECTURE.md`
