# Podcast Generation Workflow

Generate professional podcast audio from markdown scripts with optimized narration.

## Overview

This workflow:
1. **Enhances** your script for natural spoken delivery (copywriter)
2. **Generates** professional audio with your voice (narrator-podcast)

## Prerequisites

**API Keys Required:**
- `ANTHROPIC_API_KEY` - For script enhancement
- `ELEVENLABS_API_KEY` - For voice generation
- `ELEVENLABS_VOICE_ID` - Your cloned voice ID

**Setup:**
```bash
export ANTHROPIC_API_KEY=sk-ant-...
export ELEVENLABS_API_KEY=...
export ELEVENLABS_VOICE_ID=...

# Or add to .env file in project root
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
echo "ELEVENLABS_API_KEY=..." >> .env
echo "ELEVENLABS_VOICE_ID=..." >> .env
```

## Quick Start

**1. Copy this template to your workflows directory:**
```bash
cp -r workflows_templates/podcast-generation workflows/
```

**2. Add your script to input directory:**
```bash
cp your-podcast-script.md workflows/podcast-generation/input/
```

**3. Run the workflow:**

**Watch mode** (auto-process new files):
```bash
superskills run podcast-generation --watch
```

**Batch mode** (process all existing files):
```bash
superskills run podcast-generation --batch
```

**Single file**:
```bash
superskills run podcast-generation --input workflows/podcast-generation/input/your-script.md
```

**4. Get your output:**
```bash
ls -lh workflows/podcast-generation/output/

# Example output:
# your-script_enhanced_20241220_123456.md  - Enhanced script
# your-script_podcast_20241220_123456.mp3  - Podcast audio (30 min)
```

## Input Format

Your markdown script should include:
- Episode title
- Main content/talking points
- Optional: Intro/outro sections

**Example:**
```markdown
# Episode 15: AI Automation in Coaching

## Introduction
Welcome back to the Superworker Podcast...

## Main Content
Today we're exploring three key trends...

## Conclusion
To recap, we covered...
```

## Customization

Edit `workflow.yaml` to customize:

**Voice style:**
```yaml
variables:
  voice_style: meditation  # podcast, meditation, educational, marketing, social
```

**Output format:**
```yaml
config:
  output_format: wav  # mp3, wav
  quality: ultra  # standard, high, ultra
```

## Expected Costs

Based on 2,000-word script (~10 min audio):
- Script enhancement: ~$0.05 (Claude Sonnet)
- Voice generation: ~$0.30 (ElevenLabs)
- **Total: ~$0.35 per episode**

Use `--dry-run` to estimate before processing:
```bash
superskills run podcast-generation --dry-run
```

## Troubleshooting

**Issue: "Workflow not found"**
- Ensure you copied the template to `workflows/` directory
- Check: `superskills workflow list`

**Issue: "API key not found"**
- Verify environment variables are set
- Check: `superskills status`

**Issue: "Voice not found"**
- Ensure `ELEVENLABS_VOICE_ID` is set
- Verify voice ID at: https://elevenlabs.io/app/voice-library

## Advanced Usage

**Process multiple scripts in batch:**
```bash
# Add all scripts to input/
cp episode-*.md workflows/podcast-generation/input/

# Process all
superskills run podcast-generation --batch
```

**Custom voice per episode:**
Edit script frontmatter:
```markdown
---
voice_id: your_alternative_voice_id
---

# Episode content...
```

## Output Structure

```
output/
├── script-name_enhanced_TIMESTAMP.md   # Enhanced script
├── script-name_podcast_TIMESTAMP.mp3   # Audio file
└── script-name_metadata_TIMESTAMP.json # Generation metadata
```

Metadata includes:
- Total duration
- Word count
- Generation timestamp
- Voice settings used
- Estimated cost
