"""
Workflow execution engine.
"""
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from cli.core.skill_executor import SkillExecutor
from cli.utils.config import CLIConfig
from cli.utils.paths import get_workflows_dir
from cli.utils.logger import get_logger
from cli.utils.progress import ProgressIndicator
from cli.utils.validation import WorkflowValidator, PathSanitizer


class WorkflowEngine:
    def __init__(self, config: CLIConfig, show_progress: bool = True):
        self.config = config
        self.executor = SkillExecutor(config)
        self.context: Dict[str, Any] = {}
        self.logger = get_logger()
        self.progress = ProgressIndicator(show_progress=show_progress)
        self.validator = WorkflowValidator()
    
    def load_workflow(self, workflow_name: str) -> Dict[str, Any]:
        self.logger.info(f"Loading workflow: {workflow_name}")
        workflow_file = self._find_workflow_file(workflow_name)
        
        if not workflow_file:
            self.logger.error(f"Workflow not found: {workflow_name}")
            raise FileNotFoundError(f"Workflow not found: {workflow_name}")
        
        # Validate workflow before loading
        self.logger.debug(f"Validating workflow: {workflow_file}")
        is_valid, errors = self.validator.validate_workflow(workflow_file)
        if not is_valid:
            error_msg = f"Workflow validation failed:\n  " + "\n  ".join(errors)
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.logger.debug(f"Reading workflow from: {workflow_file}")
        with open(workflow_file, 'r') as f:
            workflow = yaml.safe_load(f)
        
        self.logger.info(f"Workflow loaded: {workflow.get('name', workflow_name)} with {len(workflow.get('steps', []))} steps")
        return workflow
    
    def _find_workflow_file(self, workflow_name: str) -> Optional[Path]:
        """Find workflow file, checking both simple YAML files and folder-based workflows."""
        from ..utils.paths import get_project_root
        
        paths_to_check = [
            # Simple workflow definitions (YAML files in definitions/ or custom/)
            get_workflows_dir('definitions') / f"{workflow_name}.yaml",
            get_workflows_dir('custom') / f"{workflow_name}.yaml",
            # Folder-based workflows (workflow.yaml inside workflow folder)
            get_project_root() / 'workflows' / workflow_name / 'workflow.yaml',
        ]
        
        for path in paths_to_check:
            if path.exists():
                return path
        
        return None
    
    def execute(self, workflow_name: str, variables: Optional[Dict[str, Any]] = None, dry_run: bool = False) -> Dict[str, Any]:
        self.logger.info(f"Starting workflow execution: {workflow_name} (dry_run={dry_run})")
        workflow = self.load_workflow(workflow_name)
        
        if variables:
            self.logger.debug(f"Received variables: {list(variables.keys())}")
            self.context.update(variables)
        
        if 'variables' in workflow:
            for key, value in workflow['variables'].items():
                if key not in self.context:
                    resolved_value = self._resolve_variable(value)
                    self.context[key] = resolved_value
                    self.logger.debug(f"Set workflow variable: {key} = {resolved_value}")
        
        # If dry-run, just show what would happen
        if dry_run:
            return self._dry_run_workflow(workflow_name, workflow)
        
        results = {}
        total_steps = len(workflow.get('steps', []))
        
        with self.progress.create_workflow_progress(total_steps, f"Workflow: {workflow_name}") as prog:
            for idx, step in enumerate(workflow.get('steps', []), 1):
                step_name = step.get('name')
                skill_name = step.get('skill')
                
                self.logger.info(f"Step {idx}/{total_steps}: {step_name} (skill: {skill_name})")
                prog.update(idx - 1, f"Step {idx}/{total_steps}: {step_name}")
                
                input_text = self._resolve_variable(step.get('input', ''))
                self.logger.debug(f"Resolved input for step {step_name}: {len(input_text)} characters")
                
                step_config = step.get('config', {})
                
                result = self.executor.execute(skill_name, input_text, **step_config)
                
                output_var = step.get('output')
                if output_var:
                    self.context[output_var] = result['output']
                    results[step_name] = result
                    self.logger.debug(f"Stored output in variable: {output_var}")
            
            prog.update(total_steps, "Workflow completed")
        
        self.logger.info(f"Workflow {workflow_name} completed successfully")
        
        return {
            'workflow': workflow_name,
            'steps': results,
            'final_output': self.context.get(workflow.get('steps', [])[-1].get('output')) if workflow.get('steps') else None
        }
    
    def _resolve_variable(self, value: Any) -> Any:
        if not isinstance(value, str):
            return value
        
        if not value.startswith('${') or not value.endswith('}'):
            return value
        
        var_name = value[2:-1]
        
        if '.' in var_name:
            parts = var_name.split('.')
            current = self.context
            
            for part in parts:
                if isinstance(current, dict):
                    current = current.get(part)
                else:
                    return value
            
            return current if current is not None else value
        
        return self.context.get(var_name, value)
    
    def _dry_run_workflow(self, workflow_name: str, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform a dry-run of the workflow without executing skills.
        
        Shows what would happen without making API calls.
        """
        print(f"\n{'='*60}")
        print(f"DRY RUN: Workflow '{workflow_name}'")
        print(f"{'='*60}\n")
        
        print(f"Description: {workflow.get('description', 'No description')}")
        print(f"Total steps: {len(workflow.get('steps', []))}\n")
        
        # Show variables
        if 'variables' in workflow or self.context:
            print("Variables:")
            for key, value in self.context.items():
                value_preview = str(value)[:100] + '...' if len(str(value)) > 100 else str(value)
                print(f"  {key} = {value_preview}")
            print()
        
        # Show steps
        print("Execution Plan:")
        print("-" * 60)
        
        total_tokens_estimate = 0
        
        for idx, step in enumerate(workflow.get('steps', []), 1):
            step_name = step.get('name')
            skill_name = step.get('skill')
            input_template = step.get('input', '')
            output_var = step.get('output', 'None')
            
            # Resolve input to show what would be used
            try:
                resolved_input = self._resolve_variable(input_template)
            except:
                resolved_input = input_template
            
            input_length = len(resolved_input)
            # Rough token estimate (1 token ≈ 4 characters)
            estimated_tokens = input_length // 4 + 1000  # +1000 for output
            total_tokens_estimate += estimated_tokens
            
            print(f"\nStep {idx}: {step_name}")
            print(f"  Skill: {skill_name}")
            print(f"  Input: {input_length} characters (~{input_length//4} tokens)")
            
            if len(resolved_input) > 200:
                print(f"  Preview: {resolved_input[:200]}...")
            else:
                print(f"  Preview: {resolved_input}")
            
            print(f"  Output variable: {output_var}")
            print(f"  Est. API tokens: ~{estimated_tokens}")
            
            # Update context with placeholder for next step
            if output_var and output_var != 'None':
                self.context[output_var] = f"<output from {skill_name}>"
        
        print("\n" + "-" * 60)
        print(f"\nEstimated total API tokens: ~{total_tokens_estimate}")
        
        # Rough cost estimate (Claude Sonnet 4 pricing)
        # $3 per million input tokens, $15 per million output tokens
        # Assuming 50/50 split for simplicity
        avg_cost_per_million = (3 + 15) / 2
        estimated_cost = (total_tokens_estimate / 1_000_000) * avg_cost_per_million
        
        print(f"Estimated cost (Claude Sonnet 4): ~${estimated_cost:.4f}")
        
        print(f"\n{'='*60}")
        print("This was a DRY RUN - no actual API calls were made")
        print(f"{'='*60}\n")
        
        return {
            'workflow': workflow_name,
            'dry_run': True,
            'total_steps': len(workflow.get('steps', [])),
            'estimated_tokens': total_tokens_estimate,
            'estimated_cost': estimated_cost
        }
    
    def list_workflows(self) -> List[Dict[str, str]]:
        workflows = []
        
        for workflow_dir in ['definitions', 'custom']:
            dir_path = get_workflows_dir(workflow_dir)
            if not dir_path.exists():
                continue
            
            for workflow_file in dir_path.glob('*.yaml'):
                try:
                    with open(workflow_file, 'r') as f:
                        workflow = yaml.safe_load(f)
                    
                    workflows.append({
                        'name': workflow.get('name', workflow_file.stem),
                        'description': workflow.get('description', 'No description'),
                        'type': 'built-in' if workflow_dir == 'definitions' else 'custom',
                        'file': str(workflow_file)
                    })
                except Exception as e:
                    print(f"Warning: Failed to load {workflow_file}: {e}")
        
        # Scan folder-based workflows in workflows/ root
        workflows_root = get_workflows_dir()
        if workflows_root.exists():
            for workflow_folder in workflows_root.iterdir():
                if not workflow_folder.is_dir():
                    continue
                if workflow_folder.name in ['definitions', 'custom']:
                    continue  # Already scanned above
                
                workflow_file = workflow_folder / 'workflow.yaml'
                if workflow_file.exists():
                    try:
                        with open(workflow_file, 'r') as f:
                            workflow = yaml.safe_load(f)
                        
                        workflows.append({
                            'name': workflow.get('name', workflow_folder.name),
                            'description': workflow.get('description', 'No description'),
                            'type': 'user',
                            'file': str(workflow_file)
                        })
                    except Exception as e:
                        print(f"Warning: Failed to load {workflow_file}: {e}")
        
        return workflows
    
    def watch_and_execute(self, workflow_name: str, interval: int = 1) -> int:
        """
        Watch workflow input directory and automatically process new files.
        
        Args:
            workflow_name: Name of the workflow to execute
            interval: Check interval in seconds
            
        Returns:
            Exit code (0 for success)
        """
        import time
        from datetime import datetime
        
        self.logger.info(f"Starting watch mode for workflow: {workflow_name}")
        
        # Load workflow to get io configuration
        workflow = self.load_workflow(workflow_name)
        io_config = workflow.get('io', {})
        
        if not io_config or 'input_dir' not in io_config:
            print("Error: Workflow does not have io.input_dir configured")
            print("Watch mode requires a workflow with input/output directory configuration")
            return 1
        
        # Resolve input directory (relative to workflow file location)
        workflow_file = self._find_workflow_file(workflow_name)
        if not workflow_file:
            print(f"Error: Could not find workflow file for {workflow_name}")
            return 1
        
        workflow_dir = workflow_file.parent
        input_dir = workflow_dir / io_config['input_dir']
        
        if not input_dir.exists():
            print(f"Error: Input directory does not exist: {input_dir}")
            return 1
        
        print(f"Watching directory: {input_dir}")
        print(f"Check interval: {interval} second(s)\n")
        
        # Track processed files to avoid reprocessing
        processed_files = set()
        
        # Get initial file list
        for file_path in input_dir.glob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                processed_files.add(str(file_path))
        
        print(f"Ignoring {len(processed_files)} existing file(s)")
        print("Waiting for new files...\n")
        
        try:
            while True:
                # Check for new files
                current_files = set()
                for file_path in input_dir.glob('*'):
                    if file_path.is_file() and not file_path.name.startswith('.'):
                        current_files.add(str(file_path))
                
                new_files = current_files - processed_files
                
                for file_str in new_files:
                    file_path = Path(file_str)
                    print(f"\n{'='*60}")
                    print(f"New file detected: {file_path.name}")
                    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"{'='*60}\n")
                    
                    try:
                        # Read file content
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Execute workflow with file content
                        variables = {
                            'input': content,
                            'input_file': content,
                            'filename': file_path.stem
                        }
                        
                        result = self.execute(workflow_name, variables, dry_run=False)
                        
                        print(f"\n✓ Successfully processed: {file_path.name}")
                        processed_files.add(str(file_path))
                        
                    except Exception as e:
                        print(f"\n✗ Error processing {file_path.name}: {e}")
                        self.logger.error(f"Failed to process {file_path}: {e}", exc_info=True)
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\nWatch mode stopped")
            return 0
    
    def batch_execute(self, workflow_name: str) -> int:
        """
        Process all files in workflow input directory.
        
        Args:
            workflow_name: Name of the workflow to execute
            
        Returns:
            Exit code (0 for success, 1 for errors)
        """
        self.logger.info(f"Starting batch execution for workflow: {workflow_name}")
        
        # Load workflow to get io configuration
        workflow = self.load_workflow(workflow_name)
        io_config = workflow.get('io', {})
        
        if not io_config or 'input_dir' not in io_config:
            print("Error: Workflow does not have io.input_dir configured")
            print("Batch mode requires a workflow with input/output directory configuration")
            return 1
        
        # Resolve input directory
        workflow_file = self._find_workflow_file(workflow_name)
        if not workflow_file:
            print(f"Error: Could not find workflow file for {workflow_name}")
            return 1
        
        workflow_dir = workflow_file.parent
        input_dir = workflow_dir / io_config['input_dir']
        
        if not input_dir.exists():
            print(f"Error: Input directory does not exist: {input_dir}")
            return 1
        
        # Collect all files
        files_to_process = []
        for file_path in input_dir.glob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                files_to_process.append(file_path)
        
        if not files_to_process:
            print(f"No files found in {input_dir}")
            return 0
        
        print(f"Found {len(files_to_process)} file(s) to process\n")
        
        success_count = 0
        error_count = 0
        
        for idx, file_path in enumerate(files_to_process, 1):
            print(f"\n{'='*60}")
            print(f"Processing file {idx}/{len(files_to_process)}: {file_path.name}")
            print(f"{'='*60}\n")
            
            try:
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Execute workflow with file content
                variables = {
                    'input': content,
                    'input_file': content,
                    'filename': file_path.stem
                }
                
                result = self.execute(workflow_name, variables, dry_run=False)
                
                print(f"\n✓ Successfully processed: {file_path.name}")
                success_count += 1
                
            except Exception as e:
                print(f"\n✗ Error processing {file_path.name}: {e}")
                self.logger.error(f"Failed to process {file_path}: {e}", exc_info=True)
                error_count += 1
        
        print(f"\n{'='*60}")
        print(f"Batch processing completed")
        print(f"{'='*60}")
        print(f"  Success: {success_count}")
        print(f"  Errors:  {error_count}")
        print(f"  Total:   {len(files_to_process)}\n")
        
        return 0 if error_count == 0 else 1
