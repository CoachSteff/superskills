# SuperSkills CLI Quick Start

## Installation Check

```bash
superskills --version
```

**If command not found,** run setup first:

```bash
cd /path/to/superskills
bash setup.sh  # Choose option 1 (pipx) for global access
```

See [Troubleshooting](#troubleshooting).

## Common Tasks

### Personalize Your Skills (5-15 Minutes)

**Why?** Profiles transform generic AI output into content that sounds like YOU.

**Quick Setup (Interactive):**
```bash
# Create your Master Briefing (brand voice foundation)
superskills call profile-builder "help me create my master briefing"

# Generate profiles for your most-used skills
superskills call profile-builder "generate a profile for copywriter"
superskills call profile-builder "generate a profile for researcher"
```

**Manual Setup:**
```bash
# Copy and edit Master Briefing template
cp MASTER_BRIEFING_TEMPLATE.yaml ~/.superskills/master-briefing.yaml
nano ~/.superskills/master-briefing.yaml  # Fill in your brand voice

# Copy and edit skill profiles
cp superskills/copywriter/PROFILE.md.template superskills/copywriter/PROFILE.md
nano superskills/copywriter/PROFILE.md  # Customize for your voice
```

**Test Your Profile:**
```bash
# Before profile: generic AI output
superskills call copywriter "Write a LinkedIn post about AI adoption"

# After profile: sounds like YOU
# (Same command, personalized output matching your brand voice)
```

**See full guide:** [PROFILE_CUSTOMIZATION.md](PROFILE_CUSTOMIZATION.md)

---

### Generate Podcast from Markdown

**Setup (one-time):**
```bash
# 1. Copy workflow templates
cp -r workflows_templates workflows

# 2. Set API keys
export ANTHROPIC_API_KEY=sk-ant-...
export ELEVENLABS_API_KEY=...

# Or add to .env file in project root
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
echo "ELEVENLABS_API_KEY=..." >> .env
```

**Generate:**
```bash
# Place script in input folder
cp /path/to/your-script.md workflows/podcast-generation/input/

# Option 1: Watch mode (auto-process new files)
superskills run podcast-generation --watch

# Option 2: Batch process all files
superskills run podcast-generation --batch

# Option 3: Single file
superskills run podcast-generation \
  --input /path/to/script.md
```

**Output:** Enhanced script + MP3 in `workflows/podcast-generation/output/`

### List Available Skills

```bash
superskills list
superskills show narrator
```

### Run Individual Skill

```bash
# Recommended: Use workflow
superskills run podcast-generation --input script.md

# Alternative: Direct skill call
superskills call narrator-podcast --input script.md

# Other content types
superskills call narrator-meditation --input meditation-script.md
superskills call narrator-educational --input lesson.md
```

## Troubleshooting

### Command Not Found

**If you haven't installed yet:**
```bash
cd /path/to/superskills
bash setup.sh
# Choose option 1 (pipx) for global access
```

**If pipx installed but command not found:**
```bash
pipx ensurepath
# Restart your terminal
```

**If using virtual environment (developers):**
```bash
cd /path/to/superskills
source .venv/bin/activate
superskills --version
```

**Alternative - use full path:**
```bash
# For pipx installation
~/.local/pipx/venvs/superskills/bin/superskills --help

# For venv installation
/path/to/superskills/.venv/bin/superskills --help
```

**Note:** `python3 -m cli` requires dependencies installed in system Python. Use virtual environment for best results.

### Model Errors

**If you see model-related errors:**

The CLI uses model aliases that automatically fall back to stable versions:
- `claude-3-sonnet-latest` → fallback to `claude-3-5-sonnet-20241022`
- `claude-3-opus-latest` → fallback to `claude-3-opus-20240229`
- `claude-3-haiku-latest` → fallback to `claude-3-5-haiku-20241022`

**If you see "model: claude-sonnet-4" or "claude-4.5-sonnet" error:**

This means you have an outdated config file. The CLI should auto-regenerate it, but if not:

```bash
# Option 1: Delete config (CLI will regenerate with claude-3-sonnet-latest)
rm ~/.superskills/config.yaml
superskills init

# Option 2: Edit manually
nano ~/.superskills/config.yaml
# Change: model: 'claude-4.5-sonnet'
# To:     model: 'claude-3-sonnet-latest'
```

**Customize model in config:**

Edit `~/.superskills/config.yaml`:
```yaml
api:
  anthropic:
    model: 'claude-3-sonnet-latest'  # or opus-latest, haiku-latest
    max_tokens: 4000
    temperature: 0.7
```

### Environment Variables Not Loading

**If API keys in .env are ignored:**

1. Ensure .env file is in project root:
   ```bash
   ls -la /path/to/superskills/.env
   ```

2. Verify format (no spaces around =):
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ELEVENLABS_API_KEY=...
   ```

3. The CLI auto-loads .env from (in order of precedence):
   - **Skill-specific** (highest): `superskills/{skill-name}/.env`
   - User config: `~/.superskills/.env`
   - Project root: `/path/to/superskills/.env`
   - **System env vars** (always respected)
   
   Note: Skill-specific .env files override global settings for that skill only.

4. Alternatively, export manually:
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...
   ```

### Configure Voice (Narrator Skill)

For custom voice (e.g., "CoachSteff" voice profile):

1. **Copy template:**
   ```bash
   cp superskills/narrator/voice_profiles.json.template \
      superskills/narrator/voice_profiles.json
   ```

2. **Get your ElevenLabs voice ID:**
   - Go to: https://elevenlabs.io/app/voice-library
   - Create or select your voice
   - Copy the voice ID

3. **Edit `voice_profiles.json`:**
   ```json
   {
     "podcast": {
       "voice_id": "YOUR_VOICE_ID_HERE",
       "name": "CoachSteff",
       "model": "eleven_turbo_v2_5",
       "stability": 0.5,
       "similarity_boost": 0.75,
       "style": 0.0,
       "use_speaker_boost": true
     }
   }
   ```

## Available Workflows

After copying templates (`cp -r workflows_templates workflows`), you'll have access to:

1. **podcast-generation** - Markdown scripts → Professional podcast audio
2. **content-creation** - Topic → Publication-ready article (researcher → strategist → author → editor)
3. **training-material** - Recordings → Structured training guides

See [workflows_templates/README.md](../workflows_templates/README.md) for complete documentation.

## File Locations

- **Templates:** `workflows_templates/` (read-only examples, in git)
- **Your Workflows:** `workflows/` (personal, gitignored)
- **Input:** `workflows/{workflow-name}/input/`
- **Output:** `workflows/{workflow-name}/output/`
- **Logs:** Run with `superskills --verbose run ...`
- **Config:** `workflows/{workflow-name}/workflow.yaml`

## Example: Complete Podcast Generation

```bash
# 1. Ensure API keys are set
export ANTHROPIC_API_KEY=sk-ant-...
export ELEVENLABS_API_KEY=...

# 2. Copy your markdown script
cp ~/Documents/my-podcast-script.md workflows/podcast-generation/input/

# 3. Generate podcast (watch mode)
superskills run podcast-generation --watch

# 4. Wait for processing to complete, then check output
ls -lh workflows/podcast-generation/output/
```

Expected output files:
- `my-podcast-script_enhanced_20241209_123456.md` - Enhanced narration script
- `my-podcast-script_podcast_20241209_123456.mp3` - Podcast audio (30 min)

## See Also

- [README.md](../README.md) - Complete documentation
- [CLI Setup Guide](../dev/CLI_SETUP.md) - Detailed installation
- [Workflow Templates](../workflows_templates/README.md) - All available workflows
- [CHANGELOG.md](../CHANGELOG.md) - Recent changes and migration guide
