"""
SuperSkills CLI - Main entry point
"""
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
from .commands.init import init_command
from .commands.list_skills import list_command
from .commands.show import show_command
from .commands.call import call_command
from .commands.run import run_command
from .commands.status import status_command
from .commands.workflow import workflow_list_command, workflow_validate_command
from .commands.export import export_command
from .commands.discover import discover_command
from .commands.validate import validate_command
from .commands.config import (
    config_get_command, config_set_command, config_list_command,
    config_reset_command, config_edit_command, config_path_command
)
from .utils.logger import get_logger
from .utils.paths import get_project_root


def load_environment():
    """Load environment variables from .env files.
    
    This provides base .env loading for CLI operations.
    Individual skills use superskills/core/credentials.py which:
    - Loads global .env (override=False - respects system env)
    - Loads skill-specific .env (override=True - takes precedence over global)
    
    Precedence (highest to lowest):
    1. System environment variables
    2. Skill-specific .env (superskills/{skill}/.env)
    3. User config .env (~/.superskills/.env)
    4. Project root .env
    """
    # Try user config directory .env first (lower priority)
    user_env = Path.home() / '.superskills' / '.env'
    if user_env.exists():
        load_dotenv(user_env, override=False)
    
    # Try project root .env (will be overridden by skill-specific)
    project_env = get_project_root() / '.env'
    if project_env.exists():
        load_dotenv(project_env, override=False)


def get_version():
    """Read version from pyproject.toml"""
    pyproject_path = get_project_root() / "pyproject.toml"
    try:
        with open(pyproject_path, 'r') as f:
            for line in f:
                if line.strip().startswith('version'):
                    version = line.split('=')[1].strip().strip('"').strip("'")
                    return f"SuperSkills v{version}"
    except Exception:
        pass
    return "SuperSkills (version unknown)"


