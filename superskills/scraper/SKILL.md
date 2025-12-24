---
name: scraper
description: AI-friendly web scraping and data extraction using Crawl4AI. Use when you need to extract clean content from websites, scrape multiple pages, or gather research data from the web.
version: 1.0.0
---

# Scraper

> **Note**: Review [PROFILE.md](PROFILE.md) for user-specific scraping preferences, extraction strategies, and output formatting.
> 
> **Master Briefing**: Global brand voice at `~/.superskills/master-briefing.yaml` applies automatically. Skill profile overrides when conflicts exist.

Extract clean, AI-ready content from websites using intelligent web scraping. Optimized for LLM consumption with markdown output.

## Tools

**WebScraper.py** (in src/):
- Clean content extraction in markdown format
- Async operations for high-performance scraping
- Pre-defined extraction strategies (article, product, contact)
- Batch URL processing with concurrency control
- Multiple output formats (JSON, Markdown, HTML)
- Smart waiting for dynamic JavaScript content
- Rate limiting and ethical scraping practices

## Core Workflow

### 1. Target Identification
- Receive URL(s) to scrape
- Identify content type (article, product, general)
- Determine if dynamic content loading needed
- Plan extraction strategy

### 2. Content Extraction
- Scrape page(s) using Crawl4AI
- Apply extraction strategy if needed
- Convert to clean markdown format
- Extract structured data (titles, dates, metadata)
- Handle pagination and multi-page content

### 3. Delivery
- Export in requested format (markdown, JSON, HTML)
- Validate content completeness
- Package with metadata (URL, timestamp, success status)
- Handoff to downstream skills (researcher, author)

## Usage

**Single URL:**
```python
from superskills.scraper.src import scrape_url

result = scrape_url("https://example.com/article")
print(result.title)
print(result.content)
```

**Multiple URLs:**
```python
from superskills.scraper.src import scrape_urls

urls = ["https://example.com/page1", "https://example.com/page2"]
results = scrape_urls(urls, max_concurrent=3)

for result in results:
    print(f"{result.title}: {len(result.content)} characters")
```

**Advanced Async:**
```python
import asyncio
from superskills.scraper.src import WebScraper

async def main():
    scraper = WebScraper(extraction_mode="markdown")
    result = await scraper.scrape(
        "https://example.com",
        extraction_strategy="article",
        wait_for_selector=".content-loaded"
    )
    print(result.content)

asyncio.run(main())
```

## Extraction Strategies

**Article**: Extracts title, author, date, content, tags  
**Product**: Extracts name, price, description, rating, reviews  
**Contact**: Extracts name, email, phone, address, social links  

## Environment Variables

```bash
# No API keys required - Crawl4AI is free and open-source
# Optional: Configure browser settings in config/scraper_config.yaml
```

## Quality Checklist

- [ ] Content extracted cleanly (no navigation/ads)
- [ ] Markdown formatting preserved
- [ ] Metadata captured (title, URL, timestamp)
- [ ] Rate limiting respected (delay between requests)
- [ ] robots.txt honored
- [ ] Dynamic content loaded if needed
- [ ] Success status checked before use

## Avoid

- **Overwhelming Servers**: Single requests → Rate-limited batch processing with delays
- **Incomplete Scraping**: Immediate extraction → Use wait_for_selector for JS-heavy sites
- **Ignoring Policies**: Scrape everything → Check robots.txt and respect rate limits
- **Raw HTML Output**: HTML format → Markdown for AI/LLM consumption

## Escalate When

- Website blocks scraping attempts (requires authentication)
- Content is behind CAPTCHA or anti-bot protection
- Need to scrape sites requiring login/cookies
- Legal/ethical concerns about scraping specific site
- Rate limits too restrictive for project needs

## Integration Examples

**With Researcher Skill:**
```python
from superskills.scraper.src import scrape_urls
from superskills.researcher.src import Researcher

urls = ["https://source1.com", "https://source2.com"]
results = scrape_urls(urls)

researcher = Researcher()
for result in results:
    analysis = researcher.analyze(result.content)
```

**With Author Skill:**
```python
from superskills.scraper.src import scrape_url
from superskills.author.src import ContentWriter

result = scrape_url("https://example.com/article")

writer = ContentWriter()
summary = writer.summarize(result.content)
```
