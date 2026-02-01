"""
Skill execution engine.
"""
import importlib
import json
from typing import Any, Dict, Optional

from cli.core.skill_loader import SkillInfo, SkillLoader
from cli.utils.config import CLIConfig
from cli.utils.llm_client import LLMProvider
from cli.utils.logger import get_logger


class SkillExecutor:
    def __init__(self, config: CLIConfig):
        self.config = config
        self.loader = SkillLoader()
        self.llm_provider = None
        self.logger = get_logger()

    def execute(self, skill_name: str, input_text: str, **kwargs) -> Dict[str, Any]:
        skill_info = self.loader.get_skill(skill_name)
        if not skill_info:
            self.logger.error(f"Skill not found: {skill_name}")
            raise ValueError(f"Skill not found: {skill_name}")

        self.logger.info(f"Executing {skill_info.skill_type} skill: {skill_name}")
        self.logger.debug(f"Input length: {len(input_text)} characters")

        if skill_info.skill_type == 'prompt':
            return self._execute_prompt_skill(skill_info, input_text, **kwargs)
        else:
            return self._execute_python_skill(skill_info, input_text, **kwargs)

    def _execute_prompt_skill(self, skill_info: SkillInfo, input_text: str, **kwargs) -> Dict[str, Any]:
        self.logger.debug(f"Loading skill content for: {skill_info.name}")
        content = self.loader.load_skill_content(skill_info.name)

        # Build hierarchical system prompt with all three layers
        system_prompt = self._build_system_prompt(
            content['skill'],
            content['master_briefing'],
            content['profile']
        )

        if self.llm_provider is None:
            self.logger.debug("Initializing LLM provider")

            # Support both old (api.anthropic.*) and new (api.provider) config structures
            provider_name = self.config.get('api.provider')
            if provider_name:
                # New config structure
                model = self.config.get('api.model', 'gemini-flash-latest')
                max_tokens = self.config.get('api.max_tokens', 4000)
                temperature = self.config.get('api.temperature', 0.7)
            else:
                # Legacy config structure (api.anthropic.*)
                provider_name = 'anthropic'
                model = self.config.get('api.anthropic.model', 'claude-sonnet-latest')
                max_tokens = self.config.get('api.anthropic.max_tokens', 4000)
                temperature = self.config.get('api.anthropic.temperature', 0.7)

            self.llm_provider = LLMProvider.create(
                provider=provider_name,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature
            )

        self.logger.info(f"Calling {self.llm_provider.__class__.__name__}")
        output = self.llm_provider.call(
            system_prompt=system_prompt,
            user_prompt=input_text,
            **kwargs
        )

        self.logger.info(f"Skill execution completed. Output length: {len(output)} characters")

        return {
            'output': output,
            'metadata': {
                'skill': skill_info.name,
                'type': 'prompt',
                'provider': self.llm_provider.__class__.__name__
            }
        }

    def _build_system_prompt(
        self,
        skill_content: str,
        master_briefing: Optional[str],
        profile_content: Optional[str]
    ) -> str:
        """
        Build system prompt with hierarchical context.

        Priority (most specific wins):
        1. Skill PROFILE.md (skill-specific customization - highest priority)
        2. Master Briefing (global brand voice)
        3. SKILL.md (role definition - baseline)

        The system prompt explicitly instructs the LLM which layer takes priority
        when conflicts arise.
        """
        prompt_parts = [
            "You are an AI assistant with specialized skills.",
            "",
            "# Your Role and Guidelines",
            skill_content,
        ]

        # Layer 1: Master Briefing (global context)
        if master_briefing:
            prompt_parts.extend([
                "",
                "# Global Brand Context (Master Briefing)",
                "The following defines your overall brand voice, audience, and principles.",
                "Use this as your foundation, but defer to skill-specific customization when provided.",
                "",
                master_briefing,
            ])

        # Layer 2: Skill Profile (specific customization - highest priority)
        if profile_content:
            prompt_parts.extend([
                "",
                "# Skill-Specific Customization (PROFILE.md)",
                "The following customizes this specific skill. These instructions take priority over general guidelines.",
                "",
                profile_content,
            ])

        return "\n".join(prompt_parts)

    def _execute_python_skill(self, skill_info: SkillInfo, input_text: str, **kwargs) -> Dict[str, Any]:
        if not skill_info.python_module:
            self.logger.error(f"Python module not configured for skill: {skill_info.name}")
            raise ValueError(f"Python module not configured for skill: {skill_info.name}")

        # Load skill-specific credentials before executing
        # This ensures skill-specific .env files override global settings
        try:
            from superskills.core.credentials import load_credentials
            load_credentials(skill_name=skill_info.name, verbose=False)
            self.logger.debug(f"Loaded credentials for skill: {skill_info.name}")
        except ImportError:
            self.logger.warning("Could not import superskills.core.credentials")
        except Exception as e:
            self.logger.debug(f"Credential loading info: {e}")

        module_path, class_name = skill_info.python_module.split(':')

        try:
            self.logger.debug(f"Loading Python module: {module_path}")
            module = importlib.import_module(module_path)
            skill_class = getattr(module, class_name)

            output_dir = kwargs.get('output_dir', self.config.cache_dir)

            if skill_info.name == 'narrator' or skill_info.name.startswith('narrator-'):
                # Map narrator subskill names to content and profile types
                narrator_config = {
                    'narrator': ('podcast', 'podcast'),  # Default for backward compatibility
                    'narrator-podcast': ('podcast', 'podcast'),
                    'narrator-meditation': ('meditation', 'meditation'),
                    'narrator-educational': ('educational', 'narration'),
                    'narrator-marketing': ('marketing', 'narration'),
                    'narrator-social': ('social', 'narration'),
                }

                content_type, profile_type = narrator_config.get(
                    skill_info.name,
                    ('podcast', 'podcast')
                )

                self.logger.debug(f"Initializing {skill_info.name} with profile: {profile_type}")
                skill_instance = skill_class(
                    output_dir=str(output_dir),
                    profile_type=profile_type
                )

                self.logger.info(f"Generating {content_type} narration")
                result = skill_instance.generate(
                    script=input_text,
                    content_type=content_type,
                    output_filename=kwargs.get('output_filename')
                )

                self.logger.info(f"Narration generated: {result['output_file']}")

                return {
                    'output': result['output_file'],
                    'metadata': {
                        'skill': skill_info.name,
                        'type': 'python',
                        **result
                    }
                }

            elif skill_info.name == 'transcriber':
                self.logger.debug("Initializing transcriber")
                skill_instance = skill_class()
                self.logger.info(f"Transcribing audio file: {input_text}")
                result = skill_instance.transcribe(input_text)

                self.logger.info("Transcription completed")

                return {
                    'output': result,
                    'metadata': {
                        'skill': skill_info.name,
                        'type': 'python'
                    }
                }

            elif skill_info.name == 'obsidian':
                # Parse JSON input
                try:
                    params = json.loads(input_text)
                except json.JSONDecodeError:
                    raise ValueError(f"Obsidian skill requires JSON input. Got: {input_text[:100]}")

                # Import the execute function directly
                obsidian_module = importlib.import_module('superskills.obsidian.src')
                result = obsidian_module.execute(**params)

                return {
                    'output': result,
                    'metadata': {
                        'skill': skill_info.name,
                        'type': 'python'
                    }
                }

            elif skill_info.name == 'audiobook':
                # Import the execute function from audiobook skill
                audiobook_module = importlib.import_module('superskills.audiobook.src')
                
                # Pass input_text and all kwargs to the execute function
                result = audiobook_module.execute(input_text, **kwargs)
                
                return result

            else:
                self.logger.error(f"Python skill execution not implemented for: {skill_info.name}")
                raise NotImplementedError(f"Python skill execution not implemented for: {skill_info.name}")

        except Exception as e:
            self.logger.error(f"Failed to execute Python skill {skill_info.name}: {e}", exc_info=True)
            raise RuntimeError(f"Failed to execute Python skill {skill_info.name}: {e}")
