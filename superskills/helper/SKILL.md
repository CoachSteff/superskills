---
name: helper
description: SuperSkills expert assistant for usage guidance, setup, profile creation, workflow design, and troubleshooting. Use when users need help understanding commands, configuring SuperSkills, creating profiles, or solving problems.
---

# SuperSkills Helper

Your expert guide for everything SuperSkills - from first setup to advanced workflow design.

## Overview

The Helper skill is your go-to resource for:
- Understanding CLI commands and options
- Setting up API keys and configuration
- Creating and customizing PROFILE.md files
- Designing and debugging workflows
- Troubleshooting common issues
- Discovering the right skill for your task

Use this skill when users ask "how-to" questions, need setup guidance, want to understand SuperSkills features, or encounter problems.

## Core Capabilities

### 1. Usage Guidance
Explain CLI commands, options, and best practices for using SuperSkills effectively.

### 2. Setup Assistance
Guide users through installation, API key configuration, environment setup, and initialization.

### 3. Profile Creation
Help users create customized PROFILE.md files for skills that support personalization (voice, tone, brand, audience).

### 4. Workflow Design
Assist with designing, structuring, and validating YAML workflow definitions.

### 5. Troubleshooting
Diagnose and resolve common errors, configuration issues, and skill execution problems.

## Core Workflow

### 1. Understand the Request
- Identify which help category applies (usage, setup, profile, workflow, troubleshooting)
- Clarify the user's current context and goal
- Determine their experience level with SuperSkills

**Questions to Consider:**
- What is the user trying to accomplish?
- What have they already tried?
- Are they brand new or experienced with SuperSkills?
- Is this a conceptual question or a specific error?

### 2. Gather Context
- Ask relevant clarifying questions if needed
- Understand what the user has already attempted
- Identify specific blockers or pain points
- Check what's already configured (if troubleshooting)

**Context Checklist:**
- [ ] User's goal is clear
- [ ] Current setup status known
- [ ] Specific error messages captured (if applicable)
- [ ] Relevant skill or workflow identified

### 3. Provide Guidance
Deliver clear, actionable guidance tailored to the user's needs:

**For Conceptual Questions:**
- Explain the concept in simple, jargon-free language
- Use analogies when helpful
- Connect to what they already know

**For How-To Questions:**
- Provide step-by-step instructions
- Include exact commands with options
- Show expected output
- Explain what each step does

**For Troubleshooting:**
- Diagnose the root cause
- Explain why the error occurred
- Provide the fix with verification steps
- Suggest prevention strategies

**Always Include:**
- Specific file paths (use absolute paths)
- Exact commands to run
- Expected results
- Relevant examples

### 4. Validate Understanding
- Summarize the key points
- Provide verification steps the user can run
- Ask if anything is unclear
- Check if the solution addresses their goal

**Verification Examples:**
```bash
# After setup guidance
superskills status

# After skill creation
superskills validate

# After workflow design
superskills workflow validate {workflow-name}
```

### 5. Provide Follow-up Resources
- Link to related skills that might help
- Suggest logical next steps
- Offer additional help if needed
- Reference relevant documentation sections

## Knowledge Base

### CLI Commands Reference

#### Core Commands

**`superskills init`**
- Purpose: Initialize SuperSkills CLI and create config directory
- Creates: `~/.superskills/` directory with `config.yaml`
- Run: After installation, before first use

**`superskills list`**
- Purpose: List all available skills with descriptions
- Output: Shows 46 skills (30 prompt-based, 15+ Python-powered)
- Useful: Discovering what skills exist

**`superskills show {skill}`**
- Purpose: Display detailed information about a specific skill
- Shows: First 30 lines of SKILL.md, PROFILE status, Python module info
- Example: `superskills show researcher`

**`superskills call {skill} {input}`**
- Purpose: Execute a single skill with input
- Formats: `--format plain|json|yaml|markdown`
- Example: `superskills call researcher "AI automation trends"`

**`superskills run {workflow}`**
- Purpose: Execute a multi-step workflow
- Options: `--watch`, `--batch`, `--dry-run`, `--input`, `--topic`
- Example: `superskills run content-creation --topic "AI testing"`

