"""
CLI command: validate - Validate skill integrity and completeness
"""
from pathlib import Path
from typing import List, Dict, Any
from cli.core.skill_loader import SkillLoader
from cli.utils.paths import get_skills_dir
import yaml


def validate_command():
    """
    Validate skill integrity and completeness.
    
    Checks:
    - All skills have SKILL.md files
    - YAML frontmatter is valid
    - Python skills have src/ directories
    - No deprecated .skill files exist
    - PROFILE.md.template exists for prompt skills
    """
    print("Checking skill integrity...\n")
    
    loader = SkillLoader()
    skills_dir = get_skills_dir()
    
    issues = []
    warnings = []
    
    all_dirs = [d for d in skills_dir.iterdir() 
                if d.is_dir() and d.name not in ['core', 'template', '__pycache__']]
    
    skill_count = len(all_dirs)
    skills_with_skill_md = 0
    python_skills = 0
    prompt_skills = 0
    
    for skill_dir in all_dirs:
        skill_name = skill_dir.name
        
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            issues.append(f"  - {skill_name}: Missing SKILL.md")
            continue
        
        skills_with_skill_md += 1
        
        if not _validate_yaml_frontmatter(skill_md):
            issues.append(f"  - {skill_name}: Invalid YAML frontmatter in SKILL.md")
        
        has_src = (skill_dir / "src").exists()
        has_profile_template = (skill_dir / "PROFILE.md.template").exists()
        
        if has_src:
            python_skills += 1
            
            if not any((skill_dir / "src").glob("*.py")):
                warnings.append(f"  - {skill_name}: Has src/ directory but no Python files")
            
            env_template = skill_dir / ".env.template"
            if not env_template.exists() and skill_name in loader.PYTHON_SKILLS:
                warnings.append(f"  - {skill_name}: Missing .env.template (API-dependent skill)")
        else:
            prompt_skills += 1
            
            if not has_profile_template:
                warnings.append(f"  - {skill_name}: Missing PROFILE.md.template")
        
        deprecated_skill_file = skill_dir / f"{skill_name}.skill"
        if deprecated_skill_file.exists():
            issues.append(f"  - {skill_name}: Contains deprecated .skill file")
    
    print(f"✓ {skill_count} total skill directories found")
    print(f"✓ {skills_with_skill_md} skills have SKILL.md")
    print(f"✓ {python_skills} Python skills")
    print(f"✓ {prompt_skills} Prompt skills")
    
    if not issues and not warnings:
        print("\n✓ All checks passed!")
        return 0
    
    if warnings:
        print(f"\n⚠ {len(warnings)} warnings found:")
        for warning in warnings:
            print(warning)
    
    if issues:
        print(f"\n✗ {len(issues)} issues found:")
        for issue in issues:
            print(issue)
        return 1
    
    return 0


def _validate_yaml_frontmatter(skill_md_path: Path) -> bool:
    """Validate YAML frontmatter in SKILL.md file."""
    try:
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.startswith('---'):
            return False
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            return False
        
        frontmatter = parts[1].strip()
        
        data = yaml.safe_load(frontmatter)
        
        if not isinstance(data, dict):
            return False
        
        if 'name' not in data or 'description' not in data:
            return False
        
        return True
    except Exception:
        return False
