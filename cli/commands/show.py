"""
CLI command: show - Display detailed information about a skill
"""
from cli.core.skill_loader import SkillLoader
from cli.utils.master_briefing import MasterBriefingLoader


def show_command(skill_name: str):
    loader = SkillLoader()
    skill = loader.get_skill(skill_name)

    if not skill:
        print(f"Error: Skill '{skill_name}' not found")
        print("\nRun 'superskills list' to see all available skills")
        return 1

    print(f"Skill: {skill.name}")
    print(f"Type: {skill.skill_type}")
    print(f"Description: {skill.description}")
    print(f"Location: {skill.path}")

    if skill.python_module:
        print(f"Python Module: {skill.python_module}")

    print()

    if skill.has_profile:
        print("✓ Has custom PROFILE.md")
    else:
        profile_template = skill.path / "PROFILE.md.template"
        if profile_template.exists():
            print("⚠ PROFILE.md.template available but not customized")
            print("  → Copy to PROFILE.md to personalize this skill:")
            print(f"    cp {skill.path}/PROFILE.md.template {skill.path}/PROFILE.md")

    # Display Master Briefing status
    master_loader = MasterBriefingLoader()
    master_briefing = master_loader.load()

    if master_briefing:
        formatted = master_loader.format_for_prompt()
        print(f"\n✓ Master Briefing loaded (~{len(formatted)} chars)")
        print("  Location: ~/.superskills/master-briefing.yaml")
    else:
        print("\n⚠ No Master Briefing found")
        print("  Create one to establish global brand voice across all skills:")
        print("    superskills call profile-builder \"help me create my master briefing\"")

    print()
    print("SKILL.md Preview:")
    print("-" * 60)

    skill_md_path = skill.path / "SKILL.md"
    try:
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        preview_lines = lines[:30]

        for line in preview_lines:
            print(line)

        if len(lines) > 30:
            print(f"\n... ({len(lines) - 30} more lines)")
            print(f"\nFull content at: {skill_md_path}")

    except Exception as e:
        print(f"Error reading SKILL.md: {e}")
        return 1

    print("-" * 60)

    return 0
