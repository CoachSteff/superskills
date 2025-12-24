"""
Output formatters for various data types and formats.
"""
import json
import yaml
from datetime import datetime
from typing import Dict, Any, Optional


class OutputFormatter:
    """Format output data in various formats."""
    
    @staticmethod
    def format(data: Dict[str, Any], format_type: str = 'markdown') -> str:
        """
        Format data according to specified format.
        
        Args:
            data: Data to format
            format_type: One of 'json', 'yaml', 'markdown', 'plain'
        
        Returns:
            Formatted string
        """
        if format_type == 'json':
            return OutputFormatter.to_json(data)
        elif format_type == 'yaml':
            return OutputFormatter.to_yaml(data)
        elif format_type == 'markdown':
            return OutputFormatter.to_markdown(data)
        elif format_type == 'plain':
            return OutputFormatter.to_plain(data)
        else:
            raise ValueError(f"Unknown format: {format_type}")
    
    @staticmethod
    def to_json(data: Dict[str, Any], pretty: bool = True) -> str:
        """Format as JSON."""
        # Add status if not present (for IDE integration compatibility)
        if 'status' not in data:
            # Infer status from presence of output
            data['status'] = 'success' if 'output' in data or 'final_output' in data else 'error'
        
        # Add timestamp if not present
        if 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        if pretty:
            return json.dumps(data, indent=2, ensure_ascii=False)
        return json.dumps(data, ensure_ascii=False)
    
    @staticmethod
    def to_yaml(data: Dict[str, Any]) -> str:
        """Format as YAML."""
        return yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    @staticmethod
    def to_markdown(data: Dict[str, Any]) -> str:
        """Format as Markdown."""
        lines = []
        
        # Title
        if 'skill' in data:
            lines.append(f"# {data['skill'].title()} Output\n")
        elif 'workflow' in data:
            lines.append(f"# {data['workflow'].title()} Workflow Results\n")
        
        # Metadata
        if 'metadata' in data:
            lines.append("## Metadata\n")
            for key, value in data['metadata'].items():
                lines.append(f"- **{key.replace('_', ' ').title()}**: {value}")
            lines.append("")
        
        # Main output
        if 'output' in data:
            lines.append("## Output\n")
            lines.append(str(data['output']))
        elif 'final_output' in data:
            lines.append("## Final Output\n")
            lines.append(str(data['final_output']))
        
        # Steps (for workflows)
        if 'steps' in data and isinstance(data['steps'], dict):
            lines.append("\n## Workflow Steps\n")
            for step_name, step_data in data['steps'].items():
                lines.append(f"### {step_name}\n")
                if isinstance(step_data, dict) and 'output' in step_data:
                    output_preview = str(step_data['output'])[:200]
                    if len(str(step_data['output'])) > 200:
                        output_preview += '...'
                    lines.append(output_preview)
                    lines.append("")
        
        return '\n'.join(lines)
    
    @staticmethod
    def to_plain(data: Dict[str, Any]) -> str:
        """Format as plain text (output only)."""
        if 'output' in data:
            return str(data['output'])
        elif 'final_output' in data:
            return str(data['final_output'])
        elif 'steps' in data and isinstance(data['steps'], dict):
            # For workflows, return last step output
            steps = list(data['steps'].values())
            if steps and isinstance(steps[-1], dict) and 'output' in steps[-1]:
                return str(steps[-1]['output'])
        
        # Fallback to string representation
        return str(data)


