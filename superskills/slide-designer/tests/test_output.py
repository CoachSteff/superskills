import sys
from pathlib import Path
import tempfile
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from superskills.slide_designer import SlideDesigner


def test_design_from_script():
    with tempfile.TemporaryDirectory() as tmpdir:
        designer = SlideDesigner(output_dir=tmpdir, theme="dark")
        
        result = designer.design_from_script(
            script="Welcome to AI automation. Today we learn three key concepts: prompt engineering, personalization, and your second brain.",
            title="AI Workshop",
            output_name="test_presentation"
        )
        
        assert result.slide_count >= 1
        assert result.slide_count <= 7
        assert len(result.html_files) == result.slide_count
        assert result.combined_html is not None
        assert result.combined_html.exists()
        
        for html_file in result.html_files:
            assert html_file.exists()
            content = html_file.read_text()
            assert "1920" in content
            assert "1080" in content
        
        print(f"✓ Script design: {result.slide_count} slides created")
        print(f"  Estimated duration: {result.estimated_duration_seconds}s")
        print(f"  Combined deck: {result.combined_html.name}")


def test_design_from_outline():
    with tempfile.TemporaryDirectory() as tmpdir:
        designer = SlideDesigner(output_dir=tmpdir, theme="dark")
        
        outline = """
# Welcome
## AI Automation Workshop

# Topics
- Prompt engineering
- Personalization
- Second brain
"""
        
        result = designer.design_from_outline(
            outline=outline,
            output_name="test_outline"
        )
        
        assert result.slide_count >= 1
        assert len(result.html_files) == result.slide_count
        
        print(f"✓ Outline design: {result.slide_count} slides created")


def test_design_from_specs():
    with tempfile.TemporaryDirectory() as tmpdir:
        designer = SlideDesigner(output_dir=tmpdir, theme="dark")
        
        slides = [
            {"type": "title", "heading": "Test Presentation", "subheading": "From Specs"},
            {"type": "content", "heading": "Key Points", "bullets": ["Point 1", "Point 2", "Point 3"]},
            {"type": "question", "heading": "Any questions?"}
        ]
        
        result = designer.design_from_specs(
            slides=slides,
            output_name="test_specs"
        )
        
        assert result.slide_count == 3
        assert len(result.html_files) == 3
        
        print(f"✓ Specs design: {result.slide_count} slides created")


def test_html_structure():
    with tempfile.TemporaryDirectory() as tmpdir:
        designer = SlideDesigner(output_dir=tmpdir, theme="dark")
        
        result = designer.design_from_script(
            script="Test slide",
            title="Test",
            output_name="structure_test"
        )
        
        html_content = result.html_files[0].read_text()
        
        assert "<!DOCTYPE html>" in html_content
        assert "width: 1920px" in html_content
        assert "height: 1080px" in html_content
        assert "#00BFFF" in html_content
        assert "CoachSteff" in html_content or "logo" in html_content.lower()
        
        print("✓ HTML structure validation passed")


def test_theme_switching():
    with tempfile.TemporaryDirectory() as tmpdir:
        designer_dark = SlideDesigner(output_dir=tmpdir, theme="dark")
        result_dark = designer_dark.design_from_script(
            script="Test",
            title="Dark Theme Test",
            output_name="dark_test"
        )
        
        designer_light = SlideDesigner(output_dir=tmpdir, theme="light")
        result_light = designer_light.design_from_script(
            script="Test",
            title="Light Theme Test",
            output_name="light_test"
        )
        
        dark_html = result_dark.html_files[0].read_text()
        light_html = result_light.html_files[0].read_text()
        
        assert "#1f2937" in dark_html
        assert "#ffffff" in light_html
        
        print("✓ Theme switching works")


if __name__ == "__main__":
    print("Testing HTML Output...\n")
    test_design_from_script()
    print()
    test_design_from_outline()
    print()
    test_design_from_specs()
    print()
    test_html_structure()
    print()
    test_theme_switching()
    print("\n✅ All output tests passed!")
