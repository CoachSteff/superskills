from dataclasses import dataclass
from typing import List, Optional, Literal
from pathlib import Path

try:
    from .StyleEngine import load_brand, BrandConfig
    from .HTMLGenerator import render_deck
    from .ContentAnalyzer import analyze_script, analyze_markdown, SlideChunk
    from .LayoutSelector import select_layout, enforce_variety
except ImportError:
    from StyleEngine import load_brand, BrandConfig
    from HTMLGenerator import render_deck
    from ContentAnalyzer import analyze_script, analyze_markdown, SlideChunk
    from LayoutSelector import select_layout, enforce_variety


@dataclass
class SlideSpec:
    type: Literal["title", "content", "image", "quote", "question"]
    heading: str
    subheading: Optional[str] = None
    bullets: Optional[List[str]] = None
    image_url: Optional[str] = None
    caption: Optional[str] = None
    quote_text: Optional[str] = None
    quote_author: Optional[str] = None
    text: Optional[str] = None


@dataclass
class DesignResult:
    slides: List[SlideSpec]
    html_files: List[Path]
    combined_html: Optional[Path]
    slide_count: int
    estimated_duration_seconds: float
    theme: str


class SlideDesigner:
    def __init__(
        self,
        output_dir: str = "output/slides",
        theme: str = "dark",
        brand_config: Optional[str] = None
    ):
        self.output_dir = Path(output_dir)
        self.theme = theme
        self.brand = load_brand(brand_config)
    
    def design_from_script(
        self,
        script: str,
        title: Optional[str] = None,
        max_slides: int = 7,
        output_name: str = "presentation"
    ) -> DesignResult:
        chunks = analyze_script(script, target_slides=max_slides)
        
        if title and chunks:
            chunks[0].heading = title
            chunks[0].suggested_type = "title"
        
        slides = self._chunks_to_slides(chunks)
        
        html_files, combined_html = render_deck(
            slides=slides,
            brand=self.brand,
            theme=self.theme,
            output_dir=self.output_dir,
            output_name=output_name
        )
        
        estimated_duration = self._estimate_duration(slides)
        
        return DesignResult(
            slides=slides,
            html_files=html_files,
            combined_html=combined_html,
            slide_count=len(slides),
            estimated_duration_seconds=estimated_duration,
            theme=self.theme
        )
    
    def design_from_outline(
        self,
        outline: str,
        output_name: str = "presentation"
    ) -> DesignResult:
        chunks = analyze_markdown(outline)
        
        slides = self._chunks_to_slides(chunks)
        
        html_files, combined_html = render_deck(
            slides=slides,
            brand=self.brand,
            theme=self.theme,
            output_dir=self.output_dir,
            output_name=output_name
        )
        
        estimated_duration = self._estimate_duration(slides)
        
        return DesignResult(
            slides=slides,
            html_files=html_files,
            combined_html=combined_html,
            slide_count=len(slides),
            estimated_duration_seconds=estimated_duration,
            theme=self.theme
        )
    
    def design_from_specs(
        self,
        slides: List[dict],
        output_name: str = "presentation"
    ) -> DesignResult:
        slide_specs = []
        for slide_dict in slides:
            slide_specs.append(SlideSpec(**slide_dict))
        
        html_files, combined_html = render_deck(
            slides=slide_specs,
            brand=self.brand,
            theme=self.theme,
            output_dir=self.output_dir,
            output_name=output_name
        )
        
        estimated_duration = self._estimate_duration(slide_specs)
        
        return DesignResult(
            slides=slide_specs,
            html_files=html_files,
            combined_html=combined_html,
            slide_count=len(slide_specs),
            estimated_duration_seconds=estimated_duration,
            theme=self.theme
        )
    
    def _chunks_to_slides(self, chunks: List[SlideChunk]) -> List[SlideSpec]:
        slides = []
        previous_layouts = []
        
        for idx, chunk in enumerate(chunks):
            if idx == 0:
                position = "first"
            elif idx == len(chunks) - 1:
                position = "last"
            else:
                position = "middle"
            
            layout = select_layout(chunk, previous_layouts, position)
            previous_layouts.append(layout)
            
            if layout == "title":
                slide = SlideSpec(
                    type="title",
                    heading=chunk.heading or "Welcome",
                    subheading=chunk.key_points[0] if chunk.key_points else None
                )
            
            elif layout == "question":
                slide = SlideSpec(
                    type="question",
                    heading=chunk.heading or chunk.content,
                    bullets=chunk.key_points[:3] if len(chunk.key_points) > 1 else None
                )
            
            elif layout == "quote":
                slide = SlideSpec(
                    type="quote",
                    heading=None,
                    quote_text=chunk.content,
                    quote_author=None
                )
            
            elif layout == "image":
                slide = SlideSpec(
                    type="image",
                    heading=chunk.heading,
                    image_url="",
                    caption=chunk.key_points[0] if chunk.key_points else None
                )
            
            else:
                slide = SlideSpec(
                    type="content",
                    heading=chunk.heading or "Key Points",
                    bullets=chunk.key_points[:5] if chunk.key_points else None,
                    text=None
                )
            
            slides.append(slide)
        
        layout_types = [s.type for s in slides]
        adjusted_layouts = enforce_variety(layout_types)
        
        for i, adjusted_type in enumerate(adjusted_layouts):
            if adjusted_type != slides[i].type and adjusted_type in ["content", "question"]:
                old_slide = slides[i]
                if adjusted_type == "question":
                    slides[i] = SlideSpec(
                        type="question",
                        heading=old_slide.heading + "?",
                        bullets=old_slide.bullets[:3] if old_slide.bullets else None
                    )
                else:
                    slides[i] = SlideSpec(
                        type="content",
                        heading=old_slide.heading,
                        bullets=old_slide.bullets if old_slide.bullets else None
                    )
        
        return slides
    
    def _estimate_duration(self, slides: List[SlideSpec]) -> float:
        total_seconds = 0.0
        
        for slide in slides:
            if slide.type == "title":
                total_seconds += 5.0
            elif slide.type == "question":
                total_seconds += 8.0
            elif slide.type == "quote":
                total_seconds += 10.0
            elif slide.type == "image":
                total_seconds += 12.0
            else:
                bullet_count = len(slide.bullets) if slide.bullets else 0
                total_seconds += 10.0 + (bullet_count * 2.0)
        
        return total_seconds
