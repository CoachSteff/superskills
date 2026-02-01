#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from superskills.slide_designer import SlideDesigner

def main():
    print("=== Slide Designer Demo ===\n")
    
    designer = SlideDesigner(output_dir="demo_output", theme="dark")
    
    script = """
    Welcome to the AI Automation Workshop. Today we will explore how artificial intelligence
    can transform your daily work. We'll cover three essential topics: prompt engineering,
    which helps you communicate effectively with AI tools; personalization techniques to
    customize AI for your needs; and building your second brain system for knowledge management.
    By the end of this session, you'll have practical skills to become a superworker.
    """
    
    print("Creating slides from script...")
    result = designer.design_from_script(
        script=script,
        title="AI Automation Workshop",
        output_name="workshop"
    )
    
    print(f"\n✅ Success! Created {result.slide_count} slides")
    print(f"   Estimated duration: {result.estimated_duration_seconds:.1f} seconds")
    print(f"   Output directory: demo_output/")
    print(f"\nSlides created:")
    
    for i, (slide_file, slide_spec) in enumerate(zip(result.html_files, result.slides), 1):
        print(f"  {i}. {slide_file.name} - {slide_spec.type.upper()}: {slide_spec.heading}")
    
    print(f"\n   Combined deck: {result.combined_html.name}")
    print(f"\nYou can open these HTML files in your browser to view the slides.")
    print(f"Each slide is 1920x1080 and ready for video recording.\n")

if __name__ == "__main__":
    main()