**`superskills status`**
- Purpose: Check CLI configuration and API key status
- Shows: Skills count, workflows available, API keys configured
- Use: Verify setup is complete

**`superskills validate`**
- Purpose: Verify all skills have proper structure
- Checks: SKILL.md files, frontmatter, Python modules, templates
- Returns: Count of valid skills by type

**`superskills workflow list`**
- Purpose: List all available workflows
- Shows: Built-in and custom workflows
- Location: `workflows/` directory

**`superskills workflow validate {name}`**
- Purpose: Validate workflow YAML against schema
- Checks: Syntax, skill references, variables, dependencies
- Example: `superskills workflow validate podcast-generation`

**`superskills config get`**
- Purpose: Display current configuration
- Shows: API settings, intent parser, search paths, output options

**`superskills config set {key} {value}`**
- Purpose: Update configuration value
- Example: `superskills config set api.anthropic.model claude-sonnet-4-20250514`

**`superskills discover --query {text}`**
- Purpose: Search skills by capability, name, or description
- Ranking: Scores based on relevance and synonym matching
- Example: `superskills discover --query "video editing"`

**`superskills prompt {query}`**
- Purpose: Natural language interface to SuperSkills
- Routes: Automatically interprets intent and executes appropriate command
- Example: `superskills prompt "find skills for podcasting"`

**`superskills export {skill}`**
- Purpose: Export skill metadata in JSON format
- Use: IDE integration, programmatic access

### Configuration System

#### Config File Location
`~/.superskills/config.yaml`

#### Key Configuration Sections

**API Settings:**
```yaml
api:
  anthropic:
    model: 'claude-3-sonnet-latest'
    max_tokens: 4000
    temperature: 0.7
```

**Intent Parser:**
```yaml
intent:
  enabled: true
  provider: 'gemini'
  model: 'gemini-2.0-flash-exp'
  confidence_threshold: 0.5
  always_confirm_medium: true
```

**Search Paths:**
```yaml
search:
  paths:
    - '${OBSIDIAN_VAULT_PATH}'
    - '~/Documents'
    - '~/Downloads'
    - '.'
  use_ripgrep: true
  max_results: 50
```

**Output Options:**
```yaml
output:
  default_format: 'markdown'
  save_intermediates: true
```

**Workflows:**
```yaml
workflows:
  auto_save: true
  show_progress: true
```

#### Environment Variables

**Required API Keys:**
- `ANTHROPIC_API_KEY` - Primary LLM provider (Claude models)
- `ELEVENLABS_API_KEY` - Voice generation (narrator skills)
- `OPENAI_API_KEY` - Alternative LLM, transcription (Whisper)
- `GEMINI_API_KEY` - Intent parsing, alternative LLM

**Precedence Order (highest to lowest):**
1. System environment variables
2. Skill-specific `.env` file
3. User config `.env` (`~/.superskills/.env`)
4. Project root `.env`

### Skill System

#### Skill Types

**Prompt-Based Skills (30)**
- Use Claude's instruction-following capabilities
- Defined entirely in SKILL.md
- Support PROFILE.md customization
- Examples: researcher, copywriter, author, strategist, editor

**Python-Powered Skills (15+)**
- Include Python implementation in `src/` directory
- Integrate with external APIs and tools
- Examples: narrator, scraper, transcriber, videoeditor

#### Skill Structure

**Required:**
- `SKILL.md` - Skill definition with YAML frontmatter

**Optional:**
- `PROFILE.md.template` - Customization template for prompt skills
- `PROFILE.md` - User's personalized profile (gitignored)
- `config/` - Skill-specific configuration files
- `src/` - Python implementation (for Python skills)
- `.env.template` - Environment variable guide
- `assets/`, `references/`, `scripts/` - Supporting files

#### SKILL.md Format

**Frontmatter (YAML):**
```yaml
---
name: skill-name
description: One-line description of what the skill does
---
```

**Body (Markdown):**
- H1 title
- Overview/purpose
- Tools available (if applicable)
- Core workflow (numbered steps)
- Usage examples
- Environment variables (if applicable)
- Quality checklist

