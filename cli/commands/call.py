"""
CLI command: call - Execute a single skill
"""
import sys
from pathlib import Path

from cli.core.skill_executor import SkillExecutor
from cli.core.skill_loader import SkillLoader
from cli.utils.config import CLIConfig
from cli.utils.formatters import OutputFormatter
from cli.utils.paths import get_skills_dir


def call_command(skill_name: str, input_text: str = None, **kwargs):
    config = CLIConfig()
    executor = SkillExecutor(config)

    output_format = kwargs.get('format', 'markdown')
    input_file = kwargs.get('input_file')
    output_file = kwargs.get('output_file')

    # Read input
    if not sys.stdin.isatty():
        input_text = sys.stdin.read()
    elif input_file:
        input_path = Path(input_file)
        if not input_path.exists():
            print(f"Error: Input file not found: {input_file}")
            return 1

        with open(input_path, 'r', encoding='utf-8') as f:
            input_text = f.read()

    if not input_text:
        print("Error: Provide input via argument, --input flag, or stdin")
        return 1

    if output_format == 'plain':
        # Silent mode for plain output
        pass
    else:
        # Print informational message to stderr to keep stdout clean for JSON/structured output
        print(f"Calling skill: {skill_name}", file=sys.stderr)

    try:
        result = executor.execute(skill_name, input_text, **kwargs)

        # Format output
        formatted = OutputFormatter.format(result, output_format)

        # Write or print
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(formatted)

            if output_format != 'plain':
                print(f"\n✓ Output saved to: {output_file}", file=sys.stderr)
        else:
            print(formatted)

        return 0

    except FileNotFoundError as e:
        error_msg = str(e)
        if 'Skill' in error_msg and 'not found' in error_msg:
            _print_helpful_skill_not_found_error(skill_name)
        else:
            print(f"Error: {e}")
        return 1

    except Exception as e:
        print(f"Error executing skill: {e}")
        return 1


def _print_helpful_skill_not_found_error(skill_name: str):
    """Print helpful error message when skill is not found."""
    print(f"Error: Skill '{skill_name}' not found\n")

    skills_dir = get_skills_dir()
    skill_dir = skills_dir / skill_name

    # Check if directory exists but no SKILL.md
    if skill_dir.exists() and skill_dir.is_dir():
        has_src = (skill_dir / "src").exists()
        has_readme = (skill_dir / "README.md").exists()

        print(f"The skill '{skill_name}' exists but is missing a SKILL.md file.")

        if has_src:
            print("This is a Python-based skill that requires manual setup.\n")

        print("Suggested actions:")

        if has_src:
            src_files = list((skill_dir / "src").glob("*.py"))
            if src_files:
                print(f"1. Check Python implementation: {skill_dir / 'src'}")

        if has_readme:
            print(f"2. Read documentation: {skill_dir / 'README.md'}")

        # Suggest similar skills
        loader = SkillLoader()
        try:
            available_skills = loader.discover_skills()
            similar = _find_similar_skills(skill_name, [s.name for s in available_skills])
            if similar:
                print(f"3. Or try similar skills: {', '.join(similar[:3])}")
        except Exception:
            # Silently ignore skill discovery errors (non-critical for error message)
            pass

        print("\nRun 'superskills list' to see all available skills")
    else:
        # Skill directory doesn't exist at all
        print(f"No skill directory found for '{skill_name}'.\n")

        # Try to suggest similar skills
        loader = SkillLoader()
        try:
            available_skills = loader.discover_skills()
            similar = _find_similar_skills(skill_name, [s.name for s in available_skills])

            if similar:
                print("Did you mean one of these?")
                for skill in similar[:5]:
                    print(f"  - {skill}")
                print()
        except Exception:
            # Silently ignore skill discovery errors (non-critical for error message)
            pass

        print("Run 'superskills list' to see all available skills")


def _find_similar_skills(target: str, available: list) -> list:
    """Find skills with similar names using simple string matching."""
    target_lower = target.lower()

    # Exact substring matches
    exact_matches = [s for s in available if target_lower in s.lower() or s.lower() in target_lower]

    if exact_matches:
        return sorted(exact_matches)

    # Similar starting letters
    similar = [s for s in available if s.lower().startswith(target_lower[:3])]

    return sorted(similar)[:5]
