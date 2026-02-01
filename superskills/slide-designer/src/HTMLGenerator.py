from pathlib import Path
from typing import List, Tuple, Optional
from jinja2 import Environment, FileSystemLoader

try:
    from .StyleEngine import BrandConfig
except ImportError:
    from StyleEngine import BrandConfig


def render_slide(
    slide: 'SlideSpec',
    template_name: str,
    brand: BrandConfig,
    theme: str,
    logo_path: Optional[str] = None
) -> str:
    template_dir = Path(__file__).parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    
    template = env.get_template(f"{template_name}.html.j2")
    
    theme_colors = brand.themes.get(theme, brand.themes['dark'])
    
    context = {
        'slide': slide,
        'brand': brand,
        'theme_colors': theme_colors,
        'logo_path': logo_path,
        'title': slide.heading if hasattr(slide, 'heading') else 'Slide'
    }
    
    return template.render(**context)


def render_deck(
    slides: List['SlideSpec'],
    brand: BrandConfig,
    theme: str,
    output_dir: Path,
    output_name: str
) -> Tuple[List[Path], Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logo_path_abs = Path(__file__).parent.parent / "brand" / brand.identity['logo']['file']
    logo_path_rel = f"../brand/{brand.identity['logo']['file']}"
    
    individual_files = []
    
    layout_map = {
        'title': 'title',
        'content': 'content',
        'question': 'question',
        'image': 'image',
        'quote': 'quote'
    }
    
    for idx, slide in enumerate(slides, start=1):
        template_name = layout_map.get(slide.type, 'content')
        
        html_content = render_slide(
            slide=slide,
            template_name=template_name,
            brand=brand,
            theme=theme,
            logo_path=str(logo_path_abs) if logo_path_abs.exists() else None
        )
        
        output_file = output_dir / f"{output_name}_{idx:03d}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        individual_files.append(output_file)
    
    combined_parts = []
    for idx, slide in enumerate(slides, start=1):
        template_name = layout_map.get(slide.type, 'content')
        html_content = render_slide(
            slide=slide,
            template_name=template_name,
            brand=brand,
            theme=theme,
            logo_path=str(logo_path_abs) if logo_path_abs.exists() else None
        )
        
        if idx > 1:
            combined_parts.append('<div style="page-break-after: always;"></div>')
        combined_parts.append(html_content)
    
    combined_file = output_dir / f"{output_name}_deck.html"
    with open(combined_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(combined_parts))
    
    return individual_files, combined_file
