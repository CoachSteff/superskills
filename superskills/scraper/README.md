# Scraper SuperSkill 🕷️

AI-friendly web scraping and data extraction using [Crawl4AI](https://github.com/unclecode/crawl4ai).

## Features

- **Clean Content Extraction**: Get markdown-formatted content optimized for LLMs
- **Async Operations**: High-performance concurrent scraping
- **Smart Strategies**: Pre-defined extraction patterns for common use cases
- **Multiple Formats**: Output as JSON, Markdown, or plain text
- **Flexible Configuration**: Customizable extraction rules and browser settings

## Installation

```bash
pip install crawl4ai
```

For development with tests:
```bash
pip install -r tests/requirements.txt
```

## Quick Start

### Basic Scraping

```python
from superskills.scraper.src import scrape_url

# Scrape a single URL (synchronous)
result = scrape_url("https://example.com/article")
print(result.title)
print(result.content)
```

### Async Scraping

```python
import asyncio
from superskills.scraper.src import WebScraper

async def main():
    scraper = WebScraper(extraction_mode="markdown")
    result = await scraper.scrape("https://example.com")
    print(result.content)

asyncio.run(main())
```

### Scrape Multiple URLs

```python
from superskills.scraper.src import scrape_urls

urls = [
    "https://example.com/page1",
    "https://example.com/page2",
    "https://example.com/page3"
]

results = scrape_urls(urls, max_concurrent=3)
for result in results:
    print(f"{result.title}: {len(result.content)} characters")
```

## Extraction Modes

### Markdown (Default)
Best for LLMs and AI workflows. Clean, structured content.
```python
scraper = WebScraper(extraction_mode="markdown")
```

### HTML
Full HTML content for detailed parsing.
```python
scraper = WebScraper(extraction_mode="html")
```

### Structured
Cleaned HTML with structure preserved.
```python
scraper = WebScraper(extraction_mode="structured")
```

## Extraction Strategies

Pre-defined strategies for common use cases:

### Article Extraction
```python
result = await scraper.scrape(
    "https://blog.example.com/post",
    extraction_strategy="article"
)
# Extracts: title, author, date, content, tags
```

### Product Extraction
```python
result = await scraper.scrape(
    "https://shop.example.com/product",
    extraction_strategy="product"
)
# Extracts: name, price, description, rating, reviews
```

### Contact Information
```python
result = await scraper.scrape(
    "https://company.example.com/contact",
    extraction_strategy="contact"
)
# Extracts: name, email, phone, address, social links
```

## Advanced Usage

### Wait for Dynamic Content
```python
result = await scraper.scrape(
    "https://dynamic-site.com",
    wait_for_selector=".content-loaded",
    wait_for_timeout=5000  # milliseconds
)
```

### Save Results
```python
# Save single result
scraper._save_result(result, "output.json", format="json")
scraper._save_result(result, "output.md", format="markdown")

# Save batch of results
results = await scraper.scrape_multiple(urls)
scraper.save_batch(results, "batch_results.json")
```

### Custom Output Directory
```python
scraper = WebScraper(output_dir="my_scraped_data")
result = await scraper.scrape("https://example.com")
```

## Configuration

Edit `config/scraper_config.yaml` to customize:

```yaml
extraction_strategies:
  article:
    fields:
      - title
      - author
      - content
    css_selectors:
      title: "h1, .article-title"
      author: ".author, .byline"

browser:
  headless: true
  user_agent: "Mozilla/5.0 ..."
  timeout: 30000

rate_limiting:
  max_concurrent: 3
  delay_between_requests: 1000
```

## API Reference

### WebScraper

**Constructor:**
```python
WebScraper(
    output_dir="scraped_data",
    extraction_mode="markdown",
    verbose=True,
    headless=True,
    user_agent=None
)
```

**Methods:**

- `scrape(url, wait_for_selector=None, extraction_strategy=None)` - Scrape single URL
- `scrape_multiple(urls, max_concurrent=3)` - Scrape multiple URLs concurrently
- `save_batch(results, filename)` - Save multiple results to JSON

### ScrapingResult

**Attributes:**
- `url`: Source URL
- `title`: Page title
- `content`: Extracted content
- `metadata`: Scraping metadata (status, timestamp, etc.)
- `extracted_data`: Structured data (if using extraction strategy)
- `timestamp`: ISO format timestamp

## Examples

See the [examples](examples/) directory for complete examples:

- `basic_scraping.py` - Simple scraping examples
- `batch_scraping.py` - Scrape multiple URLs
- `article_extraction.py` - Extract blog posts/articles
- `product_scraping.py` - Extract e-commerce products

## Integration

### With Researcher SuperSkill
```python
from superskills.scraper.src import scrape_urls
from superskills.researcher.src import Researcher

# Scrape research sources
urls = ["https://source1.com", "https://source2.com"]
results = scrape_urls(urls)

# Analyze with researcher
researcher = Researcher()
for result in results:
    analysis = researcher.analyze(result.content)
```

### With Author SuperSkill
```python
from superskills.scraper.src import scrape_url
from superskills.author.src import ContentWriter

# Scrape source material
result = scrape_url("https://example.com/article")

# Generate summary
writer = ContentWriter()
summary = writer.summarize(result.content)
```

## Best Practices

1. **Respect robots.txt** - Always check site's scraping policy
2. **Rate limiting** - Use `max_concurrent` to avoid overwhelming servers
3. **Error handling** - Check `metadata.success` before processing
4. **Dynamic content** - Use `wait_for_selector` for JavaScript-heavy sites
5. **Batch processing** - Use `scrape_multiple` for efficient bulk operations

## Testing

Run tests:
```bash
pytest tests/test_scraper.py -v
```

Run with coverage:
```bash
pytest tests/test_scraper.py -v --cov=superskills/scraper
```

## Troubleshooting

### ImportError: crawl4ai not found
```bash
pip install crawl4ai
```

### Slow scraping
- Reduce `max_concurrent` value
- Increase `wait_for_timeout`
- Check your internet connection

### Empty content
- Try different `extraction_mode`
- Use `wait_for_selector` for dynamic content
- Check if site requires authentication

## Dependencies

- **crawl4ai** (>=0.3.0) - Web crawling library
- **asyncio** - Async operations (Python stdlib)

## Version

1.0.0

## License

MIT

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## Support

- **GitHub Issues**: [Report bugs](https://github.com/yourusername/superskills/issues)
- **Documentation**: [Full docs](https://superskills.dev/docs/scraper)
- **Examples**: See `examples/` directory

---

Built with ❤️ using [Crawl4AI](https://github.com/unclecode/crawl4ai)
