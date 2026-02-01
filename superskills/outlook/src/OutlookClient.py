"""
OutlookClient - Main orchestrator for Microsoft Graph API operations
"""
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from .AuthManager import AuthManager
from .OutlookConfig import OutlookConfig
from .EmailParser import EmailParser

logger = logging.getLogger(__name__)


class OutlookClient:
    """Main client for Outlook email management via Microsoft Graph API."""
    
    GRAPH_ENDPOINT = "https://graph.microsoft.com/v1.0"
    MAX_RETRIES = 3
    RETRY_DELAY = 2
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize OutlookClient.
        
        Args:
            config_path: Optional path to custom PROFILE.md
            
        Raises:
            ImportError: If required dependencies not installed
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError(
                "requests library not installed. Install with: pip install requests"
            )
        
        self.auth = AuthManager()
        self.config = OutlookConfig(config_path)
        self.parser = EmailParser()
        
        logger.info("OutlookClient initialized")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with authorization token."""
        token = self.auth.get_access_token()
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        """
        Make HTTP request to Graph API with retry logic.
        
        Args:
            method: HTTP method (GET, POST, PATCH, etc.)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            
        Returns:
            Response JSON data
            
        Raises:
            Exception: If request fails after retries
        """
        url = f"{self.GRAPH_ENDPOINT}{endpoint}"
        
        for attempt in range(self.MAX_RETRIES):
            try:
                headers = self._get_headers()
                
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params,
                    timeout=30
                )
                
                if response.status_code == 401:
                    logger.warning("Token expired, refreshing...")
                    self.auth.clear_cache()
                    headers = self._get_headers()
                    
                    response = requests.request(
                        method=method,
                        url=url,
                        headers=headers,
                        json=data,
                        params=params,
                        timeout=30
                    )
                
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', self.RETRY_DELAY))
                    logger.warning(f"Rate limited, retrying after {retry_after}s")
                    time.sleep(retry_after)
                    continue
                
                response.raise_for_status()
                
                if response.content:
                    return response.json()
                return {}
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed (attempt {attempt + 1}/{self.MAX_RETRIES}): {e}")
                
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY * (attempt + 1))
                else:
                    raise
        
        raise Exception("Request failed after all retries")
    
    def read_inbox(
        self,
        filter: str = "all",
        limit: int = 10,
        folder: str = "inbox"
    ) -> List[Dict]:
        """
        Read inbox messages with optional filter.
        
        Args:
            filter: Filter type ('all', 'unread', 'flagged')
            limit: Maximum number of messages to return
            folder: Folder name (default: 'inbox')
            
        Returns:
            List of message dictionaries
        """
        logger.info(f"Reading {folder} with filter='{filter}', limit={limit}")
        
        params = {
            '$top': limit,
            '$orderby': 'receivedDateTime DESC',
            '$select': 'id,subject,from,receivedDateTime,isRead,hasAttachments,body,bodyPreview'
        }
        
        if filter == "unread":
            params['$filter'] = 'isRead eq false'
        elif filter == "flagged":
            params['$filter'] = 'flag/flagStatus eq \'flagged\''
        
        endpoint = "/me/mailFolders/inbox/messages"
        
        response = self._make_request('GET', endpoint, params=params)
        
        messages = response.get('value', [])
        
        parsed_messages = []
        for msg in messages:
            body_content = msg.get('body', {}).get('content', '')
            body_type = msg.get('body', {}).get('contentType', 'text')
            
            if body_type == 'html':
                text_body = self.parser.parse_html_body(body_content)
            else:
                text_body = body_content
            
            preview = self.parser.extract_preview(text_body)
            sender_name = self.parser.extract_sender_name(msg.get('from'))
            sender_email = self.parser.extract_sender_email(msg.get('from'))
            
            parsed_messages.append({
                'id': msg.get('id'),
                'subject': msg.get('subject', '(No Subject)'),
                'from': sender_name,
                'from_email': sender_email,
                'received': msg.get('receivedDateTime'),
                'is_read': msg.get('isRead', False),
                'has_attachments': msg.get('hasAttachments', False),
                'preview': preview,
                'body': text_body
            })
        
        logger.info(f"Retrieved {len(parsed_messages)} messages")
        return parsed_messages
    
    def categorize_inbox(self, limit: int = 50) -> Dict:
        """
        Analyze and categorize inbox messages.
        
        Args:
            limit: Maximum number of messages to analyze
            
        Returns:
            Dictionary with categorization results
        """
        logger.info(f"Categorizing inbox (limit={limit})")
        
        messages = self.read_inbox(filter="all", limit=limit)
        
        urgent = []
        action_required = []
        fyi = []
        newsletters = []
        
        for msg in messages:
            text = f"{msg['subject']} {msg['body']}"
            sender_email = msg['from_email']
            
            is_urgent = self.config.is_urgent_content(text)
            should_flag = self.config.should_flag_sender(sender_email)
            intent = self.parser.detect_intent(msg['body'])
            
            if is_urgent or should_flag:
                urgent.append(msg)
            elif intent in ['question', 'request']:
                action_required.append(msg)
            elif 'unsubscribe' in msg['body'].lower() or 'newsletter' in msg['subject'].lower():
                newsletters.append(msg)
            else:
                fyi.append(msg)
        
        results = {
            'total_analyzed': len(messages),
            'urgent': urgent,
            'urgent_count': len(urgent),
            'action_required': action_required,
            'action_count': len(action_required),
            'fyi': fyi,
            'fyi_count': len(fyi),
            'newsletters': newsletters,
            'newsletter_count': len(newsletters)
        }
        
        logger.info(
            f"Categorization complete: {results['urgent_count']} urgent, "
            f"{results['action_count']} action required, "
            f"{results['fyi_count']} FYI, {results['newsletter_count']} newsletters"
        )
        
        return results
    
    def draft_reply(
        self,
        message_id: str,
        content: str,
        tone: Optional[str] = None
    ) -> Dict:
        """
        Create draft reply with user profile settings.
        
        Args:
            message_id: ID of message to reply to
            content: Reply body content
            tone: Optional tone override
            
        Returns:
            Draft message data
        """
        logger.info(f"Creating draft reply to message {message_id[:20]}...")
        
        endpoint = f"/me/messages/{message_id}/createReply"
        
        reply_data = self._make_request('POST', endpoint)
        
        draft_id = reply_data.get('id')
        
        if not tone:
            tone = self.config.get_tone()
        
        signature = self.config.get_signature()
        full_content = f"{content}\n\n{signature}"
        
        update_endpoint = f"/me/messages/{draft_id}"
        update_data = {
            'body': {
                'contentType': 'Text',
                'content': full_content
            }
        }
        
        self._make_request('PATCH', update_endpoint, data=update_data)
        
        logger.info(f"Draft reply created: {draft_id[:20]}...")
        
        return {
            'id': draft_id,
            'status': 'draft_created',
            'message': 'Draft saved to Drafts folder. Review before sending.'
        }
    
    def send_draft(self, draft_id: str) -> Dict:
        """
        Send an existing draft (requires explicit confirmation).
        
        Args:
            draft_id: ID of draft message to send
            
        Returns:
            Send status
        """
        logger.info(f"Sending draft {draft_id[:20]}...")
        
        endpoint = f"/me/messages/{draft_id}/send"
        
        self._make_request('POST', endpoint)
        
        logger.info("Draft sent successfully")
        
        return {
            'status': 'sent',
            'draft_id': draft_id,
            'message': 'Email sent successfully'
        }
    
    def search_emails(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Search mailbox with Graph API query syntax.
        
        Args:
            query: Search query string
            limit: Maximum results
            
        Returns:
            List of matching messages
        """
        logger.info(f"Searching emails: '{query}' (limit={limit})")
        
        params = {
            '$search': f'"{query}"',
            '$top': limit,
            '$orderby': 'receivedDateTime DESC',
            '$select': 'id,subject,from,receivedDateTime,bodyPreview'
        }
        
        endpoint = "/me/messages"
        
        response = self._make_request('GET', endpoint, params=params)
        
        messages = response.get('value', [])
        
        results = []
        for msg in messages:
            results.append({
                'id': msg.get('id'),
                'subject': msg.get('subject', '(No Subject)'),
                'from': self.parser.extract_sender_name(msg.get('from')),
                'received': msg.get('receivedDateTime'),
                'preview': msg.get('bodyPreview', '')
            })
        
        logger.info(f"Found {len(results)} matching messages")
        return results
    
    def get_message_details(self, message_id: str) -> Dict:
        """
        Get detailed information about a specific message.
        
        Args:
            message_id: Message ID
            
        Returns:
            Detailed message data
        """
        logger.info(f"Fetching message details: {message_id[:20]}...")
        
        endpoint = f"/me/messages/{message_id}"
        params = {
            '$select': 'id,subject,from,to,receivedDateTime,body,hasAttachments,attachments'
        }
        
        msg = self._make_request('GET', endpoint, params=params)
        
        body_content = msg.get('body', {}).get('content', '')
        body_type = msg.get('body', {}).get('contentType', 'text')
        
        if body_type == 'html':
            text_body = self.parser.parse_html_body(body_content)
        else:
            text_body = body_content
        
        attachments = msg.get('attachments', [])
        attachment_metadata = self.parser.extract_attachments_metadata(attachments)
        
        return {
            'id': msg.get('id'),
            'subject': msg.get('subject'),
            'from': self.parser.extract_sender_name(msg.get('from')),
            'from_email': self.parser.extract_sender_email(msg.get('from')),
            'to': [r.get('emailAddress', {}).get('address') for r in msg.get('to', [])],
            'received': msg.get('receivedDateTime'),
            'body': text_body,
            'has_attachments': msg.get('hasAttachments', False),
            'attachments': attachment_metadata,
            'intent': self.parser.detect_intent(text_body),
            'action_items': self.parser.identify_action_items(text_body)
        }