#### PROFILE.md Purpose

Customizes how skills interpret and respond to your unique context:

**Common Sections:**
- Author/business information
- Brand voice and tone guidelines
- Target audience definitions
- Key messaging and positioning
- Style preferences

**Skills That Use Profiles:**
- copywriter, author, editor (content creation)
- coach, strategist (consulting)
- marketer, influencer (marketing)

**How to Create:**
1. Copy template: `cp superskills/{skill}/PROFILE.md.template superskills/{skill}/PROFILE.md`
2. Edit with your information
3. Verify: `superskills show {skill}` (should show "✓ PROFILE.md customized")

### Workflow System

#### Workflow Definition Format (YAML)

```yaml
name: workflow-name
description: What this workflow accomplishes

variables:
  topic: ${input}

steps:
  - name: step-identifier
    skill: skill-name
    input: ${variable_or_text}
    output: variable_name
    config:
      option: value
```

#### Variable Reference Syntax
- Input variable: `${input}`
- Step output: `${step_output_name}`
- Workflow variable: `${topic}`
- Nested: `${parent.child}`

#### Workflow Locations

**Built-in Workflows:**
`workflows/definitions/` - Included with SuperSkills

**Custom Workflows:**
`workflows/custom/` - Your personal workflows

**Templates:**
`workflows_templates/` - Copy to create personal workflows

**Folder-Based:**
```
workflows/{workflow-name}/
├── workflow.yaml
├── input/
└── output/
```

#### Workflow Modes

**Watch Mode:**
```bash
superskills run {workflow} --watch
```
Continuously monitors input directory, processes new files automatically.

**Batch Mode:**
```bash
superskills run {workflow} --batch
```
Processes all files in input directory at once.

**Dry Run:**
```bash
superskills run {workflow} --dry-run
```
Estimates token usage and cost without executing.

### Common Troubleshooting

#### Issue: Model 404 Error
**Symptom:** `Error: Model 'claude-3-sonnet-latest' not available`

**Cause:** Configured model name doesn't match current Anthropic API models.

**Solution:**
1. Check current config: `superskills config get`
2. Update model: `superskills config set api.anthropic.model claude-sonnet-4-20250514`
3. Verify: `superskills call researcher "test"`

**Note:** v2.2.1+ includes automatic fallback to `claude-sonnet-4-20250514`.

#### Issue: Missing API Keys
**Symptom:** `Error: ANTHROPIC_API_KEY not found`

**Solutions:**

**Option 1: Environment Variables**
```bash
export ANTHROPIC_API_KEY=sk-ant-...
export ELEVENLABS_API_KEY=...
```

**Option 2: .env File (Project Root)**
```bash
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
echo "ELEVENLABS_API_KEY=..." >> .env
```

**Option 3: User Config .env**
```bash
echo "ANTHROPIC_API_KEY=sk-ant-..." > ~/.superskills/.env
```

**Verify:**
```bash
superskills status
```

#### Issue: Skill Not Found
**Symptom:** `Error: Skill 'skillname' not found`

**Diagnosis:**
```bash
superskills list | grep skillname
superskills validate
```

**Common Causes:**
- Typo in skill name
- Skill directory missing SKILL.md
- YAML frontmatter invalid

**Solution:**
- Check exact spelling: `superskills list`
- Validate structure: `superskills validate`

#### Issue: Workflow Validation Failed
**Symptom:** `Workflow validation failed: ...`

**Common Errors:**

**Undefined Variable:**
```
Step 2: Undefined variable '${topic}' in input
```
**Solution:** Define in `variables:` section or previous step's `output:`

**Skill Not Found:**
```
Step 1: Skill 'researcher-pro' not found
```
**Solution:** Check skill name: `superskills list`

**Invalid YAML:**
```
YAML syntax error at line 5
```
**Solution:** Validate YAML syntax (indentation, colons, quotes)

**Validation Command:**
```bash
superskills workflow validate {workflow-name}
```

#### Issue: PROFILE.md Not Loading
**Symptom:** Skill doesn't use custom voice/style

**Diagnosis:**
```bash
superskills show {skill}
```

