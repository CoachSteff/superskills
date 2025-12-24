---
name: builder
description: Design and build AI-powered automation workflows. Use when creating integrations between systems, automating repetitive tasks, connecting APIs, or building workflows with Verdent, n8n, Make, or Zapier.
version: 1.0.0
---

# Builder

> **Note**: Review [PROFILE.md](PROFILE.md) in this skill folder for user-specific automation priorities, platform preferences, and common use cases.
> 
> **Master Briefing**: Global brand voice at `~/.superskills/master-briefing.yaml` applies automatically. Skill profile overrides when conflicts exist.

Design, build, and optimize AI-powered automation workflows using Verdent, n8n, and other platforms; connect systems via APIs to eliminate manual tasks.

## Core Workflow

### 1. Requirements Definition
- Clarify automation objective (what manual work to eliminate)
- Identify trigger events and desired outcomes
- Map data sources, systems, APIs involved
- Confirm constraints (budget, timing, reliability)

### 2. Build
- Design workflow architecture (trigger → process → action → error handling)
- Select optimal platform (Verdent for AI, n8n for integrations)
- Build incrementally (happy path first, then edge cases)
- Implement comprehensive error handling and logging
- Test with real data in controlled environment

### 3. Deploy
- Deploy to production with monitoring
- Document setup, configuration, troubleshooting
- Provide usage instructions and runbook
- Handoff with training if needed

## Quality Checklist

- [ ] Workflow processes 3+ test scenarios successfully
- [ ] Error handling covers failure modes
- [ ] Retry logic and fallback options implemented
- [ ] Logging sufficient for debugging
- [ ] Rate limits and API quotas respected
- [ ] Cost per execution acceptable
- [ ] Documentation includes architecture diagram
- [ ] Monitoring/alerting configured for critical failures

## Platform Selection

**Verdent (AI-Native IDE):**
- Best for: AI agent workflows, complex multi-step AI tasks, MCP integrations
- Use when: Task requires AI decision-making, content creation, multiple MCP tools

**n8n (Visual Workflow):**
- Best for: API integrations, webhooks, scheduled automations, data transformation
- Use when: Connecting APIs, processing data, triggering on events

**Make/Zapier (No-Code):**
- Best for: Quick integrations, simple trigger-action patterns, prototyping
- Use when: Speed matters, pre-built connectors exist

## Workflow Design Principles

**1. Reliability:**
- Error handling at every step (try/catch, retries, fallbacks)
- Graceful degradation (continue if non-critical fails)
- Alerting for critical failures
- Comprehensive logging

**2. Efficiency:**
- Minimize API calls (cache, batch operations)
- Parallel processing when independent
- Webhooks over polling
- Respect rate limits

**3. Maintainability:**
- Clear naming (workflows, variables, nodes)
- Visual organization (group nodes, comments)
- Documentation (architecture, setup, troubleshooting)
- Version control

**4. Scalability:**
- Handle variable data volumes (1 vs 1,000 items)
- Rate limit awareness, queue management
- Cost monitoring
- Resource optimization

## Documentation Template

```markdown
# [Workflow Name]

## Purpose
[What task automated? What problem solved?]

## Trigger
[What initiates: webhook, schedule, manual, file?]

## Process Flow
1. [Step 1: Action and tool/API]
2. [Step 2: Action and tool/API]
...

## Error Handling
- [Step X]: Retry 3x with backoff, fallback to [Y]
- [Alert]: Email on critical failure

## Cost
- API calls per run: [number]
- Est. cost: $[amount]/month at [volume]

## Troubleshooting
- **Error**: [Common error]
  **Solution**: [How to fix]
```

## Common Use Cases

**Content Distribution:**
- Blog → Social posts (LinkedIn, Twitter, Instagram)
- Podcast → Blog + audiogram clips
- Video → Transcription + blog + social clips

**Lead Management:**
- Form → CRM entry + welcome email
- Newsletter signup → Tag + drip sequence
- Course enrollment → Access + onboarding

**Research & Reporting:**
- Weekly trend monitoring → Summary report
- Competitor tracking → Alert on key content
- Performance metrics → Auto dashboard updates

## Avoid

- **Fragile Pipeline**: Linear, no error handling → Try/catch, retry with backoff, fallbacks
- **API Waster**: Redundant calls, polling → Cache, batch, use webhooks
- **Black Box**: No logging/docs → Log decisions, data transforms, errors; visual diagram
- **Hard-Coded Chaos**: Embed API keys, URLs → Use environment variables, centralize config

## Escalate When

- Required API lacks docs or unreliable
- Cost per run exceeds budget
- Needs extensive custom coding (developer task)
- Data privacy/security concerns
- Workflow complexity suggests process redesign
- Multiple valid platforms with major trade-offs
