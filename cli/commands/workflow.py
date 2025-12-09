"""
CLI command: workflow - Manage workflows
"""
from pathlib import Path
from cli.core.workflow_engine import WorkflowEngine
from cli.utils.config import CLIConfig
from cli.utils.validation import WorkflowValidator
from cli.utils.paths import get_workflows_dir
from cli.utils.formatters import WorkflowListFormatter


def workflow_list_command(**kwargs):
    output_format = kwargs.get('format', 'markdown')
    
    config = CLIConfig()
    engine = WorkflowEngine(config, show_progress=False)
    
    workflows = engine.list_workflows()
    
    if not workflows:
        print("No workflows found.")
        return 0
    
    output = WorkflowListFormatter.format(workflows, output_format)
    
    print(output)
    
    return 0


def workflow_validate_command(workflow_name: str):
    """
    Validate a workflow definition.
    
    Args:
        workflow_name: Name of workflow to validate
    
    Returns:
        0 if valid, 1 if invalid
    """
    # Find workflow file
    workflow_file = None
    for subdir in ['definitions', 'custom']:
        path = get_workflows_dir(subdir) / f"{workflow_name}.yaml"
        if path.exists():
            workflow_file = path
            break
    
    if not workflow_file:
        print(f"Error: Workflow '{workflow_name}' not found")
        print("\nRun 'superskills workflow list' to see available workflows")
        return 1
    
    print(f"Validating workflow: {workflow_name}")
    print(f"File: {workflow_file}\n")
    
    validator = WorkflowValidator()
    is_valid, errors = validator.validate_workflow(workflow_file)
    
    if is_valid:
        print("✓ Workflow is valid!")
        print("\nValidation checks passed:")
        print("  ✓ YAML syntax is correct")
        print("  ✓ Schema validation passed")
        print("  ✓ All referenced skills exist")
        print("  ✓ Variable references are valid")
        print("  ✓ No circular dependencies detected")
        return 0
    else:
        print("✗ Workflow validation failed!\n")
        print("Errors found:")
        for idx, error in enumerate(errors, 1):
            print(f"  {idx}. {error}")
        print("\nPlease fix these issues and try again.")
        return 1
