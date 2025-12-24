"""
Master Briefing loader for global brand voice and context.

The Master Briefing is a YAML document stored at ~/.superskills/master-briefing.yaml
that defines brand voice, audience, frameworks, and other context shared across all skills.
"""
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from cli.utils.logger import get_logger


class MasterBriefingLoader:
    """Load and format Master Briefing for system prompts."""

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize Master Briefing loader.
        
        Args:
            config_dir: Configuration directory path. Defaults to ~/.superskills
        """
        if config_dir is None:
            config_dir = Path.home() / ".superskills"

        self.config_dir = Path(config_dir)
        self.master_briefing_path = self.config_dir / "master-briefing.yaml"
        self.logger = get_logger()
        self._cached_content: Optional[Dict[str, Any]] = None
        self._cache_mtime: Optional[float] = None

    def load(self) -> Optional[Dict[str, Any]]:
        """
        Load Master Briefing from YAML file.
        
        Returns:
            Dictionary containing Master Briefing data, or None if file doesn't exist
        """
        if not self.master_briefing_path.exists():
            self.logger.debug("Master Briefing not found (this is optional)")
            return None

        try:
            # Check cache validity
            current_mtime = self.master_briefing_path.stat().st_mtime
            if self._cached_content and self._cache_mtime == current_mtime:
                self.logger.debug("Using cached Master Briefing")
                return self._cached_content

            # Load and parse YAML
            with open(self.master_briefing_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)

            if not isinstance(content, dict):
                self.logger.warning("Master Briefing is not a valid YAML dictionary")
                return None

            # Cache the result
            self._cached_content = content
            self._cache_mtime = current_mtime

            self.logger.debug(f"Master Briefing loaded from {self.master_briefing_path}")
            return content

        except yaml.YAMLError as e:
            self.logger.warning(f"Failed to parse Master Briefing YAML: {e}")
            return None
        except Exception as e:
            self.logger.warning(f"Failed to load Master Briefing: {e}")
            return None

    def get_section(self, section_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific section from Master Briefing.
        
        Args:
            section_name: Name of section (e.g., 'identity', 'voice', 'audience')
        
        Returns:
            Section content as dictionary, or None if not found
        """
        briefing = self.load()
        if not briefing:
            return None

        return briefing.get(section_name)

    def format_for_prompt(self) -> str:
        """
        Format Master Briefing as markdown for inclusion in system prompt.
        
        Returns:
            Formatted markdown string, or empty string if no briefing
        """
        briefing = self.load()
        if not briefing:
            return ""

        sections = []

        # 1. Identity & Context
        if 'identity' in briefing:
            identity = briefing['identity']
            sections.append("## Identity & Context")
            if identity.get('name'):
                sections.append(f"**Name**: {identity['name']}")
            if identity.get('role'):
                sections.append(f"**Role**: {identity['role']}")
            if identity.get('business'):
                sections.append(f"**Business**: {identity['business']}")
            if identity.get('domain'):
                sections.append(f"**Domain**: {identity['domain']}")
            if identity.get('experience'):
                sections.append(f"**Experience**: {identity['experience']}")
            sections.append("")

        # 2. Audience
        if 'audience' in briefing:
            audience = briefing['audience']
            sections.append("## Audience")
            if audience.get('primary'):
                sections.append(f"**Primary**: {audience['primary']}")
            if audience.get('secondary'):
                sections.append(f"**Secondary**: {audience['secondary']}")
            if audience.get('pain_points'):
                sections.append("\n**Pain Points**:")
                for point in audience['pain_points']:
                    sections.append(f"- {point}")
            if audience.get('desired_feeling'):
                sections.append(f"\n**Desired Feeling**: {audience['desired_feeling']}")
            sections.append("")

        # 3. Voice & Tone
        if 'voice' in briefing:
            voice = briefing['voice']
            sections.append("## Voice & Tone")
            if voice.get('style'):
                sections.append(f"**Style**: {voice['style']}")

            if voice.get('characteristics'):
                sections.append("\n**Characteristics**:")
                for char in voice['characteristics']:
                    sections.append(f"- {char}")

            if voice.get('language_patterns'):
                sections.append("\n**Language Patterns**:")
                for pattern in voice['language_patterns']:
                    sections.append(f"- {pattern}")

            if voice.get('signature_elements'):
                sections.append("\n**Signature Elements**:")
                for element in voice['signature_elements']:
                    sections.append(f"- {element}")

            if voice.get('avoid'):
                sections.append("\n**Avoid**:")
                for item in voice['avoid']:
                    sections.append(f"- {item}")
            sections.append("")

        # 4. Perspective & Positioning
        if 'perspective' in briefing:
            perspective = briefing['perspective']
            sections.append("## Perspective & Positioning")
            if perspective.get('lens'):
                sections.append(f"**Lens**: {perspective['lens']}")
            if perspective.get('goal'):
                sections.append(f"**Goal**: {perspective['goal']}")
            if perspective.get('reader_positioning'):
                sections.append(f"**Reader Positioning**: {perspective['reader_positioning']}")
            if perspective.get('guiding_principle'):
                sections.append(f"**Guiding Principle**: {perspective['guiding_principle']}")
            sections.append("")

        # 5. Frameworks
        if 'frameworks' in briefing and isinstance(briefing['frameworks'], list):
            sections.append("## Core Frameworks")
            for framework in briefing['frameworks']:
                if isinstance(framework, dict) and framework.get('name'):
                    sections.append(f"\n**{framework['name']}**")
                    if framework.get('description'):
                        sections.append(f"{framework['description']}")
                    if framework.get('when_to_use'):
                        sections.append(f"*When to use*: {framework['when_to_use']}")
                    if framework.get('components'):
                        for component in framework['components']:
                            sections.append(f"- {component}")
            sections.append("")

        # 6. Expertise
        if 'expertise' in briefing:
            expertise = briefing['expertise']
            sections.append("## Expertise")
            if expertise.get('areas'):
                sections.append("**Areas**:")
                for area in expertise['areas']:
                    sections.append(f"- {area}")
            if expertise.get('credentials'):
                sections.append("\n**Credentials**:")
                for cred in expertise['credentials']:
                    sections.append(f"- {cred}")
            if expertise.get('proof_points'):
                sections.append("\n**Proof Points**:")
                for point in expertise['proof_points']:
                    sections.append(f"- {point}")
            if expertise.get('industries'):
                sections.append(f"\n**Industries**: {', '.join(expertise['industries'])}")
            sections.append("")

        # 7. Examples & Voice Samples
        if 'examples' in briefing:
            examples = briefing['examples']
            sections.append("## Examples & Voice Samples")

            if examples.get('signature_stories'):
                sections.append("**Signature Stories**:")
                for story in examples['signature_stories']:
                    sections.append(f"- {story}")

            if examples.get('sample_voice'):
                sections.append("\n**Sample Voice**:")
                sections.append(examples['sample_voice'])

            if examples.get('typical_hooks'):
                sections.append("\n**Typical Hooks**:")
                for hook in examples['typical_hooks']:
                    sections.append(f"- {hook}")

            if examples.get('before_after'):
                sections.append("\n**Before/After Examples**:")
                for example in examples['before_after']:
                    if isinstance(example, dict):
                        sections.append(f"- **{example.get('scenario', 'Example')}**:")
                        sections.append(f"  - Before: {example.get('before', 'N/A')}")
                        sections.append(f"  - After: {example.get('after', 'N/A')}")
            sections.append("")

        # 8. Guardrails
        if 'guardrails' in briefing:
            guardrails = briefing['guardrails']
            sections.append("## Guardrails & Compliance")

            if guardrails.get('privacy'):
                sections.append("**Privacy**:")
                for item in guardrails['privacy']:
                    sections.append(f"- {item}")

            if guardrails.get('ethics'):
                sections.append("\n**Ethics**:")
                for item in guardrails['ethics']:
                    sections.append(f"- {item}")

            if guardrails.get('compliance'):
                sections.append("\n**Compliance**:")
                for item in guardrails['compliance']:
                    sections.append(f"- {item}")

            if guardrails.get('human_judgment_required'):
                sections.append("\n**Human Judgment Required**:")
                for item in guardrails['human_judgment_required']:
                    sections.append(f"- {item}")
            sections.append("")

        return "\n".join(sections)
