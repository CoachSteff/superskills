"""
WebScraper.py - AI-friendly web scraping using Crawl4AI.
"""
import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Literal, Optional

try:
    from crawl4ai import AsyncWebCrawler
    from crawl4ai.extraction_strategy import CosineStrategy, LLMExtractionStrategy
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False
    print("Warning: crawl4ai not available - install with: pip install crawl4ai")


ExtractionMode = Literal["markdown", "html", "structured", "llm"]
OutputFormat = Literal["json", "markdown", "text"]


@dataclass
class ScrapingResult:
    """Result from a web scraping operation."""
    url: str
    title: str
    content: str
    metadata: Dict
    extracted_data: Optional[Dict] = None
    timestamp: str = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class WebScraper:
    """AI-friendly web scraper using Crawl4AI."""

    # Default extraction strategies
    EXTRACTION_STRATEGIES = {
        "article": {
            "fields": ["title", "author", "published_date", "content", "tags"],
            "description": "Extract article information"
        },
        "product": {
            "fields": ["name", "price", "description", "rating", "reviews"],
            "description": "Extract product information"
        },
        "contact": {
            "fields": ["name", "email", "phone", "address", "social_links"],
            "description": "Extract contact information"
        }
    }

    def __init__(
        self,
        output_dir: str = "scraped_data",
        extraction_mode: ExtractionMode = "markdown",
        verbose: bool = True,
        headless: bool = True,
        user_agent: Optional[str] = None
    ):
        """Initialize WebScraper.
        
        Args:
            output_dir: Directory to save scraped content
            extraction_mode: How to extract content (markdown, html, structured, llm)
            verbose: Enable verbose logging
            headless: Run browser in headless mode
            user_agent: Custom user agent string
        """
        if not CRAWL4AI_AVAILABLE:
            raise ImportError("crawl4ai is required. Install with: pip install crawl4ai")

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.extraction_mode = extraction_mode
        self.verbose = verbose
        self.headless = headless
        self.user_agent = user_agent or "Mozilla/5.0 (compatible; SuperSkillsBot/1.0)"

    async def scrape(
        self,
        url: str,
        wait_for_selector: Optional[str] = None,
        wait_for_timeout: int = 5000,
        extraction_strategy: Optional[str] = None,
        css_selector: Optional[str] = None,
        output_filename: Optional[str] = None
    ) -> ScrapingResult:
        """Scrape a single URL.
        
        Args:
            url: URL to scrape
            wait_for_selector: CSS selector to wait for before scraping
            wait_for_timeout: Maximum time to wait (milliseconds)
            extraction_strategy: Pre-defined strategy (article, product, contact)
            css_selector: CSS selector to extract specific content
            output_filename: Custom filename for output
            
        Returns:
            ScrapingResult with extracted content
        """
        if self.verbose:
            print(f"Scraping: {url}")

        async with AsyncWebCrawler(verbose=self.verbose, headless=self.headless) as crawler:
            # Build crawler configuration
            config = {
                "wait_for": wait_for_selector,
                "delay_before_return_html": wait_for_timeout / 1000.0 if wait_for_timeout else 5.0
            }

            # Add extraction strategy if specified
            if extraction_strategy and extraction_strategy in self.EXTRACTION_STRATEGIES:
                strategy_config = self.EXTRACTION_STRATEGIES[extraction_strategy]
                if self.verbose:
                    print(f"Using extraction strategy: {extraction_strategy}")

            # Perform the crawl
            result = await crawler.arun(url=url, **config)

            # Extract content based on mode
            content = ""
            extracted_data = None

            if self.extraction_mode == "markdown":
                content = result.markdown if hasattr(result, 'markdown') else result.cleaned_html
            elif self.extraction_mode == "html":
                content = result.html
            elif self.extraction_mode == "structured":
                content = result.cleaned_html
                # Extract using CSS selector if provided
                if css_selector and hasattr(result, 'fit_markdown'):
                    content = result.fit_markdown

            # Get metadata
            metadata = {
                "url": url,
                "status_code": getattr(result, 'status_code', None),
                "success": getattr(result, 'success', True),
                "extraction_mode": self.extraction_mode,
                "timestamp": datetime.now().isoformat()
            }

            # Get title
            title = getattr(result, 'title', url.split('/')[-1] or 'Untitled')

            # Create result object
            scraping_result = ScrapingResult(
                url=url,
                title=title,
                content=content,
                metadata=metadata,
                extracted_data=extracted_data
            )

            # Save to file if requested
            if output_filename:
                self._save_result(scraping_result, output_filename)

            if self.verbose:
                print(f"✓ Scraped successfully: {len(content)} characters")

            return scraping_result

    async def scrape_multiple(
        self,
        urls: List[str],
        max_concurrent: int = 3,
        **kwargs
    ) -> List[ScrapingResult]:
        """Scrape multiple URLs concurrently.
        
        Args:
            urls: List of URLs to scrape
            max_concurrent: Maximum number of concurrent requests
            **kwargs: Additional arguments passed to scrape()
            
        Returns:
            List of ScrapingResult objects
        """
        if self.verbose:
            print(f"Scraping {len(urls)} URLs (max {max_concurrent} concurrent)...")

        results = []
        semaphore = asyncio.Semaphore(max_concurrent)

        async def scrape_with_limit(url):
            async with semaphore:
                try:
                    return await self.scrape(url, **kwargs)
                except Exception as e:
                    print(f"Error scraping {url}: {e}")
                    return ScrapingResult(
                        url=url,
                        title="Error",
                        content="",
                        metadata={"error": str(e), "success": False}
                    )

        tasks = [scrape_with_limit(url) for url in urls]
        results = await asyncio.gather(*tasks)

        successful = sum(1 for r in results if r.metadata.get('success', True))
        if self.verbose:
            print(f"✓ Completed: {successful}/{len(urls)} successful")

        return results

    def _save_result(
        self,
        result: ScrapingResult,
        filename: str,
        format: OutputFormat = "json"
    ):
        """Save scraping result to file.
        
        Args:
            result: ScrapingResult to save
            filename: Output filename
            format: Output format (json, markdown, text)
        """
        output_path = self.output_dir / filename

        if format == "json":
            data = {
                "url": result.url,
                "title": result.title,
                "content": result.content,
                "metadata": result.metadata,
                "extracted_data": result.extracted_data,
                "timestamp": result.timestamp
            }
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        elif format == "markdown":
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# {result.title}\n\n")
                f.write(f"**URL:** {result.url}\n\n")
                f.write(f"**Scraped:** {result.timestamp}\n\n")
                f.write("---\n\n")
                f.write(result.content)

        elif format == "text":
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.content)

        if self.verbose:
            print(f"✓ Saved to: {output_path}")

    def save_batch(
        self,
        results: List[ScrapingResult],
        filename: str = "batch_results.json"
    ):
        """Save multiple results to a single JSON file.
        
        Args:
            results: List of ScrapingResult objects
            filename: Output filename
        """
        output_path = self.output_dir / filename

        data = {
            "total_results": len(results),
            "timestamp": datetime.now().isoformat(),
            "results": [
                {
                    "url": r.url,
                    "title": r.title,
                    "content": r.content[:500] + "..." if len(r.content) > 500 else r.content,
                    "metadata": r.metadata,
                    "extracted_data": r.extracted_data
                }
                for r in results
            ]
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        if self.verbose:
            print(f"✓ Batch saved to: {output_path}")


def scrape_url(url: str, output_dir: str = "scraped_data", **kwargs) -> ScrapingResult:
    """Convenience function to scrape a single URL synchronously.
    
    Args:
        url: URL to scrape
        output_dir: Output directory
        **kwargs: Additional arguments for WebScraper
        
    Returns:
        ScrapingResult
    """
    scraper = WebScraper(output_dir=output_dir, **kwargs)
    return asyncio.run(scraper.scrape(url))


def scrape_urls(urls: List[str], output_dir: str = "scraped_data", **kwargs) -> List[ScrapingResult]:
    """Convenience function to scrape multiple URLs synchronously.
    
    Args:
        urls: List of URLs to scrape
        output_dir: Output directory
        **kwargs: Additional arguments for WebScraper
        
    Returns:
        List of ScrapingResult objects
    """
    scraper = WebScraper(output_dir=output_dir, **kwargs)
    return asyncio.run(scraper.scrape_multiple(urls))
