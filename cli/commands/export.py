"""
CLI command: export - Export skill metadata for IDE AI consumption
"""
import json
from pathlib import Path
from typing import Any, Dict, List

from cli.core.skill_loader import SkillLoader
from cli.utils.paths import get_project_root


def _get_version() -> str:
    """Read version from pyproject.toml."""
    pyproject_path = get_project_root() / "pyproject.toml"
    try:
        with open(pyproject_path, 'r') as f:
            for line in f:
                if line.strip().startswith('version'):
                    version = line.split('=')[1].strip().strip('"').strip("'")
                    return version
    except Exception:
        pass
    return "unknown"


def export_command(output_file: str = None, format_type: str = 'json',
                   skill_type: str = None, has_api: bool = None,
                   markdown: bool = False):
    """
    Export skill metadata for IDE AI consumption.
    
    Args:
        output_file: Optional output file path (default: stdout)
        format_type: Output format (json or markdown)
        skill_type: Filter by type (prompt or python)
        has_api: Filter skills that require API keys
        markdown: Output as markdown table
    """
    loader = SkillLoader()
    skills = loader.discover_skills()

    if skill_type:
        skills = [s for s in skills if s.skill_type == skill_type]

    if has_api is not None:
        api_skills = set(loader.PYTHON_SKILLS.keys())
        if has_api:
            skills = [s for s in skills if s.name in api_skills]
        else:
            skills = [s for s in skills if s.name not in api_skills]

    if markdown or format_type == 'markdown':
        output = _generate_markdown(skills)
    else:
        metadata = _generate_metadata(skills, loader)
        output = json.dumps(metadata, indent=2)

    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)

        print(f"Metadata exported to: {output_file}")
        return 0
    else:
        print(output)
        return 0


def _generate_metadata(skills: List, loader: SkillLoader) -> Dict[str, Any]:
    """Generate JSON metadata structure."""
    skills_data = []

    for skill in skills:
        skill_data = {
            'name': skill.name,
            'type': skill.skill_type,
            'description': skill.description,
            'has_profile': skill.has_profile,
            'requires_api': skill.name in loader.PYTHON_SKILLS,
            'capabilities': _extract_capabilities(skill),
            'examples': _extract_examples(skill)
        }

        if skill.skill_type == 'python':
            skill_data['python_module'] = skill.python_module
            skill_data['apis'] = _get_api_requirements(skill.name)
        else:
            skill_data['apis'] = ['anthropic']

        skills_data.append(skill_data)

    workflows_data = _get_workflows_metadata()

    return {
        'version': _get_version(),
        'total_skills': len(skills_data),
        'skills': skills_data,
        'workflows': workflows_data,
        'metadata': {
            'prompt_skills': len([s for s in skills if s.skill_type == 'prompt']),
            'python_skills': len([s for s in skills if s.skill_type == 'python']),
            'api_integrated_skills': len([s for s in skills if s.name in loader.PYTHON_SKILLS])
        }
    }


def _extract_capabilities(skill) -> List[str]:
    """Extract capabilities from skill description."""
    capability_keywords = {
        'author': ['writing', 'ghostwriting', 'content-creation', 'brand-voice'],
        'narrator': ['voice-generation', 'text-to-speech', 'audio', 'podcast'],
        'researcher': ['research', 'analysis', 'web-search', 'data-gathering'],
        'designer': ['image-generation', 'ai-art', 'visual-design', 'brand-assets'],
        'transcriber': ['transcription', 'speech-to-text', 'audio-processing', 'subtitles'],
        'editor': ['editing', 'proofreading', 'quality-control', 'refinement'],
        'copywriter': ['marketing-copy', 'sales-messaging', 'persuasive-writing'],
        'strategist': ['strategy', 'planning', 'frameworks', 'analysis'],
        'scraper': ['web-scraping', 'data-extraction', 'content-harvesting', 'crawl4ai'],
        'marketer': ['social-media', 'scheduling', 'multi-platform-posting'],
        'craft': ['document-management', 'craft-docs', 'export', 'collaboration'],
        'presenter': ['slides', 'presentations', 'powerpoint', 'visual-communication'],
        'coach': ['coaching', 'session-design', 'client-guidance'],
        'developer': ['code-generation', 'debugging', 'software-development'],
        'translator': ['translation', 'localization', 'multilingual'],
        'publisher': ['publishing', 'distribution', 'content-delivery'],
        'producer': ['media-production', 'workflow-automation'],
        'sales': ['sales', 'outreach', 'lead-generation'],
        'manager': ['project-management', 'coordination', 'team-leadership'],
        'webmaster': ['website-management', 'web-maintenance'],
        'coursepackager': ['course-creation', 'packaging', 'pdf-generation', 'workbooks'],
        'emailcampaigner': ['email-marketing', 'campaigns', 'sendgrid', 'audience-engagement'],
        'knowledgebase': ['knowledge-management', 'documentation', 'search', 'wiki'],
        'videoeditor': ['video-editing', 'ffmpeg', 'media-production', 'automation'],
    }

    return capability_keywords.get(skill.name, [skill.skill_type])


