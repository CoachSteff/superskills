# Quick Start Guide — Using Your AI Agent Team

**For:** Steff Vanhaverbeke  
**Purpose:** Get started with your multi-agent content production team

---

## Getting Started in 3 Steps

### Step 1: Copy the Manager Prompt
1. Open `agents/00-manager.md`
2. Copy the entire prompt (from "# AI Agent Team Manager" to the end)
3. Start a new Claude conversation
4. Paste the prompt

### Step 2: Give Your Request
Tell the Manager what you need. Be as specific or general as you like:

**Examples:**
- "Create a LinkedIn article about cognitive agility for L&D professionals, around 800 words"
- "I need workshop materials for teaching CRAFTER to beginners, 90 minutes"
- "Write a blog post explaining why AI adoption fails due to human factors, not technical ones"

### Step 3: Follow the Workflow
The Manager will:
1. Propose a workflow plan
2. Confirm with you before starting
3. Delegate to agents in sequence
4. Deliver final files to you

---

## Complete Worked Example

Let's walk through a real production workflow from start to finish.

### Your Request to Manager

```
I need a LinkedIn article about why cognitive agility matters more than 
technical skills in AI adoption. Target audience is L&D professionals. 
Around 800 words. Use recent data to make the case.
```

### Manager's Response

```
## Workflow Plan
We'll produce an 800-word LinkedIn article on cognitive agility for L&D professionals.

**Agents Involved:** Researcher, Analyst, Copywriter, Editor, Publisher
**Estimated Steps:** 5

**Sequence:**
1. Researcher: Find current data on AI adoption challenges and cognitive agility research
2. Analyst: Structure key arguments and create content outline
3. Copywriter: Draft article with your frameworks (CAF) and practical examples
4. Editor: Refine for LinkedIn tone and L&D audience
5. Publisher: Format for LinkedIn and create final markdown file

Ready to proceed?
```

You confirm: "Yes, proceed."

---

### Behind the Scenes: Agent Workflow

**What happens next (you don't see this, but it's helpful to understand):**

#### Stage 1: Research
Manager creates a brief for Researcher:
- Research AI adoption barriers (human vs technical)
- Find data on training investment vs outcomes
- European sources preferred
- Last 2 years data

Researcher:
- Uses web search to find McKinsey, Deloitte, Gartner reports
- Validates sources and extracts key statistics
- Documents findings in `workspace/research-ai-adoption-2024-11-13.md`
- Hands off to Analyst

#### Stage 2: Analysis
Manager briefs Analyst:
- Review research findings
- Create structure for 800-word LinkedIn article
- Target: L&D professionals
- Integrate CAF framework

Analyst:
- Identifies key themes (technical investment vs human barriers)
- Creates content outline with sections
- Recommends tone and approach
- Documents in `workspace/analysis-cognitive-agility-ld-2024-11-13.md`
- Hands off to Copywriter

#### Stage 3: Copywriting
Manager briefs Copywriter:
- Follow Analyst's outline
- Write in Steff's voice (warm, clear, practical)
- Include research data strategically
- Target: peer-to-peer tone for L&D audience

Copywriter:
- Writes full draft following structure
- Opens with the paradox stat
- Integrates CAF framework
- Keeps paragraphs short for LinkedIn
- Documents in `workspace/draft-cognitive-agility-ld-2024-11-13.md`
- Hands off to Editor

#### Stage 4: Editing
Manager briefs Editor:
- Polish for Steff's voice
- Check for jargon (eliminate)
- Verify facts and framework accuracy
- Ensure LinkedIn-appropriate tone

Editor:
- Reviews draft completely
- Tightens language, removes fluff
- Verifies CAF is correctly represented
- Ensures warm-but-professional tone
- Documents in `workspace/edited-cognitive-agility-ld-2024-11-13.md`
- Hands off to Publisher

#### Stage 5: Publishing
Manager briefs Publisher:
- Format for LinkedIn
- Create both article and post versions
- Move to outputs directory
- Prepare usage guidance

Publisher:
- Formats for LinkedIn's platform
- Optimizes line breaks for mobile
- Creates two versions (full article + shorter post)
- Moves files to `/mnt/user-data/outputs`
- Hands back to Manager

---

### Manager's Final Delivery to You

```
## Deliverables Ready

[View your LinkedIn article](computer:///mnt/user-data/outputs/cognitive-agility-linkedin-full-2024-11-13.md)

[View shorter post version](computer:///mnt/user-data/outputs/cognitive-agility-linkedin-post-2024-11-13.txt)

Article written for L&D professionals, emphasizes practical application 
of CAF framework, includes three real-world examples from recent research.

Full version: 812 words
Post version: 347 words (1,847 characters)

Want me to adjust the tone or add more specific examples?
```

You can now:
- Open the files and review
- Request revisions ("Make it more conversational")
- Use immediately ("Perfect, thanks!")

---

## Revision Example

Let's say you want changes:

**Your Request:**
```
The article feels too formal. Make it more conversational.
```

