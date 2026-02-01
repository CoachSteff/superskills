"""Test suite for TextCleaner."""
import pytest
from superskills.audiobook.src.TextCleaner import TextCleaner


class TestTextCleaner:
    """Tests for TextCleaner class."""
    
    def test_remove_page_numbers_standalone(self):
        """Test removal of standalone page numbers."""
        text = "Paragraph one.\n\n42\n\nParagraph two."
        cleaner = TextCleaner()
        result = cleaner.clean(text)
        assert "42" not in result
        assert "Paragraph one" in result
        assert "Paragraph two" in result
    
    def test_remove_page_numbers_with_page_prefix(self):
        """Test removal of 'Page X' patterns."""
        text = "Content here.\nPage 15\nMore content."
        cleaner = TextCleaner()
        result = cleaner.clean(text)
        assert "Page 15" not in result
        assert "Content here" in result
        assert "More content" in result
    
    def test_remove_headers_footers(self):
        """Test removal of headers and footers."""
        text = "Chapter 5\n\nActual chapter content.\n\n© 2024 Publisher"
        cleaner = TextCleaner()
        result = cleaner.clean(text)
        assert "© 2024 Publisher" not in result
        assert "Actual chapter content" in result
    
    def test_fix_hyphenation(self):
        """Test word break fixing."""
        text = "This is an exam-\nple of hyphenation."
        cleaner = TextCleaner()
        result = cleaner.clean(text)
        assert "example" in result
        assert "exam-\nple" not in result
    
    def test_normalize_whitespace(self):
        """Test whitespace normalization."""
        text = "Line 1\n\n\n\n\nLine 2"
        cleaner = TextCleaner()
        result = cleaner.clean(text)
        # Should have at most 2 consecutive newlines
        assert "\n\n\n" not in result
        assert "Line 1" in result
        assert "Line 2" in result
    
    def test_remove_repeated_lines(self):
        """Test duplicate line removal."""
        text = "Chapter Title\nChapter Title\nActual content."
        cleaner = TextCleaner()
        result = cleaner.clean(text)
        # Should only have one "Chapter Title"
        assert result.count("Chapter Title") == 1
        assert "Actual content" in result
    
    def test_custom_patterns(self):
        """Test custom removal patterns."""
        text = "Keep this.\nREMOVE_ME\nKeep this too."
        cleaner = TextCleaner(custom_patterns=[r'^REMOVE_ME$'])
        result = cleaner.clean(text)
        assert "REMOVE_ME" not in result
        assert "Keep this" in result
        assert "Keep this too" in result
    
    def test_disable_cleaning(self):
        """Test disabling cleaning features."""
        text = "Content.\n42\nMore content."
        cleaner = TextCleaner(remove_page_numbers=False)
        result = cleaner.clean(text)
        assert "42" in result  # Should keep page numbers when disabled
    
    def test_page_number_with_separator(self):
        """Test removal of page numbers with separators."""
        text = "Chapter content.\n42 | Chapter Title\nMore content."
        cleaner = TextCleaner()
        result = cleaner.clean(text)
        assert "42 | Chapter Title" not in result
        assert "Chapter content" in result
    
    def test_multiple_spaces_normalized(self):
        """Test multiple consecutive spaces are normalized."""
        text = "Word1    Word2     Word3"
        cleaner = TextCleaner()
        result = cleaner.clean(text)
        assert "    " not in result
        assert "Word1 Word2 Word3" in result
