"""
CLI command: init - Initialize the SuperSkills CLI
"""
import shutil
from pathlib import Path
from cli.utils.config import CLIConfig
from cli.utils.paths import get_workflows_dir, get_project_root
from cli.core.skill_loader import SkillLoader


def _get_available_workflow_templates():
    """Get list of available workflow templates."""
    templates_dir = get_project_root() / 'workflows_templates'
    
    if not templates_dir.exists():
        return []
    
    templates = []
    for template_dir in templates_dir.iterdir():
        if template_dir.is_dir() and not template_dir.name.startswith('.'):
            workflow_file = template_dir / 'workflow.yaml'
            if workflow_file.exists():
                # Read description from README if available
                readme = template_dir / 'README.md'
                desc = "Example workflow"
                if readme.exists():
                    try:
                        with open(readme) as f:
                            lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
                            if lines:
                                desc = lines[0][:80]  # First non-empty, non-header line
                    except:
                        pass
                
                templates.append({
                    'name': template_dir.name,
                    'path': template_dir,
                    'description': desc
                })
    
    return sorted(templates, key=lambda x: x['name'])


def _copy_workflow_template(template_path, workflow_name):
    """Copy a workflow template to the workflows directory."""
    workflows_dir = get_workflows_dir()
    workflows_dir.mkdir(parents=True, exist_ok=True)
    
    dest_dir = workflows_dir / workflow_name
    
    # Check if already exists
    if dest_dir.exists():
        print(f"  ⚠ Workflow '{workflow_name}' already exists, skipping")
        return False
    
    try:
        # Copy entire template directory
        shutil.copytree(template_path, dest_dir)
        
        # Create input/output directories if they don't exist
        (dest_dir / 'input').mkdir(exist_ok=True)
        (dest_dir / 'output').mkdir(exist_ok=True)
        
        print(f"  ✓ Installed: {workflow_name}")
        return True
    except Exception as e:
        print(f"  ✗ Failed to copy {workflow_name}: {e}")
        return False


def _prompt_workflow_setup():
    """Interactively prompt user to set up workflow templates."""
    templates = _get_available_workflow_templates()
    
    if not templates:
        return 0
    
    print("\n" + "=" * 60)
    print("📦 Workflow Template Setup")
    print("=" * 60)
    print("\nAvailable workflow templates:\n")
    
    for idx, template in enumerate(templates, 1):
        print(f"  {idx}. {template['name']}")
        print(f"     {template['description']}\n")
    
    print(f"  {len(templates) + 1}. All of the above")
    print(f"  {len(templates) + 2}. Skip (manual setup later)\n")
    
    try:
        choice = input("Select option [1-{}]: ".format(len(templates) + 2)).strip()
        
        if not choice or not choice.isdigit():
            print("\nSkipping workflow setup.")
            return 0
        
        choice_num = int(choice)
        
        if choice_num == len(templates) + 2:
            print("\nSkipping workflow setup.")
            print("You can manually copy templates later from: workflows_templates/")
            return 0
        
        installed_count = 0
        
        if choice_num == len(templates) + 1:
            # Install all
            print("\nInstalling all workflow templates...")
            for template in templates:
                if _copy_workflow_template(template['path'], template['name']):
                    installed_count += 1
        
        elif 1 <= choice_num <= len(templates):
            # Install selected template
            template = templates[choice_num - 1]
            print(f"\nInstalling {template['name']}...")
            if _copy_workflow_template(template['path'], template['name']):
                installed_count += 1
        else:
            print("\nInvalid choice. Skipping workflow setup.")
            return 0
        
        if installed_count > 0:
            print(f"\n✓ {installed_count} workflow(s) installed\n")
            print("Next steps:")
            print("  • View workflows: superskills workflow list")
            print("  • Test a workflow: superskills run <workflow-name> --dry-run")
            print("  • Customize workflows: Edit workflows/<workflow-name>/workflow.yaml")
        
        return installed_count
    
    except KeyboardInterrupt:
        print("\n\nSkipping workflow setup.")
        return 0
    except Exception as e:
        print(f"\n\nError during workflow setup: {e}")
        return 0


def init_command(skip_workflows=False):
    """
    Initialize the SuperSkills CLI.
    
    Args:
        skip_workflows: If True, skip interactive workflow setup (for CI/CD)
    """
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
    gemini_ok = api_keys.get('GEMINI_API_KEY', False)
    anthropic_ok = api_keys.get('ANTHROPIC_API_KEY', False)
    
    if gemini_ok or anthropic_ok:
        print("✓ API keys configured")
    else:
        print("⚠ No API keys found")
        print("  → Set GEMINI_API_KEY or ANTHROPIC_API_KEY in your environment")
    
    # Check existing workflows
    workflows_dir = get_workflows_dir('definitions')
    existing_workflow_count = 0
    
    if workflows_dir.exists():
        existing_workflow_count = len(list(workflows_dir.glob('*.yaml')))
        print(f"✓ {existing_workflow_count} built-in workflow(s) available")
    
    # Check user workflows
    user_workflows_dir = get_workflows_dir()
    user_workflow_folders = []
    if user_workflows_dir.exists():
        user_workflow_folders = [
            d for d in user_workflows_dir.iterdir()
            if d.is_dir() and d.name not in ['definitions', 'custom', 'workflows_templates']
            and (d / 'workflow.yaml').exists()
        ]
    
    if user_workflow_folders:
        print(f"✓ {len(user_workflow_folders)} user workflow(s) installed")
    
    print("\n✓ Setup complete!")
    
    # Offer workflow template setup if no user workflows exist
    if not skip_workflows and not user_workflow_folders:
        templates = _get_available_workflow_templates()
        if templates:
            _prompt_workflow_setup()
    
    # Next steps guidance
    print("\nNext steps:")
    
    if not gemini_ok and not anthropic_ok:
        print("  1. Set GEMINI_API_KEY or ANTHROPIC_API_KEY in your environment")
    
    print("  2. List all skills: superskills list")
    print("  3. Try a skill: superskills call researcher \"AI trends\"")
    
    if existing_workflow_count > 0 or user_workflow_folders:
        print("  4. Run a workflow: superskills workflow list")
    
    return 0
