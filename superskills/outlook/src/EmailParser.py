"""
EmailParser - Parse email bodies and extract metadata
"""
import logging
import re
from typing import Dict, List, Optional

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

logger = logging.getLogger(__name__)


class EmailParser:
    """Parse and analyze email content."""
    
    ACTION_KEYWORDS = [
        'please', 'could you', 'can you', 'would you', 'need you to',
        'action required', 'todo', 'to-do', 'deadline', 'due date',
        'respond', 'reply', 'get back to', 'let me know', 'confirm'
    ]
    
    QUESTION_PATTERNS = [
        r'\?',
        r'\bwhat\b.*\?',
        r'\bwhen\b.*\?',
        r'\bwhere\b.*\?',
        r'\bwho\b.*\?',
        r'\bhow\b.*\?',
        r'\bwhy\b.*\?'
    ]
    
    def __init__(self):
        """Initialize EmailParser."""
        if not BS4_AVAILABLE:
            logger.warning(
                "BeautifulSoup4 not installed. HTML parsing will be limited. "
                "Install with: pip install beautifulsoup4"
            )
    
    def parse_html_body(self, html_content: str) -> str:
        """
        Convert HTML email body to plain text.
        
        Args:
            html_content: HTML email body
            
        Returns:
            Plain text content
        """
        if not html_content:
            return ""
        
        if not BS4_AVAILABLE:
            return self._simple_html_strip(html_content)
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text(separator='\n', strip=True)
            
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            text = '\n'.join(lines)
            
            return text
        except Exception as e:
            logger.error(f"Failed to parse HTML: {e}")
            return self._simple_html_strip(html_content)
    
    def _simple_html_strip(self, html_content: str) -> str:
        """Simple HTML tag removal (fallback)."""
        text = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL)
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'&nbsp;', ' ', text)
        text = re.sub(r'&[a-z]+;', '', text)
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)
    
    def extract_preview(self, text: str, max_length: int = 100) -> str:
        """
        Extract preview text from email body.
        
        Args:
            text: Email body text
            max_length: Maximum preview length
            
        Returns:
            Preview text
        """
        if not text:
            return ""
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        preview = ' '.join(lines)
        
        if len(preview) <= max_length:
            return preview
        
        return preview[:max_length].rsplit(' ', 1)[0] + "..."
    
    def extract_attachments_metadata(self, attachments_data: List[Dict]) -> List[Dict]:
        """
        Extract attachment metadata.
        
        Args:
            attachments_data: Raw attachment data from Graph API
            
        Returns:
            List of attachment metadata dicts
        """
        metadata = []
        
        for attachment in attachments_data:
            metadata.append({
                'name': attachment.get('name', 'Unknown'),
                'size': attachment.get('size', 0),
                'content_type': attachment.get('contentType', 'application/octet-stream'),
                'is_inline': attachment.get('isInline', False)
            })
        
        return metadata
    
    def detect_intent(self, text: str) -> str:
        """
        Detect email intent (question, request, info, etc.).
        
        Args:
            text: Email body text
            
        Returns:
            Intent string: 'question', 'request', 'info'
        """
        if not text:
            return 'info'
        
        text_lower = text.lower()
        
        for pattern in self.QUESTION_PATTERNS:
            if re.search(pattern, text_lower):
                return 'question'
        
        for keyword in self.ACTION_KEYWORDS:
            if keyword in text_lower:
                return 'request'
        
        return 'info'
    
    def identify_action_items(self, text: str) -> List[str]:
        """
        Identify action items in email text.
        
        Args:
            text: Email body text
            
        Returns:
            List of identified action items
        """
        if not text:
            return []
        
        action_items = []
        text_lower = text.lower()
        
        for keyword in self.ACTION_KEYWORDS:
            if keyword in text_lower:
                start_idx = text_lower.find(keyword)
                
                snippet_start = max(0, start_idx - 20)
                snippet_end = min(len(text), start_idx + 100)
                
                snippet = text[snippet_start:snippet_end].strip()
                
                if snippet and snippet not in action_items:
                    action_items.append(snippet)
        
        return action_items[:5]
    
    def summarize_thread(self, messages: List[Dict], max_messages: int = 3) -> str:
        """
        Summarize email thread (keep most recent messages).
        
        Args:
            messages: List of message dicts with 'from', 'date', 'body'
            max_messages: Maximum messages to include
            
        Returns:
            Thread summary text
        """
        if not messages:
            return ""
        
        sorted_messages = sorted(
            messages,
            key=lambda m: m.get('date', ''),
            reverse=True
        )
        
        recent_messages = sorted_messages[:max_messages]
        
        summary_parts = []
        for msg in reversed(recent_messages):
            sender = msg.get('from', 'Unknown')
            body = msg.get('body', '')
            preview = self.extract_preview(body, max_length=150)
            
            summary_parts.append(f"From {sender}: {preview}")
        
        return '\n\n'.join(summary_parts)
    
    def extract_sender_name(self, from_field: Dict) -> str:
        """
        Extract sender name from 'from' field.
        
        Args:
            from_field: Graph API 'from' object
            
        Returns:
            Sender name or email
        """
        if not from_field:
            return "Unknown"
        
        email_address = from_field.get('emailAddress', {})
        name = email_address.get('name')
        address = email_address.get('address')
        
        return name or address or "Unknown"
    
    def extract_sender_email(self, from_field: Dict) -> str:
        """
        Extract sender email address.
        
        Args:
            from_field: Graph API 'from' object
            
        Returns:
            Email address
        """
        if not from_field:
            return ""
        
        email_address = from_field.get('emailAddress', {})
        return email_address.get('address', '')
