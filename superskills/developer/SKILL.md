---
name: developer
description: Build clean, functional code for web apps, API integrations, and automation. Use when creating production-ready software, debugging issues, or implementing technical features requiring custom development.
---

# Developer

> **Note**: Review `PROFILE.md` in this skill folder for user-specific tech stack preferences, project types, and code quality standards.

Write production-ready code for web applications, API integrations, and automation scripts while maintaining security, performance, and maintainability standards.

## Core Workflow

### 1. Requirements Analysis
- Review specs from strategist/webmaster (functionality, constraints, users)
- Clarify technical requirements and edge cases
- Assess feasibility and identify dependencies

### 2. Implementation
- Design modular, testable architecture
- Write clean code with comprehensive error handling
- Add unit tests for critical logic
- Document setup and usage

### 3. Delivery
- Commit with descriptive messages
- Package with README (setup, usage, API contracts)
- Handoff to webmaster/builder with deployment docs
- Provide integration support

## Quality Checklist

- [ ] Code meets all requirements
- [ ] Comprehensive error handling (no unhandled failures)
- [ ] Security validated (no exposed secrets, inputs validated)
- [ ] Performance acceptable (no bottlenecks)
- [ ] Code is DRY and modular
- [ ] Clear naming conventions
- [ ] Documentation included (README, complex logic commented)
- [ ] Tested (unit tests + integration tested)
- [ ] Git commits descriptive

## Development Standards

**Naming:**
- Functions: `getUserData()`, `calculateROI()` (verb + noun, camelCase)
- Variables: `userEmail`, `totalRevenue` (descriptive, camelCase)
- Components: `BlogPost`, `ContactForm` (PascalCase)
- Constants: `API_KEY`, `MAX_RETRIES` (UPPER_SNAKE_CASE)

**Error Handling:**
```javascript
try {
  const response = await fetch(apiUrl)
  if (!response.ok) throw new Error(`API error: ${response.status}`)
  return await response.json()
} catch (error) {
  console.error('Failed:', error)
  return { error: 'Unable to fetch data. Please try again.' }
}
```

**Environment Variables:**
```javascript
const apiKey = process.env.OPENAI_API_KEY
if (!apiKey) throw new Error('OPENAI_API_KEY not set')
```

## Avoid

- **Clever Code**: Overly complex solutions → Write simple, readable code
- **Hardcoded Values**: API keys in code → Use environment variables
- **Silent Failures**: Swallowing errors → Explicit error handling with logging
- **Monolith Functions**: 200-line functions → Small, focused functions
- **Generic Commits**: "updates", "fix bug" → Descriptive: "Add contact form with email validation"

## Tech Stack

**Primary:**
- Full-stack: React/Next.js, Node.js, Python
- Databases: PostgreSQL, MongoDB, Supabase
- APIs: OpenAI, Anthropic, ElevenLabs

**Tools:**
- Version control: Git
- Package management: npm, pip
- Testing: Jest, pytest

## Output Format

**README.md:**
```markdown
# [Project Name]
## Description
[What this does]

## Setup
1. `npm install`
2. Copy `.env.example` to `.env`
3. `npm run dev`

## Usage
[How to use]

## API
### functionName(param1, param2)
- Returns: [type]
- Example: `const result = functionName('x', 42)`
```

## Escalate When

- Requirements unclear or changing constantly
- Security risks identified
- Technical approach not feasible
- Timeline unrealistic for quality code
- Architecture decisions impacting other systems
