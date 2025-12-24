"""Scraper agent tools."""

from .WebScraper import ScrapingResult, WebScraper, scrape_url, scrape_urls

__all__ = [
    'WebScraper',
    'ScrapingResult',
    'scrape_url',
    'scrape_urls'
]

__version__ = "1.0.0"
