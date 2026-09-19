"""
Regression tests for the 2026-07 audit fixes:

1. Embedded ${var} template resolution in workflow inputs
2. Runtime-variable whitelist + scalar workflow variables (shipped workflows validate)
3. Watch/batch output written to io.output_dir; failed files not retried forever
4. Path traversal rejected for io dirs and workflow names
5. Config migration preserves user customizations
6. LLMProvider.create(model=None) falls through to provider defaults
"""
import yaml
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from cli.core.workflow_engine import WorkflowEngine
from cli.utils.validation import WorkflowValidator
from cli.utils.config import CLIConfig

PROJECT_ROOT = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_engine(context=None):
    """Build a WorkflowEngine without running __init__ (no config needed)."""
    engine = WorkflowEngine.__new__(WorkflowEngine)
    engine.context = context or {}
    engine.logger = MagicMock()
    engine.progress = MagicMock()
    engine.validator = MagicMock()
    engine.validator.validate_workflow.return_value = (True, [])
    engine.executor = MagicMock()
    engine.executor.execute.return_value = {'output': 'STEP OUTPUT'}
    prog_cm = MagicMock()
    prog_cm.__enter__ = MagicMock(return_value=MagicMock())
    prog_cm.__exit__ = MagicMock(return_value=False)
    engine.progress.create_workflow_progress.return_value = prog_cm
    return engine


def write_workflow(wf_dir: Path, workflow: dict):
    wf_dir.mkdir(parents=True, exist_ok=True)
    (wf_dir / 'workflow.yaml').write_text(yaml.dump(workflow), encoding='utf-8')
    return wf_dir / 'workflow.yaml'


# ---------------------------------------------------------------------------
# 1. Variable resolution
# ---------------------------------------------------------------------------

class TestVariableResolution:
    def test_embedded_variables_resolve(self):
        engine = make_engine({'topic': 'AI', 'research': 'data'})
        result = engine._resolve_variable('Topic: ${topic}\nResearch: ${research}')
        assert result == 'Topic: AI\nResearch: data'

    def test_whole_string_preserves_type(self):
        engine = make_engine({'flag': True, 'meta': {'author': 'Steff'}})
        assert engine._resolve_variable('${flag}') is True
        assert engine._resolve_variable('${meta}') == {'author': 'Steff'}

    def test_dotted_path_embedded(self):
        engine = make_engine({'meta': {'author': 'Steff'}})
        assert engine._resolve_variable('By ${meta.author}') == 'By Steff'

    def test_unresolved_variable_stays_literal_and_warns(self):
        engine = make_engine({'topic': 'AI'})
        result = engine._resolve_variable('X: ${missing} Y: ${topic}')
        assert result == 'X: ${missing} Y: AI'
        assert engine.logger.warning.called

    def test_non_string_passthrough(self):
        engine = make_engine()
        assert engine._resolve_variable(42) == 42
        assert engine._resolve_variable(None) is None

    def test_variable_set_to_none_resolves_to_none(self):
        # A variable legitimately set to None is distinguishable from missing
        engine = make_engine({'empty': None})
        assert engine._resolve_variable('${empty}') is None
        assert not engine.logger.warning.called


# ---------------------------------------------------------------------------
# 2. Validator: runtime variables + scalar workflow variables
# ---------------------------------------------------------------------------

