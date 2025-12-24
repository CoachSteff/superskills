"""
Input validation and sanitization for workflows and user inputs.
"""
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import jsonschema
import yaml

from cli.core.skill_loader import SkillLoader
from cli.utils.logger import get_logger


class WorkflowValidator:
    """Validates workflow definitions."""

    def __init__(self):
        self.logger = get_logger()
        self.skill_loader = SkillLoader()
        self._schema = self._load_schema()

    def _load_schema(self) -> Dict[str, Any]:
        """Load the workflow JSON schema."""
        schema_path = Path(__file__).parent.parent / "schemas" / "workflow_schema.json"
        with open(schema_path, 'r') as f:
            return json.load(f)

    def validate_workflow(self, workflow_path: Path) -> Tuple[bool, List[str]]:
        """
        Validate a workflow file.
        
        Args:
            workflow_path: Path to workflow YAML file
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check file exists
        if not workflow_path.exists():
            return False, [f"Workflow file not found: {workflow_path}"]

        # Parse YAML
        try:
            with open(workflow_path, 'r') as f:
                workflow = yaml.safe_load(f)
        except yaml.YAMLError as e:
            return False, [f"Invalid YAML syntax: {e}"]
        except Exception as e:
            return False, [f"Failed to read workflow file: {e}"]

        # Validate against JSON schema
        try:
            jsonschema.validate(instance=workflow, schema=self._schema)
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation failed: {e.message}")
            return False, errors

        # Validate skills exist
        available_skills = {s.name for s in self.skill_loader.discover_skills()}

        for idx, step in enumerate(workflow.get('steps', []), 1):
            skill_name = step.get('skill')
            if skill_name not in available_skills:
                errors.append(f"Step {idx} ({step.get('name')}): Skill '{skill_name}' not found")

        # Validate variable references
        defined_vars = set(workflow.get('variables', {}).keys())
        output_vars = set()

        for idx, step in enumerate(workflow.get('steps', []), 1):
            step_name = step.get('name')

            # Track output variables
            if 'output' in step:
                output_var = step['output']
                if output_var in output_vars:
                    errors.append(f"Step {idx} ({step_name}): Duplicate output variable '{output_var}'")
                output_vars.add(output_var)

            # Check input variable references
            input_text = step.get('input', '')
            referenced_vars = self._extract_variables(input_text)

            for var in referenced_vars:
                if var not in defined_vars and var not in output_vars:
                    errors.append(
                        f"Step {idx} ({step_name}): Undefined variable '${{{var}}}' in input"
                    )

        # Check for circular dependencies (simplified check)
        if self._has_circular_dependency(workflow):
            errors.append("Circular dependency detected in workflow variables")

        if errors:
            return False, errors

        return True, []

    def _extract_variables(self, text: str) -> List[str]:
        """Extract variable references from text (e.g., ${var_name})."""
        pattern = r'\$\{([a-zA-Z_][a-zA-Z0-9_.]*)\}'
        matches = re.findall(pattern, text)
        return [m.split('.')[0] for m in matches]  # Get base variable name

    def _has_circular_dependency(self, workflow: Dict[str, Any]) -> bool:
        """
        Check for circular dependencies in workflow variables.
        
        Simplified check: workflow variables shouldn't reference each other.
        """
        workflow_vars = workflow.get('variables', {})

        for var_name, var_value in workflow_vars.items():
            if isinstance(var_value, str):
                referenced = self._extract_variables(var_value)
                if var_name in referenced:
                    return True
                for ref in referenced:
                    if ref in workflow_vars:
                        return True

        return False


class PathSanitizer:
    """Sanitize file paths to prevent directory traversal attacks."""

    @staticmethod
    def sanitize_path(path: str, base_dir: Optional[Path] = None) -> Path:
        """
        Sanitize a file path to prevent directory traversal.
        
        Args:
            path: Path to sanitize
            base_dir: Base directory to restrict access to
        
        Returns:
            Sanitized absolute path
        
        Raises:
            ValueError: If path attempts directory traversal
        """
        # Convert to Path object
        p = Path(path).expanduser().resolve()

        # If base_dir specified, ensure path is within it
        if base_dir:
            base = Path(base_dir).expanduser().resolve()
            try:
                p.relative_to(base)
            except ValueError:
                raise ValueError(
                    f"Path '{path}' is outside allowed directory '{base_dir}'"
                )

        # Check for common attack patterns
        path_str = str(p)
        if '..' in Path(path).parts:
            raise ValueError(f"Directory traversal detected in path: {path}")

        return p

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize a filename to remove dangerous characters.
        
        Args:
            filename: Filename to sanitize
        
        Returns:
            Sanitized filename
        """
        # Remove path separators and null bytes
        sanitized = filename.replace('/', '_').replace('\\', '_').replace('\0', '')

        # Remove leading dots (hidden files)
        sanitized = sanitized.lstrip('.')

        # Limit length
        if len(sanitized) > 255:
            name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
            sanitized = name[:255 - len(ext) - 1] + '.' + ext if ext else name[:255]

        # Ensure not empty
        if not sanitized:
            raise ValueError("Filename cannot be empty after sanitization")

        return sanitized


class InputValidator:
    """Validate user inputs."""

    @staticmethod
    def validate_skill_name(name: str) -> bool:
        """
        Validate skill name format.
        
        Args:
            name: Skill name
        
        Returns:
            True if valid
        """
        pattern = r'^[a-z][a-z0-9_-]*$'
        return bool(re.match(pattern, name))

    @staticmethod
    def validate_variable_name(name: str) -> bool:
        """
        Validate variable name format.
        
        Args:
            name: Variable name
        
        Returns:
            True if valid
        """
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
        return bool(re.match(pattern, name))

    @staticmethod
    def validate_workflow_depth(workflow: Dict[str, Any], max_depth: int = 50) -> bool:
        """
        Validate workflow doesn't exceed maximum depth.
        
        Args:
            workflow: Workflow definition
            max_depth: Maximum number of steps allowed
        
        Returns:
            True if valid
        """
        steps = workflow.get('steps', [])
        return len(steps) <= max_depth
