"""
Configuration management for CLI.
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


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
        
        return self._config
    
    def save(self):
        if self._config is None:
            return
        
        self.ensure_directories()
        
        with open(self.config_file, 'w') as f:
            yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)
    
    def _get_default_config(self) -> Dict[str, Any]:
        return {
            'api': {
                'anthropic': {
                    'model': 'claude-sonnet-4',
                    'max_tokens': 4000,
                    'temperature': 0.7
                }
            },
            'output': {
                'default_format': 'markdown',
                'save_intermediates': True
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
