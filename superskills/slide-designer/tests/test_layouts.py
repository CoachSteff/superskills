import sys
from pathlib import Path

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from LayoutSelector import (
    select_layout,
    detect_framework,
    enforce_variety
)
from ContentAnalyzer import SlideChunk


def test_select_layout():
    chunk = SlideChunk(
        content="Welcome to the presentation",
        suggested_type="title",
        key_points=[],
        heading="Welcome"
    )
    
    layout = select_layout(chunk, [], "first")
    assert layout == "title"
    
    layout = select_layout(chunk, ["title"], "middle")
    assert layout in ["title", "content", "question"]
    
    print("✓ Layout selection works")


def test_detect_framework():
    text_craft = "We use the CRAFT framework for content creation"
    text_code = "The CODE methodology helps organize"
    text_none = "This is just regular text"
    
    assert detect_framework(text_craft) == "CRAFT"
    assert detect_framework(text_code) == "CODE"
    assert detect_framework(text_none) is None
    
    print("✓ Framework detection works")


def test_enforce_variety():
    layouts = ["title", "content", "content", "content", "question"]
    
    adjusted = enforce_variety(layouts)
    
    consecutive_count = 0
    for i in range(2, len(adjusted)):
        if adjusted[i] == adjusted[i-1] == adjusted[i-2]:
            consecutive_count += 1
    
    assert consecutive_count == 0
    
    print("✓ Variety enforcement works")
    print(f"  Original: {layouts}")
    print(f"  Adjusted: {adjusted}")


def test_no_consecutive_questions():
    layouts = ["title", "question", "question", "content"]
    
    adjusted = enforce_variety(layouts)
    
    for i in range(1, len(adjusted)):
        if adjusted[i] == "question" and adjusted[i-1] == "question":
            assert False, "Found consecutive questions"
    
    print("✓ No consecutive questions")


if __name__ == "__main__":
    print("Testing LayoutSelector...\n")
    test_select_layout()
    print()
    test_detect_framework()
    print()
    test_enforce_variety()
    print()
    test_no_consecutive_questions()
    print("\n✅ All LayoutSelector tests passed!")
