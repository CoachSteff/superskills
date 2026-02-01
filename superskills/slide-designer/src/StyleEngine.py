from dataclasses import dataclass
from typing import Optional, Dict, Any
from pathlib import Path
import yaml


@dataclass
class BrandConfig:
    identity: Dict[str, Any]
    colors: Dict[str, str]
    typography: Dict[str, Any]
    spacing: Dict[str, str]
    slides: Dict[str, Any]
    themes: Dict[str, Dict[str, str]]


def load_brand(config_path: Optional[str] = None) -> BrandConfig:
    if config_path is None:
        config_path = Path(__file__).parent.parent / "brand" / "default.yaml"
    else:
        config_path = Path(config_path)
    
    with open(config_path, 'r') as f:
        data = yaml.safe_load(f)
    
    return BrandConfig(
        identity=data['identity'],
        colors=data['colors'],
        typography=data['typography'],
        spacing=data['spacing'],
        slides=data['slides'],
        themes=data['themes']
    )


def generate_css_variables(brand: BrandConfig, theme: str) -> str:
    theme_colors = brand.themes.get(theme, brand.themes['dark'])
    
    css_vars = [
        ":root {",
        f"  --color-primary: {brand.colors['primary']};",
        f"  --color-background: {theme_colors['background']};",
        f"  --color-text: {theme_colors['text']};",
        f"  --color-text-secondary: {brand.colors['text_secondary']};",
        f"  --font-heading: {brand.typography['heading']['family']};",
        f"  --font-body: {brand.typography['body']['family']};",
        f"  --size-title-heading: {brand.typography['sizes']['title_heading']};",
        f"  --size-content-heading: {brand.typography['sizes']['content_heading']};",
        f"  --size-body: {brand.typography['sizes']['body']};",
        f"  --size-caption: {brand.typography['sizes']['caption']};",
        f"  --padding: {brand.spacing['padding']};",
        "}"
    ]
    
    return "\n".join(css_vars)


def validate_contrast(foreground: str, background: str) -> bool:
    def hex_to_rgb(hex_color: str) -> tuple:
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def relative_luminance(rgb: tuple) -> float:
        r, g, b = [x / 255.0 for x in rgb]
        r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
        g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
        b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    fg_rgb = hex_to_rgb(foreground)
    bg_rgb = hex_to_rgb(background)
    
    l1 = relative_luminance(fg_rgb)
    l2 = relative_luminance(bg_rgb)
    
    lighter = max(l1, l2)
    darker = min(l1, l2)
    contrast_ratio = (lighter + 0.05) / (darker + 0.05)
    
    return contrast_ratio >= 4.5