def _extract_examples(skill) -> List[str]:
    """Extract example use cases."""
    examples = {
        'author': ['Write LinkedIn post about AI trends', 'Create blog article from research'],
        'narrator': ['Generate podcast voiceover', 'Create educational video narration'],
        'researcher': ['Research AI automation trends', 'Analyze competitor strategies'],
        'designer': ['Generate brand hero image', 'Create social media graphics'],
        'transcriber': ['Transcribe podcast episode', 'Convert video to text'],
        'editor': ['Polish draft article', 'Review and refine content'],
        'copywriter': ['Write product launch copy', 'Create email campaign'],
        'strategist': ['Develop content strategy', 'Plan marketing campaign'],
        'scraper': ['Extract website content', 'Harvest competitive intelligence'],
        'marketer': ['Schedule social media posts', 'Publish to multiple platforms'],
        'craft': ['Export Craft document', 'Manage document library'],
    }

    return examples.get(skill.name, [f'Use {skill.name} for {skill.description.lower()}'])


def _get_api_requirements(skill_name: str) -> List[str]:
    """Get API requirements for a skill."""
    api_map = {
        'narrator': ['elevenlabs'],
        'transcriber': ['openai', 'assemblyai'],
        'designer': ['google-gemini', 'midjourney'],
        'scraper': ['crawl4ai'],
        'craft': ['craft-docs'],
        'marketer': ['postiz'],
        'presenter': ['anthropic'],
        'videoeditor': ['ffmpeg'],
    }

    return api_map.get(skill_name, ['anthropic'])


def _get_workflows_metadata() -> List[Dict[str, Any]]:
    """Get metadata about available workflows."""
    workflows = []

    workflow_definitions = {
        'content-creation': {
            'description': 'End-to-end content production pipeline',
            'steps': ['researcher', 'strategist', 'author', 'editor'],
            'inputs': ['topic'],
            'outputs': ['final article'],
            'use_cases': ['Blog post creation', 'Article writing', 'Content marketing']
        },
        'podcast-generation': {
            'description': 'Script enhancement and audio generation',
            'steps': ['copywriter', 'narrator'],
            'inputs': ['script'],
            'outputs': ['MP3 audio file'],
            'use_cases': ['Podcast production', 'Audio content', 'Voice narration']
        },
        'training-material': {
            'description': 'Transform recordings into training content',
            'steps': ['transcriber', 'author', 'editor'],
            'inputs': ['audio/video file'],
            'outputs': ['structured training content'],
            'use_cases': ['Course creation', 'Training documentation', 'Educational content']
        },
        'client-engagement': {
            'description': 'Automated research and personalized outreach',
            'steps': ['scraper', 'researcher', 'copywriter', 'sales'],
            'inputs': ['website URL'],
            'outputs': ['personalized outreach message'],
            'use_cases': ['Lead generation', 'Sales outreach', 'Client research']
        }
    }

    for name, data in workflow_definitions.items():
        workflows.append({
            'name': name,
            'description': data['description'],
            'steps': data['steps'],
            'step_count': len(data['steps']),
            'inputs': data['inputs'],
            'outputs': data['outputs'],
            'use_cases': data['use_cases']
        })

    return workflows


def _generate_markdown(skills: List) -> str:
    """Generate markdown table of skills."""
    lines = [
        "# SuperSkills Reference",
        "",
        "## Available Skills",
        "",
        "| Skill | Type | Description | Profile | APIs |",
        "|-------|------|-------------|---------|------|"
    ]

    loader = SkillLoader()

    for skill in sorted(skills, key=lambda s: s.name):
        skill_type = skill.skill_type.capitalize()
        profile_marker = "✓" if skill.has_profile else "-"
        apis = ", ".join(_get_api_requirements(skill.name)) if skill.name in loader.PYTHON_SKILLS else "Anthropic"

        lines.append(
            f"| **{skill.name}** | {skill_type} | {skill.description} | {profile_marker} | {apis} |"
        )

    lines.extend([
        "",
        "## Categorization",
        "",
        "### Content Skills",
        "author, copywriter, editor, translator",
        "",
        "### Media Skills",
        "narrator, designer, transcriber, videoeditor, presenter",
        "",
        "### Business Skills",
        "coach, strategist, marketer, sales, publisher",
        "",
        "### Technical Skills",
        "developer, scraper, craft, webmaster",
        ""
    ])

    return "\n".join(lines)
