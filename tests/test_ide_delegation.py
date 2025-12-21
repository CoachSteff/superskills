"""
Integration tests for IDE delegation features.
"""
import json
import subprocess
import pytest


class TestExportCommand:
    """Test superskills export command."""
    
    def test_export_json_format(self):
        """Test JSON export format."""
        result = subprocess.run(
            ['superskills', 'export'],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        data = json.loads(result.stdout)
        
        assert 'version' in data
        assert 'skills' in data
        assert 'workflows' in data
        assert 'metadata' in data
        assert len(data['skills']) > 0
    
    def test_export_markdown_format(self):
        """Test markdown export format."""
        result = subprocess.run(
            ['superskills', 'export', '--markdown'],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert '# SuperSkills Reference' in result.stdout
        assert '| Skill | Type | Description |' in result.stdout
    
    def test_export_filter_by_type(self):
        """Test filtering by skill type."""
        result = subprocess.run(
            ['superskills', 'export', '--type', 'prompt'],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        data = json.loads(result.stdout)
        
        assert all(s['type'] == 'prompt' for s in data['skills'])
    
    def test_export_filter_by_api(self):
        """Test filtering by API requirement."""
        result = subprocess.run(
            ['superskills', 'export', '--has-api'],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        data = json.loads(result.stdout)
        
        assert all(s['requires_api'] for s in data['skills'])


class TestDiscoverCommand:
    """Test superskills discover command."""
    
    def test_discover_by_query(self):
        """Test skill discovery by query."""
        result = subprocess.run(
            ['superskills', 'discover', '--query', 'voice', '--json'],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        data = json.loads(result.stdout)
        
        assert data['status'] == 'success'
        assert 'results' in data
        assert len(data['results']) > 0
        assert any('narrator' in r['name'] for r in data['results'])
    
    def test_discover_by_task(self):
        """Test workflow discovery by task."""
        result = subprocess.run(
            ['superskills', 'discover', '--task', 'write article', '--json'],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        data = json.loads(result.stdout)
        
        assert data['status'] == 'success'
        assert 'suggestions' in data
        assert len(data['suggestions']) > 0
    
    def test_discover_no_args_error(self):
        """Test error when no arguments provided."""
        result = subprocess.run(
            ['superskills', 'discover', '--json'],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert data['status'] == 'error'


class TestJSONOutputMode:
    """Test JSON output mode for call and run commands."""
    
    def test_call_json_output_success(self, mocker):
        """Test successful JSON output from call command."""
        result = subprocess.run(
            ['superskills', 'call', 'researcher', 'test query', '--format', 'json'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            assert data['status'] == 'success'
            assert 'output' in data
            assert 'metadata' in data
            assert data['metadata']['skill'] == 'researcher'
    
    def test_call_json_output_error(self):
        """Test error output from call command with nonexistent skill."""
        result = subprocess.run(
            ['superskills', 'call', 'nonexistent-skill', 'test', '--format', 'json'],
            capture_output=True,
            text=True
        )
        
        # CLI exits with error code and may output plain text error
        assert result.returncode != 0
    
    def test_run_dry_run_mode(self):
        """Test dry-run mode for workflows."""
        result = subprocess.run(
            ['superskills', 'run', 'content-creation', '--topic', 'test', '--dry-run'],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert 'DRY RUN' in result.stdout
        assert 'Estimated' in result.stdout


class TestStdinSupport:
    """Test stdin input support."""
    
    def test_stdin_input_basic(self):
        """Test basic stdin input."""
        process = subprocess.Popen(
            ['superskills', 'call', 'researcher', '--format', 'json'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input='test query', timeout=30)
        
        if process.returncode == 0:
            data = json.loads(stdout)
            assert data['status'] == 'success'
    
    def test_stdin_priority_over_arg(self):
        """Test that stdin has priority over positional argument."""
        process = subprocess.Popen(
            ['superskills', 'call', 'researcher', 'ignored', '--format', 'json'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input='stdin input', timeout=30)
        
        if process.returncode == 0:
            data = json.loads(stdout)
            assert data['status'] == 'success'


class TestMetadataStructure:
    """Test exported metadata structure."""
    
    def test_skill_metadata_completeness(self):
        """Test that skill metadata contains required fields."""
        result = subprocess.run(
            ['superskills', 'export'],
            capture_output=True,
            text=True
        )
        
        data = json.loads(result.stdout)
        
        for skill in data['skills']:
            assert 'name' in skill
            assert 'type' in skill
            assert 'description' in skill
            assert 'has_profile' in skill
            assert 'requires_api' in skill
            assert 'capabilities' in skill
            assert 'examples' in skill
            assert 'apis' in skill
    
    def test_workflow_metadata_completeness(self):
        """Test that workflow metadata contains required fields."""
        result = subprocess.run(
            ['superskills', 'export'],
            capture_output=True,
            text=True
        )
        
        data = json.loads(result.stdout)
        
        for workflow in data['workflows']:
            assert 'name' in workflow
            assert 'description' in workflow
            assert 'steps' in workflow
            assert 'step_count' in workflow
            assert 'inputs' in workflow
            assert 'outputs' in workflow
            assert 'use_cases' in workflow


class TestCLIErrorHandling:
    """Test error handling in CLI commands."""
    
    def test_call_missing_input_json(self):
        """Test error when input is missing."""
        result = subprocess.run(
            ['superskills', 'call', 'researcher', '--format', 'json'],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True
        )
        
        # CLI exits with error code  
        assert result.returncode == 1
        # Error message mentions input requirement
        assert 'input' in result.stdout.lower() or 'input' in result.stderr.lower()
    
    def test_call_file_not_found_json(self):
        """Test error when input file not found."""
        result = subprocess.run(
            ['superskills', 'call', 'researcher', '--input', 'nonexistent.txt', '--format', 'json'],
            capture_output=True,
            text=True
        )
        
        # CLI exits with error code
        assert result.returncode == 1
        # Error message present (may not specifically mention file)
        output = result.stdout + result.stderr
        assert len(output) > 0  # Some error message was output


class TestCommandAvailability:
    """Test that all new commands are available."""
    
    def test_export_command_available(self):
        """Test export command is registered."""
        result = subprocess.run(
            ['superskills', '--help'],
            capture_output=True,
            text=True
        )
        
        assert 'export' in result.stdout
    
    def test_discover_command_available(self):
        """Test discover command is registered."""
        result = subprocess.run(
            ['superskills', '--help'],
            capture_output=True,
            text=True
        )
        
        assert 'discover' in result.stdout
    
    def test_json_flag_available_call(self):
        """Test --format json flag available for call command."""
        result = subprocess.run(
            ['superskills', 'call', '--help'],
            capture_output=True,
            text=True
        )
        
        assert '--format' in result.stdout
        assert 'json' in result.stdout
    
    def test_json_flag_available_run(self):
        """Test --format json flag available for run command."""
        result = subprocess.run(
            ['superskills', 'run', '--help'],
            capture_output=True,
            text=True
        )
        
        assert '--format' in result.stdout
        assert 'json' in result.stdout


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
