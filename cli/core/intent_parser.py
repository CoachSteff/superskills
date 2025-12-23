"""
Intent parser: Convert natural language to structured intent JSON
"""
import json
import os
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from pathlib import Path
from functools import lru_cache
import jsonschema

from cli.utils.llm_client import LLMProvider
from cli.utils.config import CLIConfig
from cli.core.skill_loader import SkillLoader
from cli.utils.logger import get_logger


@dataclass
class IntentResult:
    """Structured intent result"""
    action: str
    target: Optional[str]
    parameters: Dict[str, Any]
    confidence: float
    reasoning: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'action': self.action,
            'target': self.target,
            'parameters': self.parameters,
            'confidence': self.confidence,
            'reasoning': self.reasoning
        }


class IntentParser:
    """Parse natural language into structured intent"""
    
    def __init__(self, config: CLIConfig):
        self.config = config
        self.logger = get_logger()
        self.skill_loader = SkillLoader()
        
        # Load intent schema
        schema_path = Path(__file__).parent.parent / 'schemas' / 'intent_schema.json'
        with open(schema_path, 'r') as f:
            self.schema = json.load(f)
        
        # Initialize LLM provider with model resolution
        from cli.utils.model_resolver import ModelResolver
        
        provider_name = os.getenv('SUPERSKILLS_INTENT_PROVIDER') or config.get('intent.provider', 'gemini')
        model_alias = os.getenv('SUPERSKILLS_INTENT_MODEL') or config.get('intent.model', 'gemini-flash-latest')
        
        # Resolve model alias to concrete ID
        resolved_model = model_alias
        try:
            # Get API key for model resolution (if needed)
            api_key = os.getenv('GEMINI_API_KEY') or os.getenv('ANTHROPIC_API_KEY') or os.getenv('OPENAI_API_KEY') or ''
            resolved_model = ModelResolver.resolve(model_alias, api_key, provider=provider_name)
            if resolved_model != model_alias:
                self.logger.info(f"Resolved model: {model_alias} → {resolved_model}")
        except Exception as e:
            self.logger.warning(f"Model resolution failed, using alias directly: {e}")
        
        try:
            self.llm_provider = LLMProvider.create(
                provider=provider_name,
                model=resolved_model,
                temperature=0.3,
                max_tokens=2000
            )
        except ValueError as e:
            self.logger.error(f"Failed to initialize LLM provider: {e}")
            raise
    
    @lru_cache(maxsize=128)
    def _get_skill_context(self) -> str:
        """Get cached skill metadata for context"""
        try:
            skills = self.skill_loader.discover_skills()
            skill_list = []
            for skill in skills:
                skill_list.append(f"- {skill.name}: {skill.description}")
            return "\n".join(skill_list)
        except Exception as e:
            self.logger.warning(f"Could not load skills for context: {e}")
            return ""
    
    def parse(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> IntentResult:
        """Parse natural language input into structured intent"""
        context = context or {}
        
        # Build system prompt
        system_prompt = self._build_system_prompt()
        
        # Call LLM
        try:
            response = self.llm_provider.call(
                system_prompt=system_prompt,
                user_prompt=user_input
            )
            
            # Parse JSON response
            intent_json = self._extract_json(response)
            
            # Validate against schema
            jsonschema.validate(intent_json, self.schema)
            
            # Convert to IntentResult
            result = IntentResult(
                action=intent_json['action'],
                target=intent_json.get('target'),
                parameters=intent_json.get('parameters', {}),
                confidence=intent_json['confidence'],
                reasoning=intent_json['reasoning']
            )
            
            self.logger.debug(f"Parsed intent: {result.action} (confidence: {result.confidence})")
            return result
            
        except jsonschema.ValidationError as e:
            self.logger.error(f"Intent JSON validation failed: {e}")
            raise ValueError(f"Invalid intent structure: {e.message}")
        
        except Exception as e:
            self.logger.error(f"Intent parsing failed: {e}")
            raise ValueError(f"Failed to parse intent: {e}")
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with context"""
        skill_context = self._get_skill_context()
        
        prompt = f"""You are an intent parser for the Superskills CLI, a tool that provides AI-powered automation skills.

Available Skills:
{skill_context}

Available Commands:
- list: Show all available skills
- show <skill>: Display detailed information about a skill
- call <skill> <input>: Execute a specific skill with input
- run <workflow>: Execute a predefined workflow
- config get/set: Manage configuration settings
- discover: Find skills by capability
- search: Search for files or content

Your task: Parse the user's natural language input into a structured intent JSON.

Intent Schema:
{{
  "action": "search|execute_skill|run_workflow|list|show|config|discover",
  "target": "skill_name, workflow_name, or null",
  "parameters": {{ ... }},
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation of your interpretation"
}}

Confidence Guidelines:
- 0.9-1.0: Very clear, unambiguous request
- 0.7-0.8: Clear request with minor assumptions
- 0.5-0.6: Requires some interpretation
- 0.0-0.4: Ambiguous or unclear

Examples:

Input: "Find the Superworker executive summary"
Output: {{"action": "search", "target": null, "parameters": {{"query": "Superworker executive summary", "type": "file"}}, "confidence": 0.9, "reasoning": "File search for 'Superworker executive summary'"}}

Input: "Run copywriter on summary.txt"
Output: {{"action": "execute_skill", "target": "copywriter", "parameters": {{"input_file": "summary.txt"}}, "confidence": 0.95, "reasoning": "Execute copywriter skill with file input"}}

Input: "List all skills"
Output: {{"action": "list", "target": null, "parameters": {{}}, "confidence": 1.0, "reasoning": "List all available skills"}}

Input: "What can help me with podcasts?"
Output: {{"action": "discover", "target": null, "parameters": {{"query": "podcasts"}}, "confidence": 0.85, "reasoning": "Discover skills related to podcasts"}}

Input: "Set temperature to 0.5"
Output: {{"action": "config", "target": null, "parameters": {{"key": "api.anthropic.temperature", "value": "0.5"}}, "confidence": 0.8, "reasoning": "Set API temperature configuration"}}

Input: "Show me the narrator skill"
Output: {{"action": "show", "target": "narrator", "parameters": {{}}, "confidence": 0.95, "reasoning": "Display narrator skill details"}}

Input: "Generate a podcast about AI"
Output: {{"action": "run_workflow", "target": "podcast-generation-simple", "parameters": {{"topic": "AI"}}, "confidence": 0.75, "reasoning": "Run podcast generation workflow with AI topic"}}

Important:
- Output ONLY valid JSON, no markdown formatting or code blocks
- Be concise in reasoning (1 sentence)
- Use confidence scores honestly
- Prefer specific skills/workflows when clearly indicated
- For ambiguous requests, use lower confidence scores
"""
        return prompt
    
    def _extract_json(self, response: str) -> Dict[str, Any]:
        """Extract JSON from LLM response"""
        # Remove markdown code blocks if present
        response = response.strip()
        if response.startswith('```'):
            lines = response.split('\n')
            # Remove first and last lines (code fence)
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].startswith('```'):
                lines = lines[:-1]
            response = '\n'.join(lines)
        
        # Remove 'json' language identifier if present
        response = response.strip()
        if response.lower().startswith('json'):
            response = response[4:].strip()
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {response}")
            raise ValueError(f"Invalid JSON response from LLM: {e}")
    
    def suggest_alternatives(self, intent: IntentResult) -> List[str]:
        """Suggest alternative interpretations for low-confidence intents"""
        suggestions = []
        
        # Generic suggestions based on action
        if intent.action == 'search':
            suggestions.append("List all available skills (superskills list)")
            suggestions.append("Search for a specific skill by capability")
        elif intent.action == 'execute_skill':
            suggestions.append(f"Show details about the '{intent.target}' skill first")
            suggestions.append("List all available skills to find the right one")
        else:
            suggestions.append("List all available skills (superskills list)")
            suggestions.append("Show CLI status (superskills status)")
            suggestions.append("Describe what you want to do more specifically")
        
        return suggestions[:3]
