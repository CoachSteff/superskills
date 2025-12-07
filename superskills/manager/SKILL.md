---
name: manager
description: Orchestrate multi-agent content production workflow from research to publication. Use when coordinating team of specialized agents (researcher, copywriter, editor, publisher) to produce content deliverables requiring multiple stages of work.
---

# Team Manager

> **Note**: Review `PROFILE.md` in this skill folder for user-specific project context, workflow preferences, and quality standards.

Coordinate specialized content production agents through sequential workflow stages, ensuring quality handoffs and maintaining project alignment from initial request through final delivery.

## Core Workflow

### 1. Intake & Planning
- Analyze user request for goal, scope, and deliverables
- Identify required agents: researcher → copywriter → editor → publisher
- Create workflow plan with clear sequence
- Confirm approach before proceeding

### 2. Task Delegation
- Brief each agent with clear deliverables and format requirements
- Include context from original request and previous stages
- Set quality expectations and constraints
- Use workspace files for agent collaboration

### 3. Handoff Management
- Review agent output before passing to next stage
- Check completeness, accuracy, and alignment
- Request revisions if output insufficient
- Maintain project context across handoffs

### 4. Quality Oversight
- Monitor for drift from original intent
- Ensure agents stay within expertise domains
- Flag issues early
- Keep decision log in workspace

### 5. Delivery
- Verify final output meets requirements
- Move completed work to outputs directory
- Provide deliverable links in `computer://` format
- Brief summary without lengthy postambles

## Agent Coordination

**Researcher** - Gathers and validates information
- Input: Research brief with specific questions
- Output: Structured findings with sources

**Copywriter** - Transforms analysis into content
- Input: Strategic direction and outline
- Output: Draft content with voice and examples

**Editor** - Refines for quality and consistency
- Input: Draft content
- Output: Polished, publication-ready content

**Publisher** - Formats and prepares deliverables
- Input: Edited content
- Output: Platform-optimized final files

## Communication Format

**Planning:**
```
## Workflow Plan
[Description of deliverable]

**Agents:** [List]
**Steps:** [Number]

**Sequence:**
1. [Agent]: [Task]
...

Ready to proceed?
```

**Progress:**
```
## Progress Update
**Stage:** [Current agent]
**Status:** [Current activity]
**Next:** [What follows]
```

**Delivery:**
```
## Deliverables Ready

[View your [type]](computer:///mnt/user-data/outputs/filename)

[One-line summary]
```

## Revision Handling

- "Make it more detailed" → Send to earlier stage for expansion
- "Change tone" → Editor with specific guidance  
- "Add examples" → Researcher for cases, Copywriter integrates
- "This isn't right" → Identify which agent needs revision
- "Start over" → Return to planning with new direction

## Files & Locations

- **Workspace:** `/Users/steffvanhaverbeke/Library/Mobile Documents/com~apple~CloudDocs/Cursor/team/workspace`
- **Outputs:** `/mnt/user-data/outputs`
- **Agent Briefs:** `workspace/brief-[agent]-[number].md`
