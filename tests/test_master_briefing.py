"""
Unit tests for Master Briefing loader.
"""
import sys
import tempfile
from pathlib import Path

import yaml

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from cli.utils.master_briefing import MasterBriefingLoader


def test_load_master_briefing_missing():
    """Test graceful handling when Master Briefing file doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        loader = MasterBriefingLoader(config_dir=tmpdir)
        result = loader.load()

        assert result is None, "Should return None for missing file"
        print("✓ Gracefully handles missing Master Briefing")


def test_load_master_briefing_exists():
    """Test loading valid Master Briefing YAML."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test Master Briefing
        briefing_path = Path(tmpdir) / "master-briefing.yaml"
        test_data = {
            'identity': {
                'name': 'Test User',
                'role': 'Developer',
                'business': 'Tech Company'
            },
            'voice': {
                'style': 'Professional',
                'characteristics': ['Clear', 'Concise']
            }
        }

        with open(briefing_path, 'w') as f:
            yaml.dump(test_data, f)

        loader = MasterBriefingLoader(config_dir=tmpdir)
        result = loader.load()

        assert result is not None, "Should load valid YAML"
        assert result['identity']['name'] == 'Test User'
        assert result['voice']['style'] == 'Professional'
        print("✓ Loads valid Master Briefing YAML")


def test_load_master_briefing_invalid_yaml():
    """Test handling of malformed YAML."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create invalid YAML
        briefing_path = Path(tmpdir) / "master-briefing.yaml"
        with open(briefing_path, 'w') as f:
            f.write("invalid: yaml: content:\n  - broken\n  indentation")

        loader = MasterBriefingLoader(config_dir=tmpdir)
        result = loader.load()

        assert result is None, "Should return None for invalid YAML"
        print("✓ Handles invalid YAML gracefully")


def test_get_section():
    """Test extracting specific sections from Master Briefing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        briefing_path = Path(tmpdir) / "master-briefing.yaml"
        test_data = {
            'identity': {'name': 'Test User'},
            'voice': {'style': 'Professional'},
            'audience': {'primary': 'Developers'}
        }

        with open(briefing_path, 'w') as f:
            yaml.dump(test_data, f)

        loader = MasterBriefingLoader(config_dir=tmpdir)

        identity = loader.get_section('identity')
        assert identity == {'name': 'Test User'}

        voice = loader.get_section('voice')
        assert voice == {'style': 'Professional'}

        missing = loader.get_section('nonexistent')
        assert missing is None

        print("✓ Extracts sections correctly")


def test_format_for_prompt():
    """Test markdown formatting for system prompt."""
    with tempfile.TemporaryDirectory() as tmpdir:
        briefing_path = Path(tmpdir) / "master-briefing.yaml"
        test_data = {
            'identity': {
                'name': 'Test User',
                'role': 'Developer'
            },
            'voice': {
                'style': 'Professional',
                'characteristics': ['Clear', 'Concise']
            },
            'audience': {
                'primary': 'Engineers',
                'pain_points': ['Complexity', 'Time pressure']
            }
        }

        with open(briefing_path, 'w') as f:
            yaml.dump(test_data, f)

        loader = MasterBriefingLoader(config_dir=tmpdir)
        formatted = loader.format_for_prompt()

        assert '## Identity & Context' in formatted
        assert 'Test User' in formatted
        assert '## Voice & Tone' in formatted
        assert 'Professional' in formatted
        assert '## Audience' in formatted
        assert 'Engineers' in formatted
        assert 'Complexity' in formatted

        print("✓ Formats Master Briefing as markdown")


