---
name: template-skill
description: Replace with clear description of what the skill does and when Claude should use it. Be specific about the skill's purpose, capabilities, and ideal use cases.
license: MIT
---

# [Skill Name]

[Brief introduction explaining what this skill does and why it's useful]

## Purpose

This skill helps you [primary objective]. Use it when you need to [specific scenarios].

## Instructions

When activated, this skill will:

1. [First action or capability]
2. [Second action or capability]
3. [Third action or capability]

### Key Guidelines

- **[Guideline Category 1]**: [Specific guidance - e.g., "Voice and Tone: Match the user's brand voice from PROFILE.md"]
- **[Guideline Category 2]**: [Specific guidance - e.g., "Quality Standards: Ensure accuracy, clarity, and actionability"]
- **[Guideline Category 3]**: [Specific guidance - e.g., "Format: Use clear structure with headings and bullet points"]

### Quality Standards

- [Standard 1 - e.g., "Accurate and fact-checked information"]
- [Standard 2 - e.g., "Clear, actionable guidance"]
- [Standard 3 - e.g., "Consistent with brand voice and style"]
- [Standard 4 - e.g., "Appropriate depth and detail for audience"]

## Examples

### Example 1: [Use Case Name]
**Input:** [Example input or request]  
**Expected Output:** [Description of expected output or behavior]

**Example:**
```
[Show concrete example of output if applicable]
```

### Example 2: [Use Case Name]
**Input:** [Example input or request]  
**Expected Output:** [Description of expected output or behavior]

**Example:**
```
[Show concrete example of output if applicable]
```

### Example 3: [Use Case Name - Edge Case or Advanced Usage]
**Input:** [Example input or request]  
**Expected Output:** [Description of expected output or behavior]

## Tools & Integrations

[If this skill uses Python tools, API integrations, or external services, document them here]

**Required:**
- [Tool/service 1 - e.g., "OpenAI API for text generation"]
- [Tool/service 2 - e.g., "Notion API for content storage"]

**Optional:**
- [Tool/service 3 - e.g., "ElevenLabs for voice synthesis"]

## Configuration

[If the skill requires configuration, environment variables, or API keys, document setup here]

### Environment Variables

```bash
# Example .env configuration
SKILL_API_KEY=your_api_key_here
SKILL_CONFIG_OPTION=value
SKILL_ENDPOINT=https://api.example.com
```

### Setup Instructions

1. Copy `.env.template` to `.env` in this skill directory
2. Add your API credentials to `.env`
3. [Additional setup steps if needed]
4. Verify setup with: `python scripts/validate_credentials.py`

## User Profile Integration

This skill loads your personal profile from `PROFILE.md` in the same directory.

**Setup:**
1. Copy `PROFILE.md.template` to `PROFILE.md`
2. Fill in your information (name, role, voice characteristics, expertise)
3. The skill will automatically match your brand voice and context

**What the skill uses from your profile:**
- [Element 1 - e.g., "Voice characteristics to match your writing style"]
- [Element 2 - e.g., "Expertise areas to tailor recommendations"]
- [Element 3 - e.g., "Example hooks to understand your communication patterns"]

## Tips & Best Practices

- **Tip 1**: [Helpful usage tip - e.g., "Be specific in your requests - include target audience, tone, and desired length"]
- **Tip 2**: [Common pitfall to avoid - e.g., "Don't ask for generic content - reference your PROFILE.md for personalization"]
- **Tip 3**: [Best practice - e.g., "Review and edit outputs - AI is a co-creator, not a replacement"]
- **Tip 4**: [Optimization tip - e.g., "For complex requests, break into steps and iterate"]

## Common Issues & Troubleshooting

### Issue: [Common Problem]
**Symptom**: [What the user experiences]  
**Solution**: [How to fix it]

### Issue: [Common Problem]
**Symptom**: [What the user experiences]  
**Solution**: [How to fix it]

## Related Skills

**Skills that work well together:**
- **[Related Skill 1]**: [When to use instead/together - e.g., "Use researcher skill first to gather information, then this skill to synthesize"]
- **[Related Skill 2]**: [When to use instead/together - e.g., "Pair with editor skill for quality control"]
- **[Related Skill 3]**: [When to use instead/together]

## Limitations

[Be honest about what this skill cannot do]

- [Limitation 1 - e.g., "Cannot access real-time data without API integration"]
- [Limitation 2 - e.g., "Requires manual review for factual accuracy"]
- [Limitation 3 - e.g., "Works best for [specific use case], less effective for [other use case]"]

## Version History

**Current Version**: 1.0.0

- **v1.0.0** - [Date] - Initial release
  - [Feature 1]
  - [Feature 2]

## Credits & Attribution

[If this skill is based on external work, frameworks, or methodologies, provide attribution]

- Based on: [Framework/methodology name]
- Inspired by: [Person/organization]
- License: [License type - e.g., MIT, Apache 2.0]

## Support & Feedback

- **Issues**: Report bugs or request features at [GitHub issues link]
- **Documentation**: [Link to extended documentation if available]
- **Community**: [Link to discussions or community forum]
