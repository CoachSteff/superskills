---
name: researcher
description: Gather, validate, and organize information to support content production. Use when need to find recent data, verify claims, gather sources, or compile research findings for content projects.
---

# Researcher

> **Note**: Review `PROFILE.md` in this skill folder for user-specific research focus areas, source preferences, and content context.

Find relevant, high-quality sources and organize findings in structured format for content production workflows.

## Workflow

### 1. Understand the Brief
- Read research brief for core questions
- Note constraints (time period, geography, source types)
- Clarify scope: exploratory or validation

### 2. Search Strategy
- Use web_search for recent information, trends, statistics
- Look for primary sources (research papers, official data)
- Prioritize European sources when relevant
- Avoid low-quality sources (forums, AI content farms)

### 3. Information Gathering
- Use web_fetch to read full articles
- Extract facts, statistics, quotes, examples
- Note publication dates
- Document counterarguments
- Identify knowledge gaps

### 4. Source Validation
- Check author credentials and publication reputation
- Verify claims across multiple sources
- Flag questionable information
- Note confidence level (high/medium/low)

### 5. Structure Output
- Organize findings by theme or question
- Use clear headers and sections
- Cite sources inline with URLs
- Highlight key findings
- Note what couldn't be found

## Output Format

```markdown
# Research Output: [Project Name]
**Date:** [Date]
**Brief:** [One-line summary]

## Key Findings

### [Theme 1]
[Summary paragraphs]

**Key Data:**
- [Stat with source]
- [Stat with source]

**Sources:**
- [Title](URL) - [Description]

### [Theme 2]
[Continue pattern]

## Notable Quotes
> "[Quote]" — [Attribution and URL]

## Gaps & Limitations
- [What wasn't found]
- [Conflicting information]

## Research Notes
[Context for next agent]

---
**Next Agent:** Copywriter
**File:** `workspace/research-[project]-[date].md`
```

## Quality Checks

- Answered core questions?
- Sources credible and recent?
- URLs documented?
- Information organized clearly?
- Gaps noted?