class TestValidator:
    @pytest.mark.parametrize('wf_path', sorted(
        (PROJECT_ROOT / 'workflows').glob('*/workflow.yaml')
    ) + sorted(
        (PROJECT_ROOT / 'workflows_templates').glob('*/workflow.yaml')
    ), ids=lambda p: f"{p.parent.parent.name}/{p.parent.name}")
    def test_shipped_workflows_validate(self, wf_path):
        validator = WorkflowValidator()
        is_valid, errors = validator.validate_workflow(wf_path)
        assert is_valid, f"{wf_path}: {errors}"

    def test_runtime_variables_whitelisted(self, tmp_path):
        wf = write_workflow(tmp_path / 'wf', {
            'name': 'rt',
            'steps': [{'name': 's1', 'skill': 'copywriter',
                       'input': '${input_file} ${filename} ${input}', 'output': 'r'}],
        })
        is_valid, errors = WorkflowValidator().validate_workflow(wf)
        assert is_valid, errors

    def test_boolean_variable_allowed(self, tmp_path):
        wf = write_workflow(tmp_path / 'wf', {
            'name': 'boolvar',
            'variables': {'flag': True, 'count': 3, 'label': 'x'},
            'steps': [{'name': 's1', 'skill': 'copywriter',
                       'input': '${flag} ${count} ${label}', 'output': 'r'}],
        })
        is_valid, errors = WorkflowValidator().validate_workflow(wf)
        assert is_valid, errors

    def test_step_referencing_own_output_rejected(self, tmp_path):
        wf = write_workflow(tmp_path / 'wf', {
            'name': 'selfref',
            'steps': [{'name': 's1', 'skill': 'copywriter',
                       'input': '${r}', 'output': 'r'}],
        })
        is_valid, errors = WorkflowValidator().validate_workflow(wf)
        assert not is_valid
        assert any('Undefined variable' in e for e in errors)


# ---------------------------------------------------------------------------
# 3. Batch output + context isolation
# ---------------------------------------------------------------------------

class TestBatchExecution:
    def _setup_workflow(self, tmp_path, io_config):
        wf_dir = tmp_path / 'workflows' / 'testwf'
        (wf_dir / 'input').mkdir(parents=True)
        (wf_dir / 'input' / 'article.txt').write_text('hello', encoding='utf-8')
        write_workflow(wf_dir, {
            'name': 'testwf',
            'io': io_config,
            'steps': [{'name': 's1', 'skill': 'copywriter',
                       'input': 'Process ${input_file}', 'output': 'result'}],
        })
        return wf_dir

    def test_batch_writes_output_file(self, tmp_path):
        wf_dir = self._setup_workflow(tmp_path, {'input_dir': 'input', 'output_dir': 'output'})
        engine = make_engine()
        with patch.object(WorkflowEngine, '_find_workflow_file',
                          return_value=wf_dir / 'workflow.yaml'):
            rc = engine.batch_execute('testwf')
        assert rc == 0
        outputs = list((wf_dir / 'output').glob('article_*.md'))
        assert len(outputs) == 1
        assert outputs[0].read_text(encoding='utf-8') == 'STEP OUTPUT'

    def test_batch_resolved_input_reaches_executor(self, tmp_path):
        wf_dir = self._setup_workflow(tmp_path, {'input_dir': 'input', 'output_dir': 'output'})
        engine = make_engine()
        with patch.object(WorkflowEngine, '_find_workflow_file',
                          return_value=wf_dir / 'workflow.yaml'):
            engine.batch_execute('testwf')
        # the ${input_file} placeholder must have been substituted
        assert engine.executor.execute.call_args[0][1] == 'Process hello'

    def test_context_reset_between_executions(self, tmp_path):
        wf_dir = self._setup_workflow(tmp_path, {'input_dir': 'input', 'output_dir': 'output'})
        engine = make_engine({'stale_output': 'LEAKED FROM PREVIOUS FILE'})
        with patch.object(WorkflowEngine, '_find_workflow_file',
                          return_value=wf_dir / 'workflow.yaml'):
            engine.batch_execute('testwf')
        assert 'stale_output' not in engine.context


# ---------------------------------------------------------------------------
# 4. Path traversal
# ---------------------------------------------------------------------------

