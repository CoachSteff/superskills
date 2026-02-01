"""
Test suite for OutlookClient
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path


@pytest.fixture
def mock_credentials():
    """Mock credential loading."""
    with patch('superskills.outlook.src.AuthManager.load_credentials'):
        with patch('superskills.outlook.src.AuthManager.get_credential') as mock_get:
            mock_get.side_effect = lambda key, **kwargs: {
                'MICROSOFT_CLIENT_ID': 'test_client_id',
                'MICROSOFT_APPLICATION_ID': 'test_app_id',
                'MICROSOFT_CLIENT_SECRET': 'test_secret',
                'MICROSOFT_TENANT_ID': 'test_tenant',
                'MICROSOFT_REDIRECT_URI': 'http://localhost:8000'
            }.get(key, kwargs.get('default'))
            yield mock_get


@pytest.fixture
def mock_auth_manager(mock_credentials):
    """Mock AuthManager."""
    with patch('superskills.outlook.src.AuthManager.AuthManager') as mock_auth:
        instance = Mock()
        instance.get_access_token.return_value = 'test_token'
        mock_auth.return_value = instance
        yield instance


@pytest.fixture
def mock_requests():
    """Mock requests library."""
    with patch('superskills.outlook.src.OutlookClient.requests') as mock_req:
        response = Mock()
        response.status_code = 200
        response.json.return_value = {'value': []}
        response.content = b'{"value": []}'
        mock_req.request.return_value = response
        yield mock_req


class TestOutlookClient:
    """Test OutlookClient functionality."""
    
    def test_initialization(self, mock_credentials, mock_auth_manager):
        """Test OutlookClient initialization."""
        from superskills.outlook.src import OutlookClient
        
        client = OutlookClient()
        
        assert client is not None
        assert client.auth is not None
        assert client.config is not None
        assert client.parser is not None
    
    def test_read_inbox_all(self, mock_credentials, mock_auth_manager, mock_requests):
        """Test reading all inbox messages."""
        from superskills.outlook.src import OutlookClient
        
        mock_requests.request.return_value.json.return_value = {
            'value': [
                {
                    'id': 'msg1',
                    'subject': 'Test Email',
                    'from': {
                        'emailAddress': {
                            'name': 'John Doe',
                            'address': 'john@example.com'
                        }
                    },
                    'receivedDateTime': '2026-01-29T10:00:00Z',
                    'isRead': False,
                    'hasAttachments': False,
                    'body': {
                        'contentType': 'text',
                        'content': 'Test message content'
                    },
                    'bodyPreview': 'Test message'
                }
            ]
        }
        
        client = OutlookClient()
        messages = client.read_inbox(filter="all", limit=10)
        
        assert len(messages) == 1
        assert messages[0]['subject'] == 'Test Email'
        assert messages[0]['from'] == 'John Doe'
    
    def test_read_inbox_unread(self, mock_credentials, mock_auth_manager, mock_requests):
        """Test reading unread messages with filter."""
        from superskills.outlook.src import OutlookClient
        
        mock_requests.request.return_value.json.return_value = {'value': []}
        
        client = OutlookClient()
        client.read_inbox(filter="unread", limit=5)
        
        call_args = mock_requests.request.call_args
        assert 'params' in call_args.kwargs
        assert 'isRead eq false' in call_args.kwargs['params'].get('$filter', '')
    
    def test_categorize_inbox(self, mock_credentials, mock_auth_manager, mock_requests):
        """Test inbox categorization."""
        from superskills.outlook.src import OutlookClient
        
        mock_requests.request.return_value.json.return_value = {
            'value': [
                {
                    'id': 'msg1',
                    'subject': 'URGENT: Action Required',
                    'from': {
                        'emailAddress': {
                            'name': 'Boss',
                            'address': 'boss@company.com'
                        }
                    },
                    'receivedDateTime': '2026-01-29T10:00:00Z',
                    'isRead': False,
                    'hasAttachments': False,
                    'body': {
                        'contentType': 'text',
                        'content': 'Please respond ASAP'
                    },
                    'bodyPreview': 'Please respond'
                }
            ]
        }
        
        client = OutlookClient()
        results = client.categorize_inbox(limit=10)
        
        assert results['total_analyzed'] == 1
        assert results['urgent_count'] >= 0
        assert 'urgent' in results
        assert 'action_required' in results
    
    def test_draft_reply(self, mock_credentials, mock_auth_manager, mock_requests):
        """Test draft reply creation."""
        from superskills.outlook.src import OutlookClient
        
        mock_requests.request.return_value.json.return_value = {
            'id': 'draft123'
        }
        
        client = OutlookClient()
        result = client.draft_reply(
            message_id='msg123',
            content='Thanks for the email'
        )
        
        assert result['status'] == 'draft_created'
        assert 'id' in result
    
    def test_search_emails(self, mock_credentials, mock_auth_manager, mock_requests):
        """Test email search."""
        from superskills.outlook.src import OutlookClient
        
        mock_requests.request.return_value.json.return_value = {
            'value': [
                {
                    'id': 'msg1',
                    'subject': 'Project Alpha Update',
                    'from': {
                        'emailAddress': {
                            'name': 'Alice',
                            'address': 'alice@company.com'
                        }
                    },
                    'receivedDateTime': '2026-01-29T09:00:00Z',
                    'bodyPreview': 'Project update...'
                }
            ]
        }
        
        client = OutlookClient()
        results = client.search_emails('project alpha', limit=10)
        
        assert len(results) == 1
        assert 'Project Alpha' in results[0]['subject']


class TestEmailParser:
    """Test EmailParser functionality."""
    
    def test_parse_html_body(self):
        """Test HTML to text conversion."""
        from superskills.outlook.src.EmailParser import EmailParser
        
        parser = EmailParser()
        html = '<html><body><p>Hello <b>World</b></p></body></html>'
        text = parser.parse_html_body(html)
        
        assert 'Hello' in text
        assert 'World' in text
        assert '<' not in text
    
    def test_extract_preview(self):
        """Test preview extraction."""
        from superskills.outlook.src.EmailParser import EmailParser
        
        parser = EmailParser()
        long_text = 'This is a very long email message. ' * 20
        preview = parser.extract_preview(long_text, max_length=50)
        
        assert len(preview) <= 53
        assert preview.endswith('...')
    
    def test_detect_intent_question(self):
        """Test question intent detection."""
        from superskills.outlook.src.EmailParser import EmailParser
        
        parser = EmailParser()
        text = 'Can you help me with this project?'
        intent = parser.detect_intent(text)
        
        assert intent == 'question'
    
    def test_detect_intent_request(self):
        """Test request intent detection."""
        from superskills.outlook.src.EmailParser import EmailParser
        
        parser = EmailParser()
        text = 'Please review the attached document.'
        intent = parser.detect_intent(text)
        
        assert intent == 'request'
    
    def test_identify_action_items(self):
        """Test action item identification."""
        from superskills.outlook.src.EmailParser import EmailParser
        
        parser = EmailParser()
        text = 'Please review the document by Friday. Could you also confirm attendance?'
        actions = parser.identify_action_items(text)
        
        assert len(actions) > 0


class TestOutlookConfig:
    """Test OutlookConfig functionality."""
    
    def test_default_config(self):
        """Test default configuration values."""
        from superskills.outlook.src.OutlookConfig import OutlookConfig
        
        config = OutlookConfig()
        
        assert config.get_tone() in ['professional', 'casual', 'concise', 'friendly']
        assert len(config.get_signature()) > 0
        assert isinstance(config.get_urgent_keywords(), list)
    
    def test_urgent_detection(self):
        """Test urgent content detection."""
        from superskills.outlook.src.OutlookConfig import OutlookConfig
        
        config = OutlookConfig()
        
        assert config.is_urgent_content('This is URGENT')
        assert config.is_urgent_content('Please respond ASAP')
        assert not config.is_urgent_content('Just FYI')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
