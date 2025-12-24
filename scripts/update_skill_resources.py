#!/usr/bin/env python3
"""
Update all SKILL.md files with Claude Skills compatible resource references.

This script:
1. Adds version: 1.0.0 to YAML frontmatter
2. Converts PROFILE.md text references to markdown links
3. Adds Master Briefing references
"""

import re
import sys
from pathlib import Path
from typing import Dict, Tuple

# Skills that use Python and may have .env.template
PYTHON_SKILLS = {
    'coursepackager', 'craft', 'designer', 'emailcampaigner',
    'marketer', 'narrator', 'obsidian', 'presenter',
    'scraper', 'transcriber', 'videoeditor'
}

# Skills that don't have PROFILE.md reference patterns
SPECIAL_CASES = {
    'profile-builder'  # Meta-skill that creates profiles
}


def read_skill_file(skill_path: Path) -> str:
    """Read SKILL.md file content."""
    with open(skill_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_skill_file(skill_path: Path, content: str):
    """Write updated SKILL.md content."""
    with open(skill_path, 'w', encoding='utf-8') as f:
        f.write(content)


def parse_frontmatter(content: str) -> Tuple[str, str, str]:
    """
    Split content into frontmatter, body.
    Returns: (frontmatter_lines, body, full_content)
    """
    if not content.startswith('---'):
        return '', content, content

    parts = content.split('---', 2)
    if len(parts) < 3:
        return '', content, content

    return parts[1].strip(), parts[2], content


def add_version_to_frontmatter(frontmatter: str) -> str:
    """Add version: 1.0.0 to frontmatter if not present."""
    lines = frontmatter.split('\n')

    # Check if version already exists
    for line in lines:
        if line.strip().startswith('version:'):
            return frontmatter

    # Find position to insert (after description, before license if it exists)
    new_lines = []
    inserted = False

    for line in lines:
        new_lines.append(line)
        if line.strip().startswith('description:') and not inserted:
            new_lines.append('version: 1.0.0')
            inserted = True

    # If not inserted after description, add at end
    if not inserted:
        new_lines.append('version: 1.0.0')

    return '\n'.join(new_lines)


def convert_profile_reference_to_link(body: str, skill_name: str) -> str:
    """Convert PROFILE.md text reference to markdown link."""

    # Pattern 1: In blockquote note
    # > **Note**: Review `PROFILE.md` in this skill folder...
    pattern1 = r'(> \*\*Note\*\*: Review) `PROFILE\.md`( in this skill folder)'
    replacement1 = r'\1 [PROFILE.md](PROFILE.md)\2'
    body = re.sub(pattern1, replacement1, body)

    # Pattern 2: In regular text
    # Review `PROFILE.md` for...
    pattern2 = r'Review `PROFILE\.md`'
    replacement2 = 'Review [PROFILE.md](PROFILE.md)'
    body = re.sub(pattern2, replacement2, body)

    # Pattern 3: Match the user's brand voice from PROFILE.md
    pattern3 = r'from PROFILE\.md'
    replacement3 = 'from [PROFILE.md](PROFILE.md)'
    body = re.sub(pattern3, replacement3, body)

    return body


def add_master_briefing_reference(body: str, skill_name: str, is_python: bool) -> str:
    """Add Master Briefing reference after PROFILE.md note."""

    # Special case: profile-builder doesn't have PROFILE.md
    if skill_name == 'profile-builder':
        # Find first heading after frontmatter
        lines = body.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('# '):
                # Insert after title
                lines.insert(i + 1, '')
                lines.insert(i + 2, '> **Note**: This skill helps you create PROFILE.md and Master Briefing files for other skills.')
                lines.insert(i + 3, '')
                return '\n'.join(lines)
        return body

    # Pattern: Find PROFILE.md note in blockquote
    pattern = r'(> \*\*Note\*\*: Review \[PROFILE\.md\]\(PROFILE\.md\)[^\n]+)'

    # Check if Master Briefing already mentioned
    if 'Master Briefing' in body:
        return body

    # Add Master Briefing reference
    def add_mb_note(match):
        original = match.group(1)
        mb_note = (
            f"{original}\n"
            f"> \n"
            f"> **Master Briefing**: Global brand voice at `~/.superskills/master-briefing.yaml` "
            f"applies automatically. Skill profile overrides when conflicts exist."
        )
        return mb_note

    body = re.sub(pattern, add_mb_note, body, count=1)

    return body


def update_skill_file(skill_path: Path, dry_run: bool = False) -> Dict:
    """
    Update a single SKILL.md file.
    
    Returns dict with status info.
    """
    skill_name = skill_path.parent.name
    is_python = skill_name in PYTHON_SKILLS

    try:
        # Read current content
        content = read_skill_file(skill_path)
        original_content = content

        # Parse frontmatter and body
        frontmatter, body, _ = parse_frontmatter(content)

        if not frontmatter:
            return {
                'skill': skill_name,
                'status': 'error',
                'message': 'No valid YAML frontmatter'
            }

        # Step 1: Add version to frontmatter
        new_frontmatter = add_version_to_frontmatter(frontmatter)

        # Step 2: Convert PROFILE.md reference to markdown link
        new_body = convert_profile_reference_to_link(body, skill_name)

        # Step 3: Add Master Briefing reference
        new_body = add_master_briefing_reference(new_body, skill_name, is_python)

        # Reconstruct file
        new_content = f"---\n{new_frontmatter}\n---{new_body}"

        # Check if anything changed
        if new_content == original_content:
            return {
                'skill': skill_name,
                'status': 'unchanged',
                'message': 'No changes needed'
            }

        # Write if not dry run
        if not dry_run:
            write_skill_file(skill_path, new_content)

        return {
            'skill': skill_name,
            'status': 'updated',
            'message': 'Successfully updated',
            'changes': {
                'version_added': 'version:' not in frontmatter,
                'profile_link': '[PROFILE.md](PROFILE.md)' in new_body and '[PROFILE.md](PROFILE.md)' not in body,
                'master_briefing': 'Master Briefing' in new_body and 'Master Briefing' not in body
            }
        }

    except Exception as e:
        return {
            'skill': skill_name,
            'status': 'error',
            'message': str(e)
        }


def main():
    """Main execution."""
    dry_run = '--dry-run' in sys.argv

    project_root = Path(__file__).parent.parent
    skills_dir = project_root / 'superskills'

    if not skills_dir.exists():
        print(f"Error: Skills directory not found: {skills_dir}")
        return 1

    # Find all SKILL.md files
    skill_files = list(skills_dir.glob('*/SKILL.md'))

    print(f"{'DRY RUN - ' if dry_run else ''}Updating {len(skill_files)} SKILL.md files...\n")

    results = {
        'updated': [],
        'unchanged': [],
        'errors': []
    }

    for skill_file in sorted(skill_files):
        result = update_skill_file(skill_file, dry_run=dry_run)

        status = result['status']
        skill_name = result['skill']

        if status == 'updated':
            results['updated'].append(result)
            changes = result.get('changes', {})
            change_list = []
            if changes.get('version_added'):
                change_list.append('version')
            if changes.get('profile_link'):
                change_list.append('PROFILE link')
            if changes.get('master_briefing'):
                change_list.append('Master Briefing')
            print(f"✓ {skill_name:30s} - Updated ({', '.join(change_list)})")

        elif status == 'unchanged':
            results['unchanged'].append(result)
            print(f"  {skill_name:30s} - No changes needed")

        elif status == 'error':
            results['errors'].append(result)
            print(f"✗ {skill_name:30s} - ERROR: {result['message']}")

    # Summary
    print(f"\n{'='*60}")
    print("Summary:")
    print(f"  ✓ Updated: {len(results['updated'])}")
    print(f"    Unchanged: {len(results['unchanged'])}")
    print(f"  ✗ Errors: {len(results['errors'])}")

    if dry_run:
        print("\n⚠️  DRY RUN - No files were modified")
        print("   Run without --dry-run to apply changes")

    return 0 if len(results['errors']) == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
