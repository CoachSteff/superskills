# Training Material Development Workflow

Convert training session recordings into structured, reusable documentation.

## Overview

This workflow:
1. **Transcribes** audio/video recordings (transcriber)
2. **Structures** content into learning-optimized format (author)
3. **Polishes** for clarity and instructional quality (editor)

## Prerequisites

**API Keys:**
- `OPENAI_API_KEY` or `ASSEMBLYAI_API_KEY` - For transcription
- `ANTHROPIC_API_KEY` - For structuring and editing

**Setup:**
```bash
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
```

## Quick Start

**1. Copy template:**
```bash
cp -r workflows_templates/training-material workflows/
```

**2. Add your recording:**
```bash
cp training-session.mp4 workflows/training-material/input/
```

**3. Run workflow:**
```bash
superskills run training-material --input workflows/training-material/input/training-session.mp4
```

**4. Get structured training guide:**
```bash
ls workflows/training-material/output/

# Output:
# training-session_transcript_TIMESTAMP.txt
# training-session_structured_TIMESTAMP.md
# training-session_final_TIMESTAMP.md
```

## Supported Formats

**Audio:** MP3, WAV, M4A, FLAC  
**Video:** MP4, MOV, AVI, MKV

Max file size: 25MB (OpenAI Whisper) or 2GB (AssemblyAI)

## Output Structure

The final training material includes:

1. **Learning Objectives** - What participants will learn
2. **Prerequisites** - Required knowledge/tools
3. **Key Concepts** - Core ideas with explanations
4. **Step-by-Step Procedures** - Actionable how-to sections
5. **Examples** - Real scenarios from the session
6. **Common Questions** - FAQ from participant questions
7. **Takeaways** - Summary and next actions
8. **Resources** - Links, tools, references mentioned

## Customization

**Training type:**
```yaml
variables:
  training_type: "course"  # workshop, webinar, course, tutorial
```

**Transcription provider:**
```yaml
config:
  provider: assemblyai  # whisper (OpenAI), assemblyai
```

**Speaker labels:**
```yaml
config:
  include_speaker_labels: true  # Identifies different speakers
```

## Expected Costs

For 60-minute training session:
- Transcription: ~$0.36 (Whisper) or ~$0.60 (AssemblyAI)
- Structuring: ~$0.20 (Claude Sonnet)
- Editing: ~$0.10
- **Total: ~$0.66-$0.90 per hour of recording**

## Advanced Usage

**Batch process multiple sessions:**
```bash
cp session-*.mp4 workflows/training-material/input/
superskills run training-material --batch
```

**Customize output format:**

Edit workflow.yaml to add custom instructions:
```yaml
- name: structure
  skill: author
  input: |
    Transcript: ${transcript}
    
    Additional requirements:
    - Include quiz questions
    - Add code examples
    - Create visual diagrams descriptions
```

**Multi-language support:**
```yaml
config:
  language: es  # Spanish, French (fr), German (de), etc.
```

## Tips for Best Results

1. **Good audio quality** = better transcription accuracy
2. **Shorter sessions** (30-60 min) = more focused materials
3. **Clear speaker introductions** = better speaker labels
4. **Visual content:** Mention what's on screen during recording
5. **Review transcript first:** Correct any errors before structuring

## Troubleshooting

**Issue: Poor transcription accuracy**
- Use AssemblyAI instead of Whisper (better for low-quality audio)
- Clean up audio with noise reduction before processing
- Speak clearly and avoid overlapping speakers

**Issue: Generic training content**
- Add training context to workflow variables
- Include your teaching style in PROFILE.md
- Specify target audience skill level

**Issue: Missing visual elements**
- Narrate screen content during recording
- Add slide deck separately as reference
- Edit final output to insert [Screenshot] placeholders

## Integration with Other Workflows

Combine with other skills:

**Training → Slides:**
```bash
# 1. Generate training material
superskills run training-material --input session.mp4

# 2. Create presentation
superskills call presenter --input workflows/training-material/output/final_*.md
```

**Training → Quiz:**
```bash
# Use output to create assessment
superskills call author "Create 10 quiz questions from: $(cat final_training.md)"
```
