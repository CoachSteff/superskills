"""
Unit tests for intent router
"""
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from cli.core.intent_parser import IntentResult
from cli.core.intent_router import IntentRouter
from cli.utils.config import CLIConfig


@pytest.fixture
def mock_config():
    """Create a mock config"""
    return Mock(spec=CLIConfig)


@pytest.fixture
def router(mock_config):
    """Create intent router"""
    return IntentRouter(mock_config)


class TestIntentRouter:
    """Test intent router functionality"""

    @pytest.mark.skip(reason="search_command feature not implemented")
    @patch('cli.core.intent_router.search_command')
    def test_route_search(self, mock_search, router):
        """Test routing search intent"""
        mock_search.return_value = 0

        intent = IntentResult(
            action="search",
            target=None,
            parameters={"query": "test query", "type": "file"},
            confidence=0.9,
            reasoning="Search for files"
        )

        result = router.route(intent)

        assert result == 0
        mock_search.assert_called_once_with(query="test query", search_type="file")

    @patch('cli.core.intent_router.call_command')
    def test_route_execute_skill(self, mock_call, router):
        """Test routing execute_skill intent"""
        mock_call.return_value = 0

        intent = IntentResult(
            action="execute_skill",
            target="copywriter",
            parameters={"input": "test input"},
            confidence=0.95,
            reasoning="Execute skill"
        )

        result = router.route(intent)

        assert result == 0
        mock_call.assert_called_once_with("copywriter", "test input")

    @patch('cli.core.intent_router.call_command')
    def test_route_execute_skill_with_file(self, mock_call, router):
        """Test routing execute_skill intent with file input"""
        mock_call.return_value = 0

        # Create temp file
        temp_file = Path("/tmp/test_input.txt")
        temp_file.write_text("test content")

        try:
            intent = IntentResult(
                action="execute_skill",
                target="copywriter",
                parameters={"input_file": str(temp_file)},
                confidence=0.95,
                reasoning="Execute skill with file"
            )

            result = router.route(intent)

            assert result == 0
            mock_call.assert_called_once()
            call_args = mock_call.call_args
            assert call_args[0][0] == "copywriter"
            assert "input_file" in call_args[1]
        finally:
            if temp_file.exists():
                temp_file.unlink()

    @patch('cli.core.intent_router.run_command')
    def test_route_run_workflow(self, mock_run, router):
        """Test routing run_workflow intent"""
        mock_run.return_value = 0

        intent = IntentResult(
            action="run_workflow",
            target="podcast-generation-simple",
            parameters={"topic": "AI"},
            confidence=0.8,
            reasoning="Run workflow"
        )

        result = router.route(intent)

        assert result == 0
        mock_run.assert_called_once_with("podcast-generation-simple", topic="AI")

    @patch('cli.core.intent_router.list_command')
    def test_route_list(self, mock_list, router):
        """Test routing list intent"""
        mock_list.return_value = 0

        intent = IntentResult(
            action="list",
            target=None,
            parameters={"format": "json"},
            confidence=1.0,
            reasoning="List skills"
        )

        result = router.route(intent)

        assert result == 0
        mock_list.assert_called_once_with(format="json")

    @patch('cli.core.intent_router.show_command')
    def test_route_show(self, mock_show, router):
        """Test routing show intent"""
        mock_show.return_value = 0

        intent = IntentResult(
            action="show",
            target="narrator",
            parameters={},
            confidence=0.9,
            reasoning="Show skill"
        )

        result = router.route(intent)

        assert result == 0
        mock_show.assert_called_once_with("narrator")

    @patch('cli.core.intent_router.config_set_command')
    def test_route_config_set(self, mock_config_set, router):
        """Test routing config set intent"""
        mock_config_set.return_value = 0

        intent = IntentResult(
            action="config",
            target=None,
            parameters={"key": "api.temperature", "value": "0.5"},
            confidence=0.8,
            reasoning="Set config"
        )

        result = router.route(intent)

        assert result == 0
        mock_config_set.assert_called_once_with("api.temperature", "0.5")

    @patch('cli.core.intent_router.config_get_command')
    def test_route_config_get(self, mock_config_get, router):
        """Test routing config get intent"""
        mock_config_get.return_value = 0

        intent = IntentResult(
            action="config",
            target=None,
            parameters={"key": "api.temperature"},
            confidence=0.8,
            reasoning="Get config"
        )

        result = router.route(intent)

        assert result == 0
        mock_config_get.assert_called_once_with("api.temperature")

    @patch('cli.core.intent_router.discover_command')
    def test_route_discover(self, mock_discover, router):
        """Test routing discover intent"""
        mock_discover.return_value = 0

        intent = IntentResult(
            action="discover",
            target=None,
            parameters={"query": "podcasts"},
            confidence=0.85,
            reasoning="Discover skills"
        )

        result = router.route(intent)

        assert result == 0
        mock_discover.assert_called_once_with(query="podcasts")

    def test_route_missing_target_for_execute_skill(self, router, capsys):
        """Test error when execute_skill has no target"""
        intent = IntentResult(
            action="execute_skill",
            target=None,
            parameters={},
            confidence=0.9,
            reasoning="Execute skill"
        )

        result = router.route(intent)

        assert result == 1
        captured = capsys.readouterr()
        assert "Skill name is required" in captured.out

    def test_route_unknown_action(self, router, capsys):
        """Test handling unknown action"""
        intent = IntentResult(
            action="unknown_action",
            target=None,
            parameters={},
            confidence=0.9,
            reasoning="Unknown"
        )

        result = router.route(intent)

        assert result == 1
        captured = capsys.readouterr()
        assert "Unknown action" in captured.out
