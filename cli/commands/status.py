"""
CLI command: status - Show CLI status and configuration
"""
from cli.core.skill_loader import SkillLoader
from cli.core.workflow_engine import WorkflowEngine
from cli.utils.config import CLIConfig


def status_command():
    config = CLIConfig()
    loader = SkillLoader()
    engine = WorkflowEngine(config)

    print("SuperSkills CLI Status\n")
    print("=" * 50)

    print("\nConfiguration:")
    print(f"  ✓ CLI directory: {config.config_dir}")

    skills = loader.discover_skills()
    print(f"  ✓ Skills registered: {len(skills)}")

    workflows = engine.list_workflows()
    builtin_count = len([w for w in workflows if w['type'] == 'built-in'])
    custom_count = len([w for w in workflows if w['type'] == 'custom'])
    print(f"  ✓ Workflows available: {len(workflows)} ({builtin_count} built-in, {custom_count} custom)")

    print("\nAPI Keys:")
    api_keys = config.check_api_keys()
    for key, status in api_keys.items():
        marker = "✓" if status else "✗"
        print(f"  {marker} {key}")

    print("\nRun: superskills list for all skills")
    print("Run: superskills workflow list for all workflows")

    return 0
