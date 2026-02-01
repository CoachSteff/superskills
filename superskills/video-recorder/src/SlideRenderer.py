"""SlideRenderer - HTML to PNG rendering for video-recorder skill."""

from pathlib import Path
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright
import yaml
from jinja2 import Environment, FileSystemLoader


class SlideRenderer:
    """Render HTML slides to PNG frames using headless browser."""
    
    def __init__(
        self,
        brand_config_path: Optional[Path] = None,
        resolution: tuple = (1920, 1080),
        output_dir: str = "output/frames"
    ):
        """
        Initialize slide renderer.
        
        Args:
            brand_config_path: Path to brand.yaml (default: skill's brand/default.yaml)
            resolution: Output resolution (width, height)
            output_dir: Where to save PNG frames
        """
        self.width, self.height = resolution
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load brand configuration
        if brand_config_path is None:
            brand_config_path = Path(__file__).parent.parent / "brand" / "default.yaml"
        
        with open(brand_config_path, 'r') as f:
            self.brand = yaml.safe_load(f)
        
        # Resolve logo file path
        self._resolve_logo_path(brand_config_path)
        
        # Setup Jinja2 for templates
        template_dir = Path(__file__).parent.parent / "templates"
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))
    
    def _resolve_logo_path(self, brand_config_path: Path) -> None:
        """
        Resolve logo file path and validate existence.
        
        Supports:
        - Relative paths (from brand/ directory)
        - Absolute paths
        - Null/missing file (falls back to text)
        
        Args:
            brand_config_path: Path to brand.yaml (for relative resolution)
        """
        logo_config = self.brand.get('logo', {})
        logo_file = logo_config.get('file')
        
        if not logo_file:
            # No file specified, will use text fallback
            self.brand['logo']['resolved_path'] = None
            return
        
        # Try as absolute path first
        logo_path = Path(logo_file)
        if logo_path.is_absolute():
            if logo_path.exists():
                self.brand['logo']['resolved_path'] = str(logo_path.absolute())
                return
            else:
                print(f"  ⚠ Logo file not found: {logo_path}")
                self.brand['logo']['resolved_path'] = None
                return
        
        # Try as relative path (from brand/ directory)
        brand_dir = brand_config_path.parent
        relative_path = brand_dir / logo_file
        
        if relative_path.exists():
            self.brand['logo']['resolved_path'] = str(relative_path.absolute())
            print(f"  ✓ Logo loaded: {relative_path.name}")
        else:
            print(f"  ⚠ Logo file not found: {relative_path}")
            print(f"    Falling back to text logo: '{logo_config.get('text', '')}'")
            self.brand['logo']['resolved_path'] = None
    
    def render_slide(
        self,
        slide_data: Dict,
        output_path: Path,
        slide_index: int = 0
    ) -> Path:
        """
        Render a single slide to PNG.
        
        Args:
            slide_data: Slide definition (type, heading, bullets, etc.)
            output_path: Where to save PNG
            slide_index: Slide number (for temp file naming)
        
        Returns:
            Path to rendered PNG
        """
        # Select template based on slide type
        slide_type = slide_data.get('type', 'content')
        template = self.jinja_env.get_template(f"slide_{slide_type}.html.j2")
        
        # Render HTML with brand configuration
        html_content = template.render(
            brand=self.brand,
            slide=slide_data,
            title=slide_data.get('heading', 'Slide')
        )
        
        # Save temporary HTML
        temp_html = self.output_dir / f"temp_slide_{slide_index}.html"
        temp_html.write_text(html_content, encoding='utf-8')
        
        # Render to PNG using Playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                viewport={'width': self.width, 'height': self.height}
            )
            page.goto(f'file://{temp_html.absolute()}')
            
            # Wait for fonts to load
            page.wait_for_load_state('networkidle')
            
            page.screenshot(path=str(output_path), full_page=False)
            browser.close()
        
        # Cleanup temp HTML
        temp_html.unlink()
        
        return output_path
    
    def render_slides(self, slides: List[Dict]) -> List[Path]:
        """
        Render all slides to PNG frames.
        
        Args:
            slides: List of slide definitions
        
        Returns:
            List of paths to rendered PNG files
        """
        frames = []
        
        for i, slide_data in enumerate(slides):
            frame_path = self.output_dir / f"slide_{i:03d}.png"
            self.render_slide(slide_data, frame_path, i)
            frames.append(frame_path)
            print(f"  ✓ Rendered slide {i+1}/{len(slides)}: {slide_data.get('heading', 'Untitled')}")
        
        return frames
