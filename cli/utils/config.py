"""
Configuration management for CLI.
"""
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class CLIConfig:
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

    def save(self):
        if self._config is None:
            return

        self.ensure_directories()

        with open(self.config_file, 'w') as f:
            yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)

    def _get_default_config(self) -> Dict[str, Any]:
        return {
            'version': '2.5.0',
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
