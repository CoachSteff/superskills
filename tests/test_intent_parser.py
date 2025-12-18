"""
Unit tests for intent parser
"""
import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from cli.core.intent_parser import IntentParser, IntentResult
from cli.utils.config import CLIConfig


@pytest.fixture
def mock_config():
    """Create a mock config"""
    config = Mock(spec=CLIConfig)
    config.get = Mock(side_effect=lambda key, default=None: {
        'intent.provider': 'gemini',
        'intent.model': 'gemini-2.0-flash-exp',
        'intent.confidence_threshold': 0.5,
    }.get(key, default))
    return config


@pytest.fixture
def mock_llm_provider():
    """Create a mock LLM provider"""
    with patch('cli.core.intent_parser.LLMProvider') as mock:
        provider_instance = Mock()
        mock.create.return_value = provider_instance
        yield provider_instance


@pytest.fixture
def mock_skill_loader():
    """Create a mock skill loader"""
    with patch('cli.core.intent_parser.SkillLoader') as mock:
        loader_instance = Mock()
        mock.return_value = loader_instance
        
        # Mock skills
        skill1 = Mock()
        skill1.name = 'copywriter'
        skill1.description = 'Transform analysis into compelling content'
        
        skill2 = Mock()
        skill2.name = 'narrator'
        skill2.description = 'Generate voice-overs for content'
        
        loader_instance.discover_skills.return_value = [skill1, skill2]
        
        yield loader_instance


class TestIntentParser:
    """Test intent parser functionality"""
    
    def test_parse_file_search(self, mock_config, mock_llm_provider, mock_skill_loader):
        """Test parsing file search intent"""
        # Mock LLM response
        mock_llm_provider.call.return_value = json.dumps({
            "action": "search",
            "target": None,
            "parameters": {"query": "Superworker executive summary", "type": "file"},
            "confidence": 0.9,
            "reasoning": "File search for 'Superworker executive summary'"
        })
        
        parser = IntentParser(mock_config)
        result = parser.parse("Find the Superworker executive summary")
        
        assert result.action == "search"
        assert result.target is None
        assert result.parameters["query"] == "Superworker executive summary"
        assert result.confidence == 0.9
        assert "File search" in result.reasoning
    
    def test_parse_execute_skill(self, mock_config, mock_llm_provider, mock_skill_loader):
        """Test parsing execute skill intent"""
        mock_llm_provider.call.return_value = json.dumps({
            "action": "execute_skill",
            "target": "copywriter",
            "parameters": {"input_file": "summary.txt"},
            "confidence": 0.95,
            "reasoning": "Execute copywriter skill with file input"
        })
        
        parser = IntentParser(mock_config)
        result = parser.parse("Run copywriter on summary.txt")
        
        assert result.action == "execute_skill"
        assert result.target == "copywriter"
        assert result.parameters["input_file"] == "summary.txt"
        assert result.confidence == 0.95
    
    def test_parse_list_skills(self, mock_config, mock_llm_provider, mock_skill_loader):
        """Test parsing list skills intent"""
        mock_llm_provider.call.return_value = json.dumps({
            "action": "list",
            "target": None,
            "parameters": {},
            "confidence": 1.0,
            "reasoning": "List all available skills"
        })
        
        parser = IntentParser(mock_config)
        result = parser.parse("List all skills")
        
        assert result.action == "list"
        assert result.confidence == 1.0
    
    def test_parse_show_skill(self, mock_config, mock_llm_provider, mock_skill_loader):
        """Test parsing show skill intent"""
        mock_llm_provider.call.return_value = json.dumps({
            "action": "show",
            "target": "narrator",
            "parameters": {},
            "confidence": 0.95,
            "reasoning": "Display narrator skill details"
        })
        
        parser = IntentParser(mock_config)
        result = parser.parse("Show me the narrator skill")
        
        assert result.action == "show"
        assert result.target == "narrator"
    
    def test_parse_config_set(self, mock_config, mock_llm_provider, mock_skill_loader):
        """Test parsing config set intent"""
        mock_llm_provider.call.return_value = json.dumps({
            "action": "config",
            "target": None,
            "parameters": {"key": "api.anthropic.temperature", "value": "0.5"},
            "confidence": 0.8,
            "reasoning": "Set API temperature configuration"
        })
        
        parser = IntentParser(mock_config)
        result = parser.parse("Set temperature to 0.5")
        
        assert result.action == "config"
        assert result.parameters["key"] == "api.anthropic.temperature"
        assert result.parameters["value"] == "0.5"
    
    def test_extract_json_with_markdown(self, mock_config, mock_llm_provider, mock_skill_loader):
        """Test extracting JSON from markdown code blocks"""
        mock_llm_provider.call.return_value = '''```json
{
    "action": "list",
    "target": null,
    "parameters": {},
    "confidence": 1.0,
    "reasoning": "List skills"
}
```'''
        
        parser = IntentParser(mock_config)
        result = parser.parse("List skills")
        
        assert result.action == "list"
        assert result.confidence == 1.0
    
    def test_invalid_json_raises_error(self, mock_config, mock_llm_provider, mock_skill_loader):
        """Test that invalid JSON raises an error"""
        mock_llm_provider.call.return_value = "This is not JSON"
        
        parser = IntentParser(mock_config)
        
        with pytest.raises(ValueError, match="Invalid JSON"):
            parser.parse("Some query")
    
    def test_suggest_alternatives(self, mock_config, mock_llm_provider, mock_skill_loader):
        """Test suggesting alternatives for low confidence"""
        parser = IntentParser(mock_config)
        
        intent = IntentResult(
            action="search",
            target=None,
            parameters={},
            confidence=0.3,
            reasoning="Unclear request"
        )
        
        suggestions = parser.suggest_alternatives(intent)
        
        assert len(suggestions) > 0
        assert any("skills" in s.lower() for s in suggestions)
