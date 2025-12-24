#!/usr/bin/env python3
"""
Validate that all SKILL.md files follow Claude Skills structure.

Checks:
1. Valid YAML frontmatter with required fields
2. Version field present
3. PROFILE.md references are markdown links
4. Master Briefing mentioned
5. Markdown links point to existing files or templates
"""

import sys
from pathlib import Path
from typing import Dict


def read_file(path: Path) -> str:
    """Read file content."""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def parse_frontmatter(content: str) -> Dict:
    """Extract and parse YAML frontmatter."""
    if not content.startswith('---'):
        return {}

    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}

    frontmatter_text = parts[1].strip()
    body = parts[2]

    # Parse YAML (simple key: value pairs)
    metadata = {}
    for line in frontmatter_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip()

    metadata['_body'] = body
    return metadata


def validate_skill(skill_path: Path) -> Dict:
    """
    Validate a single SKILL.md file.

    Returns dict with validation results.
    """
    skill_name = skill_path.parent.name
    issues = []
    warnings = []

    try:
        content = read_file(skill_path)
        metadata = parse_frontmatter(content)

        if not metadata:
            issues.append("No valid YAML frontmatter")
            return {
                'skill': skill_name,
                'valid': False,
                'issues': issues,
                'warnings': warnings
            }

        body = metadata.get('_body', '')

        # Check 1: Required fields
        if 'name' not in metadata:
            issues.append("Missing 'name' field in frontmatter")

        if 'description' not in metadata:
            issues.append("Missing 'description' field in frontmatter")

        # Check 2: Version field
        if 'version' not in metadata:
            issues.append("Missing 'version' field in frontmatter")

        # Check 3: PROFILE.md references should be markdown links
        if 'PROFILE.md' in body:
            # Check if it's a markdown link
            if '[PROFILE.md](PROFILE.md)' not in body and 'PROFILE.md' in body:
                # Check if it's plain text reference (should be converted)
                if '`PROFILE.md`' in body:
                    issues.append("PROFILE.md referenced as plain text, should be markdown link")

        # Check 4: Master Briefing mentioned (except profile-builder)
        if skill_name != 'profile-builder':
            if 'Master Briefing' not in body:
                warnings.append("Master Briefing not mentioned")

        # Check 5: Check for PROFILE.md or template existence
        skill_dir = skill_path.parent
        profile_md = skill_dir / "PROFILE.md"
        profile_template = skill_dir / "PROFILE.md.template"

        if not profile_md.exists() and not profile_template.exists():
            if skill_name != 'profile-builder':
                warnings.append("Neither PROFILE.md nor PROFILE.md.template exists")
        elif not profile_md.exists() and profile_template.exists():
            warnings.append("PROFILE.md.template exists but not customized to PROFILE.md")

        return {
            'skill': skill_name,
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

    except Exception as e:
        return {
            'skill': skill_name,
            'valid': False,
            'issues': [f"Exception: {str(e)}"],
            'warnings': []
        }


def main():
    """Main validation."""
    project_root = Path(__file__).parent.parent
    skills_dir = project_root / 'superskills'

    if not skills_dir.exists():
        print(f"Error: Skills directory not found: {skills_dir}")
        return 1

    # Find all SKILL.md files
    skill_files = list(skills_dir.glob('*/SKILL.md'))

    print(f"Validating {len(skill_files)} SKILL.md files...\n")

    results = {
        'valid': [],
        'invalid': [],
        'warnings': []
    }

    for skill_file in sorted(skill_files):
        result = validate_skill(skill_file)

        skill_name = result['skill']
        valid = result['valid']
        issues = result['issues']
        warnings = result['warnings']

        if valid and not warnings:
            results['valid'].append(result)
            print(f"✓ {skill_name:30s} - OK")

        elif valid and warnings:
            results['warnings'].append(result)
            print(f"⚠ {skill_name:30s} - OK with warnings:")
            for warning in warnings:
                print(f"    • {warning}")

        else:
            results['invalid'].append(result)
            print(f"✗ {skill_name:30s} - INVALID:")
            for issue in issues:
                print(f"    • {issue}")
            if warnings:
                print("  Warnings:")
                for warning in warnings:
                    print(f"    • {warning}")

    # Summary
    print(f"\n{'='*60}")
    print("Summary:")
    print(f"  ✓ Valid: {len(results['valid'])}")
    print(f"  ⚠ Valid with warnings: {len(results['warnings'])}")
    print(f"  ✗ Invalid: {len(results['invalid'])}")

    # Detailed checks
    total = len(skill_files)

    # Count specific validations
    has_version = sum(1 for f in skill_files if 'version:' in read_file(f))
    has_profile_link = sum(1 for f in skill_files if '[PROFILE.md](PROFILE.md)' in read_file(f))
    has_master_briefing = sum(1 for f in skill_files if 'Master Briefing' in read_file(f))

    print("\nDetailed Checks:")
    print(f"  ✓ {has_version}/{total} have version field")
    print(f"  ✓ {has_profile_link}/{total} have PROFILE.md as markdown link")
    print(f"  ✓ {has_master_briefing}/{total} mention Master Briefing")

    if len(results['invalid']) > 0:
        print(f"\n⚠️  {len(results['invalid'])} skills failed validation")
        return 1

    print("\n✅ All skills passed validation!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