def main():
    # Load environment variables from .env files
    load_environment()
    
    parser = argparse.ArgumentParser(
        prog='superskills',
        description='SuperSkills CLI - AI-powered automation skills'
    )
    
    parser.add_argument('--version', action='version', version=get_version())
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose logging (DEBUG level)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    subparsers.add_parser('init', help='Initialize the CLI')
    
    list_parser = subparsers.add_parser('list', help='List all available skills')
    list_parser.add_argument('--format', choices=['json', 'yaml', 'markdown', 'plain'],
                            default='markdown', help='Output format (default: markdown)')
    
    show_parser = subparsers.add_parser('show', help='Show detailed information about a skill')
    show_parser.add_argument('skill', help='Skill name')
    
    call_parser = subparsers.add_parser('call', help='Execute a single skill')
    call_parser.add_argument('skill', help='Skill name')
    call_parser.add_argument('input', nargs='?', help='Input text')
    call_parser.add_argument('--input', dest='input_file', help='Input file path')
    call_parser.add_argument('--output', help='Output file path')
    call_parser.add_argument('--format', choices=['json', 'yaml', 'markdown', 'plain'],
                            default='markdown', help='Output format (default: markdown)')
    call_parser.add_argument('--content-type', 
                            choices=['podcast', 'educational', 'marketing', 'social', 'meditation'],
                            help='Content type for narrator skill (podcast/educational/marketing/social/meditation)')
    call_parser.add_argument('--profile-type',
                            choices=['podcast', 'narration', 'meditation'],
                            help='Voice profile for narrator skill (podcast/narration/meditation)')
    
    run_parser = subparsers.add_parser('run', help='Execute a workflow')
    run_parser.add_argument('workflow', help='Workflow name')
    run_parser.add_argument('--input', help='Input file or text')
    run_parser.add_argument('--output', help='Output file path')
    run_parser.add_argument('--topic', help='Topic (for workflows that need it)')
    run_parser.add_argument('--dry-run', action='store_true', 
                           help='Show what would happen without executing')
    run_parser.add_argument('--watch', action='store_true',
                           help='Watch workflow input folder and auto-process new files')
    run_parser.add_argument('--batch', action='store_true',
                           help='Process all files in workflow input folder')
    run_parser.add_argument('--interval', type=int, default=1,
                           help='Watch interval in seconds (default: 1)')
    run_parser.add_argument('--format', choices=['json', 'yaml', 'markdown', 'plain'],
                           default='markdown', help='Output format (default: markdown)')
    
    subparsers.add_parser('status', help='Show CLI status')
    
    subparsers.add_parser('validate', help='Validate skill integrity and completeness')
    
    workflow_parser = subparsers.add_parser('workflow', help='Manage workflows')
    workflow_subparsers = workflow_parser.add_subparsers(dest='workflow_command')
    
    workflow_list_parser = workflow_subparsers.add_parser('list', help='List all workflows')
    workflow_list_parser.add_argument('--format', choices=['json', 'yaml', 'markdown', 'plain'],
                                     default='markdown', help='Output format (default: markdown)')
    
    validate_parser = workflow_subparsers.add_parser('validate', help='Validate a workflow definition')
    validate_parser.add_argument('workflow', help='Workflow name')
    
    export_parser = subparsers.add_parser('export', help='Export skill metadata for IDE AI')
    export_parser.add_argument('--output', help='Output file path (default: stdout)')
    export_parser.add_argument('--format', dest='format_type', choices=['json', 'markdown'], 
                              default='json', help='Output format')
    export_parser.add_argument('--type', dest='skill_type', choices=['prompt', 'python'], 
                              help='Filter by skill type')
    export_parser.add_argument('--has-api', action='store_true', 
                              help='Only skills requiring API keys')
    export_parser.add_argument('--markdown', action='store_true', 
                              help='Output as markdown table')
    
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_subparsers = config_parser.add_subparsers(dest='config_command')
    
    config_get_parser = config_subparsers.add_parser('get', help='Get configuration value')
    config_get_parser.add_argument('key', nargs='?', help='Configuration key (dot-notation) or empty for all')
    config_get_parser.add_argument('--format', choices=['json', 'yaml', 'plain'],
                                   default='plain', help='Output format')
    
    config_set_parser = config_subparsers.add_parser('set', help='Set configuration value')
    config_set_parser.add_argument('key', help='Configuration key (dot-notation)')
    config_set_parser.add_argument('value', help='Value to set')
    
    config_list_parser = config_subparsers.add_parser('list', help='List all configuration')
    config_list_parser.add_argument('--format', choices=['json', 'yaml', 'markdown', 'plain'],
                                    default='markdown', help='Output format')
    
    config_reset_parser = config_subparsers.add_parser('reset', help='Reset configuration to defaults')
    config_reset_parser.add_argument('--confirm', action='store_true',
                                     help='Confirm reset operation')
    
    config_edit_parser = config_subparsers.add_parser('edit', help='Edit configuration in editor')
    config_edit_parser.add_argument('--editor', help='Editor to use (default: $EDITOR)')
    
    config_subparsers.add_parser('path', help='Show configuration file path')
    
    discover_parser = subparsers.add_parser('discover', help='Discover skills by capability')
    discover_parser.add_argument('--query', help='Search query for skill capabilities')
    discover_parser.add_argument('--task', help='Task description to find matching workflow')
    discover_parser.add_argument('--json', dest='json_output', action='store_true', 
                                help='Output in JSON format')
    
    args = parser.parse_args()
    
    logger = get_logger(verbose=args.verbose)
    
    if not args.command:
        parser.print_help()
        return 0
    
    logger.info(f"Executing command: {args.command}")
    
    try:
        if args.command == 'init':
            return init_command()
        
        elif args.command == 'list':
            kwargs = {}
            if hasattr(args, 'format') and args.format:
                kwargs['format'] = args.format
            return list_command(**kwargs)
        
        elif args.command == 'show':
            return show_command(args.skill)
        
        elif args.command == 'call':
            kwargs = {}
            if hasattr(args, 'input_file') and args.input_file:
                kwargs['input_file'] = args.input_file
            if hasattr(args, 'output') and args.output:
                kwargs['output_file'] = args.output
            if hasattr(args, 'format') and args.format:
                kwargs['format'] = args.format
            if hasattr(args, 'content_type') and args.content_type:
                kwargs['content_type'] = args.content_type
            if hasattr(args, 'profile_type') and args.profile_type:
                kwargs['profile_type'] = args.profile_type
            
            return call_command(args.skill, args.input, **kwargs)
        
        elif args.command == 'run':
            kwargs = {}
            if args.input:
                kwargs['input'] = args.input
            if args.output:
                kwargs['output'] = args.output
            if args.topic:
                kwargs['topic'] = args.topic
            if hasattr(args, 'dry_run') and args.dry_run:
                kwargs['dry_run'] = True
            if hasattr(args, 'watch') and args.watch:
                kwargs['watch'] = True
            if hasattr(args, 'batch') and args.batch:
                kwargs['batch'] = True
            if hasattr(args, 'interval') and args.interval:
                kwargs['interval'] = args.interval
            if hasattr(args, 'format') and args.format:
                kwargs['format'] = args.format
            
            return run_command(args.workflow, **kwargs)
        
        elif args.command == 'status':
            return status_command()
        
        elif args.command == 'validate':
            return validate_command()
        
        elif args.command == 'workflow':
            if args.workflow_command == 'list':
                kwargs = {}
                if hasattr(args, 'format') and args.format:
                    kwargs['format'] = args.format
                return workflow_list_command(**kwargs)
            elif args.workflow_command == 'validate':
                return workflow_validate_command(args.workflow)
            else:
                workflow_parser.print_help()
                return 0
        
        elif args.command == 'export':
            kwargs = {}
            if hasattr(args, 'output') and args.output:
                kwargs['output_file'] = args.output
            if hasattr(args, 'format_type'):
                kwargs['format_type'] = args.format_type
            if hasattr(args, 'skill_type') and args.skill_type:
                kwargs['skill_type'] = args.skill_type
            if hasattr(args, 'has_api') and args.has_api:
                kwargs['has_api'] = True
            if hasattr(args, 'markdown') and args.markdown:
                kwargs['markdown'] = True
            
            return export_command(**kwargs)
        
        elif args.command == 'config':
            if args.config_command == 'get':
                kwargs = {}
                if hasattr(args, 'format') and args.format:
                    kwargs['format'] = args.format
                return config_get_command(args.key, **kwargs)
            elif args.config_command == 'set':
                return config_set_command(args.key, args.value)
            elif args.config_command == 'list':
                kwargs = {}
                if hasattr(args, 'format') and args.format:
                    kwargs['format'] = args.format
                return config_list_command(**kwargs)
            elif args.config_command == 'reset':
                kwargs = {}
                if hasattr(args, 'confirm') and args.confirm:
                    kwargs['confirm'] = True
                return config_reset_command(**kwargs)
            elif args.config_command == 'edit':
                kwargs = {}
                if hasattr(args, 'editor') and args.editor:
                    kwargs['editor'] = args.editor
                return config_edit_command(**kwargs)
            elif args.config_command == 'path':
                return config_path_command()
            else:
                config_parser.print_help()
                return 0
        
        elif args.command == 'discover':
            kwargs = {}
            if hasattr(args, 'query') and args.query:
                kwargs['query'] = args.query
            if hasattr(args, 'task') and args.task:
                kwargs['task'] = args.task
            if hasattr(args, 'json_output') and args.json_output:
                kwargs['json_output'] = True
            
            return discover_command(**kwargs)
        
        else:
            parser.print_help()
            return 0
    
    except KeyboardInterrupt:
        logger.warning("Operation interrupted by user")
        print("\n\nInterrupted by user.")
        return 130
    
    except Exception as e:
        logger.error(f"Command failed: {e}", exc_info=True)
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
