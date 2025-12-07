# AI Agent Team — Content Production Workflow

**Created by:** Steff Vanhaverbeke (CoachSteff)  
**Framework:** CRAFTER SuperPrompt Framework v0.1  
**Purpose:** Multi-agent content production from research to publication

---

## Team Structure

This is a coordinated team of Claude Code Agents, each with specialized expertise:

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| **Manager** | Workflow coordination | User requests | Task delegation & quality oversight |
| **Researcher** | Information gathering | Research brief | Validated sources & data |
| **Analyst** | Insight synthesis | Research data | Structured analysis & outline |
| **Copywriter** | Content creation | Analysis & outline | Draft content |
| **Editor** | Quality refinement | Draft content | Polished, brand-aligned content |
| **Publisher** | Format & delivery | Edited content | Final deliverables |

---

## How to Use

### Step 1: Start with the Manager
All requests go through the **Manager Agent** (see `agents/00-manager.md`). The Manager will:
- Analyze your request
- Create a workflow plan
- Delegate to appropriate agents
- Monitor quality and handoffs
- Deliver final outputs

### Step 2: Agent Workflow
The typical flow is:
```
User Request → Manager → Researcher → Analyst → Copywriter → Editor → Publisher → Deliverable
```

Not every project needs all agents. The Manager determines the right sequence.

### Step 3: Review & Iterate
- Check deliverables in `/mnt/user-data/outputs`
- Request revisions through the Manager
- Manager sends work back to the appropriate agent

---

## Directory Structure

```
team/
├── README.md                    ← You are here
├── agents/                      ← Agent superprompts
│   ├── 00-manager.md           ← Start here
│   ├── 01-researcher.md
│   ├── 02-analyst.md
│   ├── 03-copywriter.md
│   ├── 04-editor.md
│   └── 05-publisher.md
├── workspace/                   ← Agent collaboration space
└── templates/                   ← Reusable templates
```

---

## Quick Start

1. **Copy** the Manager prompt from `agents/00-manager.md`
2. **Paste** into a new Claude conversation
3. **Give** your content production request
4. **Follow** the Manager's workflow plan
5. **Review** deliverables when complete

---

## Agent Responsibilities

### Manager (Orchestrator)
- Interprets user requests
- Creates workflow plans
- Delegates tasks to agents
- Reviews quality at each stage
- Communicates progress and blockers

### Researcher (Information Gatherer)
- Finds relevant sources and data
- Validates information accuracy
- Documents citations
- Identifies knowledge gaps
- Delivers structured research notes

### Analyst (Insight Synthesizer)
- Analyzes research findings
- Identifies patterns and themes
- Creates content structure/outline
- Defines key messages
- Delivers structured framework

### Copywriter (Content Creator)
- Transforms analysis into compelling content
- Applies appropriate frameworks (CAF, Superworker, etc.)
- Creates examples and stories
- Writes in target voice and style
- Delivers draft content

### Editor (Quality Refiner)
- Improves clarity and readability
- Ensures brand voice consistency
- Checks accuracy and logic
- Refines tone for target audience
- Delivers polished content

### Publisher (Format & Delivery)
- Formats content for target medium
- Creates final file structures
- Prepares multiple formats if needed
- Moves to output directory
- Delivers with clear documentation

---

## Principles

**Human-Centric:** Every piece of content serves human readers, not algorithms.

**Quality Over Speed:** Each agent reviews work before handoff. Bad work doesn't move forward.

**Clear Handoffs:** Every agent provides context for the next agent in the chain.

**Transparency:** The Manager keeps you informed about progress and decisions.

**Iterative:** Revisions are normal. Send work back when it needs improvement.

---

## Examples of Use Cases

- **Blog posts & articles** for LinkedIn, Medium, or websites
- **Workshop materials** including facilitator guides and worksheets
- **Training content** with exercises and examples
- **Marketing copy** for landing pages or email campaigns
- **Research reports** synthesizing multiple sources
- **Documentation** for products or processes
- **Presentation decks** with speaker notes
- **Case studies** with analysis and recommendations

---

## Notes on Claude Code Agents

Each agent operates as an independent Claude instance with its own superprompt. They don't share memory automatically, so the Manager is responsible for maintaining context across handoffs.

**Best Practices:**
- Keep each agent focused on their domain
- Use the workspace directory for agent-to-agent communication
- Final outputs always go to `/mnt/user-data/outputs`
- Be specific in your initial request to the Manager

---

**Framework:** CoachSteff's CRAFTER (SuperPrompt Framework v0.1)  
**License:** CC-BY 4.0 — Attribution: Steff Vanhaverbeke (coachsteff.live)  
**Repository:** https://github.com/coachsteff/superprompt
