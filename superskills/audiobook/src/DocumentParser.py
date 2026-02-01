"""
DocumentParser.py - Unified document text extraction for multiple formats.
"""
import re
from pathlib import Path
from typing import Literal, Optional

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    print("Warning: PyPDF2 not available - install with: pip install PyPDF2")

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("Warning: python-docx not available - install with: pip install python-docx")

try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False
    print("Warning: markdown not available - install with: pip install markdown")


DocumentFormat = Literal["pdf", "txt", "md", "docx"]


class DocumentParser:
    """Extract text from documents in multiple formats."""

    SUPPORTED_EXTENSIONS = {
        ".pdf": "pdf",
        ".txt": "txt",
        ".md": "md",
        ".markdown": "md",
        ".docx": "docx",
    }

    def __init__(self):
        """Initialize DocumentParser."""
        pass

    def get_format(self, file_path: str) -> DocumentFormat:
        """Detect document format from file extension.
        
        Args:
            file_path: Path to document file
            
        Returns:
            Document format identifier
            
        Raises:
            ValueError: If file extension not supported
        """
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext not in self.SUPPORTED_EXTENSIONS:
            supported = ", ".join(self.SUPPORTED_EXTENSIONS.keys())
            raise ValueError(
                f"Unsupported file format '{ext}'. Supported formats: {supported}"
            )
        
        return self.SUPPORTED_EXTENSIONS[ext]

    def parse_file(self, file_path: str, clean_text: bool = True) -> str:
        """Extract full text content from document.
        
        Args:
            file_path: Path to document file
            clean_text: Apply text cleaning (remove page numbers, headers, etc.)
            
        Returns:
            Extracted text content
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If format unsupported or parsing fails
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        format_type = self.get_format(file_path)
        
        parsers = {
            "pdf": self._parse_pdf,
            "txt": self._parse_text,
            "md": self._parse_markdown,
            "docx": self._parse_docx,
        }
        
        parser = parsers[format_type]
        text = parser(str(path))
        
        if not text or not text.strip():
            raise ValueError(f"No text extracted from {file_path}")
        
        # Apply text cleaning for PDFs (most common source of noise)
        if clean_text and format_type == "pdf":
            from .TextCleaner import TextCleaner
            cleaner = TextCleaner()
            text = cleaner.clean(text)
        
        return text

    def _parse_pdf(self, file_path: str) -> str:
        """Extract text from PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text
            
        Raises:
            ImportError: If PyPDF2 not installed
            ValueError: If PDF parsing fails
        """
        if not PYPDF2_AVAILABLE:
            raise ImportError(
                "PyPDF2 is required for PDF parsing. Install with: pip install PyPDF2"
            )
        
        try:
            text_parts = []
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            
            return "\n\n".join(text_parts)
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {e}")

    def _parse_docx(self, file_path: str) -> str:
        """Extract text from DOCX file.
        
        Args:
            file_path: Path to DOCX file
            
        Returns:
            Extracted text
            
        Raises:
            ImportError: If python-docx not installed
            ValueError: If DOCX parsing fails
        """
        if not DOCX_AVAILABLE:
            raise ImportError(
                "python-docx is required for DOCX parsing. Install with: pip install python-docx"
            )
        
        try:
            doc = docx.Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n\n".join(paragraphs)
        except Exception as e:
            raise ValueError(f"Failed to parse DOCX: {e}")

    def _parse_markdown(self, file_path: str) -> str:
        """Extract text from Markdown file.
        
        Args:
            file_path: Path to Markdown file
            
        Returns:
            Raw markdown text (preserving structure for chapter detection)
        """
        return self._parse_text(file_path)

    def _parse_text(self, file_path: str) -> str:
        """Extract text from plain text file.
        
        Args:
            file_path: Path to text file
            
        Returns:
            File contents
            
        Raises:
            ValueError: If encoding issues occur
        """
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        
        raise ValueError(
            f"Failed to decode file with encodings: {', '.join(encodings)}"
        )
