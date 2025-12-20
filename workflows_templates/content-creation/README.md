# Content Creation Workflow

Automated end-to-end content production from research to publication-ready article.

## Overview

This workflow orchestrates 4 specialized skills:
1. **Researcher** - Gathers data, validates claims, compiles sources
2. **Strategist** - Defines messaging, audience focus, creative approach
3. **Author** - Writes in your authentic voice
4. **Editor** - Polishes for clarity, brand consistency, impact

## Prerequisites

**API Keys:**
- `ANTHROPIC_API_KEY` - Powers all 4 skills (researcher, strategist, author, editor)

**Setup:**
```bash
export ANTHROPIC_API_KEY=sk-ant-...
# Or add to .env file
```

## Quick Start

**1. Copy template:**
```bash
cp -r workflows_templates/content-creation workflows/
```

**2. Create topic file:**
```bash
echo "AI automation trends for freelance coaches in 2025" > workflows/content-creation/input/topic.txt
```

**3. Run workflow:**
```bash
superskills run content-creation --input workflows/content-creation/input/topic.txt
```

**4. Get publication-ready content:**
```bash
cat workflows/content-creation/output/final_content_*.md
```

## Input Format

Simple text file with your topic:
```
The future of AI-powered coaching businesses
```

Or detailed brief:
```
Topic: AI coaching automation
Angle: Practical implementation guide
Target: Solo coaches earning $50-150K/year
Goal: Position as thought leader
```

## Output

You'll receive:
1. `research_findings_TIMESTAMP.md` - Compiled research with sources
2. `content_strategy_TIMESTAMP.md` - Strategic brief and outline
3. `draft_content_TIMESTAMP.md` - Initial draft
4. `final_content_TIMESTAMP.md` - Publication-ready article

## Customization

Edit `workflow.yaml` variables:

```yaml
variables:
  topic: "Your topic"
  target_audience: "startup founders"
  content_length: "2500-3000 words"
```

Or override via CLI:
```bash
superskills run content-creation --input topic.txt --var target_audience="executives"
```

## Expected Costs

For 2,000-word article:
- Research: ~$0.10 (Claude Sonnet)
- Strategy: ~$0.05
- Draft: ~$0.15
- Edit: ~$0.08
- **Total: ~$0.38 per article**

Use `--dry-run` for exact estimates.

## Advanced Usage

**Batch production:**
```bash
# Create multiple topic files
echo "Topic 1" > workflows/content-creation/input/topic1.txt
echo "Topic 2" > workflows/content-creation/input/topic2.txt

# Process all
superskills run content-creation --batch
```

**Custom workflow steps:**

Skip strategy if you have your own brief:
```yaml
steps:
  - name: draft
    skill: author
    input: ${input_file}  # Your brief
    output: draft_content
```

## Tips for Best Results

1. **Specific topics work better:** "AI automation for coaches" > "AI trends"
2. **Set your PROFILE.md:** Ensures authentic voice in authoring
3. **Review research output:** Validate sources before drafting
4. **Iterate on edits:** Run editor again if needed

## Troubleshooting

**Issue: Generic/bland content**
- Set up `superskills/author/PROFILE.md` with your voice
- Provide more specific topic angle
- Include target audience in input

**Issue: Inaccurate research**
- Increase `sources_required` in workflow.yaml
- Manually verify high-impact claims
- Add domain expertise to PROFILE.md