**Expected Output:**
- `✓ PROFILE.md customized` (if custom profile exists)
- `⚠ Using PROFILE.md.template` (if not customized)

**Solution:**
1. Check file exists: `ls superskills/{skill}/PROFILE.md`
2. If not: `cp superskills/{skill}/PROFILE.md.template superskills/{skill}/PROFILE.md`
3. Edit with your information
4. Verify: `superskills show {skill}`

#### Issue: Workflow Not Found
**Symptom:** `Error: Workflow 'name' not found`

**Check Locations:**
```bash
ls workflows/definitions/
ls workflows/custom/
ls workflows/*/workflow.yaml
```

**Solution:**
- Copy from templates: `cp -r workflows_templates/{name} workflows/`
- Create custom: Create `workflows/custom/{name}.yaml`
- Verify: `superskills workflow list`

## Output Format Templates

### Usage Guidance Response

```markdown
## Command: {command_name}

**Purpose:** {brief description of what it does}

**Syntax:**
{command} [options] [arguments]

**Options:**
{list relevant options with descriptions}

**Examples:**

1. Basic usage:
   $ {example command}
   {expected output}

2. Advanced usage:
   $ {example with options}
   {expected output}

**Common Use Cases:**
- {scenario 1}
- {scenario 2}

**Related Commands:**
- {related command}: {brief description}

**Next Steps:**
{suggested follow-up actions}
```

### Setup Guidance Response

```markdown
## Setup: {topic}

**Current Status:**
{what's already configured / what's missing}

**Steps:**

1. {Action description}
   ```bash
   {exact command}
   ```
   {explanation of what this does}

2. {Next action}
   ```bash
   {exact command}
   ```
   {explanation}

3. {Verification step}
   ```bash
   {verification command}
   ```
   **Expected:** {what you should see}

**Verification:**

Run this to confirm:
```bash
{comprehensive verification command}
```

You should see:
{expected output description}

**Troubleshooting:**

If you see {error}, it means {diagnosis}:
- Solution: {fix}

**Next Steps:**
{what to do after setup complete}
```

### Profile Creation Response

```markdown
## Creating PROFILE.md for {skill}

**Purpose:**
{explain why this skill uses profiles and what it enables}

**Questions to Answer:**

Before creating your profile, gather this information:

1. {Question about voice/brand}
   Example: {example answer}

2. {Question about audience}
   Example: {example answer}

3. {Question about style preferences}
   Example: {example answer}

**Template Structure:**

Your PROFILE.md should include:

```markdown
# {Section Name}
{description of what goes here}

# {Section Name}
{description}
```

**Step-by-Step:**

1. Copy the template:
   ```bash
   cp superskills/{skill}/PROFILE.md.template superskills/{skill}/PROFILE.md
   ```

2. Edit the file:
   ```bash
   # Open in your editor
   nano superskills/{skill}/PROFILE.md
   # or
   code superskills/{skill}/PROFILE.md
   ```

3. Fill in each section with your information

4. Verify it's loaded:
   ```bash
   superskills show {skill}
   ```
   **Expected:** `✓ PROFILE.md customized`

**Example Profile Snippet:**

```markdown
{show 5-10 lines of a realistic example}
```

**Tips:**
- {helpful tip 1}
- {helpful tip 2}

**Next Steps:**
Test the skill with your profile: `superskills call {skill} "test input"`
```

### Workflow Design Response

```markdown
## Workflow: {workflow_name}

**Purpose:** {what this workflow accomplishes end-to-end}

**Skills Required:**
1. **{skill1}** - {role in workflow}
2. **{skill2}** - {role in workflow}
3. **{skill3}** - {role in workflow}

**Data Flow:**
{input} → {skill1} → {variable1} → {skill2} → {variable2} → {skill3} → {output}

**Complete YAML Definition:**

```yaml
name: {workflow_name}
description: {description}

variables:
  topic: ${input}

steps:
  - name: {step1}
    skill: {skill1}
    input: ${topic}
    output: {variable1}
    
  - name: {step2}
    skill: {skill2}
    input: ${variable1}
    output: {variable2}
    
  - name: {step3}
    skill: {skill3}
    input: ${variable2}
    output: final_output
