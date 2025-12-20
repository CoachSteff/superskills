"""Image Generator - AI-powered visual content creation."""

import os
from pathlib import Path
from typing import Optional, Literal
from dataclasses import dataclass
import requests
from PIL import Image
from io import BytesIO
from datetime import datetime


@dataclass
class ImageGenerationResult:
    """Result from image generation."""
    output_file: str
    prompt: str
    provider: str
    dimensions: str
    file_size_kb: float
    generation_time_seconds: float


class ImageGenerator:
    """Generate images using AI providers (Gemini, Midjourney)."""
    
    # Platform specifications
    PLATFORM_SPECS = {
        "linkedin-feed": {"width": 1200, "height": 627},
        "linkedin-square": {"width": 1200, "height": 1200},
        "instagram-square": {"width": 1080, "height": 1080},
        "instagram-portrait": {"width": 1080, "height": 1350},
        "twitter": {"width": 1200, "height": 675},
        "blog-hero": {"width": 1920, "height": 1080},
        "blog-inline": {"width": 1000, "height": 667},
    }
    
    def __init__(
        self,
        output_dir: str = "output/images",
        provider: Literal["gemini", "midjourney"] = "gemini",
        brand_style: Optional[str] = None
    ):
        """Initialize image generator.
        
        Args:
            output_dir: Directory to save generated images
            provider: AI provider to use (gemini or midjourney)
            brand_style: Optional brand style guidelines. If not provided,
                        uses a clean, professional default aesthetic.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.provider = provider
        self.brand_style = brand_style or (
            "Clean, professional design with accessibility focus. "
            "Modern and approachable aesthetic."
        )
        
        # Load API keys
        if provider == "gemini":
            self.api_key = os.getenv("GEMINI_API_KEY")
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set")
        elif provider == "midjourney":
            self.api_key = os.getenv("MIDJOURNEY_API_KEY")
            if not self.api_key:
                raise ValueError("MIDJOURNEY_API_KEY environment variable not set")
    
    def optimize_prompt(
        self,
        concept: str,
        platform: Optional[str] = None,
        style_override: Optional[str] = None
    ) -> str:
        """Optimize prompt for visual generation.
        
        Args:
            concept: Core visual concept to generate
            platform: Target platform (affects composition)
            style_override: Override default brand style
            
        Returns:
            Optimized prompt string
        """
        style = style_override or self.brand_style
        
        # Add composition guidance based on platform
        composition = ""
        if platform and platform in self.PLATFORM_SPECS:
            aspect = self.PLATFORM_SPECS[platform]
            if aspect["width"] > aspect["height"]:
                composition = "Horizontal composition, landscape orientation. "
            elif aspect["width"] < aspect["height"]:
                composition = "Vertical composition, portrait orientation. "
            else:
                composition = "Square composition, centered focus. "
        
        prompt = f"{concept}. {composition}{style}"
        return prompt
    
    def generate(
        self,
        concept: str,
        platform: str = "blog-inline",
        optimize_prompt: bool = True,
        output_filename: Optional[str] = None,
        format: Literal["png", "jpg"] = "png"
    ) -> ImageGenerationResult:
        """Generate image using AI.
        
        Args:
            concept: Visual concept description
            platform: Target platform for sizing
            optimize_prompt: Whether to enhance prompt with brand style
            output_filename: Custom output filename (auto-generated if None)
            format: Output format (png or jpg)
            
        Returns:
            ImageGenerationResult with generation details
        """
        start_time = datetime.now()
        
        # Optimize prompt if requested
        if optimize_prompt:
            prompt = self.optimize_prompt(concept, platform)
        else:
            prompt = concept
        
        # Get dimensions
        specs = self.PLATFORM_SPECS.get(platform, {"width": 1024, "height": 1024})
        dimensions = f"{specs['width']}x{specs['height']}"
        
        # Generate filename
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            safe_concept = "".join(c for c in concept[:30] if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_concept = safe_concept.replace(' ', '-')
            output_filename = f"{timestamp}-{safe_concept}.{format}"
        
        output_path = self.output_dir / output_filename
        
        # Call appropriate provider
        if self.provider == "gemini":
            image = self._generate_with_gemini(prompt, specs["width"], specs["height"])
        elif self.provider == "midjourney":
            image = self._generate_with_midjourney(prompt, specs["width"], specs["height"])
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
        
        # Save image (convert jpg to jpeg for PIL compatibility)
        save_format = "JPEG" if format.lower() == "jpg" else format.upper()
        image.save(output_path, format=save_format, optimize=True)
        
        # Calculate file size
        file_size_kb = output_path.stat().st_size / 1024
        
        # Calculate generation time
        generation_time = (datetime.now() - start_time).total_seconds()
        
        return ImageGenerationResult(
            output_file=str(output_path),
            prompt=prompt,
            provider=self.provider,
            dimensions=dimensions,
            file_size_kb=file_size_kb,
            generation_time_seconds=generation_time
        )
    
    def _generate_with_gemini(self, prompt: str, width: int, height: int) -> Image.Image:
        """Generate image using Google Gemini Imagen.
        
        Args:
            prompt: Image generation prompt
            width: Image width
            height: Image height
            
        Returns:
            PIL Image object
        """
        # Note: This is a placeholder implementation
        # Actual Gemini Imagen API integration would go here
        # For now, create a placeholder image
        
        try:
            from google import genai
            
            client = genai.Client(api_key=self.api_key)
            
            # Use Gemini's image generation
            # This is simplified - actual implementation may vary based on API
            response = client.models.generate_images(
                model="imagen-3.0-generate-001",
                prompt=prompt,
                config={
                    "number_of_images": 1,
                    "aspect_ratio": f"{width}:{height}"
                }
            )
            
            # Get first image
            image_data = response.images[0].image.data
            image_bytes = Image.open(BytesIO(image_data))
            return image_bytes
            
        except Exception as e:
            # Fallback: create placeholder
            print(f"Gemini generation failed: {e}. Creating placeholder.")
            return self._create_placeholder(width, height, prompt)
    
    def _generate_with_midjourney(self, prompt: str, width: int, height: int) -> Image.Image:
        """Generate image using Midjourney API.
        
        Args:
            prompt: Image generation prompt
            width: Image width
            height: Image height
            
        Returns:
            PIL Image object
        """
        # Note: This is a placeholder implementation
        # Actual Midjourney API integration would go here
        
        try:
            # Midjourney API call would go here
            # For now, create placeholder
            return self._create_placeholder(width, height, prompt)
            
        except Exception as e:
            print(f"Midjourney generation failed: {e}. Creating placeholder.")
            return self._create_placeholder(width, height, prompt)
    
    def _create_placeholder(self, width: int, height: int, text: str) -> Image.Image:
        """Create placeholder image for testing.
        
        Args:
            width: Image width
            height: Image height
            text: Text to display
            
        Returns:
            PIL Image object
        """
        from PIL import Image, ImageDraw, ImageFont
        
        # Create image with brand colors
        img = Image.new('RGB', (width, height), color='#f5f5f5')
        draw = ImageDraw.Draw(img)
        
        # Add text (truncated)
        text_short = text[:50] + "..." if len(text) > 50 else text
        
        # Simple centered text
        bbox = draw.textbbox((0, 0), text_short)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        position = ((width - text_width) // 2, (height - text_height) // 2)
        draw.text(position, text_short, fill='#333333')
        
        return img
    
    def validate_accessibility(self, image_path: str) -> dict:
        """Validate image accessibility.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dict with accessibility validation results
        """
        img = Image.open(image_path)
        
        # Check file size
        file_size_kb = Path(image_path).stat().st_size / 1024
        size_ok = file_size_kb < 200  # Target < 200KB for web
        
        # Check dimensions
        width, height = img.size
        mobile_friendly = width >= 1080  # Minimum for mobile clarity
        
        return {
            "file_size_kb": file_size_kb,
            "file_size_ok": size_ok,
            "dimensions": f"{width}x{height}",
            "mobile_friendly": mobile_friendly,
            "passes_validation": size_ok and mobile_friendly
        }


if __name__ == "__main__":
    # Example usage
    generator = ImageGenerator(provider="gemini")
    
    result = generator.generate(
        concept="AI adoption framework with 3 steps: Audit, Identify, Implement",
        platform="linkedin-square",
        optimize_prompt=True
    )
    
    print(f"Generated: {result.output_file}")
    print(f"Dimensions: {result.dimensions}")
    print(f"File size: {result.file_size_kb:.2f}KB")
    print(f"Time: {result.generation_time_seconds:.2f}s")
    
    # Validate accessibility
    validation = generator.validate_accessibility(result.output_file)
    print(f"Accessibility: {'✓ PASS' if validation['passes_validation'] else '✗ FAIL'}")
