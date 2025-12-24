"""
CLI command: list - List all available skills
"""
from cli.core.skill_loader import SkillLoader
from cli.utils.formatters import SkillListFormatter


def list_command(**kwargs):
    output_format = kwargs.get('format', 'markdown')

    loader = SkillLoader()
    skills = loader.discover_skills()

    output = SkillListFormatter.format(skills, output_format)

    print(output)

    return 0
