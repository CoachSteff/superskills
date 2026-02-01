"""
Migration utilities for exporting and importing profiles and settings.
"""
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
import shutil

from cli.utils.paths import get_project_root, get_user_config_dir


def collect_skill_profiles() -> List[Tuple[str, Path]]:
    """
    Collect all PROFILE.md files from skill directories.
    
    Returns:
        List of (skill_name, profile_path) tuples
    """
    profiles = []
    skills_dir = get_project_root() / "superskills"
    
    if not skills_dir.exists():
        return profiles
    
    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir():
            continue
        
        profile_path = skill_dir / "PROFILE.md"
        if profile_path.exists():
            profiles.append((skill_dir.name, profile_path))
    
    return profiles


def collect_skill_configs() -> List[Tuple[str, Path]]:
    """
    Collect all skill-specific configuration files.
    
    Returns:
        List of (relative_path, config_path) tuples
    """
    configs = []
    skills_dir = get_project_root() / "superskills"
    
    if not skills_dir.exists():
        return configs
    
    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir():
            continue
        
        skill_name = skill_dir.name
        
        # Check for config directory
        config_dir = skill_dir / "config"
        if config_dir.exists() and config_dir.is_dir():
            for config_file in config_dir.glob("*.yaml"):
                relative_path = f"{skill_name}/config/{config_file.name}"
                configs.append((relative_path, config_file))
        
        # Check for voice_profiles.json (narrator specific)
        voice_profiles = skill_dir / "voice_profiles.json"
        if voice_profiles.exists():
            relative_path = f"{skill_name}/voice_profiles.json"
            configs.append((relative_path, voice_profiles))
    
    return configs


def calculate_checksum(file_path: Path) -> str:
    """
    Calculate SHA256 checksum of a file.
    
    Args:
        file_path: Path to file
        
    Returns:
        Hex digest of SHA256 checksum
    """
    sha256 = hashlib.sha256()
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    
    return sha256.hexdigest()


def validate_manifest(manifest_data: Dict[str, Any]) -> bool:
    """
    Validate manifest structure and required fields.
    
    Args:
        manifest_data: Parsed manifest JSON
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['version', 'export_timestamp', 'files', 'flags']
    
    for field in required_fields:
        if field not in manifest_data:
            return False
    
    # Validate files structure
    if not isinstance(manifest_data['files'], dict):
        return False
    
    # Validate flags structure
    if not isinstance(manifest_data['flags'], dict):
        return False
    
    return True


def create_backup(files_to_backup: List[Path], backup_dir: Path) -> None:
    """
    Create backup of existing files before import.
    
    Args:
        files_to_backup: List of file paths to backup
        backup_dir: Directory to store backups
    """
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    for file_path in files_to_backup:
        if not file_path.exists():
            continue
        
        # Determine relative path for backup structure
        if file_path.is_relative_to(get_user_config_dir()):
            relative_path = file_path.relative_to(get_user_config_dir())
            backup_path = backup_dir / "user-config" / relative_path
        elif file_path.is_relative_to(get_project_root()):
            relative_path = file_path.relative_to(get_project_root())
            backup_path = backup_dir / "project" / relative_path
        else:
            # Fallback: use filename only
            backup_path = backup_dir / file_path.name
        
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_path)


def merge_env_files(existing_env: Dict[str, str], new_env: Dict[str, str]) -> Dict[str, str]:
    """
    Merge environment variables with strategy: keep existing non-empty, add new.
    
    Args:
        existing_env: Current environment variables
        new_env: New environment variables from import
        
    Returns:
        Merged environment variables
    """
    merged = existing_env.copy()
    
    for key, value in new_env.items():
        # Only add/update if existing key is empty or doesn't exist
        if key not in merged or not merged[key].strip():
            merged[key] = value
    
    return merged


def parse_env_file(env_path: Path) -> Dict[str, str]:
    """
    Parse .env file into dictionary.
    
    Args:
        env_path: Path to .env file
        
    Returns:
        Dictionary of environment variables
    """
    env_vars = {}
    
    if not env_path.exists():
        return env_vars
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip().strip('"').strip("'")
    
    return env_vars


def write_env_file(env_path: Path, env_vars: Dict[str, str]) -> None:
    """
    Write environment variables to .env file.
    
    Args:
        env_path: Path to .env file
        env_vars: Dictionary of environment variables
    """
    with open(env_path, 'w') as f:
        for key, value in sorted(env_vars.items()):
            f.write(f"{key}={value}\n")
