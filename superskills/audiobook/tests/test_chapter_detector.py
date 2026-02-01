"""
Test suite for ChapterDetector.
"""
import pytest

from superskills.audiobook.src.ChapterDetector import ChapterDetector, Chapter


class TestChapterDetector:
    """Tests for ChapterDetector class."""

    def test_detect_markdown_chapters(self):
        """Test markdown heading detection."""
        # Create chapters with enough words to pass MIN_CHAPTER_WORDS threshold
        text = """# Chapter 1: The Beginning

This is the first chapter with some content. """ + "Word " * 50 + """
It has multiple paragraphs.

# Chapter 2: The Middle

This is the second chapter. """ + "More words here. " * 50 + """
More content here.

# Chapter 3: The End

Final chapter content. """ + "Even more words. " * 50
        
        detector = ChapterDetector()
        chapters = detector.detect_chapters(text, strategy="markdown")
        
        assert len(chapters) == 3
        assert chapters[0].title == "Chapter 1: The Beginning"
        assert chapters[1].title == "Chapter 2: The Middle"
        assert chapters[2].title == "Chapter 3: The End"
        assert "first chapter" in chapters[0].text
        assert "second chapter" in chapters[1].text

    def test_detect_numbered_chapters(self):
        """Test numbered chapter pattern detection."""
        text = """Chapter 1

First chapter content goes here. """ + "Word " * 50 + """
Multiple paragraphs of text.

Chapter 2

Second chapter content. """ + "More text. " * 50 + """
More text here.

CHAPTER 3

Third chapter with uppercase. """ + "Even more. " * 50
        
        detector = ChapterDetector()
        chapters = detector.detect_chapters(text, strategy="numbered")
        
        assert len(chapters) == 3
        assert chapters[0].number == 1
        assert chapters[1].number == 2
        assert chapters[2].number == 3

    def test_detect_numbered_with_titles(self):
        """Test numbered chapters with titles."""
        text = """Chapter 1: Introduction

Intro content here. """ + "Word " * 50 + """

Chapter 2: Main Content

Main content here. """ + "More text. " * 50 + """

Chapter 3: Conclusion

Conclusion here. """ + "Even more. " * 50
        
        detector = ChapterDetector()
        chapters = detector.detect_chapters(text, strategy="numbered")
        
        assert len(chapters) == 3
        assert "Introduction" in chapters[0].title
        assert "Main Content" in chapters[1].title
        assert "Conclusion" in chapters[2].title

    def test_detect_page_breaks(self):
        """Test page break detection."""
        text = "First section\n\nContent here. " + "Word " * 50 + "\f\nSecond section\n\nMore content. " + "More text. " * 50 + "\f\nThird section\n\nFinal content. " + "Even more. " * 50
        
        detector = ChapterDetector()
        chapters = detector.detect_chapters(text, strategy="pagebreak")
        
        assert len(chapters) >= 1

    def test_auto_detect_prefers_markdown(self):
        """Test auto detection prefers markdown headings."""
        text = """# Chapter 1

Content with heading. """ + "Word " * 50 + """

# Chapter 2

More content. """ + "More text. " * 50
        
        detector = ChapterDetector()
        chapters = detector.detect_chapters(text, strategy="auto")
        
        assert len(chapters) == 2

    def test_fallback_single_chapter(self):
        """Test fallback to single chapter when no patterns found."""
        text = "Just plain text without any chapter markers. " * 100
        
        detector = ChapterDetector()
        chapters = detector.detect_chapters(text, strategy="auto")
        
        assert len(chapters) == 1
        assert chapters[0].title == "Full Book"

    def test_skip_short_chapters(self):
        """Test skipping chapters below minimum word count."""
        text = """# Chapter 1

Only a few words.

# Chapter 2

""" + "word " * 100 + """

# Chapter 3

Also short."""
        
        detector = ChapterDetector()
        chapters = detector._detect_markdown_chapters(text)
        
        # Only chapter 2 should have enough words
        assert len([ch for ch in chapters if ch.word_count >= detector.MIN_CHAPTER_WORDS]) >= 1

    def test_split_large_chapters(self):
        """Test splitting oversized chapters."""
        # Create a very large chapter with paragraph breaks
        paragraphs = []
        for i in range(20):
            paragraphs.append("word " * 600)  # 600 words per paragraph
        large_text = "\n\n".join(paragraphs)  # 12,000 words total
        
        detector = ChapterDetector()
        chapters = detector._split_at_paragraphs(large_text)
        
        # Should be split into multiple parts
        assert len(chapters) > 1
        for chapter in chapters:
            assert chapter.word_count <= detector.MAX_CHAPTER_WORDS

    def test_custom_patterns(self):
        """Test custom regex pattern detection."""
        text = """SECTION A

Content for section A. """ + "Word " * 50 + """

SECTION B

Content for section B. """ + "More text. " * 50
        
        detector = ChapterDetector(custom_patterns=[r'^SECTION [A-Z]$'])
        chapters = detector.detect_chapters(text, strategy="custom")
        
        assert len(chapters) == 2

    def test_invalid_custom_pattern(self):
        """Test handling of invalid regex patterns."""
        text = "Some content"
        
        detector = ChapterDetector(custom_patterns=[r'[invalid('])
        chapters = detector.detect_chapters(text, strategy="custom")
        
        # Should return empty list, not crash
        assert chapters == []

    def test_word_count_calculation(self):
        """Test word count is calculated correctly."""
        # Add enough words to pass MIN_CHAPTER_WORDS threshold
        text = """# Chapter 1

This chapter has exactly ten words in this sentence. """ + "Word " * 50
        
        detector = ChapterDetector()
        chapters = detector.detect_chapters(text, strategy="markdown")
        
        assert len(chapters) > 0
        # Word count should be at least 50 (from padding)
        assert chapters[0].word_count >= 50

    def test_chapter_positions(self):
        """Test chapter start/end positions are tracked."""
        text = """# First

Content. """ + "Word " * 50 + """

# Second

More. """ + "More text. " * 50
        
        detector = ChapterDetector()
        chapters = detector.detect_chapters(text, strategy="markdown")
        
        assert len(chapters) == 2
        assert chapters[0].start_position < chapters[1].start_position
        assert chapters[0].end_position <= chapters[1].start_position

    def test_empty_text(self):
        """Test handling of empty text."""
        detector = ChapterDetector()
        
        # Should not crash, might return empty or fallback
        chapters = detector.detect_chapters("", strategy="auto")
        assert isinstance(chapters, list)

    def test_post_process_renumbers_chapters(self):
        """Test post-processing renumbers chapters correctly."""
        # Create chapters with non-sequential numbers
        chapters = [
            Chapter(5, "First", "text " * 100, 0, 100, 100),
            Chapter(10, "Second", "text " * 100, 100, 200, 100),
        ]
        
        detector = ChapterDetector()
        processed = detector._post_process_chapters(chapters)
        
        assert processed[0].number == 1
        assert processed[1].number == 2

    def test_detect_prologue(self):
        """Test detection of prologue section."""
        text = """Prologue

This is the prologue content. """ + "Word " * 100 + """

Chapter 1: The Beginning

This is chapter 1 content. """ + "Word " * 100
        
        detector = ChapterDetector()
        chapters = detector.detect_chapters(text, strategy="numbered")
        
        assert len(chapters) == 2
        assert "prologue" in chapters[0].title.lower()
        assert "chapter 1" in chapters[1].title.lower() or "the beginning" in chapters[1].title.lower()

    def test_detect_epilogue(self):
        """Test detection of epilogue section."""
        text = """Chapter 1: The End

This is chapter 1 content. """ + "Word " * 100 + """

Epilogue

This is the epilogue content. """ + "Word " * 100
        
        detector = ChapterDetector()
        chapters = detector.detect_chapters(text, strategy="numbered")
        
        assert len(chapters) == 2
        assert "epilogue" in chapters[1].title.lower()

    def test_detect_prologue_and_epilogue(self):
        """Test detection of both prologue and epilogue."""
        text = """Prologue: The Dark Past

Prologue text here. """ + "Word " * 100 + """

Chapter 1

Main story. """ + "Word " * 100 + """

Chapter 2

More story. """ + "Word " * 100 + """

Epilogue: What Happened Next

Epilogue text here. """ + "Word " * 100
        
        detector = ChapterDetector()
        chapters = detector.detect_chapters(text, strategy="numbered")
        
        assert len(chapters) == 4
        assert "prologue" in chapters[0].title.lower()
        assert "chapter 1" in chapters[1].title.lower()
        assert "chapter 2" in chapters[2].title.lower()
        assert "epilogue" in chapters[3].title.lower()

    def test_detect_foreword_and_afterword(self):
        """Test detection of foreword and afterword."""
        text = """Foreword

Introduction by the author. """ + "Word " * 100 + """

Chapter 1

Main content. """ + "Word " * 100 + """

Afterword

Final thoughts. """ + "Word " * 100
        
        detector = ChapterDetector()
        chapters = detector.detect_chapters(text, strategy="numbered")
        
        assert len(chapters) == 3
        assert "foreword" in chapters[0].title.lower()
        assert "afterword" in chapters[2].title.lower()