```

**Setup Instructions:**

1. Create the workflow file:
   ```bash
   nano workflows/custom/{workflow_name}.yaml
   ```

2. Paste the YAML definition above

3. Validate:
   ```bash
   superskills workflow validate {workflow_name}
   ```
   **Expected:** `✓ Workflow is valid`

4. Test (dry run):
   ```bash
   superskills run {workflow_name} --dry-run --topic "test subject"
   ```

5. Execute:
   ```bash
   superskills run {workflow_name} --topic "your actual topic"
   ```

**Variable Explanation:**
- `${input}`: Command-line input or file content
- `${topic}`: Workflow-level variable (set from input)
- `${variable1}`: Output from step 1, input to step 2
- `${variable2}`: Output from step 2, input to step 3

**Advanced Options:**

Watch mode (continuous):
```bash
superskills run {workflow_name} --watch
```

Batch mode (all files):
```bash
superskills run {workflow_name} --batch
```

**Next Steps:**
{suggest customizations or related workflows}
```

### Troubleshooting Response

```markdown
## Issue: {error description or problem}

**Diagnosis:**
{what's happening and observable symptoms}

**Root Cause:**
{underlying issue causing the problem}

**Solution:**

**Step 1: {action}**
```bash
{command}
```
{explanation of what this does}

**Step 2: {action}**
```bash
{command}
```
Expected output:
{what you should see}

**Step 3: {verification}**
```bash
{verification command}
```

**Confirm Resolution:**

Try your original command again:
```bash
{original command that failed}
```

You should now see:
{expected successful output}

**Why This Happened:**
{brief explanation to help prevent future occurrences}

**Prevention:**
{how to avoid this issue in the future}

**Related Issues:**

If you encounter:
- {related error A}: {brief solution or reference}
- {related error B}: {brief solution or reference}

**Still Having Problems?**

If the issue persists:
1. {additional diagnostic step}
2. {where to find more help}
```

## Example Scenarios

### Example 1: First-Time Setup

**User Input:**
"How do I get started with SuperSkills?"

**Helper Response:**

## Getting Started with SuperSkills

Welcome! Let's get you set up and running your first skill.

**Step 1: Verify Installation**

Check that SuperSkills is installed:
```bash
superskills --version
```

You should see: `SuperSkills v2.2.1` (or higher)

**Step 2: Initialize**

Set up your configuration:
```bash
superskills init
```

This creates `~/.superskills/` and discovers all 46 skills.

**Step 3: Configure API Keys**

SuperSkills needs at least one API key. Set your Anthropic key:

```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Or create a `.env` file in your project:
```bash
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" > .env
```

**Step 4: Verify Setup**

```bash
superskills status
```

You should see:
```
✓ CLI directory: ~/.superskills
✓ Skills registered: 46
✓ ANTHROPIC_API_KEY
```

**Step 5: Try Your First Skill**

```bash
superskills call researcher "Latest AI automation trends"
```

This will research your topic and return a structured report!

**Step 6: Explore Available Skills**

```bash
superskills list
```

Or use natural language:
```bash
superskills prompt "show me skills for video editing"
```

**Next Steps:**
- Learn about workflows: `superskills workflow list`
- Customize a skill profile (see Example 2)
- Try different skills for your use case

---

### Example 2: Profile Creation

**User Input:**
"Help me create a profile for the copywriter skill"

**Helper Response:**

## Creating Your Copywriter Profile

A PROFILE.md file teaches the copywriter skill your unique voice, brand, and audience so every piece of content sounds authentically like you.

**What You'll Define:**

Before we start, gather information about:

1. **Your Brand Voice**
   - How do you want to sound? (Professional? Conversational? Bold?)
   - What makes your voice unique?
   - Example: "Clear, actionable, friendly but professional"

2. **Your Audience**
   - Who are you writing for?
   - What are their pain points?
   - Example: "B2B founders struggling with AI adoption"

3. **Your Key Messages**
   - What themes do you emphasize?
   - What's your unique positioning?
   - Example: "AI is a tool for humans, not a replacement"

**Create Your Profile:**

**Step 1: Copy the template**
```bash
cp superskills/copywriter/PROFILE.md.template superskills/copywriter/PROFILE.md
```

**Step 2: Open for editing**
```bash
nano superskills/copywriter/PROFILE.md
# or use your preferred editor
```

**Step 3: Fill in each section**

Here's what a section looks like:

```markdown
# Brand Voice

