# Unused Configuration Files

These YAML files exist but are **NOT loaded by Python code** in the skill's `src/` directory.

## Why These Files Exist

They may be:
- **Documentation** of potential config structure for future features
- **Placeholders** from initial skill design
- **Legacy files** that were replaced by hardcoded defaults or API parameters

## What This Means

The Python execution code does **not** read these files. Configuration is handled via:
- Hardcoded defaults in Python source
- Runtime parameters passed to the skill
- Environment variables (API keys, credentials)
- Direct API configuration objects

## If You Need Execution Config

If you want to make these skills configurable via YAML:

1. **Implement loading in Python**:
   ```python
   from cli.utils.skill_config import SkillConfigLoader
   
   loader = SkillConfigLoader(skill_root=Path(__file__).parent.parent, skill_name="scraper")
   config = loader.load(config_type="config")
   ```

2. **Create a template**: `config/default.yaml.template`

3. **Update gitignore**: Ensure `**/config/*.yaml` is ignored (already done)

4. **Document in SKILL.md**: Explain config structure

## Current Skills

- **scraper**: `scraper_config.yaml` - Web scraping parameters (unused)
- **transcriber**: `transcriber_config.yaml` - Transcription settings (unused)
- **craft**: `craft_config.yaml` - Craft.do API settings (unused)
- **videoeditor**: `videoeditor_config.yaml` - Video editing settings (unused)

## SuperSkills Config Architecture

For reference, see how **slide-designer**, **video-recorder**, and **narrator** implement working configs:
- slide-designer: `brand/default.yaml` loaded by `StyleEngine.py`
- video-recorder: `brand/default.yaml` loaded by `SlideRenderer.py`
- narrator: `voice_profiles.json` loaded by `VoiceConfig.py`