**Manager's Response:**
```
## Revision Request
Sending back to Editor with instructions to:
- Reduce formality
- Add more conversational transitions  
- Use contractions where natural
- Keep professional substance but warm tone

Should have revised version in a few minutes.
```

Manager sends the edited article back to Editor with specific revision instructions. Editor makes changes, updates the file in outputs, Manager confirms with you.

---

## Tips for Working with the Team

### Be Specific in Your Initial Request
**Vague:** "Write something about AI"  
**Better:** "Create a LinkedIn article about cognitive agility for L&D professionals, 800 words, data-driven"

Include:
- Content type (article, workshop, presentation)
- Target audience (L&D professionals, business leaders, trainers)
- Approximate length or duration
- Key frameworks to include (CAF, Superworker, CRAFTER)
- Any specific requirements (must include recent data, beginner-friendly, etc.)

### Trust the Workflow
The Manager will:
- Break your request into steps
- Show you the plan before executing
- Delegate appropriately
- Monitor quality at each handoff

You don't need to manage individual agents — that's the Manager's job.

### Request Changes Through the Manager
Don't try to talk to individual agents. Tell the Manager what needs adjustment:

**Good:**
- "Make it more conversational"
- "Add more examples"
- "Too long, cut it to 600 words"
- "This doesn't sound like me"

**The Manager will:**
- Determine which agent needs to revise
- Provide specific instructions
- Return updated deliverables

### Review the Outputs Directory
All final deliverables will be in `/mnt/user-data/outputs` with clear filenames. The Manager will provide direct links.

---

## Common Use Cases

### Blog Post Production
**Request:** "Write a blog post about [topic] for [audience]"  
**Agents Used:** Researcher → Analyst → Copywriter → Editor → Publisher  
**Deliverables:** Markdown file, SEO-optimized, ready to publish  
**Typical Time:** Full workflow

### Workshop Development
**Request:** "Create workshop materials for [topic], [duration], [audience level]"  
**Agents Used:** Researcher → Analyst → Copywriter → Editor → Publisher  
**Deliverables:** Facilitator guide (DOCX), participant worksheets (PDF), resource sheets  
**Typical Time:** Full workflow with multiple outputs

### LinkedIn Content
**Request:** "Create LinkedIn content about [topic]"  
**Agents Used:** Researcher → Analyst → Copywriter → Editor → Publisher  
**Deliverables:** Article version + post version, optimized formatting  
**Typical Time:** Full workflow

### Quick Research Summary
**Request:** "Research and summarize [topic]"  
**Agents Used:** Researcher → Analyst → Copywriter → Publisher  
**Deliverables:** Summary document  
**Typical Time:** Shorter workflow (skip Editor if internal)

### Content Adaptation
**Request:** "Take this [existing content] and adapt it for [new format/audience]"  
**Agents Used:** Analyst → Copywriter → Editor → Publisher  
**Deliverables:** Reformatted version  
**Typical Time:** Shorter workflow (skip Researcher)

---

## Troubleshooting

### "The content doesn't sound like me"
Tell the Manager: "This doesn't sound like my voice."  
→ Editor will revise with specific attention to voice standards

### "I need this simpler/more complex"
Tell the Manager: "Make this more beginner-friendly" or "This needs more depth"  
→ Manager routes to appropriate agent (Analyst for structure, Copywriter for rewrite)

### "The research missed something important"
Tell the Manager: "Can you find data on [specific aspect]?"  
→ Researcher does targeted follow-up

### "Wrong format"
Tell the Manager: "I need this as [format] instead"  
→ Publisher creates alternative format

### "This is taking too long"
The full workflow is thorough by design. For faster turnaround:
- Be very specific in initial request
- Skip research if you have information already ("Here's my research notes...")
- Use shorter formats (post vs article, summary vs full report)

---

## Advanced: Bypassing Agents

Sometimes you don't need the full workflow. Tell the Manager:

**Skip Research:**
"I have the research. Here's what I know... Just need this written as a blog post."  
→ Starts at Analyst

**Skip Analysis:**
"I have an outline. Just need someone to write it."  
→ Starts at Copywriter

**Quick Polish:**
"This draft just needs editing."  
→ Starts at Editor

The Manager will adapt the workflow to your needs.

---

## Next Steps

1. **Try a simple request** to see how the team works
2. **Review the output** and request one revision to see that process
3. **Experiment with different content types** (article, workshop, etc.)
4. **Provide feedback** on voice/tone so the team learns your preferences

The team is designed to learn your needs through iteration. The more you work with it, the better the outputs become.

---

## Questions?

The Manager is your single point of contact. Ask questions, request clarifications, and provide feedback through the Manager agent.

Start your first project by copying `agents/00-manager.md` into a new Claude conversation!

---

**Framework:** CoachSteff's CRAFTER (SuperPrompt Framework v0.1)  
**License:** CC-BY 4.0 — Attribution: Steff Vanhaverbeke (coachsteff.live)
