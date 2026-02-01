#!/usr/bin/env python3
"""
Test script for slide-designer using the SuperSkills CLI
"""
import json
import sys
from pathlib import Path

# Add src to path for direct import
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from SlideDesigner import SlideDesigner

def main():
    # Read input from stdin or arguments
    if len(sys.argv) > 1:
        input_data = sys.argv[1]
    else:
        input_data = sys.stdin.read()
    
    try:
        # Try to parse as JSON
        params = json.loads(input_data)
        mode = params.get('mode', 'script')
        output_dir = params.get('output_dir', 'output/slides')
        output_name = params.get('output_name', 'presentation')
        theme = params.get('theme', 'dark')
        
        designer = SlideDesigner(output_dir=output_dir, theme=theme)
        
        if mode == 'script':
            result = designer.design_from_script(
                script=params.get('script', ''),
                title=params.get('title'),
                max_slides=params.get('max_slides', 7),
                output_name=output_name
            )
        elif mode == 'outline':
            result = designer.design_from_outline(
                outline=params.get('outline', ''),
                output_name=output_name
            )
        elif mode == 'specs':
            result = designer.design_from_specs(
                slides=params.get('slides', []),
                output_name=output_name
            )
        else:
            print(json.dumps({'error': f'Unknown mode: {mode}'}))
            return 1
        
        # Format output
        output = {
            'slide_count': result.slide_count,
            'estimated_duration_seconds': result.estimated_duration_seconds,
            'html_files': [str(f) for f in result.html_files],
            'combined_html': str(result.combined_html),
            'theme': result.theme,
            'slides': [
                {
                    'type': slide.type,
                    'heading': slide.heading,
                    'subheading': slide.subheading,
                    'bullets': slide.bullets
                }
                for slide in result.slides
            ]
        }
        
        print(json.dumps(output, indent=2))
        return 0
        
    except json.JSONDecodeError:
        # Treat as plain script text
        designer = SlideDesigner(output_dir='output/slides', theme='dark')
        result = designer.design_from_script(
            script=input_data,
            title="Presentation",
            output_name='presentation'
        )
        
        output = {
            'slide_count': result.slide_count,
            'estimated_duration_seconds': result.estimated_duration_seconds,
            'html_files': [str(f) for f in result.html_files],
            'combined_html': str(result.combined_html),
            'theme': result.theme
        }
        
        print(json.dumps(output, indent=2))
        return 0

if __name__ == '__main__':
    sys.exit(main())
