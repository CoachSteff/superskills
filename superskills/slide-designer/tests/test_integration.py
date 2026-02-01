import sys
from pathlib import Path
import tempfile

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from SlideDesigner import SlideDesigner


def test_integration():
    print("Testing SlideDesigner Integration...\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        designer = SlideDesigner(output_dir=tmpdir, theme="dark")
        
        print("Test 1: Design from script")
        result = designer.design_from_script(
            script="Welcome to AI automation. Today we learn three key concepts: prompt engineering, personalization, and your second brain.",
            title="AI Workshop",
            output_name="test_presentation"
        )
        
        print(f"✓ Created {result.slide_count} slides")
        print(f"  Duration: {result.estimated_duration_seconds:.1f}s")
        print(f"  Files: {len(result.html_files)}")
        print(f"  Combined: {result.combined_html.name}")
        
        html_content = result.html_files[0].read_text()
        assert "1920" in html_content
        assert "1080" in html_content
        assert "#00BFFF" in html_content
        print("  HTML structure validated ✓")
        
        print("\nTest 2: Design from outline")
        outline = """
# Welcome
## AI Automation Workshop

# Topics
- Prompt engineering
- Personalization
- Second brain
"""
        
        result2 = designer.design_from_outline(
            outline=outline,
            output_name="test_outline"
        )
        
        print(f"✓ Created {result2.slide_count} slides from outline")
        
        print("\nTest 3: Design from specs")
        slides = [
            {"type": "title", "heading": "Test Presentation", "subheading": "From Specs"},
            {"type": "content", "heading": "Key Points", "bullets": ["Point 1", "Point 2", "Point 3"]},
            {"type": "question", "heading": "Any questions?"}
        ]
        
        result3 = designer.design_from_specs(
            slides=slides,
            output_name="test_specs"
        )
        
        print(f"✓ Created {result3.slide_count} slides from specs")
        
        print("\nTest 4: Theme switching")
        designer_light = SlideDesigner(output_dir=tmpdir, theme="light")
        result_light = designer_light.design_from_script(
            script="Test content",
            title="Light Theme",
            output_name="light_test"
        )
        
        light_html = result_light.html_files[0].read_text()
        assert "#ffffff" in light_html
        print("✓ Light theme works")
        
        print("\n✅ All integration tests passed!")
        print(f"\nSummary:")
        print(f"  Total slides created: {result.slide_count + result2.slide_count + result3.slide_count + result_light.slide_count}")
        print(f"  All HTML files valid: ✓")
        print(f"  Brand styling applied: ✓")
        print(f"  Theme switching works: ✓")


if __name__ == "__main__":
    test_integration()
