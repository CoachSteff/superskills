"""
SuperSkills package initialization.

This module handles dynamic imports for skills with hyphenated directory names
that cannot be imported directly due to Python's identifier restrictions.
"""
import sys
import importlib.machinery
import importlib.util
from pathlib import Path

# Map hyphenated skill names to their module paths
HYPHENATED_SKILLS = {
    'video_recorder': 'video-recorder',
    'slide_designer': 'slide-designer',
    'transcriber_local': 'transcriber-local',
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
    else:
        # No __init__.py in the skill directory. Register a synthetic package so
        # that 'superskills.<module_name>.src' is importable at all: Python
        # refuses a submodule whose parent is absent from sys.modules.
        spec = importlib.machinery.ModuleSpec(full_module, None, is_package=True)
        module = importlib.util.module_from_spec(spec)
        module.__path__ = [str(skill_dir)]
        sys.modules[full_module] = module
    
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
            # Bind it on the parent too, so 'from superskills.x.src import Y' works.
            parent = sys.modules.get(full_module)
            if parent is not None:
                setattr(parent, 'src', module)

# Register all hyphenated skills
for module_name, dir_name in HYPHENATED_SKILLS.items():
    _register_hyphenated_skill(module_name, dir_name)
