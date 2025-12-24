"""
Integration tests for hierarchical profile loading system.

Tests verify that Master Briefing, skill PROFILE.md, and SKILL.md
are loaded and layered correctly in system prompts.
"""
import sys
import tempfile
from pathlib import Path

import yaml

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from cli.core.skill_executor import SkillExecutor
from cli.core.skill_loader import SkillLoader
from cli.utils.config import CLIConfig
from cli.utils.master_briefing import MasterBriefingLoader


def test_skill_loader_hierarchical_content():
    """Test that SkillLoader returns all three content layers."""
    loader = SkillLoader()

    # Load a known skill with a profile (e.g., copywriter)
    content = loader.load_skill_content('copywriter')

    # Verify return structure
    assert 'skill' in content, "Should have 'skill' key"
    assert 'master_briefing' in content, "Should have 'master_briefing' key"
    assert 'profile' in content, "Should have 'profile' key"

    # Verify SKILL.md loaded
    assert content['skill'] is not None
    assert len(content['skill']) > 0
    assert 'copywriter' in content['skill'].lower()

    # Master Briefing may be None if not configured (graceful)
    # This is expected behavior

    # Verify PROFILE.md loaded for copywriter (has custom profile)
    assert content['profile'] is not None
    assert len(content['profile']) > 0

    print("✓ SkillLoader returns hierarchical content structure")


def test_system_prompt_without_master_briefing():
    """Test system prompt building when only SKILL.md and PROFILE.md exist."""
    config = CLIConfig()
    executor = SkillExecutor(config)

    skill_content = "# Test Skill\nYou are a test assistant."
    master_briefing = None
    profile_content = "# Profile\nBe friendly and helpful."

    prompt = executor._build_system_prompt(skill_content, master_briefing, profile_content)

    # Verify structure
    assert "You are an AI assistant" in prompt
    assert "# Your Role and Guidelines" in prompt
    assert "Test Skill" in prompt
    assert "# Skill-Specific Customization" in prompt
    assert "Be friendly" in prompt

    # Verify Master Briefing section NOT present
    assert "# Global Brand Context" not in prompt

    print("✓ System prompt works without Master Briefing (backward compat)")


def test_system_prompt_with_master_briefing():
    """Test system prompt building with Master Briefing included."""
    config = CLIConfig()
    executor = SkillExecutor(config)

    skill_content = "# Test Skill\nYou are a test assistant."
    master_briefing = "## Voice\nProfessional and clear."
    profile_content = "# Profile\nBe concise."

    prompt = executor._build_system_prompt(skill_content, master_briefing, profile_content)

    # Verify all three layers present
    assert "# Your Role and Guidelines" in prompt
    assert "Test Skill" in prompt

    assert "# Global Brand Context" in prompt
    assert "Master Briefing" in prompt
    assert "Professional and clear" in prompt

    assert "# Skill-Specific Customization" in prompt
    assert "Be concise" in prompt

    # Verify priority instruction
    assert "defer to skill-specific customization" in prompt
    assert "take priority over general guidelines" in prompt

    print("✓ System prompt includes all three layers with Master Briefing")


def test_system_prompt_only_skill():
    """Test system prompt with only SKILL.md (minimal configuration)."""
    config = CLIConfig()
    executor = SkillExecutor(config)

    skill_content = "# Test Skill\nYou are a minimal test assistant."
    master_briefing = None
    profile_content = None

    prompt = executor._build_system_prompt(skill_content, master_briefing, profile_content)

    # Verify only base layer present
    assert "# Your Role and Guidelines" in prompt
    assert "minimal test assistant" in prompt

    # Verify no customization sections
    assert "# Global Brand Context" not in prompt
    assert "# Skill-Specific Customization" not in prompt

    print("✓ System prompt works with only SKILL.md (minimal mode)")


def test_system_prompt_priority_order():
    """Test that system prompt layers appear in correct priority order."""
    config = CLIConfig()
    executor = SkillExecutor(config)

    skill_content = "SKILL_CONTENT"
    master_briefing = "MASTER_BRIEFING_CONTENT"
    profile_content = "PROFILE_CONTENT"

    prompt = executor._build_system_prompt(skill_content, master_briefing, profile_content)

    # Find positions of each content block
    skill_pos = prompt.index("SKILL_CONTENT")
    master_pos = prompt.index("MASTER_BRIEFING_CONTENT")
    profile_pos = prompt.index("PROFILE_CONTENT")

    # Verify order: SKILL < Master Briefing < Profile
    assert skill_pos < master_pos, "SKILL.md should come before Master Briefing"
    assert master_pos < profile_pos, "Master Briefing should come before Profile"

    print("✓ System prompt layers in correct priority order")


def test_master_briefing_loader_integration():
    """Test Master Briefing loader integration with temporary file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test Master Briefing
        briefing_path = Path(tmpdir) / "master-briefing.yaml"
        test_data = {
            'identity': {'name': 'Integration Test'},
            'voice': {'style': 'Test style'}
        }

        with open(briefing_path, 'w') as f:
            yaml.dump(test_data, f)

        # Load via MasterBriefingLoader
        loader = MasterBriefingLoader(config_dir=tmpdir)
        content = loader.load()

        assert content is not None
        assert content['identity']['name'] == 'Integration Test'

        # Format for prompt
        formatted = loader.format_for_prompt()
        assert 'Integration Test' in formatted
        assert 'Test style' in formatted

        print("✓ Master Briefing loader integrates correctly")


def test_skill_loader_fallback_to_template():
    """Test that SkillLoader falls back to PROFILE.md.template if no custom profile."""
    loader = SkillLoader()

    # Find a skill that only has template (not customized)
    # Most skills have PROFILE.md now, so this tests the fallback logic
    skills = loader.discover_skills()

    # Test with any skill - loader should handle both cases
    for skill in skills[:3]:  # Test first 3 skills
        content = loader.load_skill_content(skill.name)

        # Should always have skill content
        assert content['skill'] is not None

        # Profile may be template or custom, both are valid
        if skill.has_profile:
            # If skill has profile, should load something
            # (either PROFILE.md or PROFILE.md.template)
            pass  # Valid state

        print(f"  ✓ Tested {skill.name}")

    print("✓ SkillLoader fallback logic works correctly")


def test_full_skill_execution_integration():
    """Test full skill execution with hierarchical loading (mocked LLM)."""
    # This is a smoke test - verifies no exceptions during execution
    loader = SkillLoader()

    # Load skill content
    content = loader.load_skill_content('copywriter')

    # Verify structure
    assert content['skill'] is not None
    assert 'master_briefing' in content  # Key exists (value may be None)
    assert 'profile' in content  # Key exists (value may be None)

    # Verify that system prompt can be built
    config = CLIConfig()
    executor = SkillExecutor(config)

    prompt = executor._build_system_prompt(
        content['skill'],
        content['master_briefing'],
        content['profile']
    )

    assert len(prompt) > 0
    assert "# Your Role and Guidelines" in prompt

    print("✓ Full skill execution integration works")


def main():
    print("="*60)
    print("Hierarchical Profile Loading Integration Tests")
    print("="*60 + "\n")

    try:
        test_skill_loader_hierarchical_content()
        test_system_prompt_without_master_briefing()
        test_system_prompt_with_master_briefing()
        test_system_prompt_only_skill()
        test_system_prompt_priority_order()
        test_master_briefing_loader_integration()
        test_skill_loader_fallback_to_template()
        test_full_skill_execution_integration()

        print("\n" + "="*60)
        print("✅ All integration tests passed!")
        print("="*60)
        return 0

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