def test_format_for_prompt_empty():
    """Test formatting when no Master Briefing exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        loader = MasterBriefingLoader(config_dir=tmpdir)
        formatted = loader.format_for_prompt()

        assert formatted == "", "Should return empty string for missing file"
        print("✓ Returns empty string when Master Briefing missing")


def test_caching_behavior():
    """Test that Master Briefing is cached based on file modification time."""
    with tempfile.TemporaryDirectory() as tmpdir:
        briefing_path = Path(tmpdir) / "master-briefing.yaml"

        # Create initial file
        test_data_v1 = {'identity': {'name': 'Version 1'}}
        with open(briefing_path, 'w') as f:
            yaml.dump(test_data_v1, f)

        loader = MasterBriefingLoader(config_dir=tmpdir)

        # First load
        result1 = loader.load()
        assert result1['identity']['name'] == 'Version 1'

        # Second load should use cache (same content)
        result2 = loader.load()
        assert result2 is result1, "Should return cached object"

        # Modify file
        import time
        time.sleep(0.1)  # Ensure mtime changes
        test_data_v2 = {'identity': {'name': 'Version 2'}}
        with open(briefing_path, 'w') as f:
            yaml.dump(test_data_v2, f)

        # Third load should reload from disk
        result3 = loader.load()
        assert result3['identity']['name'] == 'Version 2'
        assert result3 is not result1, "Should reload when file changes"

        print("✓ Caches Master Briefing based on mtime")


def test_format_all_sections():
    """Test formatting with all Master Briefing sections populated."""
    with tempfile.TemporaryDirectory() as tmpdir:
        briefing_path = Path(tmpdir) / "master-briefing.yaml"

        # Create comprehensive test data
        test_data = {
            'identity': {
                'name': 'Coach Steff',
                'role': 'AI Implementation Coach',
                'business': 'Technology Consulting',
                'domain': 'AI Transformation',
                'experience': '15+ years'
            },
            'audience': {
                'primary': 'Mid-level managers',
                'secondary': 'Individual contributors',
                'pain_points': ['Overwhelmed by AI hype', 'Lack of practical guidance'],
                'desired_feeling': 'Empowered and confident'
            },
            'voice': {
                'style': 'Warm but professional',
                'characteristics': ['Clear', 'Practical'],
                'language_patterns': ['Use active voice', 'Short sentences'],
                'signature_elements': ['Real-world examples'],
                'avoid': ['Jargon', 'Hype']
            },
            'perspective': {
                'lens': 'Technology × Psychology',
                'goal': 'Empower adoption',
                'reader_positioning': 'Peer-to-peer',
                'guiding_principle': 'Make AI accessible'
            },
            'frameworks': [
                {
                    'name': 'Value-First Framework',
                    'description': 'Start with business value',
                    'when_to_use': 'Strategic planning',
                    'components': ['Identify pain', 'Measure impact']
                }
            ],
            'expertise': {
                'areas': ['AI Integration', 'Change Management'],
                'credentials': ['MBA', 'AI Certification'],
                'proof_points': ['50+ successful implementations'],
                'industries': ['Finance', 'Healthcare']
            },
            'examples': {
                'signature_stories': ['Case study: Bank transformation'],
                'sample_voice': 'AI is not magic, it is a tool.',
                'typical_hooks': ['What if you could...'],
                'before_after': [
                    {
                        'scenario': 'Email response',
                        'before': 'Complex jargon',
                        'after': 'Clear explanation'
                    }
                ]
            },
            'guardrails': {
                'privacy': ['Never share client names'],
                'ethics': ['Disclose AI use'],
                'compliance': ['Follow GDPR'],
                'human_judgment_required': ['Legal advice', 'Medical decisions']
            }
        }

        with open(briefing_path, 'w') as f:
            yaml.dump(test_data, f)

        loader = MasterBriefingLoader(config_dir=tmpdir)
        formatted = loader.format_for_prompt()

        # Verify all section headers present
        assert '## Identity & Context' in formatted
        assert '## Audience' in formatted
        assert '## Voice & Tone' in formatted
        assert '## Perspective & Positioning' in formatted
        assert '## Core Frameworks' in formatted
        assert '## Expertise' in formatted
        assert '## Examples & Voice Samples' in formatted
        assert '## Guardrails & Compliance' in formatted

        # Verify sample content from each section
        assert 'Coach Steff' in formatted
        assert 'Mid-level managers' in formatted
        assert 'Warm but professional' in formatted
        assert 'Technology × Psychology' in formatted
        assert 'Value-First Framework' in formatted
        assert 'AI Integration' in formatted
        assert 'AI is not magic' in formatted
        assert 'Never share client names' in formatted

        print("✓ Formats all Master Briefing sections correctly")


def main():
    print("="*60)
    print("Master Briefing Loader Tests")
    print("="*60 + "\n")

    try:
        test_load_master_briefing_missing()
        test_load_master_briefing_exists()
        test_load_master_briefing_invalid_yaml()
        test_get_section()
        test_format_for_prompt()
        test_format_for_prompt_empty()
        test_caching_behavior()
        test_format_all_sections()

        print("\n" + "="*60)
        print("✅ All Master Briefing tests passed!")
        print("="*60)
        return 0

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
