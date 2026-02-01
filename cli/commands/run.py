"""
CLI command: run - Execute a workflow
"""
from pathlib import Path

from cli.core.workflow_engine import WorkflowEngine
from cli.utils.config import CLIConfig
from cli.utils.formatters import OutputFormatter


def run_command(workflow_name: str, **kwargs):
    config = CLIConfig()

    output_format = kwargs.get('format', 'markdown')
    dry_run = kwargs.get('dry_run', False)
    watch = kwargs.get('watch', False)
    batch = kwargs.get('batch', False)
    no_save = kwargs.get('no_save', False)
    silent = output_format == 'plain'
    show_progress = not dry_run and not silent

    engine = WorkflowEngine(config, show_progress=show_progress)

    # Watch mode: monitor input directory and auto-process files
    if watch:
        try:
            print(f"Starting watch mode for workflow: {workflow_name}")
            print("Press Ctrl+C to stop\n")
            return engine.watch_and_execute(workflow_name, interval=kwargs.get('interval', 1))
        except KeyboardInterrupt:
            print("\n\nWatch mode stopped by user.")
            return 0
        except Exception as e:
            print(f"Error in watch mode: {e}")
            import traceback
            traceback.print_exc()
            return 1

    # Batch mode: process all files in input directory
    if batch:
        try:
            print(f"Batch processing workflow: {workflow_name}\n")
            return engine.batch_execute(workflow_name)
        except Exception as e:
            print(f"Error in batch mode: {e}")
            import traceback
            traceback.print_exc()
            return 1

    # Standard single execution mode
    if not dry_run and not silent:
        print(f"Running workflow: {workflow_name}\n")

    try:
        variables = {}

        if 'input' in kwargs and kwargs['input']:
            input_path = Path(kwargs['input'])
            if input_path.exists():
                with open(input_path, 'r', encoding='utf-8') as f:
                    variables['input'] = f.read()
            else:
                variables['input'] = kwargs['input']

        for key, value in kwargs.items():
            if key not in ['input', 'output', 'dry_run', 'format', 'watch', 'batch', 'interval']:
                variables[key] = value

        result = engine.execute(workflow_name, variables, dry_run=dry_run)

        if dry_run:
            return 0

        # Prepare data for formatting
        result_data = {
            'workflow': workflow_name,
            'final_output': result.get('final_output', ''),
            'metadata': {
                'steps_executed': len(result.get('steps', {}))
            }
        }

        # Determine where to save output
        auto_save = config.get('output.auto_save', True) and not no_save
        
        # Save to file if requested
        if 'output' in kwargs and kwargs['output']:
            # Explicit output file specified
            output_file = Path(kwargs['output'])
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(str(result.get('final_output', '')))

            if not silent:
                print(f"\n✓ Workflow completed: {workflow_name}")
                print(f"✓ Output saved to: {output_file}")
        elif auto_save and output_format != 'plain':
            # Auto-save to output directory
            from cli.utils.paths import generate_output_filename
            
            output_dir = config.get_output_dir()
            output_filename = generate_output_filename(workflow_name, output_format)
            output_path = output_dir / output_filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(str(result.get('final_output', '')))
            
            # Print formatted output to terminal
            formatted_output = OutputFormatter.format(result_data, output_format)
            print(formatted_output)
            print(f"\n✓ Output saved to: {output_path}")
        else:
            # Print formatted output only (no save)
            formatted_output = OutputFormatter.format(result_data, output_format)
            print(formatted_output)

        return 0

    except Exception as e:
        if output_format == 'json':
            error_data = {'error': str(e)}
            print(OutputFormatter.to_json(error_data))
        else:
            print(f"Error executing workflow: {e}")
            import traceback
            traceback.print_exc()
        return 1
