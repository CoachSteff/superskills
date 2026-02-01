"""
TextCleaner.py - Clean extracted document text for audiobook narration.
"""
import re
from typing import List, Optional


class TextCleaner:
    """Clean and normalize text extracted from PDFs for natural narration."""
    
    # Common page number patterns
    PAGE_NUMBER_PATTERNS = [
        r'^\d+\s*$',                    # Standalone page numbers: "42"
        r'^Page\s+\d+\s*$',             # "Page 42"
        r'^\d+\s*\|\s*.*$',             # "42 | Chapter Title"
        r'^.*\|\s*\d+\s*$',             # "Chapter Title | 42"
        r'^\d+\s+of\s+\d+\s*$',         # "42 of 200"
    ]
    
    # Common header/footer patterns
    HEADER_FOOTER_PATTERNS = [
        r'^Chapter\s+\d+\s*$',          # Repeated "Chapter X" headers
        r'^\d{4}-\d{2}-\d{2}',          # Date stamps
        r'^©.*\d{4}',                   # Copyright notices
        r'^All rights reserved',        # Rights statements
    ]
    
    def __init__(self, 
                 remove_page_numbers: bool = True,
                 remove_headers_footers: bool = True,
                 custom_patterns: Optional[List[str]] = None):
        """Initialize TextCleaner.
        
        Args:
            remove_page_numbers: Remove page number lines
            remove_headers_footers: Remove header/footer lines
            custom_patterns: Additional regex patterns to remove (line-level)
        """
        self.remove_page_numbers = remove_page_numbers
        self.remove_headers_footers = remove_headers_footers
        self.custom_patterns = custom_patterns or []
    
    def clean(self, text: str) -> str:
        """Clean text for narration.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text ready for narration
        """
        # Split into lines for line-level cleaning
        lines = text.split('\n')
        
        # Apply line-level filters
        if self.remove_page_numbers:
            lines = self._remove_page_numbers(lines)
        
        if self.remove_headers_footers:
            lines = self._remove_headers_footers(lines)
        
        if self.custom_patterns:
            lines = self._apply_custom_patterns(lines)
        
        # Rejoin
        cleaned = '\n'.join(lines)
        
        # Apply document-level cleaning
        cleaned = self._normalize_whitespace(cleaned)
        cleaned = self._fix_hyphenation(cleaned)
        cleaned = self._remove_repeated_lines(cleaned)
        
        return cleaned.strip()
    
    def _remove_page_numbers(self, lines: List[str]) -> List[str]:
        """Remove lines that are page numbers."""
        filtered = []
        for line in lines:
            stripped = line.strip()
            is_page_num = any(
                re.match(pattern, stripped, re.IGNORECASE) 
                for pattern in self.PAGE_NUMBER_PATTERNS
            )
            if not is_page_num:
                filtered.append(line)
        return filtered
    
    def _remove_headers_footers(self, lines: List[str]) -> List[str]:
        """Remove common header/footer patterns."""
        filtered = []
        for line in lines:
            stripped = line.strip()
            is_header_footer = any(
                re.match(pattern, stripped, re.IGNORECASE) 
                for pattern in self.HEADER_FOOTER_PATTERNS
            )
            if not is_header_footer:
                filtered.append(line)
        return filtered
    
    def _apply_custom_patterns(self, lines: List[str]) -> List[str]:
        """Apply user-defined removal patterns."""
        filtered = []
        for line in lines:
            stripped = line.strip()
            should_remove = any(
                re.match(pattern, stripped, re.IGNORECASE) 
                for pattern in self.custom_patterns
            )
            if not should_remove:
                filtered.append(line)
        return filtered
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize excessive whitespace."""
        # Replace multiple newlines with max 2
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Replace multiple spaces with single space
        text = re.sub(r' {2,}', ' ', text)
        
        # Remove trailing whitespace from lines
        lines = [line.rstrip() for line in text.split('\n')]
        
        return '\n'.join(lines)
    
    def _fix_hyphenation(self, text: str) -> str:
        """Fix word breaks at line endings.
        
        Example: "exam-\nple" → "example"
        """
        # Match word followed by hyphen at end of line
        text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)
        
        return text
    
    def _remove_repeated_lines(self, text: str) -> str:
        """Remove exact duplicate consecutive lines (e.g., repeated headers)."""
        lines = text.split('\n')
        deduplicated = []
        prev_line = None
        
        for line in lines:
            stripped = line.strip()
            # Skip if same as previous non-empty line
            if stripped and stripped == prev_line:
                continue
            deduplicated.append(line)
            if stripped:
                prev_line = stripped
        
        return '\n'.join(deduplicated)
