"""
Generic skill configuration loader.

Loads skill-specific execution configuration from standardized locations:
1. skill_root/brand/default.yaml (for brand-related skills)
2. skill_root/config/default.yaml (for technical skills)
3. skill_root/{skill_name}_config.json (legacy)

Falls back to environment variables and defaults.
"""
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
import json


class SkillConfigLoader:
    """Generic configuration loader for SuperSkills execution configs."""
    
    def __init__(self, skill_root: Path, skill_name: str):
        """
        Initialize the config loader.
        
        Args:
            skill_root: Root directory of the skill
            skill_name: Name of the skill (for legacy JSON lookups)
        """
        self.skill_root = Path(skill_root)
        self.skill_name = skill_name
        self._config_cache: Optional[Dict] = None
    
    def load(self, config_type: str = "auto") -> Dict[str, Any]:
        """
        Load configuration from standardized location.
        
        Args:
            config_type: "brand", "config", or "auto" (tries both)
        
        Returns:
            Configuration dictionary (empty dict if no config found)
        """
        if self._config_cache:
            return self._config_cache
        
        if config_type == "brand" or config_type == "auto":
            brand_path = self.skill_root / "brand" / "default.yaml"
            if brand_path.exists():
                return self._load_yaml(brand_path)
        
        if config_type == "config" or config_type == "auto":
            config_path = self.skill_root / "config" / "default.yaml"
            if config_path.exists():
                return self._load_yaml(config_path)
        
        json_path = self.skill_root / f"{self.skill_name}_config.json"
        if json_path.exists():
            return self._load_json(json_path)
        
        return {}
    
    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load YAML configuration file."""
        with open(path, 'r', encoding='utf-8') as f:
            self._config_cache = yaml.safe_load(f)
        return self._config_cache
    
    def _load_json(self, path: Path) -> Dict[str, Any]:
        """Load JSON configuration file."""
        with open(path, 'r', encoding='utf-8') as f:
            self._config_cache = json.load(f)
        return self._config_cache