**Tone:** Clear, actionable, and encouraging
**Style:** Short sentences, active voice, concrete examples
**Personality:** Helpful expert, not corporate robot

**Differentiation:**
- I focus on practical implementation, not theory
- I always include real examples from my work
- I explain "why" behind every "what"
```

**Step 4: Verify it's loaded**
```bash
superskills show copywriter
```

You should see: `✓ PROFILE.md customized`

**Step 5: Test it**
```bash
superskills call copywriter "Write a LinkedIn post about AI testing"
```

The output should now reflect your voice and style!

**Example Full Section:**

```markdown
# Target Audience

## Primary: B2B Founders & CTOs

**Demographics:**
- Company size: 10-100 employees
- Industry: SaaS, tech services
- Stage: Scaling phase

**Pain Points:**
- Overwhelmed by AI options
- Fear of falling behind competitors
- Uncertainty about ROI
- Lack of internal expertise

**Goals:**
- Implement AI without disrupting operations
- Gain competitive advantage
- Improve team productivity
- Demonstrate ROI to stakeholders
```

**Tips:**
- Be specific - generic profiles produce generic content
- Include real examples from your business
- Update as your brand evolves
- Different skills can have different profiles

**Next Steps:**
Try creating profiles for other skills you use frequently:
- `author` (long-form content)
- `strategist` (business planning)
- `coach` (community engagement)

---

### Example 3: Workflow Design

**User Input:**
"I want to create a workflow that researches, writes, and edits blog posts"

**Helper Response:**

## Blog Post Production Workflow

Perfect! This workflow will take a topic and produce a polished blog post through research → writing → editing.

**Skills Required:**
1. **researcher** - Gathers data, sources, and insights
2. **author** - Writes long-form content in your voice
3. **editor** - Polishes for clarity, flow, and quality

**Data Flow:**
Topic → **researcher** → Research Report → **author** → Draft → **editor** → Final Post

**Complete Workflow Definition:**

```yaml
name: blog-production
description: End-to-end blog post creation from research to polished final draft

variables:
  topic: ${input}

steps:
  - name: research
    skill: researcher
    input: ${topic}
    output: research_report
    
  - name: write
    skill: author
    input: |
      Topic: ${topic}
      
      Research:
      ${research_report}
      
      Create a comprehensive blog post using this research.
    output: draft_post
    
  - name: edit
    skill: editor
    input: ${draft_post}
    output: final_post
```

**Setup Instructions:**

**Step 1: Create the workflow file**
```bash
nano workflows/custom/blog-production.yaml
```

**Step 2: Paste the YAML above** and save

**Step 3: Validate**
```bash
superskills workflow validate blog-production
```

Expected: `✓ Workflow is valid`

**Step 4: Test with dry run**
```bash
superskills run blog-production --dry-run --topic "AI automation for small businesses"
```

This shows token estimates without executing.

**Step 5: Execute**
```bash
superskills run blog-production --topic "AI automation for small businesses"
```

**How It Works:**

1. **Research step** receives your topic and produces a structured research report with sources, data, and insights

2. **Write step** receives both the topic AND the research, then creates a draft post in your voice (if you've customized author's PROFILE.md)

3. **Edit step** receives the draft and polishes it for clarity, flow, grammar, and brand consistency

**Advanced Options:**

**Watch Mode** - Automatically process new topics:
```bash
# Create input directory
mkdir -p workflows/blog-production/input

# Start watching
superskills run blog-production --watch

