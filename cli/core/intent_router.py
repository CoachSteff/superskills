"""
Intent router: Route parsed intents to appropriate commands
"""
from pathlib import Path

from cli.commands.call import call_command
from cli.commands.config import config_get_command, config_set_command
from cli.commands.discover import discover_command
from cli.commands.list_skills import list_command
from cli.commands.run import run_command
from cli.commands.show import show_command
from cli.core.intent_parser import IntentResult
from cli.utils.config import CLIConfig
from cli.utils.logger import get_logger


class IntentRouter:
    """Route intents to appropriate command handlers"""

    def __init__(self, config: CLIConfig):
        self.config = config
        self.logger = get_logger()

    def route(self, intent: IntentResult) -> int:
        """Route intent to appropriate command handler"""
        self.logger.debug(f"Routing intent: {intent.action}")

        try:
            if intent.action == 'search':
                return self._handle_search(intent)
            elif intent.action == 'execute_skill':
                return self._handle_execute_skill(intent)
            elif intent.action == 'run_workflow':
                return self._handle_run_workflow(intent)
            elif intent.action == 'list':
                return self._handle_list(intent)
            elif intent.action == 'show':
                return self._handle_show(intent)
            elif intent.action == 'config':
                return self._handle_config(intent)
            elif intent.action == 'discover':
                return self._handle_discover(intent)
            else:
                print(f"Unknown action: {intent.action}")
                return 1

        except Exception as e:
            self.logger.error(f"Intent routing failed: {e}")
            print(f"✗ Error: {e}")
            return 1

    def _handle_search(self, intent: IntentResult) -> int:
        """Handle search intent"""
        # Import here to avoid circular dependency
        from cli.commands.search import search_command

        query = intent.parameters.get('query', '')
        search_type = intent.parameters.get('type', 'auto')

        if not query:
            print("Error: Search query is required")
            return 1

        return search_command(query=query, search_type=search_type)

    def _handle_execute_skill(self, intent: IntentResult) -> int:
        """Handle execute_skill intent"""
        if not intent.target:
            print("Error: Skill name is required")
            return 1

        skill_name = intent.target
        params = intent.parameters

        # Extract input
        input_text = params.get('input')
        input_file = params.get('input_file')

        # Validate input
        if input_file:
            input_path = Path(input_file)
            if not input_path.exists():
                print(f"✗ Error: Input file not found: {input_file}")
                return 1

        # Build kwargs
        kwargs = {}
        if input_file:
            kwargs['input_file'] = input_file
        if 'output_file' in params:
            kwargs['output_file'] = params['output_file']
        if 'format' in params:
            kwargs['format'] = params['format']
        if 'content_type' in params:
            kwargs['content_type'] = params['content_type']
        if 'profile_type' in params:
            kwargs['profile_type'] = params['profile_type']

        return call_command(skill_name, input_text, **kwargs)

    def _handle_run_workflow(self, intent: IntentResult) -> int:
        """Handle run_workflow intent"""
        if not intent.target:
            print("Error: Workflow name is required")
            return 1

        workflow_name = intent.target
        params = intent.parameters

        # Build kwargs
        kwargs = {}
        if 'input' in params:
            kwargs['input'] = params['input']
        if 'output' in params:
            kwargs['output'] = params['output']
        if 'topic' in params:
            kwargs['topic'] = params['topic']
        if 'format' in params:
            kwargs['format'] = params['format']

        return run_command(workflow_name, **kwargs)

    def _handle_list(self, intent: IntentResult) -> int:
        """Handle list intent"""
        params = intent.parameters

        kwargs = {}
        if 'format' in params:
            kwargs['format'] = params['format']

        return list_command(**kwargs)

    def _handle_show(self, intent: IntentResult) -> int:
        """Handle show intent"""
        if not intent.target:
            print("Error: Skill name is required")
            return 1

        return show_command(intent.target)

    def _handle_config(self, intent: IntentResult) -> int:
        """Handle config intent"""
        params = intent.parameters

        if 'key' in params and 'value' in params:
            # Set config
            return config_set_command(params['key'], params['value'])
        elif 'key' in params:
            # Get config
            kwargs = {}
            if 'format' in params:
                kwargs['format'] = params['format']
            return config_get_command(params['key'], **kwargs)
        else:
            print("Error: Config key is required")
            return 1

    def _handle_discover(self, intent: IntentResult) -> int:
        """Handle discover intent"""
        params = intent.parameters

        kwargs = {}
        if 'query' in params:
            kwargs['query'] = params['query']
        if 'task' in params:
            kwargs['task'] = params['task']
        if 'json_output' in params:
            kwargs['json_output'] = params['json_output']

        return discover_command(**kwargs)
