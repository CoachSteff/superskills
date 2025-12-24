"""Unit tests for WebScraper."""
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "superskills" / "scraper" / "src"))
from WebScraper import ScrapingResult, WebScraper, scrape_url, scrape_urls


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables."""
    return {}


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def sample_html():
    """Sample HTML content."""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Test Page</title></head>
    <body>
        <h1>Test Article</h1>
        <p class="author">John Doe</p>
        <div class="content">
            <p>This is test content.</p>
            <p>More test content here.</p>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def sample_markdown():
    """Sample markdown content."""
    return """# Test Article

**Author:** John Doe

This is test content.

More test content here."""


class TestScrapingResult:
    """Test ScrapingResult dataclass."""

    def test_scraping_result_creation(self):
        """Test creating a ScrapingResult."""
        result = ScrapingResult(
            url="https://example.com",
            title="Test",
            content="Content",
            metadata={"status": 200}
        )
        assert result.url == "https://example.com"
        assert result.title == "Test"
        assert result.content == "Content"
        assert result.timestamp is not None

    def test_scraping_result_with_extracted_data(self):
        """Test ScrapingResult with extracted data."""
        result = ScrapingResult(
            url="https://example.com",
            title="Test",
            content="Content",
            metadata={},
            extracted_data={"field1": "value1"}
        )
        assert result.extracted_data == {"field1": "value1"}


class TestWebScraperInit:
    """Test WebScraper initialization."""

    def test_init_with_defaults(self, temp_output_dir):
        """Test initialization with default values."""
        scraper = WebScraper(output_dir=str(temp_output_dir))
        assert scraper.output_dir == temp_output_dir
        assert scraper.extraction_mode == "markdown"
        assert scraper.verbose
        assert scraper.headless

    def test_init_with_custom_values(self, temp_output_dir):
        """Test initialization with custom values."""
        scraper = WebScraper(
            output_dir=str(temp_output_dir),
            extraction_mode="html",
            verbose=False,
            headless=False
        )
        assert scraper.extraction_mode == "html"
        assert not scraper.verbose
        assert not scraper.headless

    def test_init_creates_output_dir(self, tmp_path):
        """Test that output directory is created."""
        output_dir = tmp_path / "new_dir"
        WebScraper(output_dir=str(output_dir))
        assert output_dir.exists()


class TestExtractionStrategies:
    """Test extraction strategies."""

    def test_strategies_defined(self):
        """Test that extraction strategies are defined."""
        assert "article" in WebScraper.EXTRACTION_STRATEGIES
        assert "product" in WebScraper.EXTRACTION_STRATEGIES
        assert "contact" in WebScraper.EXTRACTION_STRATEGIES

    def test_article_strategy_fields(self):
        """Test article strategy has correct fields."""
        strategy = WebScraper.EXTRACTION_STRATEGIES["article"]
        assert "title" in strategy["fields"]
        assert "author" in strategy["fields"]
        assert "content" in strategy["fields"]

    def test_product_strategy_fields(self):
        """Test product strategy has correct fields."""
        strategy = WebScraper.EXTRACTION_STRATEGIES["product"]
        assert "name" in strategy["fields"]
        assert "price" in strategy["fields"]
        assert "rating" in strategy["fields"]


@pytest.mark.asyncio
class TestScraping:
    """Test scraping operations (mocked)."""

    @patch('WebScraper.AsyncWebCrawler')
    async def test_scrape_basic(self, mock_crawler_class, temp_output_dir, sample_markdown):
        """Test basic scraping."""
        # Mock the crawler
        mock_crawler = MagicMock()
        mock_result = MagicMock()
        mock_result.markdown = sample_markdown
        mock_result.html = "<html>Test</html>"
        mock_result.title = "Test Article"
        mock_result.success = True
        mock_result.status_code = 200

        mock_crawler.arun = AsyncMock(return_value=mock_result)
        mock_crawler.__aenter__ = AsyncMock(return_value=mock_crawler)
        mock_crawler.__aexit__ = AsyncMock(return_value=None)
        mock_crawler_class.return_value = mock_crawler

        scraper = WebScraper(output_dir=str(temp_output_dir))
        result = await scraper.scrape("https://example.com")

        assert result.url == "https://example.com"
        assert result.title == "Test Article"
        assert "Test Article" in result.content
        assert result.metadata["success"]

    @patch('WebScraper.AsyncWebCrawler')
    async def test_scrape_with_html_mode(self, mock_crawler_class, temp_output_dir, sample_html):
        """Test scraping in HTML mode."""
        mock_crawler = MagicMock()
        mock_result = MagicMock()
        mock_result.html = sample_html
        mock_result.title = "Test Page"
        mock_result.success = True

        mock_crawler.arun = AsyncMock(return_value=mock_result)
        mock_crawler.__aenter__ = AsyncMock(return_value=mock_crawler)
        mock_crawler.__aexit__ = AsyncMock(return_value=None)
        mock_crawler_class.return_value = mock_crawler

        scraper = WebScraper(output_dir=str(temp_output_dir), extraction_mode="html")
        result = await scraper.scrape("https://example.com")

        assert "<html>" in result.content
        assert result.metadata["extraction_mode"] == "html"

    @patch('WebScraper.AsyncWebCrawler')
    async def test_scrape_with_wait_selector(self, mock_crawler_class, temp_output_dir):
        """Test scraping with wait_for_selector."""
        mock_crawler = MagicMock()
        mock_result = MagicMock()
        mock_result.markdown = "Test"
        mock_result.title = "Test"
        mock_result.success = True

        mock_crawler.arun = AsyncMock(return_value=mock_result)
        mock_crawler.__aenter__ = AsyncMock(return_value=mock_crawler)
        mock_crawler.__aexit__ = AsyncMock(return_value=None)
        mock_crawler_class.return_value = mock_crawler

        scraper = WebScraper(output_dir=str(temp_output_dir))
        await scraper.scrape(
            "https://example.com",
            wait_for_selector=".content"
        )

        mock_crawler.arun.assert_called_once()
        call_args = mock_crawler.arun.call_args
        assert call_args[1]["wait_for"] == ".content"


@pytest.mark.asyncio
class TestMultipleScraping:
    """Test scraping multiple URLs."""

    @patch('WebScraper.AsyncWebCrawler')
    async def test_scrape_multiple_urls(self, mock_crawler_class, temp_output_dir):
        """Test scraping multiple URLs."""
        mock_crawler = MagicMock()
        mock_result = MagicMock()
        mock_result.markdown = "Test content"
        mock_result.title = "Test"
        mock_result.success = True

        mock_crawler.arun = AsyncMock(return_value=mock_result)
        mock_crawler.__aenter__ = AsyncMock(return_value=mock_crawler)
        mock_crawler.__aexit__ = AsyncMock(return_value=None)
        mock_crawler_class.return_value = mock_crawler

        scraper = WebScraper(output_dir=str(temp_output_dir))
        urls = [
            "https://example.com/1",
            "https://example.com/2",
            "https://example.com/3"
        ]

        results = await scraper.scrape_multiple(urls, max_concurrent=2)

        assert len(results) == 3
        assert all(isinstance(r, ScrapingResult) for r in results)

    @patch('WebScraper.AsyncWebCrawler')
    async def test_scrape_multiple_with_error(self, mock_crawler_class, temp_output_dir):
        """Test scraping multiple URLs with one failing."""
        mock_crawler = MagicMock()
        mock_result = MagicMock()
        mock_result.markdown = "Test"
        mock_result.title = "Test"
        mock_result.success = True

        # Make arun fail on second call
        call_count = [0]
        async def arun_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 2:
                raise Exception("Network error")
            return mock_result

        mock_crawler.arun = AsyncMock(side_effect=arun_side_effect)
        mock_crawler.__aenter__ = AsyncMock(return_value=mock_crawler)
        mock_crawler.__aexit__ = AsyncMock(return_value=None)
        mock_crawler_class.return_value = mock_crawler

        scraper = WebScraper(output_dir=str(temp_output_dir))
        urls = ["https://example.com/1", "https://example.com/2", "https://example.com/3"]

        results = await scraper.scrape_multiple(urls)

        assert len(results) == 3
        # Check that second result has error
        assert not results[1].metadata.get("success")


class TestSaveResults:
    """Test saving results."""

    def test_save_result_json(self, temp_output_dir):
        """Test saving result as JSON."""
        scraper = WebScraper(output_dir=str(temp_output_dir))
        result = ScrapingResult(
            url="https://example.com",
            title="Test",
            content="Content",
            metadata={"status": 200}
        )

        scraper._save_result(result, "test.json", format="json")

        output_file = temp_output_dir / "test.json"
        assert output_file.exists()

        with open(output_file) as f:
            data = json.load(f)

        assert data["url"] == "https://example.com"
        assert data["title"] == "Test"
        assert data["content"] == "Content"

    def test_save_result_markdown(self, temp_output_dir):
        """Test saving result as markdown."""
        scraper = WebScraper(output_dir=str(temp_output_dir))
        result = ScrapingResult(
            url="https://example.com",
            title="Test Article",
            content="# Content\n\nTest content here.",
            metadata={}
        )

        scraper._save_result(result, "test.md", format="markdown")

        output_file = temp_output_dir / "test.md"
        assert output_file.exists()

        content = output_file.read_text()
        assert "# Test Article" in content
        assert "https://example.com" in content

    def test_save_result_text(self, temp_output_dir):
        """Test saving result as text."""
        scraper = WebScraper(output_dir=str(temp_output_dir))
        result = ScrapingResult(
            url="https://example.com",
            title="Test",
            content="Plain text content",
            metadata={}
        )

        scraper._save_result(result, "test.txt", format="text")

        output_file = temp_output_dir / "test.txt"
        assert output_file.exists()
        assert output_file.read_text() == "Plain text content"

    def test_save_batch(self, temp_output_dir):
        """Test saving batch of results."""
        scraper = WebScraper(output_dir=str(temp_output_dir))
        results = [
            ScrapingResult(
                url=f"https://example.com/{i}",
                title=f"Test {i}",
                content=f"Content {i}",
                metadata={}
            )
            for i in range(3)
        ]

        scraper.save_batch(results, "batch.json")

        output_file = temp_output_dir / "batch.json"
        assert output_file.exists()

        with open(output_file) as f:
            data = json.load(f)

        assert data["total_results"] == 3
        assert len(data["results"]) == 3


class TestConvenienceFunctions:
    """Test convenience functions."""

    @patch('WebScraper.AsyncWebCrawler')
    def test_scrape_url_sync(self, mock_crawler_class, temp_output_dir):
        """Test synchronous scrape_url helper."""
        mock_crawler = MagicMock()
        mock_result = MagicMock()
        mock_result.markdown = "Test"
        mock_result.title = "Test"
        mock_result.success = True

        mock_crawler.arun = AsyncMock(return_value=mock_result)
        mock_crawler.__aenter__ = AsyncMock(return_value=mock_crawler)
        mock_crawler.__aexit__ = AsyncMock(return_value=None)
        mock_crawler_class.return_value = mock_crawler

        result = scrape_url("https://example.com", output_dir=str(temp_output_dir))

        assert isinstance(result, ScrapingResult)
        assert result.url == "https://example.com"

    @patch('WebScraper.AsyncWebCrawler')
    def test_scrape_urls_sync(self, mock_crawler_class, temp_output_dir):
        """Test synchronous scrape_urls helper."""
        mock_crawler = MagicMock()
        mock_result = MagicMock()
        mock_result.markdown = "Test"
        mock_result.title = "Test"
        mock_result.success = True

        mock_crawler.arun = AsyncMock(return_value=mock_result)
        mock_crawler.__aenter__ = AsyncMock(return_value=mock_crawler)
        mock_crawler.__aexit__ = AsyncMock(return_value=None)
        mock_crawler_class.return_value = mock_crawler

        urls = ["https://example.com/1", "https://example.com/2"]
        results = scrape_urls(urls, output_dir=str(temp_output_dir))

        assert len(results) == 2
        assert all(isinstance(r, ScrapingResult) for r in results)