class WorkflowListFormatter:
    """Format workflow list output."""
    
    @staticmethod
    def format(workflows: list, format_type: str = 'markdown') -> str:
        """
        Format workflow list.
        
        Args:
            workflows: List of workflow dicts
            format_type: Output format
        
        Returns:
            Formatted string
        """
        if format_type == 'json':
            return json.dumps(workflows, indent=2)
        elif format_type == 'yaml':
            return yaml.dump(workflows, default_flow_style=False)
        elif format_type == 'plain':
            return '\n'.join(w['name'] for w in workflows)
        else:  # markdown
            lines = [f"# Available Workflows ({len(workflows)} total)\n"]
            
            builtin = [w for w in workflows if w.get('type') == 'built-in']
            custom = [w for w in workflows if w.get('type') == 'custom']
            user = [w for w in workflows if w.get('type') == 'user']
            
            if builtin:
                lines.append("## Built-in Workflows\n")
                for w in builtin:
                    lines.append(f"- **{w['name']}**: {w.get('description', 'No description')}")
                lines.append("")
            
            if user:
                lines.append("## User Workflows\n")
                for w in user:
                    lines.append(f"- **{w['name']}**: {w.get('description', 'No description')}")
                lines.append("")
            
            if custom:
                lines.append("## Custom Workflows\n")
                for w in custom:
                    lines.append(f"- **{w['name']}**: {w.get('description', 'No description')}")
                lines.append("")
            
            return '\n'.join(lines)


class SkillListFormatter:
    """Format skill list output."""
    
    @staticmethod
    def format(skills: list, format_type: str = 'markdown') -> str:
        """
        Format skill list.
        
        Args:
            skills: List of skill info objects
            format_type: Output format
        
        Returns:
            Formatted string
        """
        # Convert skill objects to dicts
        skill_dicts = []
        for skill in skills:
            skill_dicts.append({
                'name': skill.name,
                'description': skill.description,
                'type': skill.skill_type,
                'has_profile': skill.has_profile,
                'parent_skill': getattr(skill, 'parent_skill', None)
            })
        
        if format_type == 'json':
            return json.dumps(skill_dicts, indent=2)
        elif format_type == 'yaml':
            return yaml.dump(skill_dicts, default_flow_style=False)
        elif format_type == 'plain':
            return '\n'.join(s['name'] for s in skill_dicts)
        else:  # markdown with hierarchical display
            lines = [f"# Available Skills ({len(skills)} total)\n"]
            
            prompt_skills = [s for s in skill_dicts if s['type'] == 'prompt']
            python_skills = [s for s in skill_dicts if s['type'] == 'python']
            
            if prompt_skills:
                lines.append(f"## Prompt-Based Skills ({len(prompt_skills)})\n")
                lines.extend(SkillListFormatter._format_hierarchical(prompt_skills))
                lines.append("")
            
            if python_skills:
                lines.append(f"## Python-Powered Skills ({len(python_skills)})\n")
                lines.extend(SkillListFormatter._format_hierarchical(python_skills))
                lines.append("")
            
            return '\n'.join(lines)
    
    @staticmethod
    def _format_hierarchical(skill_dicts: list) -> list:
        """Format skills with hierarchical indentation for parent-child relationships."""
        lines = []
        
        # Separate parent and child skills
        parents = {}
        children = {}
        
        for s in skill_dicts:
            if s['parent_skill']:
                parent = s['parent_skill']
                if parent not in children:
                    children[parent] = []
                children[parent].append(s)
            else:
                parents[s['name']] = s
        
        # Format output with hierarchy
        for skill_name in sorted(parents.keys()):
            s = parents[skill_name]
            profile = " ✓" if s['has_profile'] else ""
            
            # Parent skill
            if skill_name in children:
                # Has children - show as parent
                lines.append(f"- **{s['name']}**: {s['description']}{profile}")
                
                # Show children with tree characters
                child_list = sorted(children[skill_name], key=lambda x: x['name'])
                for i, child in enumerate(child_list):
                    is_last = i == len(child_list) - 1
                    tree_char = "└─" if is_last else "├─"
                    child_profile = " ✓" if child['has_profile'] else ""
                    lines.append(f"  {tree_char} **{child['name']}**: {child['description']}{child_profile}")
            else:
                # No children - regular display
                lines.append(f"- **{s['name']}**: {s['description']}{profile}")
        
        return lines
