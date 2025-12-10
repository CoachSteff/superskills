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

### Generate Podcast from Markdown

**Setup (one-time):**
```bash
# Set API keys
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
superskills call narrator \
  --input script.md \
  --content-type podcast \
  --profile-type podcast
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

**If you see "model: claude-sonnet-4" error:**

This means you have an outdated config file. The CLI should auto-regenerate it, but if not:

```bash
# Option 1: Delete config (CLI will regenerate with claude-4.5-sonnet)
rm ~/.superskills/config.yaml
superskills init

# Option 2: Edit manually
nano ~/.superskills/config.yaml
# Change: model: 'claude-sonnet-4'
# To:     model: 'claude-4.5-sonnet'
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

## File Locations

- **Input:** `workflows/podcast-generation/input/`
- **Output:** `workflows/podcast-generation/output/`
- **Logs:** Run with `superskills --verbose run ...`
- **Config:** `workflows/podcast-generation/workflow.yaml`

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

- [README.md](README.md) - Complete documentation
- [CLI Setup Guide](dev/CLI_SETUP.md) - Detailed installation
- [Podcast Workflow](workflows/podcast-generation/README.md) - Workflow specifics
- [CHANGELOG.md](CHANGELOG.md) - Recent changes and migration guide
