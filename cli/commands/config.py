"""
CLI command: config - Manage CLI configuration
"""
import json
import subprocess

import yaml

from cli.utils.config import CLIConfig


def config_get_command(key: str = None, **kwargs):
    """
    Get configuration value(s).

    Args:
        key: Config key (dot-notation) or None for all
        **kwargs: Additional arguments (format)

    Returns:
        0 on success, 1 on error
    """
    config = CLIConfig()
    output_format = kwargs.get('format', 'plain')

    try:
        if key:
            value = config.get(key)
            if value is None:
                print(f"Key '{key}' not found in configuration")
                return 1

            if output_format == 'json':
                print(json.dumps({key: value}, indent=2))
            elif output_format == 'yaml':
                print(yaml.dump({key: value}, default_flow_style=False))
            else:
                if isinstance(value, (dict, list)):
                    if output_format == 'plain':
                        print(json.dumps(value, indent=2))
                    else:
                        print(yaml.dump(value, default_flow_style=False))
                else:
                    print(value)
        else:
            all_config = config.load()

            if output_format == 'json':
                print(json.dumps(all_config, indent=2))
            elif output_format == 'yaml':
                print(yaml.dump(all_config, default_flow_style=False))
            elif output_format == 'plain':
                print(json.dumps(all_config, indent=2))
            else:
                print(yaml.dump(all_config, default_flow_style=False))

        return 0

    except Exception as e:
        print(f"Error reading configuration: {e}")
        return 1


def config_set_command(key: str, value: str, **kwargs):
    """
    Set configuration value.

    Args:
        key: Config key (dot-notation)
        value: Value to set
        **kwargs: Additional arguments

    Returns:
        0 on success, 1 on error
    """
    config = CLIConfig()

    try:
        # Try to parse value as JSON for complex types
        try:
            parsed_value = json.loads(value)
        except json.JSONDecodeError:
            # If not valid JSON, treat as string
            # Try boolean conversion
            if value.lower() == 'true':
                parsed_value = True
            elif value.lower() == 'false':
                parsed_value = False
            # Try numeric conversion
            elif value.isdigit():
                parsed_value = int(value)
            elif value.replace('.', '', 1).isdigit():
                parsed_value = float(value)
            else:
                parsed_value = value

        config.set(key, parsed_value)
        print(f"✓ Set {key} = {parsed_value}")

        return 0

    except Exception as e:
        print(f"Error setting configuration: {e}")
        return 1


def config_list_command(**kwargs):
    """
    List all configuration keys and values.

    Args:
        **kwargs: Additional arguments (format)

    Returns:
        0 on success, 1 on error
    """
    config = CLIConfig()
    output_format = kwargs.get('format', 'markdown')

    try:
        all_config = config.load()

        if output_format == 'json':
            print(json.dumps(all_config, indent=2))
        elif output_format == 'yaml':
            print(yaml.dump(all_config, default_flow_style=False))
        elif output_format == 'plain':
            _print_config_flat(all_config)
        else:  # markdown
            print("# SuperSkills Configuration\n")
            _print_config_markdown(all_config)

        return 0

    except Exception as e:
        print(f"Error listing configuration: {e}")
        return 1


def config_reset_command(**kwargs):
    """
    Reset configuration to defaults.

    Args:
        **kwargs: Additional arguments (confirm)

    Returns:
        0 on success, 1 on error
    """
    config = CLIConfig()

    confirm = kwargs.get('confirm', False)

    if not confirm:
        print("⚠ This will reset all configuration to defaults.")
        print("Run with --confirm to proceed.")
        return 0

    try:
        config._config = config._get_default_config()
        config.save()

        print("✓ Configuration reset to defaults")
        print(f"  Config file: {config.config_file}")

        return 0

    except Exception as e:
        print(f"Error resetting configuration: {e}")
        return 1


def config_edit_command(**kwargs):
    """
    Open configuration file in default editor.

    Args:
        **kwargs: Additional arguments (editor)

    Returns:
        0 on success, 1 on error
    """
    config = CLIConfig()

    # Ensure config file exists
    if not config.config_file.exists():
        config.load()

    editor = kwargs.get('editor') or _detect_editor()

    if not editor:
        print("No editor found. Set EDITOR environment variable or use --editor flag.")
        print(f"Config file location: {config.config_file}")
        return 1

    try:
        subprocess.run([editor, str(config.config_file)], check=True)
        print(f"✓ Configuration edited with {editor}")
        return 0

    except subprocess.CalledProcessError as e:
        print(f"Error opening editor: {e}")
        print(f"Config file location: {config.config_file}")
        return 1
    except FileNotFoundError:
        print(f"Editor '{editor}' not found.")
        print(f"Config file location: {config.config_file}")
        return 1


def config_path_command(**kwargs):
    """
    Show configuration file path.

    Args:
        **kwargs: Additional arguments

    Returns:
        0 on success
    """
    config = CLIConfig()
    print(config.config_file)
    return 0


def _print_config_flat(config: dict, prefix: str = ''):
    """Print config in flat key=value format."""
    for key, value in config.items():
        full_key = f"{prefix}.{key}" if prefix else key

        if isinstance(value, dict):
            _print_config_flat(value, full_key)
        else:
            print(f"{full_key} = {value}")


def _print_config_markdown(config: dict, level: int = 2):
    """Print config in markdown format."""
    for key, value in config.items():
        if isinstance(value, dict):
            print(f"{'#' * level} {key.title()}\n")
            _print_config_markdown(value, level + 1)
        else:
            print(f"- **{key}**: `{value}`")

    if level == 2:
        print()


def _detect_editor():
    """Detect available text editor."""
    import os

    # Check environment variable
    if 'EDITOR' in os.environ:
        return os.environ['EDITOR']

    # Try common editors
    editors = ['nano', 'vim', 'vi', 'emacs', 'code', 'subl']

    for editor in editors:
        try:
            subprocess.run(['which', editor], capture_output=True, check=True)
            return editor
        except subprocess.CalledProcessError:
            continue

    return None
