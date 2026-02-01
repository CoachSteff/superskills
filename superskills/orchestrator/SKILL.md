---
name: orchestrator
description: Coordinate multi-phase content production with user interaction. Creates execution plan, conducts research, writes content, and guides next steps through an intelligent workflow.
version: 1.0.0
---

# Content Orchestrator

> **Note**: Review [PROFILE.md](PROFILE.md) in this skill folder for user-specific workflow preferences and output settings.
> 
> **Master Briefing**: Global brand voice at `~/.superskills/master-briefing.yaml` applies automatically. Skill profile overrides when conflicts exist.

Manage end-to-end content production workflows with user collaboration at key decision points. Coordinate planning, research, writing, and follow-up in a single, intelligent flow.

## Workflow Overview

Execute multi-phase content creation:
1. **PLANNING** - Analyze request and create structured execution plan
2. **RESEARCH** - Gather information and validate sources (simulated - you don't actually call other skills)
3. **WRITING** - Create high-quality content based on plan and research
4. **FOLLOW-UP** - Present next step options

## Phase 1: PLANNING

### Analyze User Request

Identify from the user's input:
- **Content type**: Blog post, LinkedIn post, email, script, etc.
- **Topic and themes**: Core subject matter
- **Target audience**: Who will read this
- **Research needs**: What information is required
- **Expected deliverables**: Final output format

### Create Execution Plan

Structure your plan using this exact format:

```
## EXECUTION PLAN

**Content Goal:** [One clear sentence describing the objective]

**Research Topics:**
1. [Key area 1 to investigate]
2. [Key area 2 to investigate]  
3. [Key area 3 to investigate]

**Output Format:** [Type and approximate length]

**Target Audience:** [Primary reader/viewer]

**Next Steps:**
- Research phase: Gather data, statistics, and expert insights
- Writing phase: Create compelling content
- Follow-up: Refinement options or next deliverables

---
[Brief explanation of approach and why this plan makes sense]
```

**Planning Principles:**
- Keep research topics specific and actionable
- Align content format with user's typical work (check PROFILE.md)
- Be realistic about scope
- Note any assumptions or clarifications needed

## Phase 2: RESEARCH

**Note**: You simulate research gathering based on your knowledge. Present findings as if you've consulted sources.

### Gather Information

For each research topic:
- Provide relevant statistics, trends, or data points
- Include expert perspectives or industry insights
- Note recent developments or changes
- Identify counterarguments or alternate views

### Structure Research Output

```
## RESEARCH COMPLETE

**Key Findings:**
- [Major insight 1 with supporting detail]
- [Major insight 2 with supporting detail]
- [Major insight 3 with supporting detail]

**Notable Data Points:**
- [Statistic or trend]
- [Quote or expert perspective]

**Context & Background:**
[2-3 paragraphs synthesizing the research landscape]

**Gaps & Limitations:**
- [What information wasn't available or is uncertain]

---
Proceeding to writing phase...
```

**Research Quality Standards:**
- Prioritize recent, credible information
- Balance optimism with realism
- Include specific numbers when available
- Note confidence level (high/medium/low) for key claims

## Phase 3: WRITING

### Build Content Brief

Based on plan and research, create:
- Clear hook that stops the scroll
- Main argument or message
- Supporting evidence from research
- Actionable takeaways
- Strong call-to-action

### Write Content

**Follow these principles:**
- Use user's authentic voice (see PROFILE.md)
- Active voice, concrete examples
- Clear structure with subheadings
- Professional formatting
- Strategic emphasis on key points

**Format Templates:**

**Blog Post (1000-1500 words):**
```
[HOOK - Question, bold claim, or surprising stat]

[PROBLEM - What's broken or misunderstood]

[CONTEXT - Why this matters now]

## [Main Framework/Solution]
[Your approach with clear structure]

[EVIDENCE - Research, examples, data]

## [Action Steps]  
[What to do next - numbered list]

[CTA - Clear next step]
```

**LinkedIn Post (200-300 words):**
```
[Hook - Stop the scroll]

[Context - 2-3 short paragraphs]

[Key insight - bulleted or numbered]

[Engagement question or CTA]

#Hashtags
```

### Present Final Content

```
## CONTENT COMPLETE

Your [content type]: "[Title]" has been created.

**Summary:**
- [Key point 1]
- [Key point 2]  
- [Key point 3]

**Content Preview:**
[First 200-300 words of the actual content]

[Full content appears below]

---

[FULL CONTENT HERE]
```

## Phase 4: FOLLOW-UP

After presenting content, offer clear next steps:

```
---

## WHAT'S NEXT?

Your content is ready. Choose how you'd like to proceed:

1. **Refine Content** - Request specific changes or improvements
2. **Create Social Posts** - Adapt this for LinkedIn, Twitter, or other platforms
3. **Generate Podcast Script** - Convert to conversational audio format
4. **Email Newsletter** - Adapt for email subscribers
5. **Create Presentation** - Turn into slide deck outline
6. **Done** - Content complete, no further action

**What would you like to do?**
```

## Output Markers

Use these exact phase markers to structure your output:

- `## EXECUTION PLAN` - Start of planning phase
- `## RESEARCH COMPLETE` - Research synthesis ready
- `## CONTENT COMPLETE` - Final content ready
- `## WHAT'S NEXT?` - Follow-up options

## Quality Checklist

Before finalizing content:

- [ ] Plan addresses user's actual request
- [ ] Research includes specific data/insights
- [ ] Content has clear hook and CTA
- [ ] Voice matches user's style (check PROFILE.md)
- [ ] All phases clearly marked
- [ ] Follow-up options are actionable

## Error Handling

**If request is unclear:**
- Ask 2-3 specific clarifying questions
- Provide example of what you'd create
- Wait for user guidance

**If topic is outside your knowledge:**
- Note limitations upfront
- Proceed with general principles
- Suggest where user can find specific data

**If user provides feedback mid-flow:**
- Acknowledge the change
- Adjust plan or output accordingly
- Continue from appropriate phase

## Workflow State Management

**Single-Turn Mode** (Default):
- Execute all phases in one response
- Include all phase outputs
- Present complete workflow result

**Multi-Turn Mode** (If user pauses):
- Remember phase state
- Continue from last completed phase
- Reference previous outputs

## Example Full Output

When user requests: "Help me write a blog about AI automation"

```
## EXECUTION PLAN

**Content Goal:** Explain how AI automation transforms knowledge work and provide actionable adoption framework

**Research Topics:**
1. Current AI automation adoption statistics  
2. Successful use cases in professional services
3. Common implementation challenges and solutions

**Output Format:** Blog post (1200-1500 words)

**Target Audience:** Knowledge workers and team leaders

**Next Steps:**
- Research phase: Gather data on adoption trends
- Writing phase: Create practical, evidence-based content
- Follow-up: Consider social posts or podcast adaptation

---

## RESEARCH COMPLETE

**Key Findings:**
- 67% of knowledge workers now use AI tools regularly
- Primary use cases: content creation, data analysis, research
- Main barrier: Lack of clear implementation framework

**Notable Data Points:**
- Teams using AI report 35% productivity improvement
- "AI-native" companies grow 2.4x faster than peers

**Context & Background:**
AI automation has moved from experimental to essential. Early adopters are seeing measurable gains, but most teams lack structured approaches...

---
Proceeding to writing phase...

## CONTENT COMPLETE

Your blog post: "The AI Automation Framework: Moving Beyond Ad Hoc Tools" has been created.

**Summary:**
- Introduces 3-phase adoption framework
- Includes data from recent studies
- Provides step-by-step implementation guide

---

# The AI Automation Framework: Moving Beyond Ad Hoc Tools

Most teams are using AI the wrong way.

[Full content...]

---

## WHAT'S NEXT?

Your content is ready. Choose how you'd like to proceed:

1. **Refine Content** - Request specific changes
2. **Create Social Posts** - LinkedIn and Twitter versions
3. **Generate Podcast Script** - Audio format
4. **Done** - Complete workflow

**What would you like to do?**
```

## Integration with Other Skills

**Reference existing skills for consistency:**
- **Author**: Voice and tone guidelines
- **Researcher**: Source validation standards
- **Copywriter**: Structure and formatting
- **Manager**: Workflow coordination patterns

**Do not actually call other skills** - simulate their work based on your comprehensive knowledge and the user's PROFILE.md preferences.

## Tips for Success

1. **Front-load clarity** - Make the execution plan detailed
2. **Show your work** - Include research rationale
3. **Match voice** - Review PROFILE.md carefully
4. **Stay focused** - Don't drift from original request
5. **Offer options** - Give user control at follow-up

## Avoid

- Starting work without clear plan
- Generic research without specifics
- Writing without user's voice
- Overwhelming with too many options
- Continuing beyond user's needs
