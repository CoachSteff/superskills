"""
CLI command: init - Initialize the SuperSkills CLI
"""
from cli.utils.config import CLIConfig
from cli.utils.paths import get_workflows_dir
from cli.core.skill_loader import SkillLoader


def init_command():
    print("Initializing SuperSkills CLI...")
    
    config = CLIConfig()
    config.ensure_directories()
    config.load()
    
    print(f"✓ CLI directory created: {config.config_dir}")
    
    loader = SkillLoader()
    skills = loader.discover_skills()
    
    prompt_skills = [s for s in skills if s.skill_type == 'prompt']
    python_skills = [s for s in skills if s.skill_type == 'python']
    
    print(f"✓ Found {len(skills)} skills")
    print(f"  - {len(prompt_skills)} prompt-based skills")
    print(f"  - {len(python_skills)} Python-powered skills")
    
    api_keys = config.check_api_keys()
    anthropic_ok = api_keys.get('ANTHROPIC_API_KEY', False)
    
    if anthropic_ok:
        print("✓ API keys configured")
    else:
        print("⚠ ANTHROPIC_API_KEY not found")
        print("  → Set it in your environment or .env file")
    
    workflows_dir = get_workflows_dir('definitions')
    if workflows_dir.exists():
        workflow_count = len(list(workflows_dir.glob('*.yaml')))
        print(f"✓ {workflow_count} built-in workflows available")
    
    print("\n✓ Setup complete!")
    print("\nNext steps:")
    
    if not anthropic_ok:
        print("  1. Set ANTHROPIC_API_KEY in your environment")
    
    print("  2. List all skills: superskills list")
    print("  3. Try a skill: superskills call researcher \"AI trends\"")
    print("  4. Run a workflow: superskills run content-creation")
    
    return 0
