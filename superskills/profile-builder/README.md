# Profile Builder

**Transform Superskills into YOUR personalized AI workforce.**

## What It Does

Profile Builder is a meta-skill that helps you:

1. **Create your Master Briefing** - The foundation document capturing your brand voice, expertise, and values
2. **Generate skill profiles** - Customize individual skills to match your unique approach
3. **Audit existing profiles** - Check quality and consistency
4. **Import from documents** - Extract voice from your Obsidian notes, brand guidelines, or existing content

## Quick Start

### Create Your Master Briefing (15 minutes)

```bash
superskills call profile-builder "help me create my master briefing"
```

The skill will guide you through 8 sections:
- Identity & Context
- Audience Definition
- Voice & Tone (most critical!)
- Perspective & Positioning
- Frameworks & Methodologies
- Expertise Documentation
- Examples & Voice Samples
- Guardrails & Compliance

### Generate Skill Profiles (5 minutes each)

```bash
superskills call profile-builder "generate a profile for copywriter"
superskills call profile-builder "generate a profile for researcher"
superskills call profile-builder "generate a profile for marketer"
```

### Test Your Profiles

```bash
# Before profile: generic AI output
superskills call copywriter "Write a LinkedIn post about AI adoption"

# After profile: sounds like YOU
# (Same command, output matches your brand voice)
```

## Why This Matters

**Without profiles:**
> "I can help you create engaging content for your target audience. Let me know what topic you'd like to explore."

**With profiles:**
> "Your Q3 campaign brief is ready. I've structured it using your AIDA framework: hook with the 42% stat, desire with the SaaS case study, CTA for your 'book a strategy call.' Matches your data-driven-conversational tone. Three edits to review..."

## Features

### Interactive Workflows

- **Master Briefing Creation**: Guided questions, smart defaults, voice extraction
- **Profile Generation**: Context-aware prompts based on skill type (creative/technical/strategic)
- **Quality Validation**: Checks for completeness, consistency, authenticity
- **Profile Audit**: Reviews existing profiles, identifies gaps, suggests improvements

### Document Ingestion (Roadmap)

Extract voice and context from:
- Obsidian vault exports
- Craft docs
- Brand guidelines (PDF/DOCX)
- Your published content

### Multi-Profile Support

Create different voices for different contexts:
- `master-briefing-corporate.yaml` (formal, executive audience)
- `master-briefing-social.yaml` (casual, peer audience)

## Usage Examples

### First-Time Setup

```bash
# Full interactive setup
superskills call profile-builder "help me create my master briefing"

# Quick 5-minute version
superskills call profile-builder "create a quick master briefing - I'll answer 5 questions"
```

### Skill Profile Generation

```bash
# Generate for specific skill
superskills call profile-builder "generate a profile for the author skill"

# Multiple skills
superskills call profile-builder "generate profiles for copywriter, marketer, and researcher"

# Recommendation
superskills call profile-builder "which skills should I customize first?"
```

### Profile Maintenance

```bash
# Audit single profile
superskills call profile-builder "audit my copywriter profile"

# Audit all profiles
superskills call profile-builder "audit all my profiles"

# Update existing
superskills call profile-builder "update my Master Briefing - I want to change my voice section"
```

### Import from Documents

```bash
# From Obsidian export
superskills call profile-builder "extract my voice from my Obsidian notes in ~/Documents/vault/"

# From brand guidelines
superskills call profile-builder "build my master briefing from my brand guidelines PDF"

# From published content
superskills call profile-builder "analyze my voice from these blog posts: [URLs]"
```

## Master Briefing Structure

The foundation document with 8 sections:

```yaml
identity:
  name: "[Your Name/Business]"
  role: "[Professional Role]"
  domain: "[Primary Expertise]"

audience:
  primary: "[Target Audience]"
  pain_points: [...]

voice:
  style: "[Communication Style]"
  characteristics: [...]
  language_patterns: [...]
  signature_elements: [...]
  avoid: [...]
  sample_voice: |
    [150-300 words of YOUR actual writing]

perspective:
  lens: "[Unique Perspective]"
  goal: "[Ultimate Outcome]"

frameworks: [...]
expertise: [...]
examples: [...]
guardrails: [...]
```

## Skill Profile Structure

Each skill profile has 10 sections:

1. **Identity** - What this skill does for you
2. **Voice and Tone** - Pulled from Master Briefing
3. **The [Your Name] Factor** - Your unique lens applied to this skill
4. **Core Frameworks** - 2-4 relevant frameworks from Master Briefing
5. **Inputs** - What information this skill needs
6. **Outputs** - What this skill produces
7. **Quality Gates** - Your standards for acceptable output
8. **Guardrails** - Boundaries and compliance needs
9. **Example Output Style** - 150-200 word sample in your voice
10. **Integration Notes** - How this skill works with others

## Which Skills to Customize

### Tier 1 (Customize First - Highest Voice Impact)

**Creative Skills:**
- copywriter (marketing copy, social media)
- author (blog posts, articles)
- marketer (strategy and messaging)
- narrator (voice generation)

**Strategic Skills:**
- researcher (analysis approach)
- strategist (business strategy)
- business-consultant (methodology)

### Tier 2 (Customize Next - High Value)

- editor (editorial standards)
- quality-control (quality criteria)
- email-campaigner (email voice)
- influencer (thought leadership)
- sales (sales approach)

### Tier 3 (Customize If Relevant)

- translator, community-manager, publisher, presenter

### Skip Customization

**Technical Skills** (less voice-dependent):
- developer, webmaster, builder, transcriber

## Tips for Great Profiles

### Do:
- Use real examples from your actual work
- Be specific ("data-driven with storytelling" not "professional")
- Include 150-300 word voice sample of YOUR writing
- Test profiles immediately with real tasks
- Refine based on output quality

### Don't:
- Use generic descriptions everyone could claim
- Skip the voice sample (it's critical!)
- List frameworks you don't actually use
- Create profiles for every skill at once
- Leave sections as "TODO"

## Troubleshooting

### "I don't know how to describe my voice"

```bash
superskills call profile-builder "analyze my voice from these writing samples: [paste 3-5 samples]"
```

Profile Builder will extract patterns and suggest descriptions.

### "Output doesn't sound like me"

1. Check Master Briefing has 150+ word voice sample of YOUR writing
2. Check Example Output Style in profile demonstrates your voice
3. Compare AI output to your actual writing - what's different?
4. Update profile to address gaps, test again

### "This is taking too long"

5-minute version:
```bash
superskills call profile-builder "quick setup - 5 questions only"
```

You can refine later.

## File Locations

- **Master Briefing**: `~/.superskills/master-briefing.yaml`
- **Skill Profiles**: `superskills/[skill-name]/PROFILE.md`
- **Templates**: `MASTER_BRIEFING_TEMPLATE.yaml`, `PROFILE_TEMPLATE.md`
- **Examples**: `examples/profiles/` (5 diverse user types)

## Documentation

- **Comprehensive Guide**: [docs/PROFILE_CUSTOMIZATION.md](../../docs/PROFILE_CUSTOMIZATION.md)
- **Quick Start**: [docs/QUICKSTART.md](../../docs/QUICKSTART.md#personalize-your-skills-5-15-minutes)
- **Main README**: [README.md](../../README.md) (Step 6)

## Support

```bash
# Get help
superskills call profile-builder "help"

# List capabilities
superskills call profile-builder "what can you do?"

# Troubleshooting
superskills call helper "profile creation guidance"
```

---

**Remember:** Start small. Master Briefing + 2-3 key skills = 60-90 minutes. The quality compounds across every skill you customize and every output you generate.

The goal isn't perfection—it's authentic AI output that sounds like YOU.
