"""
Test suite for DocumentParser.
"""
import pytest
from pathlib import Path
from unittest.mock import mock_open, patch, MagicMock

from superskills.audiobook.src.DocumentParser import DocumentParser


class TestDocumentParser:
    """Tests for DocumentParser class."""

    def test_get_format_pdf(self):
        """Test PDF format detection."""
        parser = DocumentParser()
        assert parser.get_format("document.pdf") == "pdf"
        assert parser.get_format("book.PDF") == "pdf"

    def test_get_format_txt(self):
        """Test plain text format detection."""
        parser = DocumentParser()
        assert parser.get_format("document.txt") == "txt"
        assert parser.get_format("notes.TXT") == "txt"

    def test_get_format_markdown(self):
        """Test markdown format detection."""
        parser = DocumentParser()
        assert parser.get_format("readme.md") == "md"
        assert parser.get_format("doc.markdown") == "md"

    def test_get_format_docx(self):
        """Test DOCX format detection."""
        parser = DocumentParser()
        assert parser.get_format("document.docx") == "docx"
        assert parser.get_format("book.DOCX") == "docx"

    def test_get_format_unsupported(self):
        """Test unsupported format raises error."""
        parser = DocumentParser()
        with pytest.raises(ValueError, match="Unsupported file format"):
            parser.get_format("document.odt")

    def test_parse_file_not_found(self):
        """Test file not found error."""
        parser = DocumentParser()
        with pytest.raises(FileNotFoundError):
            parser.parse_file("/nonexistent/file.txt")

    def test_parse_text_utf8(self):
        """Test parsing UTF-8 text file."""
        parser = DocumentParser()
        content = "Hello, world!\nThis is a test."
        
        with patch("builtins.open", mock_open(read_data=content)):
            with patch("pathlib.Path.exists", return_value=True):
                result = parser.parse_file("test.txt")
        
        assert result == content

    def test_parse_text_empty_raises_error(self):
        """Test parsing empty file raises error."""
        parser = DocumentParser()
        
        with patch("builtins.open", mock_open(read_data="")):
            with patch("pathlib.Path.exists", return_value=True):
                with pytest.raises(ValueError, match="No text extracted"):
                    parser.parse_file("test.txt")

    def test_parse_text_fallback_encoding(self):
        """Test encoding fallback mechanism."""
        parser = DocumentParser()
        content = "Test content"
        
        # Mock UTF-8 failing, latin-1 succeeding
        with patch("builtins.open", side_effect=[
            UnicodeDecodeError("utf-8", b"", 0, 1, "test"),
            mock_open(read_data=content)()
        ]):
            with patch("pathlib.Path.exists", return_value=True):
                result = parser.parse_file("test.txt")
        
        assert result == content

    @patch("superskills.audiobook.src.DocumentParser.PYPDF2_AVAILABLE", True)
    @pytest.mark.skipif(
        not hasattr(__import__('sys').modules.get('PyPDF2', type('', (), {})()), '__version__'),
        reason="PyPDF2 not installed"
    )
    def test_parse_pdf_success(self):
        """Test PDF parsing success."""
        parser = DocumentParser()
        
        # Mock PyPDF2
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 content"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Page 2 content"
        
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page1, mock_page2]
        
        try:
            import PyPDF2
            with patch("PyPDF2.PdfReader", return_value=mock_reader):
                with patch("builtins.open", mock_open()):
                    with patch("pathlib.Path.exists", return_value=True):
                        result = parser.parse_file("test.pdf")
            
            assert "Page 1 content" in result
            assert "Page 2 content" in result
        except ImportError:
            pytest.skip("PyPDF2 not available")

    @patch("superskills.audiobook.src.DocumentParser.PYPDF2_AVAILABLE", False)
    def test_parse_pdf_library_not_available(self):
        """Test PDF parsing without PyPDF2 installed."""
        parser = DocumentParser()
        
        with patch("pathlib.Path.exists", return_value=True):
            with pytest.raises(ImportError, match="PyPDF2 is required"):
                parser.parse_file("test.pdf")

    @patch("superskills.audiobook.src.DocumentParser.DOCX_AVAILABLE", True)
    @pytest.mark.skipif(
        not hasattr(__import__('sys').modules.get('docx', type('', (), {})()), '__version__'),
        reason="python-docx not installed"
    )
    def test_parse_docx_success(self):
        """Test DOCX parsing success."""
        parser = DocumentParser()
        
        # Mock python-docx
        mock_para1 = MagicMock()
        mock_para1.text = "Paragraph 1"
        mock_para2 = MagicMock()
        mock_para2.text = "Paragraph 2"
        
        mock_doc = MagicMock()
        mock_doc.paragraphs = [mock_para1, mock_para2]
        
        try:
            import docx
            with patch("docx.Document", return_value=mock_doc):
                with patch("pathlib.Path.exists", return_value=True):
                    result = parser.parse_file("test.docx")
            
            assert "Paragraph 1" in result
            assert "Paragraph 2" in result
        except ImportError:
            pytest.skip("python-docx not available")

    @patch("superskills.audiobook.src.DocumentParser.DOCX_AVAILABLE", False)
    def test_parse_docx_library_not_available(self):
        """Test DOCX parsing without python-docx installed."""
        parser = DocumentParser()
        
        with patch("pathlib.Path.exists", return_value=True):
            with pytest.raises(ImportError, match="python-docx is required"):
                parser.parse_file("test.docx")

    def test_parse_markdown(self):
        """Test markdown parsing (same as text)."""
        parser = DocumentParser()
        content = "# Heading\n\nParagraph text."
        
        with patch("builtins.open", mock_open(read_data=content)):
            with patch("pathlib.Path.exists", return_value=True):
                result = parser.parse_file("test.md")
        
        assert result == content