class TestPathTraversal:
    def test_traversal_input_dir_rejected(self, tmp_path):
        wf_dir = tmp_path / 'workflows' / 'evil'
        write_workflow(wf_dir, {
            'name': 'evil',
            'io': {'input_dir': '../../../etc'},
            'steps': [{'name': 's1', 'skill': 'copywriter', 'input': 'x', 'output': 'r'}],
        })
        engine = make_engine()
        with patch.object(WorkflowEngine, '_find_workflow_file',
                          return_value=wf_dir / 'workflow.yaml'):
            rc = engine.batch_execute('evil')
        assert rc == 1

    def test_absolute_input_dir_rejected(self, tmp_path):
        wf_dir = tmp_path / 'workflows' / 'evil2'
        write_workflow(wf_dir, {
            'name': 'evil2',
            'io': {'input_dir': '/etc'},
            'steps': [{'name': 's1', 'skill': 'copywriter', 'input': 'x', 'output': 'r'}],
        })
        engine = make_engine()
        with patch.object(WorkflowEngine, '_find_workflow_file',
                          return_value=wf_dir / 'workflow.yaml'):
            rc = engine.batch_execute('evil2')
        assert rc == 1

    @pytest.mark.parametrize('bad_name', ['../../evil', 'a/b', 'x;rm -rf', '.hidden', ''])
    def test_invalid_workflow_names_rejected(self, bad_name):
        engine = make_engine()
        with pytest.raises(ValueError):
            engine._find_workflow_file(bad_name)

    @pytest.mark.parametrize('good_name', ['content-creation', 'my_workflow2', 'A1'])
    def test_valid_workflow_names_accepted(self, good_name):
        engine = make_engine()
        # Must not raise; returns None when file doesn't exist
        engine._find_workflow_file(good_name)


# ---------------------------------------------------------------------------
# 5. Config migration
# ---------------------------------------------------------------------------

class TestConfigMigration:
    def test_migration_preserves_customizations(self, tmp_path):
        (tmp_path / 'config.yaml').write_text(yaml.dump({
            'version': '2.4.1',
            'api': {'provider': 'anthropic', 'model': 'claude-3-haiku-20240307'},
            'search': {'paths': ['/my/vault'], 'max_results': 99},
        }), encoding='utf-8')
        config = CLIConfig(config_dir=tmp_path)
        loaded = config.load()
        assert loaded['api']['provider'] == 'anthropic'
        assert loaded['search']['paths'] == ['/my/vault']
        assert loaded['search']['max_results'] == 99
        # defaults fill in missing keys
        assert loaded['search']['use_ripgrep'] is True
        # backup written
        assert (tmp_path / 'config.yaml.bak-2.4.1').exists()

    def test_invalid_model_scrubbed_but_rest_kept(self, tmp_path):
        from cli.utils.version import get_version
        (tmp_path / 'config.yaml').write_text(yaml.dump({
            'version': get_version(),
            'api': {'provider': 'gemini', 'model': 'gemini-2.0-flash-exp', 'max_tokens': 8000},
        }), encoding='utf-8')
        loaded = CLIConfig(config_dir=tmp_path).load()
        assert loaded['api']['model'] == 'gemini-flash-latest'
        assert loaded['api']['max_tokens'] == 8000

    def test_current_config_untouched(self, tmp_path):
        from cli.utils.version import get_version
        (tmp_path / 'config.yaml').write_text(yaml.dump({
            'version': get_version(),
            'api': {'provider': 'openai', 'model': 'gpt-4o-mini'},
        }), encoding='utf-8')
        loaded = CLIConfig(config_dir=tmp_path).load()
        assert loaded['api']['provider'] == 'openai'
        assert not list(tmp_path.glob('*.bak*'))

    def test_corrupt_yaml_backed_up_and_regenerated(self, tmp_path):
        (tmp_path / 'config.yaml').write_text('api: [unclosed', encoding='utf-8')
        loaded = CLIConfig(config_dir=tmp_path).load()
        assert loaded['api']['provider'] == 'gemini'
        assert (tmp_path / 'config.yaml.bak-corrupt').exists()


# ---------------------------------------------------------------------------
# 6. LLMProvider factory model=None regression
# ---------------------------------------------------------------------------

class TestLLMProviderFactory:
    def test_model_none_uses_provider_default(self):
        from cli.utils.llm_client import LLMProvider
        provider = LLMProvider.create('gemini', api_key='fake-key', model=None)
        assert provider.model_name == 'gemini-2.0-flash-exp'

    def test_explicit_model_respected(self):
        from cli.utils.llm_client import LLMProvider
        provider = LLMProvider.create('gemini', api_key='fake-key', model='my-model')
        assert provider.model_name == 'my-model'

    def test_unknown_provider_raises(self):
        from cli.utils.llm_client import LLMProvider
        with pytest.raises(ValueError, match='Unknown provider'):
            LLMProvider.create('nonsense', api_key='x')
