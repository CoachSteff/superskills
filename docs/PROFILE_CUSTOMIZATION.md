# Profile Customization Guide

**Transform Superskills from generic AI tools into your personalized AI workforce.**

---

## Table of Contents

1. [Why Profiles Matter](#why-profiles-matter)
2. [Quick Start (5 Minutes)](#quick-start-5-minutes)
3. [Master Briefing: Your Foundation](#master-briefing-your-foundation)
4. [Creating Skill Profiles](#creating-skill-profiles)
5. [Which Skills to Customize](#which-skills-to-customize)
6. [Profile Sections Explained](#profile-sections-explained)
7. [Examples by User Type](#examples-by-user-type)
8. [Advanced Topics](#advanced-topics)
9. [Troubleshooting](#troubleshooting)

---

## Why Profiles Matter

**The Problem:** Without customization, Superskills produces generic AI output that sounds like every other AI tool. It doesn't know your brand voice, your audience, your expertise, or your approach.

**The Solution:** Profiles teach each skill to sound like YOU, apply YOUR frameworks, and serve YOUR audience.

### Before vs. After Example

**Without Profile (Generic AI):**
> "I can help you create engaging content for your target audience. Let me know what topic you'd like to explore and I'll generate some ideas for you."

**With Profile (Your Voice):**
> "Your Q3 campaign brief is ready. I've structured it using your AIDA framework: hook with the 42% stat you mentioned, build desire with the SaaS case study, close with your standard 'book a strategy call' CTA. Matches your data-driven-but-conversational tone. Three edits to review before I finalize..."

### Impact by Skill Type

| Skill Type | Voice Impact | Example |
|------------|--------------|---------|
| **Creative** (copywriter, author, marketer) | ⭐⭐⭐⭐⭐ Critical | Tone, style, and voice are everything |
| **Strategic** (strategist, researcher, business-consultant) | ⭐⭐⭐⭐ Very High | Your frameworks and lens matter hugely |
| **Operational** (manager, publisher, quality-control) | ⭐⭐⭐ High | Standards and workflows need customization |
| **Technical** (developer, webmaster, builder) | ⭐⭐ Moderate | Less voice-dependent, more functionality |

---

## Quick Start (5 Minutes)

### Option 1: Use Profile Builder (Recommended)

**Interactive assistant** that guides you through the entire process:

```bash
superskills call profile-builder "help me create my master briefing"
```

The profile-builder will ask you questions about:
- Your business and expertise
- Your target audience  
- Your communication style
- Your unique approach

Then it generates your Master Briefing automatically.

### Option 2: Manual Setup

**1. Copy the Master Briefing template:**

```bash
cp MASTER_BRIEFING_TEMPLATE.yaml ~/.superskills/master-briefing.yaml
```

**2. Edit with your information:**

```bash
# Use your preferred editor
nano ~/.superskills/master-briefing.yaml
# or
code ~/.superskills/master-briefing.yaml
```

**3. Create your first profile:**

```bash
superskills call profile-builder "generate a profile for copywriter"
```

**4. Test it:**

```bash
superskills call copywriter "Draft a LinkedIn post about AI adoption for B2B SaaS marketers"
```

Compare the output to your voice. Iterate on the profile if needed.

---

## Master Briefing: Your Foundation

The Master Briefing is a YAML document that captures your brand voice and business context. **All skill profiles pull from this foundation** to maintain consistency.

### 8 Core Sections

#### 1. Identity & Context

Who you are and what you do.

**Key fields:**
- `name`: Your name or business name
- `role`: Your professional title
- `business`: One-sentence business description
- `domain`: Primary expertise area
- `experience`: Years and background

**Example:**
```yaml
identity:
  name: "Sarah Chen Marketing"
  role: "B2B SaaS Marketing Consultant"
  business: "Conversion-focused marketing agency for mid-market SaaS companies"
  domain: "B2B SaaS Marketing & Growth"
  experience: "12 years in B2B marketing, former VP Marketing at two Series B companies"
```

#### 2. Audience

Who you serve and what they need.

**Key fields:**
- `primary`: Your main audience (be specific!)
- `pain_points`: What challenges you solve
- `desired_feeling`: How you want them to feel

**Example:**
```yaml
audience:
  primary: "Marketing directors at mid-market B2B SaaS (50-500 employees)"
  pain_points:
    - "Struggling to prove ROI to executives"
    - "Don't have budget for full-service agency"
    - "Need to scale with lean teams"
  desired_feeling: "Empowered and capable, with clear next steps"
```

#### 3. Voice & Tone

**This is the most critical section.** Be specific, not generic.

**❌ Generic (Don't do this):**
```yaml
voice:
  style: "Professional and friendly"
  characteristics:
    - "High quality"
    - "Helpful"
    - "Expert"
```

**✅ Specific (Do this):**
```yaml
voice:
  style: "Data-driven with storytelling, warm but analytical"
  characteristics:
    - "Evidence-based: always backs claims with data or case studies"
    - "Practical: every insight includes implementation steps"
    - "Slightly rebellious: questions conventional SaaS marketing wisdom"
  
  language_patterns:
    - "Active voice with short, punchy sentences"
    - "Leads with specific numbers, not ranges ('42%' not '40-45%')"
    - "Second-person 'you' to engage reader directly"
  
  signature_elements:
    - "Opens with provocative data point or contrarian statement"
    - "Includes mini case studies from real clients"
  
  avoid:
    - "delve, leverage, synergy, game-changer"
    - "revolutionary, cutting-edge, next-level"
    - "think outside the box, circle back"
```

**Critical:** Include a 150-300 word `sample_voice` of your actual writing. This is the #1 factor in authentic AI output.

#### 4. Perspective & Positioning

Your unique lens and how you frame your work.

**Example:**
```yaml
perspective:
  lens: "Data × Storytelling for B2B"
  goal: "Help marketing teams prove ROI and secure executive buy-in"
  reader_positioning: "They're the capable strategist; I'm the guide removing obstacles"
  guiding_principle: "Strategy without measurement is hallucination"
```

#### 5. Frameworks & Methodologies

Your proprietary or preferred approaches.

**If you have formal frameworks:**
```yaml
frameworks:
  - name: "Revenue Attribution Model"
    description: "Multi-touch attribution system that connects marketing activities to pipeline and revenue"
    when_to_use: "Proving marketing ROI to executives"
    components:
      - "First-touch: Awareness and lead generation"
      - "Multi-touch: Nurture and engagement"
      - "Last-touch: Conversion and close"
```

**If you don't have formal frameworks, describe your approach:**
```yaml
frameworks:
  - name: "My Content Audit Process"
    description: "4-step method for evaluating existing content and identifying gaps"
    when_to_use: "Before building content strategy"
    components:
      - "Inventory: Catalog all existing assets"
      - "Analyze: Performance metrics and gaps"
      - "Prioritize: Update vs. create vs. retire"
      - "Plan: Content calendar with clear goals"
```

#### 6. Expertise

Credibility markers and proof points.

**Example:**
```yaml
expertise:
  areas:
    - "B2B SaaS demand generation"
    - "Marketing attribution and analytics"
    - "Content strategy and execution"
  
  credentials:
    - "MBA, Marketing - UCLA Anderson"
    - "HubSpot Inbound Certified"
  
  proof_points:
    - "Grew SaaS startup from $2M to $15M ARR as VP Marketing"
    - "Managed $5M+ in annual ad spend"
    - "Spoken at SaaStr and B2B Marketing Forum"
  
  industries:
    - "B2B SaaS"
    - "Marketing technology"
```

#### 7. Examples & Voice Samples

**MOST IMPORTANT SECTION for voice quality.**

```yaml
examples:
  signature_stories:
    - "The leaky bucket story: why SaaS companies should fix retention before spending more on acquisition"
  
  sample_voice: |
    Most B2B marketers obsess over CAC (customer acquisition cost). But here's what they miss: if you're losing 40% of customers annually, lowering CAC from $1,000 to $800 won't save your business.
    
    I learned this the hard way at my Series B startup. We celebrated when we cut acquisition costs by 30%. Six months later, we were still hemorrhaging revenue because churn was killing us.
    
    The math is brutal: A $1,000 customer who churns after 12 months generates $12K lifetime value. But a $1,200 customer who stays for 36 months? That's $43K. The second customer is 3.6x more valuable, even though they cost 20% more to acquire.
    
    Fix your bucket before you pour more water in.
  
  typical_hooks:
    - "Here's what no one tells you about [topic]..."
    - "I analyzed 50 B2B SaaS companies and found this pattern..."
```

**The `sample_voice` field should be YOUR actual writing**, not made-up text. Paste:
- A recent email or LinkedIn post
- Opening paragraphs of a blog post
- A section from your About page

#### 8. Guardrails & Compliance

Boundaries and requirements.

**Example:**
```yaml
guardrails:
  privacy:
    - "GDPR compliance for EU clients"
    - "Never share client names without written permission"
    - "Anonymize all case studies"
  
  ethics:
    - "No guarantees of specific outcomes ('you'll make $100k')"
    - "Recommend qualified professionals for legal/financial advice"
  
  compliance:
    - "CAN-SPAM Act for email marketing"
    - "FTC disclosure for sponsored content"
  
  human_judgment_required:
    - "Client contract terms and pricing"
    - "Publishing anything with client-identifying information"
    - "Strategic pivots or major business decisions"
```

---

## Creating Skill Profiles

Once your Master Briefing exists, create profiles for individual skills.

### Using Profile Builder (Recommended)

```bash
superskills call profile-builder "generate a profile for [skill-name]"
```

Profile Builder will:
1. Load your Master Briefing
2. Ask skill-specific questions
3. Generate a complete profile
4. Preview it for your approval
5. Save to `superskills/[skill-name]/PROFILE.md`

### Manual Profile Creation

**1. Copy the template:**

```bash
cp PROFILE_TEMPLATE.md superskills/[skill-name]/PROFILE.md
```

**2. Edit the file, pulling from your Master Briefing:**

- **Identity**: Reference your Master Briefing name and domain
- **Voice and Tone**: Copy your voice.style, characteristics, patterns
- **The [Your Name] Factor**: Apply your perspective.lens to this skill
- **Core Frameworks**: Choose 2-4 relevant frameworks from Master Briefing
- **Inputs/Outputs**: Define what this skill needs and produces
- **Quality Gates**: Your standards + voice consistency checks
- **Guardrails**: Pull from Master Briefing + skill-specific additions
- **Example Output Style**: Write a 150-200 word sample in your voice
- **Integration Notes**: How this skill works with other skills

**3. Verify the profile:**

```bash
superskills show [skill-name]
```

You should see: `✓ PROFILE.md customized`

**4. Test with real work:**

```bash
superskills call [skill-name] "[your actual task]"
```

Evaluate the output:
- Does it sound like you?
- Does it apply your frameworks?
- Does it avoid your banned words?
- Is the tone right for your audience?

If not, refine the profile and test again.

---

## Which Skills to Customize

**Start with your most-used skills** where voice matters most.

### Tier 1: Customize First (Highest Impact)

**Creative Skills** - Voice is critical:
- **copywriter** - Marketing copy, social media, emails
- **author** - Long-form content, blog posts, articles
- **marketer** - Campaign strategy and messaging
- **narrator** - Voice and script generation

**Strategic Skills** - Your frameworks matter:
- **researcher** - How you analyze and synthesize information
- **strategist** - Your approach to business strategy
- **business-consultant** - Your consulting methodology

### Tier 2: Customize Next (High Value)

- **editor** - Your editorial standards and style preferences
- **quality-control** - Your quality criteria
- **email-campaigner** - Email voice is brand-critical
- **influencer** - Thought leadership and personal brand
- **sales** - Your sales approach and messaging

### Tier 3: Customize If Relevant

- **translator** - If you work in multiple languages
- **community-manager** - If you manage online communities
- **publisher** - If you manage multi-platform content
- **presenter** - If you create presentations frequently

### Skills You Can Skip

**Technical Skills** (less voice-dependent):
- developer, webmaster, designer
- transcriber, video-editor
- builder, n8n-workflow

These are more about functionality than voice. Profiles add less value.

---

## Profile Sections Explained

### 1. Identity

**Purpose:** Define what this skill does for you.

**Template:**
```markdown
## Identity

You are a digital extension of [Your Business Name], specifically focusing on **[Skill Domain]**. You blend [your expertise] with [skill capability] to deliver [outcome].

**Primary Role**: [Creative Partner / Technical Expert / Strategic Advisor / Operational Guide]
```

**Example (Copywriter for Marketing Consultant):**
```markdown
## Identity

You are a digital extension of Sarah Chen Marketing, specifically focusing on **B2B SaaS Copywriting**. You blend data-driven marketing strategy with conversion-focused writing to deliver high-performing marketing copy.

**Primary Role**: Creative Partner
```

### 2. Voice and Tone

**Pull directly from Master Briefing:**
- voice.style
- voice.characteristics (3-5 items)
- voice.language_patterns
- voice.signature_elements
- voice.avoid

**This ensures voice consistency across all skills.**

### 3. The [Your Name] Factor

**Your unique lens applied to this skill.**

Pull from Master Briefing:
- perspective.lens
- perspective.goal (contextualized for skill)
- perspective.reader_positioning

**Example:**
```markdown
## The Sarah Chen Factor

**Perspective**: You view copywriting through the lens of Data × Storytelling. Every piece of copy should be backed by research and wrapped in narrative.

**Goal**: Help B2B SaaS marketers create copy that converts and proves ROI to executives.

**Reader as Hero**: They're the capable marketer; you're the partner helping them articulate value clearly and compellingly.
```

### 4. Core Frameworks

**Select 2-4 frameworks from Master Briefing most relevant to this skill.**

Show specific application, not just names.

**Example:**
```markdown
## Core Frameworks

**AIDA Framework** (from Master Briefing):
- Attention: Data-driven hook (specific stat or insight)
- Interest: Mini case study showing problem
- Desire: Paint picture of life after solution
- Action: Single, clear CTA

**Value Proposition Canvas**:
Apply to every copy project:
- Customer Jobs: What they're trying to accomplish
- Pains: What's frustrating or blocking them
- Gains: What success looks like
Map copy to address each explicitly.
```

### 5. Inputs

**What this skill needs to do its job well.**

Vary by skill type:

**Creative skills:**
- Topic/theme
- Target audience
- Tone/style
- Desired length
- Goal/CTA

**Technical skills:**
- Requirements/specs
- Technical constraints
- Quality standards

**Strategic skills:**
- Business context
- Objectives
- Success metrics

### 6. Outputs

**What this skill produces.**

**Example (Copywriter):**
```markdown
## Outputs

- Draft marketing copy (emails, landing pages, ads, social posts)
- Copy variations for A/B testing
- Headlines and hooks
- Call-to-action options
- Copy briefs with rationale and suggested edits
```

### 7. Quality Gates

**Your standards for acceptable output.**

**Template:**
```markdown
## Quality Gates

**Voice & Brand Consistency**:
- Matches [your voice.style from Master Briefing]
- Avoids [banned words from Master Briefing]
- Demonstrates [key characteristics]

**Content Quality**:
- [Your quality criterion 1]
- [Your quality criterion 2]

**Audience Alignment**:
- Appropriate for [your audience from Master Briefing]
- Addresses [pain points]
```

### 8. Guardrails

**Pull from Master Briefing guardrails** + add skill-specific boundaries.

**Example:**
```markdown
## Guardrails

**Privacy & Compliance**:
- GDPR compliance for EU clients (from Master Briefing)
- Never use client names without permission
- CAN-SPAM compliance for email copy

**Ethical Boundaries**:
- No guarantees of specific outcomes
- Disclose limitations honestly

**Human Judgment Required**:
- Final approval before publishing
- Pricing and contract terms
- Strategic messaging decisions
```

### 9. Example Output Style

**MOST IMPORTANT for voice matching after Master Briefing sample_voice.**

Write 150-200 words demonstrating:
- Your authentic voice
- Skill-specific application
- Concrete details (not vague)
- Realistic scenario

**❌ Generic (Don't do this):**
> "I can help you create great content that resonates with your audience. Let me know your goals and I'll generate ideas for you."

**✅ Specific (Do this):**
> "Your Q3 email campaign draft is ready. I've structured it using your AIDA framework: opened with that 42% stat you mentioned (data-driven hook), built interest with the SaaS pricing migration case study, created desire by painting the picture of board-approved marketing budget, and closed with a single CTA ('Book your strategy session'). The tone matches your 'data-driven but conversational' style—specific numbers, mini story, clear action. Three edits to review: (1) Should the subject line lead with the stat or the outcome? (2) The case study is 4 sentences—trim to 3? (3) CTA button: 'Book Strategy Session' or 'See How We Did It'? Let me know which direction and I'll finalize."

### 10. Integration Notes

**How this skill works with others in your workflow.**

**Example:**
```markdown
## Integration Notes

**Works Well With**:
- **researcher**: Research market trends → copywriter drafts campaign
- **editor**: Copywriter drafts → editor refines voice and clarity
- **quality-control**: Quality-control validates → copywriter revises
- **publisher**: Copywriter finalizes → publisher distributes

**Common Workflows**:
- Content Creation: researcher (gather data) → copywriter (draft) → editor (refine) → publisher (distribute)
- Campaign Development: strategist (plan) → copywriter (messaging) → marketer (execution)
```

---

## Examples by User Type

### Marketing Consultant

**Focus:** Copywriter, Marketer, Researcher, Strategist

**Master Briefing highlights:**
- Voice: Data-driven with storytelling
- Frameworks: AIDA, Attribution Model, Content Audit
- Audience: B2B SaaS marketing directors

**Priority profiles:**
1. Copywriter (campaigns, social media)
2. Marketer (strategy and planning)
3. Researcher (market analysis)

### Independent Content Creator

**Focus:** Author, Copywriter, Publisher, Influencer

**Master Briefing highlights:**
- Voice: Warm and conversational, slightly rebellious
- Frameworks: Storytelling Arc, Engagement Ladder
- Audience: Entrepreneurs and small business owners

**Priority profiles:**
1. Author (blog posts, articles)
2. Copywriter (social media, emails)
3. Publisher (multi-platform distribution)

### Financial Analyst

**Focus:** Researcher, Strategist, Business-Consultant

**Master Briefing highlights:**
- Voice: Analytical and data-driven, authoritative
- Frameworks: DCF Model, Risk Assessment Matrix
- Audience: Finance executives and investors

**Priority profiles:**
1. Researcher (market and financial analysis)
2. Strategist (investment recommendations)
3. Business-Consultant (advisory work)

---

## Advanced Topics

### Multiple Master Briefings

**Use case:** Different voices for different contexts (corporate vs. social, formal vs. casual).

**Approach:**
```bash
# Create multiple master briefings
~/.superskills/master-briefing-corporate.yaml
~/.superskills/master-briefing-social.yaml
```

When creating profiles, specify which to use:
```bash
superskills call profile-builder "generate copywriter profile using my social voice"
```

### Profile Maintenance

**Quarterly review checklist:**
- [ ] Does your voice still match your current brand?
- [ ] Have you added new frameworks or approaches?
- [ ] Has your target audience shifted?
- [ ] Are banned words list still accurate?
- [ ] Do example outputs still sound like you?

**Update process:**
1. Edit Master Briefing first
2. Regenerate affected profiles
3. Test with real work
4. Increment version numbers

### Profile Versioning

Track changes to profiles over time:

```markdown
**Profile Version**: 2.1  
**Last Updated**: 2024-12-24  
**Aligned with**: Master Briefing v2.0

**Changelog:**
- v2.1: Added Value Ladder framework
- v2.0: Updated voice to be more conversational
- v1.0: Initial profile
```

### Team Profiles

**For agencies or teams with multiple voices:**

Option 1: Separate Master Briefings per team member
Option 2: Voice variants in one Master Briefing
Option 3: Skill profiles by use case (client A vs. client B)

---

## Troubleshooting

### "I don't know how to describe my voice"

**Solution:** Let your existing content tell you.

1. Collect 3-5 pieces of your actual writing
2. Paste into profile-builder:
   ```bash
   superskills call profile-builder "analyze my voice from these writing samples: [paste samples]"
   ```
3. Profile-builder extracts patterns and suggests voice description
4. You review and approve

### "Profile output doesn't sound like me"

**Diagnosis:**

1. **Check Master Briefing sample_voice**: Is it 150-300 words of YOUR actual writing?
   - If no → Add authentic sample
   
2. **Check Example Output Style**: Does it demonstrate your voice?
   - If generic → Rewrite with concrete example
   
3. **Check banned words**: Are they being respected?
   - Run: `superskills call quality-control "check this output"`

4. **Compare to your writing**: Paste your actual work and AI output side-by-side
   - What's different? (Tone? Structure? Word choice?)
   - Update profile to address gaps

### "Master Briefing feels overwhelming"

**Fast-track option:**

**5-minute Master Briefing:**
1. Name and domain (30 seconds)
2. Primary audience (30 seconds)
3. Paste 200 words of your actual writing (2 minutes)
4. Three words describing your style (30 seconds)
5. Compliance needs if any (1 minute)

Done. Refine later as you use the skills.

```bash
superskills call profile-builder "create a quick master briefing - I'll answer 5 quick questions"
```

### "Which frameworks should I include?"

**If you have formal frameworks:**
- List them with descriptions

**If you don't:**
- Describe your approach to problems
- Your decision-making process
- Your teaching method
- How you structure thinking

**You don't need proprietary IP to have frameworks.** Just describe how you work.

**Example:**
```yaml
frameworks:
  - name: "My Client Discovery Process"
    description: "How I understand client needs before proposing solutions"
    components:
      - "Context: Understand their business and market"
      - "Challenges: Identify root causes, not symptoms"
      - "Constraints: Budget, timeline, resources"
      - "Criteria: How they'll measure success"
```

### "Generated profiles are too long"

**Target length:** 100-150 lines per profile

**If longer:**
- Collapse similar points
- Remove redundant examples
- Tighten language
- Focus on what's unique vs. what's standard

**Remember:** Profiles are instructions to AI, not documentation for humans. Concise and specific beats comprehensive and vague.

---

## Next Steps

**New user path:**

1. ✅ **Create Master Briefing** (15 minutes)
   ```bash
   superskills call profile-builder "help me create my master briefing"
   ```

2. ✅ **Generate first profile** for your most-used skill (5 minutes)
   ```bash
   superskills call profile-builder "generate a profile for copywriter"
   ```

3. ✅ **Test with real work** (5 minutes)
   ```bash
   superskills call copywriter "[your actual task]"
   ```

4. ✅ **Refine if needed** (5-10 minutes)
   - Edit profile based on output quality
   - Test again

5. ✅ **Repeat for 2-3 more skills** (20 minutes)
   - Focus on Tier 1 skills (highest voice impact)

**Total time investment:** 60-90 minutes  
**Result:** Personalized AI workforce that sounds like you

---

## Resources

- **Master Briefing Template**: `MASTER_BRIEFING_TEMPLATE.yaml`
- **Profile Template**: `PROFILE_TEMPLATE.md`
- **Example Profiles**: `examples/profiles/` (5 diverse user types)
- **Profile Builder Skill**: `superskills call profile-builder "help"`
- **Helper Skill**: `superskills call helper "profile creation guidance"`

---

**Remember:** Perfect is the enemy of done. Start with a basic Master Briefing and your top 2-3 skills. Refine as you use them. Your profiles will improve naturally as you see what works and what doesn't.

The goal isn't perfection—it's authentic AI output that sounds like YOU and serves YOUR audience effectively.