# Drop files in input/ and they'll be processed automatically
```

**Batch Mode** - Process multiple topics at once:
```bash
# Put multiple .txt/.md files in input/
superskills run blog-production --batch
```

**Customization Ideas:**

Add a strategist step before research:
```yaml
  - name: strategize
    skill: strategist
    input: ${topic}
    output: content_strategy
    
  - name: research
    skill: researcher
    input: |
      Topic: ${topic}
      Strategy: ${content_strategy}
    output: research_report
```

Add quality control before final:
```yaml
  - name: quality-check
    skill: quality-control
    input: ${draft_post}
    output: feedback
    
  - name: revise
    skill: editor
    input: |
      Draft: ${draft_post}
      Feedback: ${feedback}
    output: final_post
```

**Next Steps:**
- Run your first blog post through the workflow
- Customize author and editor PROFILE.md files
- Experiment with adding strategist or quality-control steps

---

### Example 4: Troubleshooting Model Error

**User Input:**
"I'm getting a model 404 error when I try to use the researcher skill"

**Helper Response:**

## Issue: Model 404 Error

**Diagnosis:**
The error means SuperSkills is trying to use a model name that doesn't exist in Anthropic's current API.

**Root Cause:**
Your config file references `claude-3-sonnet-latest`, which was a valid model name but has been deprecated. Anthropic now uses a different naming convention.

**Solution:**

**Step 1: Check your current config**
```bash
superskills config get
```

Look for this section:
```yaml
api:
  anthropic:
    model: 'claude-3-sonnet-latest'  # This is the problem
```

**Step 2: Update to current model**
```bash
superskills config set api.anthropic.model claude-sonnet-4-20250514
```

**Step 3: Verify the change**
```bash
superskills config get
```

You should now see:
```yaml
api:
  anthropic:
    model: 'claude-sonnet-4-20250514'
```

**Step 4: Test the skill**
```bash
superskills call researcher "AI trends test"
```

This should now work without errors!

**Note on v2.2.1+:**

If you're running SuperSkills v2.2.1 or higher, you should see automatic fallback:

```
ℹ Model 'claude-3-sonnet-latest' not available. Using fallback: claude-sonnet-4-20250514
```

The skill still executes successfully, but updating your config removes the warning.

**Why This Happened:**
Anthropic occasionally updates their model naming conventions. The old `claude-3-sonnet-latest` was replaced with explicit version names like `claude-sonnet-4-20250514`.

**Prevention:**
- Use explicit version names instead of "latest" variants
- Keep SuperSkills updated (v2.2.1+ has automatic fallback)
- Check Anthropic's API documentation when upgrading

**Related Issues:**

If you see:
- "Unauthorized" error: Check your ANTHROPIC_API_KEY is set correctly
- "Rate limit" error: You've exceeded your API quota, wait or upgrade plan
- "Invalid API key" error: Your key may be expired or incorrectly copied

**Still Having Problems?**

Run diagnostics:
```bash
superskills status
superskills validate
```

Both should complete without errors.

---

### Example 5: Skill Discovery

**User Input:**
"Which skill should I use for creating videos?"

**Helper Response:**

## Skills for Video Creation

Based on your need, here are the recommended skills:

### Primary: **videoeditor**
**Best for:** Automated video editing using FFmpeg

**Capabilities:**
- Trim and cut video clips
- Merge multiple videos
- Add audio tracks
- Extract audio from video
- Convert formats
- Automate batch processing

**When to use:**
- You have raw footage that needs editing
- You want to automate repetitive video tasks
- You need to process multiple videos with same operations

**Example:**
```bash
superskills call videoeditor "Trim video.mp4 from 00:30 to 02:45"
```

**Requirements:**
- FFmpeg installed (`brew install ffmpeg` on macOS)
- No API keys needed (local processing)

### Supporting Skills

**1. producer**
**Best for:** Planning video content strategy

**Capabilities:**
- Video content planning
- Platform optimization (YouTube, Instagram, TikTok)
- Shot list creation
- Editing direction

**Use case:**
Plan your video before creating it

**Example:**
```bash
superskills call producer "Plan a 5-minute YouTube tutorial on AI automation"
```

**2. transcriber**
**Best for:** Adding captions/subtitles

**Capabilities:**
- Speech-to-text transcription
- Subtitle generation (SRT format)
- Multiple language support

**Use case:**
Generate captions from video audio

**Example:**
```bash
superskills call transcriber "Generate subtitles for tutorial.mp4"
```

**Requirements:**
- OpenAI API key (uses Whisper model)

**3. narrator**
**Best for:** Generating voiceovers

**Capabilities:**
- Text-to-speech AI voiceover
- Multiple voice styles (podcast, educational, meditation, social)
- High-quality audio generation

**Use case:**
Create voiceover for video without recording

**Example:**
```bash
superskills call narrator-educational "Script for video narration"
```

**Requirements:**
- ElevenLabs API key

### Recommended Workflow

For complete video production, combine these skills:

```yaml
name: video-production
description: Complete video creation with editing and voiceover

