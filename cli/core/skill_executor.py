"""
Skill execution engine.
"""
import importlib
from pathlib import Path
from typing import Dict, Any, Optional
from cli.core.skill_loader import SkillLoader, SkillInfo
from cli.utils.api_client import APIClient
from cli.utils.config import CLIConfig
from cli.utils.logger import get_logger


class SkillExecutor:
    def __init__(self, config: CLIConfig):
        self.config = config
        self.loader = SkillLoader()
        self.api_client = None
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
        
        system_prompt = self._build_system_prompt(content['skill'], content['profile'])
        
        if self.api_client is None:
            self.logger.debug("Initializing API client")
            api_key = self.config.get_api_key('anthropic')
            model = self.config.get('api.anthropic.model', 'claude-sonnet-4')
            max_tokens = self.config.get('api.anthropic.max_tokens', 4000)
            temperature = self.config.get('api.anthropic.temperature', 0.7)
            
            self.api_client = APIClient(
                api_key=api_key,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature
            )
        
        self.logger.info(f"Calling API with model: {self.api_client.model}")
        output = self.api_client.call(
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
                'model': self.api_client.model
            }
        }
    
    def _build_system_prompt(self, skill_content: str, profile_content: Optional[str]) -> str:
        prompt_parts = [
            "You are an AI assistant with specialized skills.",
            "",
            "# Your Role and Guidelines",
            skill_content,
        ]
        
        if profile_content:
            prompt_parts.extend([
                "",
                "# Personal Profile and Customization",
                profile_content,
            ])
        
        return "\n".join(prompt_parts)
    
    def _execute_python_skill(self, skill_info: SkillInfo, input_text: str, **kwargs) -> Dict[str, Any]:
        if not skill_info.python_module:
            self.logger.error(f"Python module not configured for skill: {skill_info.name}")
            raise ValueError(f"Python module not configured for skill: {skill_info.name}")
        
        module_path, class_name = skill_info.python_module.split(':')
        
        try:
            self.logger.debug(f"Loading Python module: {module_path}")
            module = importlib.import_module(module_path)
            skill_class = getattr(module, class_name)
            
            output_dir = kwargs.get('output_dir', self.config.cache_dir)
            
            if skill_info.name == 'narrator':
                profile_type = kwargs.get('profile_type', 'podcast')
                self.logger.debug(f"Initializing narrator with profile: {profile_type}")
                skill_instance = skill_class(output_dir=str(output_dir), profile_type=profile_type)
                
                content_type = kwargs.get('content_type', 'podcast')
                self.logger.info(f"Generating narration for content type: {content_type}")
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
            
            else:
                self.logger.error(f"Python skill execution not implemented for: {skill_info.name}")
                raise NotImplementedError(f"Python skill execution not implemented for: {skill_info.name}")
        
        except Exception as e:
            self.logger.error(f"Failed to execute Python skill {skill_info.name}: {e}", exc_info=True)
            raise RuntimeError(f"Failed to execute Python skill {skill_info.name}: {e}")
