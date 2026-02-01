"""
ChapterDetector.py - Automatic chapter boundary detection.
"""
import re
from dataclasses import dataclass
from typing import List, Literal, Optional


@dataclass
class Chapter:
    """Represents a detected chapter in a document."""
    number: int
    title: str
    text: str
    start_position: int
    end_position: int
    word_count: int


DetectionStrategy = Literal["auto", "markdown", "numbered", "pagebreak", "custom"]


class ChapterDetector:
    """Detect chapter boundaries in text using various strategies."""

    MAX_CHAPTER_WORDS = 5000    # Conservative limit for Gemini's 8k token limit (~6,400 tokens)
    MAX_CHAPTER_CHARS = 32000   # Safe buffer under Gemini's ~32k char limit (8,192 tokens × 4 chars/token)
    MIN_CHAPTER_WORDS = 50      # Minimum viable chapter size

    def __init__(self, custom_patterns: Optional[List[str]] = None):
        """Initialize ChapterDetector.
        
        Args:
            custom_patterns: Optional list of regex patterns for custom detection
        """
        self.custom_patterns = custom_patterns or []

    def detect_chapters(
        self, 
        text: str, 
        strategy: DetectionStrategy = "auto"
    ) -> List[Chapter]:
        """Detect chapters in text using specified strategy.
        
        Args:
            text: Full document text
            strategy: Detection strategy to use
            
        Returns:
            List of detected chapters
        """
        if strategy == "auto":
            return self._auto_detect(text)
        elif strategy == "markdown":
            return self._detect_markdown_chapters(text)
        elif strategy == "numbered":
            return self._detect_numbered_chapters(text)
        elif strategy == "pagebreak":
            return self._detect_page_breaks(text)
        elif strategy == "custom":
            return self._apply_custom_patterns(text)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

    def _auto_detect(self, text: str) -> List[Chapter]:
        """Try detection strategies in priority order.
        
        Args:
            text: Document text
            
        Returns:
            Chapters from first successful strategy, or single chapter fallback
        """
        strategies = [
            self._detect_markdown_chapters,
            self._detect_numbered_chapters,
            self._detect_page_breaks,
        ]
        
        for strategy_func in strategies:
            chapters = strategy_func(text)
            if len(chapters) > 1:  # Found meaningful chapter breaks
                return self._post_process_chapters(chapters)
        
        # Fallback: treat as single chapter or split by size
        return self._create_fallback_chapters(text)

    def _detect_markdown_chapters(self, text: str) -> List[Chapter]:
        """Detect chapters from markdown headings.
        
        Args:
            text: Markdown text
            
        Returns:
            List of chapters based on # or ## headings
        """
        # Match lines starting with # or ## (chapter-level headings)
        pattern = r'^(#{1,2})\s+(.+)$'
        matches = list(re.finditer(pattern, text, re.MULTILINE))
        
        if not matches:
            return []
        
        chapters = []
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            
            title = match.group(2).strip()
            chapter_text = text[start:end].strip()
            
            # Remove heading line from chapter text
            chapter_text = re.sub(r'^#{1,2}\s+.+\n', '', chapter_text, count=1)
            
            word_count = len(chapter_text.split())
            
            if word_count >= self.MIN_CHAPTER_WORDS:
                chapters.append(Chapter(
                    number=len(chapters) + 1,
                    title=title,
                    text=chapter_text,
                    start_position=start,
                    end_position=end,
                    word_count=word_count
                ))
        
        return self._post_process_chapters(chapters)

    def _detect_numbered_chapters(self, text: str) -> List[Chapter]:
        """Detect chapters from numbered patterns.
        
        Args:
            text: Document text
            
        Returns:
            List of chapters based on "Chapter N", prologues, epilogues, etc.
        """
        # Patterns for special sections (prologue, epilogue, etc.)
        # Match only at start of line (not mid-text), use word boundaries
        special_patterns = [
            (r'^Prologue\b(?:\s*:\s*([^\n]*))?$', 'Prologue'),
            (r'^PROLOGUE\b(?:\s*:\s*([^\n]*))?$', 'Prologue'),
            (r'^Epilogue\b(?:\s*:\s*([^\n]*))?$', 'Epilogue'),
            (r'^EPILOGUE\b(?:\s*:\s*([^\n]*))?$', 'Epilogue'),
            (r'^Foreword\b(?:\s*:\s*([^\n]*))?$', 'Foreword'),
            (r'^FOREWORD\b(?:\s*:\s*([^\n]*))?$', 'Foreword'),
            (r'^Afterword\b(?:\s*:\s*([^\n]*))?$', 'Afterword'),
            (r'^AFTERWORD\b(?:\s*:\s*([^\n]*))?$', 'Afterword'),
            (r'^Preface\b(?:\s*:\s*([^\n]*))?$', 'Preface'),
            (r'^PREFACE\b(?:\s*:\s*([^\n]*))?$', 'Preface'),
        ]
        
        # Patterns for regular chapters  
        # Match "Chapter N" or "CHAPTER N" with optional title
        # Use [ \t] instead of \s to avoid matching newlines
        chapter_patterns = [
            r'^Chapter[ \t]+(\d+)(?:[ \t]*:[ \t]*([^\n]*))?$',
            r'^CHAPTER[ \t]+(\d+)(?:[ \t]*:[ \t]*([^\n]*))?$',
            r'^(\d+)\.[ \t]+([^\n]+)$',
        ]
        
        all_matches = []
        
        # Find special sections
        for pattern, section_type in special_patterns:
            matches = list(re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE))
            for match in matches:
                # Extract subtitle from capture group if present
                subtitle = match.group(1) if match.group(1) else ""
                subtitle = subtitle.strip() if subtitle else ""
                
                # Combine section type with subtitle
                if subtitle:
                    title = f"{section_type}: {subtitle}"
                else:
                    title = section_type
                
                all_matches.append({
                    'match': match,
                    'type': 'special',
                    'section_type': section_type,
                    'title': title,
                    'number': None
                })
        
        # Find regular chapters
        for pattern in chapter_patterns:
            matches = list(re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE))
            for match in matches:
                chapter_num = match.group(1)
                # Extract title from capture group if present, otherwise use default
                chapter_title = match.group(2) if len(match.groups()) > 1 and match.group(2) else None
                title = chapter_title.strip() if chapter_title and chapter_title.strip() else f"Chapter {chapter_num}"
                
                all_matches.append({
                    'match': match,
                    'type': 'chapter',
                    'section_type': 'Chapter',
                    'title': title,
                    'number': chapter_num
                })
        
        if not all_matches:
            return []
        
        # Sort by position in text
        all_matches.sort(key=lambda m: m['match'].start())
        
        chapters = []
        for i, item in enumerate(all_matches):
            match = item['match']
            start = match.start()
            end = all_matches[i + 1]['match'].start() if i + 1 < len(all_matches) else len(text)
            
            title = item['title']
            
            chapter_text = text[start:end].strip()
            
            # Remove heading from text
            chapter_text = re.sub(match.re.pattern, '', chapter_text, count=1, flags=re.MULTILINE | re.IGNORECASE)
            chapter_text = chapter_text.strip()
            
            word_count = len(chapter_text.split())
            
            if word_count >= self.MIN_CHAPTER_WORDS:
                chapters.append(Chapter(
                    number=len(chapters) + 1,
                    title=title,
                    text=chapter_text,
                    start_position=start,
                    end_position=end,
                    word_count=word_count
                ))
        
        return self._post_process_chapters(chapters)

    def _detect_page_breaks(self, text: str) -> List[Chapter]:
        """Detect chapters from page breaks.
        
        Args:
            text: Document text
            
        Returns:
            List of chapters based on form feed or divider patterns
        """
        # Split on form feed or triple-dash dividers
        parts = re.split(r'\f|^---+$', text, flags=re.MULTILINE)
        
        chapters = []
        position = 0
        for i, part in enumerate(parts):
            part = part.strip()
            if not part or len(part.split()) < self.MIN_CHAPTER_WORDS:
                position += len(part) + 1
                continue
            
            # Try to extract title from first line
            lines = part.split('\n', 1)
            first_line = lines[0].strip()
            
            # Check if first line looks like a title (short, capitalized)
            if len(first_line.split()) <= 10 and first_line[0].isupper():
                title = first_line
                chapter_text = lines[1].strip() if len(lines) > 1 else part
            else:
                title = f"Section {i + 1}"
                chapter_text = part
            
            word_count = len(chapter_text.split())
            
            chapters.append(Chapter(
                number=len(chapters) + 1,
                title=title,
                text=chapter_text,
                start_position=position,
                end_position=position + len(part),
                word_count=word_count
            ))
            
            position += len(part) + 1
        
        return self._post_process_chapters(chapters)

    def _apply_custom_patterns(self, text: str) -> List[Chapter]:
        """Apply custom regex patterns for chapter detection.
        
        Args:
            text: Document text
            
        Returns:
            List of chapters based on custom patterns
        """
        if not self.custom_patterns:
            return []
        
        all_matches = []
        for pattern in self.custom_patterns:
            try:
                matches = list(re.finditer(pattern, text, re.MULTILINE))
                all_matches.extend(matches)
            except re.error as e:
                print(f"Warning: Invalid regex pattern '{pattern}': {e}")
                continue
        
        if not all_matches:
            return []
        
        all_matches.sort(key=lambda m: m.start())
        
        chapters = []
        for i, match in enumerate(all_matches):
            start = match.start()
            end = all_matches[i + 1].start() if i + 1 < len(all_matches) else len(text)
            
            title = match.group(0).strip()
            chapter_text = text[start:end].strip()
            word_count = len(chapter_text.split())
            
            if word_count >= self.MIN_CHAPTER_WORDS:
                chapters.append(Chapter(
                    number=len(chapters) + 1,
                    title=title,
                    text=chapter_text,
                    start_position=start,
                    end_position=end,
                    word_count=word_count
                ))
        
        return self._post_process_chapters(chapters)

    def _create_fallback_chapters(self, text: str) -> List[Chapter]:
        """Create fallback chapters when no detection succeeds.
        
        Args:
            text: Document text
            
        Returns:
            Single chapter or split chapters if text too large
        """
        word_count = len(text.split())
        
        # If small enough, treat as single chapter
        if word_count <= self.MAX_CHAPTER_WORDS:
            return [Chapter(
                number=1,
                title="Full Book",
                text=text,
                start_position=0,
                end_position=len(text),
                word_count=word_count
            )]
        
        # Split large text at paragraph boundaries
        return self._split_at_paragraphs(text)

    def _split_at_paragraphs(self, text: str) -> List[Chapter]:
        """Split large text into chunks at paragraph boundaries.
        
        Enforces both word and character limits to ensure compatibility with TTS APIs.
        
        Args:
            text: Document text
            
        Returns:
            List of size-limited chapters
        """
        paragraphs = re.split(r'\n\s*\n', text)
        
        chapters = []
        current_text = []
        current_words = 0
        current_chars = 0
        
        for para in paragraphs:
            para_words = len(para.split())
            para_chars = len(para)
            
            # Check if adding this paragraph would exceed EITHER limit
            exceeds_word_limit = current_words + para_words > self.MAX_CHAPTER_WORDS
            exceeds_char_limit = current_chars + para_chars > self.MAX_CHAPTER_CHARS
            
            if (exceeds_word_limit or exceeds_char_limit) and current_text:
                # Save current chapter
                chapter_text = '\n\n'.join(current_text)
                chapters.append(Chapter(
                    number=len(chapters) + 1,
                    title=f"Part {len(chapters) + 1}",
                    text=chapter_text,
                    start_position=0,
                    end_position=0,
                    word_count=current_words
                ))
                current_text = []
                current_words = 0
                current_chars = 0
            
            current_text.append(para)
            current_words += para_words
            current_chars += para_chars
        
        # Save final chapter
        if current_text:
            chapter_text = '\n\n'.join(current_text)
            chapters.append(Chapter(
                number=len(chapters) + 1,
                title=f"Part {len(chapters) + 1}",
                text=chapter_text,
                start_position=0,
                end_position=0,
                word_count=current_words
            ))
        
        return chapters

    def _post_process_chapters(self, chapters: List[Chapter]) -> List[Chapter]:
        """Post-process chapters to handle edge cases.
        
        Args:
            chapters: Raw detected chapters
            
        Returns:
            Processed chapters
        """
        processed = []
        
        for chapter in chapters:
            # Skip empty chapters
            if chapter.word_count < self.MIN_CHAPTER_WORDS:
                print(f"Warning: Skipping short chapter '{chapter.title}' ({chapter.word_count} words)")
                continue
            
            # Split oversized chapters
            if chapter.word_count > self.MAX_CHAPTER_WORDS:
                print(f"Warning: Splitting large chapter '{chapter.title}' ({chapter.word_count} words)")
                sub_chapters = self._split_at_paragraphs(chapter.text)
                for i, sub_ch in enumerate(sub_chapters):
                    sub_ch.title = f"{chapter.title} - Part {i + 1}"
                    sub_ch.number = len(processed) + 1
                    processed.append(sub_ch)
            else:
                processed.append(chapter)
        
        # Renumber chapters
        for i, chapter in enumerate(processed):
            chapter.number = i + 1
        
        return processed
