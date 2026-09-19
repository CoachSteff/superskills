"""
Configuration management for CLI.
"""
import os
<<<<<<< Updated upstream
=======
import shutil
import yaml
>>>>>>> Stashed changes
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from cli.utils.version import get_version


class CLIConfig:
    # Model names known to break at runtime (removed/renamed API models).
    # Only these exact values are scrubbed during migration; everything
    # else the user configured is preserved.
    INVALID_MODELS = {
        'claude-4.5-sonnet',
        'gemini-flash-2',
        'gemini-2.0-flash-exp',
        'gemini-3-flash-preview',
    }

    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            config_dir = Path.home() / ".superskills"

        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.yaml"
        self.history_file = self.config_dir / "history.json"
        self.cache_dir = self.config_dir / "cache"

        self._config: Optional[Dict] = None

    def ensure_directories(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> Dict[str, Any]:
        if self._config is not None:
            return self._config

        if not self.config_file.exists():
            self._config = self._get_default_config()
            self.save()
            return self._config

<<<<<<< Updated upstream
        with open(self.config_file, 'r') as f:
            self._config = yaml.safe_load(f) or {}

        # Auto-regenerate if version mismatch or invalid model
        needs_regen = False
        current_version = self._config.get('version')

        if current_version != '2.5.0':
            needs_regen = True

        # Check for old config structure (api.anthropic.*)
        if 'anthropic' in self._config.get('api', {}):
            needs_regen = True

        # Check for invalid model names
        model = str(self._config.get('api', {}).get('model', ''))
        intent_model = str(self._config.get('intent', {}).get('model', ''))
        if ('claude-sonnet-4' in model or
            model == 'claude-4.5-sonnet' or
            intent_model == 'gemini-flash-2' or
            intent_model == 'gemini-2.0-flash-exp' or
            intent_model == 'gemini-3-flash-preview' or
            model == 'gemini-flash-2' or
            model == 'gemini-2.0-flash-exp' or
            model == 'gemini-3-flash-preview'):
            needs_regen = True

        if needs_regen:
            old_version = current_version or 'unknown'
            print(f"⚠ Config updated from {old_version} to v2.5.0. Now using stable Gemini 1.5 Flash.")
            self._config = self._get_default_config()
            self.save()

        return self._config

=======
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            backup = self._backup_config('corrupt')
            print(f"⚠ Config file is not valid YAML ({e}).")
            print(f"  Backed up to {backup.name} and regenerated defaults.")
            self._config = self._get_default_config()
            self.save()
            return self._config

        if not isinstance(user_config, dict):
            user_config = {}

        self._config = self._migrate_config(user_config)
        return self._config

    def _migrate_config(self, user_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate a loaded config to the current version, PRESERVING user
        customizations: defaults fill in what's missing, user values win,
        and only known-broken values are scrubbed.
        """
        app_version = get_version()
        current_version = str(user_config.get('version') or '')

        # Detect what needs fixing
        version_mismatch = app_version != 'unknown' and current_version != app_version
        legacy_structure = 'anthropic' in user_config.get('api', {})
        scrubbed = self._scrub_invalid_models(user_config)

        if not (version_mismatch or legacy_structure or scrubbed):
            return user_config

        backup = self._backup_config(current_version or 'unknown')

        if legacy_structure:
            # Old api.anthropic.* layout is incompatible with the current
            # flat api.* structure; that section reverts to defaults.
            user_config.pop('api', None)

        user_config.pop('version', None)
        migrated = self._deep_merge(self._get_default_config(), user_config)
        if app_version != 'unknown':
            migrated['version'] = app_version

        old = current_version or 'unknown'
        print(f"⚠ Config migrated from {old} to v{migrated['version']} "
              f"(backup: {backup.name}). Your custom settings were preserved.")
        if scrubbed:
            print(f"  Replaced unavailable model(s) {', '.join(sorted(scrubbed))} with defaults.")

        self._config = migrated
        self.save()
        return migrated

    def _scrub_invalid_models(self, config: Dict[str, Any]) -> set:
        """Remove known-broken model values so defaults take over. Returns the removed values."""
        removed = set()
        for section in ('api', 'intent'):
            section_cfg = config.get(section)
            if not isinstance(section_cfg, dict):
                continue
            model = str(section_cfg.get('model', ''))
            if model in self.INVALID_MODELS or 'claude-sonnet-4' in model:
                removed.add(model)
                section_cfg.pop('model', None)
        return removed

    def _backup_config(self, tag: str) -> Path:
        """Copy the current config file aside before rewriting it."""
        safe_tag = tag.replace('/', '_')
        backup = self.config_file.with_name(f"config.yaml.bak-{safe_tag}")
        shutil.copy2(self.config_file, backup)
        return backup

    @staticmethod
    def _deep_merge(defaults: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge overrides onto defaults (overrides win)."""
        result = dict(defaults)
        for key, value in overrides.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = CLIConfig._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
>>>>>>> Stashed changes
    def save(self):
        if self._config is None:
            return

        self.ensure_directories()

        with open(self.config_file, 'w') as f:
            yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)

    def _get_default_config(self) -> Dict[str, Any]:
        return {
            'version': get_version(),
            'api': {
                'provider': 'gemini',
                'model': 'gemini-flash-latest',
                'max_tokens': 4000,
                'temperature': 0.7
            },
            'intent': {
                'enabled': True,
                'provider': 'gemini',
                'model': 'gemini-flash-latest',
                'confidence_threshold': 0.5,
                'always_confirm_medium': True
            },
            'search': {
                'paths': [
                    '${OBSIDIAN_VAULT_PATH}',
                    '~/Documents',
                    '~/Downloads',
                    '.'
                ],
                'use_ripgrep': True,
                'max_results': 50
            },
            'output': {
                'default_format': 'markdown',
                'save_intermediates': True,
                'auto_save': True,
                'directory': './output'
            },
            'workflows': {
                'auto_save': True,
                'show_progress': True
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        config = self.load()

        keys = key.split('.')
        value = config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

            if value is None:
                return default

        return value

    def set(self, key: str, value: Any):
        config = self.load()

        keys = key.split('.')
        current = config

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value
        self.save()

    def get_api_key(self, service: str) -> Optional[str]:
        env_var_map = {
            'anthropic': 'ANTHROPIC_API_KEY',
            'elevenlabs': 'ELEVENLABS_API_KEY',
            'openai': 'OPENAI_API_KEY',
            'gemini': 'GEMINI_API_KEY'
        }

        env_var = env_var_map.get(service)
        if env_var:
            return os.getenv(env_var)

        return None

    def check_api_keys(self) -> Dict[str, bool]:
        return {
            'ANTHROPIC_API_KEY': bool(os.getenv('ANTHROPIC_API_KEY')),
            'ELEVENLABS_API_KEY': bool(os.getenv('ELEVENLABS_API_KEY')),
            'OPENAI_API_KEY': bool(os.getenv('OPENAI_API_KEY')),
            'GEMINI_API_KEY': bool(os.getenv('GEMINI_API_KEY'))
        }

    def get_output_dir(self) -> Path:
        """
        Get the output directory path from config.
        
        Returns absolute path, creating directory if it doesn't exist.
        """
        from cli.utils.paths import get_project_root
        
        configured_path = self.get('output.directory', './output')
        
        # Resolve path relative to project root if relative
        if configured_path.startswith('./') or configured_path.startswith('.\\'):
            output_dir = get_project_root() / configured_path[2:]
        elif configured_path.startswith('~'):
            output_dir = Path(configured_path).expanduser()
        else:
            output_dir = Path(configured_path)
        
        # Create directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        return output_dir
