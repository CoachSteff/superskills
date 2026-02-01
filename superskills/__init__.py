"""
SuperSkills package initialization.

This module handles dynamic imports for skills with hyphenated directory names
that cannot be imported directly due to Python's identifier restrictions.
"""
import sys
import importlib.util
from pathlib import Path

# Map hyphenated skill names to their module paths
HYPHENATED_SKILLS = {
    'video_recorder': 'video-recorder',
    'slide_designer': 'slide-designer',
}

def _register_hyphenated_skill(module_name: str, dir_name: str):
    """
    Register a hyphenated skill directory as an importable module.
    
    Args:
        module_name: Python-compatible name (e.g., 'video_recorder')
        dir_name: Actual directory name (e.g., 'video-recorder')
    """
    skill_dir = Path(__file__).parent / dir_name
    if not skill_dir.exists():
        return
    
    full_module = f"superskills.{module_name}"
    
    main_init = skill_dir / '__init__.py'
    if main_init.exists():
        spec = importlib.util.spec_from_file_location(
            full_module,
            str(main_init)
        )
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[full_module] = module
            try:
                spec.loader.exec_module(module)
            except Exception:
                pass
    
    src_init = skill_dir / 'src' / '__init__.py'
    if src_init.exists():
        spec = importlib.util.spec_from_file_location(
            f"{full_module}.src",
            str(src_init)
        )
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[f"{full_module}.src"] = module
            try:
                spec.loader.exec_module(module)
            except Exception:
                pass

# Register all hyphenated skills
for module_name, dir_name in HYPHENATED_SKILLS.items():
    _register_hyphenated_skill(module_name, dir_name)
