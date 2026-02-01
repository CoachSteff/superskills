import sys
from pathlib import Path

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from ContentAnalyzer import (
    analyze_script,
    analyze_markdown,
    extract_bullets,
    detect_content_type
)


def test_analyze_script():
    script = "Welcome to AI automation. Today we learn three key concepts: prompt engineering, personalization, and your second brain."
    
    chunks = analyze_script(script, target_slides=5)
    
    assert len(chunks) >= 1
    assert len(chunks) <= 7
    assert chunks[0].suggested_type == "title"
    
    print(f"✓ Script analysis: {len(chunks)} chunks created")
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i+1}: {chunk.suggested_type} - {chunk.heading}")


def test_analyze_markdown():
    markdown = """
# Welcome
## AI Automation Workshop

# Topics
- Prompt engineering
- Personalization
- Second brain

# Conclusion
Thank you for attending
"""
    
    chunks = analyze_markdown(markdown)
    
    assert len(chunks) >= 1
    assert len(chunks) <= 7
    
    print(f"✓ Markdown analysis: {len(chunks)} chunks created")
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i+1}: {chunk.heading} - {len(chunk.key_points)} bullets")


def test_extract_bullets():
    text = "We will learn about prompt engineering, how to personalize AI tools, and building your second brain system."
    
    bullets = extract_bullets(text, max_bullets=5)
    
    assert len(bullets) > 0
    assert len(bullets) <= 5
    
    for bullet in bullets:
        words = bullet.split()
        assert len(words) <= 12
    
    print(f"✓ Bullet extraction: {len(bullets)} bullets")
    for bullet in bullets:
        print(f"  - {bullet}")


def test_detect_content_type():
    assert detect_content_type("What do you think?") == "question"
    assert detect_content_type("Short title") == "title"
    
    longer_content = "This is a longer piece of content with more than eight words in it"
    assert detect_content_type(longer_content) == "content"
    
    multiline_bullets = """- Point one here
- Point two here
- Point three here
- Point four here"""
    assert detect_content_type(multiline_bullets) == "content"
    
    print("✓ Content type detection works")


if __name__ == "__main__":
    print("Testing ContentAnalyzer...\n")
    test_analyze_script()
    print()
    test_analyze_markdown()
    print()
    test_extract_bullets()
    print()
    test_detect_content_type()
    print("\n✅ All ContentAnalyzer tests passed!")