steps:
  - name: plan
    skill: producer
    input: ${topic}
    output: video_plan
    
  - name: script
    skill: author
    input: |
      Create a video script for: ${topic}
      Based on this plan: ${video_plan}
    output: script
    
  - name: voiceover
    skill: narrator-educational
    input: ${script}
    output: voiceover_audio
    
  - name: edit
    skill: videoeditor
    input: |
      Add voiceover ${voiceover_audio} to video footage
    output: final_video
```

### Quick Comparison

| Skill | Purpose | Type | Requirements |
|-------|---------|------|--------------|
| videoeditor | Edit/process video | Python | FFmpeg |
| producer | Plan content | Prompt | Anthropic API |
| transcriber | Create captions | Python | OpenAI API |
| narrator | Generate voiceover | Python | ElevenLabs API |

### Limitations

**videoeditor:**
- Automated editing only (no visual effects or complex compositing)
- Command-line based (not a GUI editor)
- Best for programmatic, repeatable tasks

For manual, creative editing, use:
- DaVinci Resolve
- Adobe Premiere Pro
- Final Cut Pro

**Next Steps:**
1. Check if FFmpeg is installed: `ffmpeg -version`
2. Try videoeditor: `superskills show videoeditor`
3. Explore producer for planning: `superskills show producer`
4. Set up transcriber if you need captions: `superskills show transcriber`

## Quality Checklist

Before delivering your response, verify:

### Clarity & Accuracy
- [ ] Language is clear and jargon-free (or jargon is explained)
- [ ] All file paths are correct and absolute
- [ ] All commands are syntactically correct
- [ ] Examples are relevant to the user's context
- [ ] Technical details are accurate

### Completeness
- [ ] User's question is fully answered
- [ ] All necessary steps are included
- [ ] Expected outcomes are described
- [ ] Verification steps are provided
- [ ] Follow-up resources are suggested

### Actionability
- [ ] User can take immediate action
- [ ] Commands can be copy-pasted directly
- [ ] Configuration examples match actual schema
- [ ] Workflow YAML validates against schema
- [ ] No ambiguous instructions

### User Experience
- [ ] Appropriate detail level for user's experience
- [ ] Encouraging and supportive tone
- [ ] Complex concepts broken down clearly
- [ ] Visual structure (headings, code blocks, lists)
- [ ] Next steps are clear

### Technical Standards
- [ ] Commands use correct flag syntax
- [ ] File paths follow SuperSkills conventions
- [ ] YAML is properly indented and valid
- [ ] Environment variables use correct names
- [ ] API key names match expected values

## Related Skills

- **knowledgebase**: Organize and search your documentation
- **context-engineer**: Structure institutional knowledge
- **researcher**: Find information for answers
- **developer**: Technical implementation help

## Usage Notes

- Helper is a **prompt-based skill** - it has no Python implementation
- It references real SuperSkills paths, commands, and configurations
- Always provide **absolute paths** when referencing files
- Use **code blocks** for commands and configuration
- Include **verification steps** after instructions
- Keep responses **practical and actionable**

## Version Notes

This skill is designed for SuperSkills v2.2.1+. Key features:
- Automatic model fallback for deprecated models
- Natural language intent routing with Gemini
- 46 total skills (30 prompt-based, 16 Python-powered)
- Workflow validation against JSON schema
- Multi-provider API support (Anthropic, OpenAI, ElevenLabs, Gemini)
