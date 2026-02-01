"""
OutlookConfig - Configuration and profile management
"""
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class OutlookConfig:
    """Manage Outlook skill configuration and user profile."""
    
    _instance = None
    
    def __new__(cls, config_path: Optional[str] = None):
        """Singleton pattern for config management."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration."""
        if self._initialized:
            return
        
        self.config_path = config_path
        self.profile_data = {}
        
        self._load_profile()
        self._initialized = True
        
        logger.info("OutlookConfig initialized")
    
    def _get_profile_path(self) -> Path:
        """Get path to PROFILE.md file."""
        if self.config_path:
            return Path(self.config_path)
        
        skill_dir = Path(__file__).parent.parent
        profile_path = skill_dir / "PROFILE.md"
        
        if not profile_path.exists():
            profile_template = skill_dir / "PROFILE.md.template"
            if profile_template.exists():
                logger.info("Using PROFILE.md.template (PROFILE.md not found)")
                return profile_template
        
        return profile_path
    
    def _load_profile(self):
        """Load user profile from PROFILE.md."""
        profile_path = self._get_profile_path()
        
        if not profile_path.exists():
            logger.warning(f"Profile not found at {profile_path}, using defaults")
            self._set_defaults()
            return
        
        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.profile_data = self._parse_profile(content)
            logger.debug(f"Profile loaded from {profile_path}")
        except Exception as e:
            logger.error(f"Failed to load profile: {e}")
            self._set_defaults()
    
    def _parse_profile(self, content: str) -> Dict:
        """Parse PROFILE.md content."""
        data = {}
        
        tone_match = re.search(r'\*\*Tone\*\*:\s*(\w+)', content)
        if tone_match:
            data['tone'] = tone_match.group(1).lower()
        
        signature_match = re.search(r'\*\*Signature\*\*:\s*```(.*?)```', content, re.DOTALL)
        if signature_match:
            data['signature'] = signature_match.group(1).strip()
        
        flag_match = re.search(r'Flag emails from:\s*`([^`]+)`', content)
        if flag_match:
            emails = [e.strip() for e in flag_match.group(1).split(',')]
            data['flag_emails_from'] = emails
        
        urgent_match = re.search(r'Urgent keywords:\s*`([^`]+)`', content)
        if urgent_match:
            keywords = [k.strip() for k in urgent_match.group(1).split(',')]
            data['urgent_keywords'] = keywords
        
        greeting_match = re.search(r'\*\*Default Greeting\*\*:\s*(.+)', content)
        if greeting_match:
            data['default_greeting'] = greeting_match.group(1).strip()
        
        closing_match = re.search(r'\*\*Default Closing\*\*:\s*(.+)', content)
        if closing_match:
            data['default_closing'] = closing_match.group(1).strip()
        
        return data
    
    def _set_defaults(self):
        """Set default configuration values."""
        self.profile_data = {
            'tone': 'professional',
            'signature': 'Best regards,\n[Your Name]',
            'flag_emails_from': [],
            'urgent_keywords': ['urgent', 'asap', 'deadline', 'critical'],
            'default_greeting': 'Hi [FirstName],',
            'default_closing': 'Best regards,'
        }
    
    def get_tone(self) -> str:
        """Get communication tone preference."""
        return self.profile_data.get('tone', 'professional')
    
    def get_signature(self) -> str:
        """Get email signature."""
        return self.profile_data.get('signature', 'Best regards,\n[Your Name]')
    
    def get_urgent_keywords(self) -> List[str]:
        """Get list of urgent keywords."""
        return self.profile_data.get('urgent_keywords', [])
    
    def get_flag_emails_from(self) -> List[str]:
        """Get list of email addresses to flag."""
        return self.profile_data.get('flag_emails_from', [])
    
    def get_default_greeting(self) -> str:
        """Get default email greeting."""
        return self.profile_data.get('default_greeting', 'Hi [FirstName],')
    
    def get_default_closing(self) -> str:
        """Get default email closing."""
        return self.profile_data.get('default_closing', 'Best regards,')
    
    def should_flag_sender(self, sender_email: str) -> bool:
        """Check if email from sender should be flagged."""
        flag_list = self.get_flag_emails_from()
        return any(
            sender_email.lower() == flagged.lower() or 
            sender_email.lower().endswith(f"@{flagged.lower().lstrip('@')}")
            for flagged in flag_list
        )
    
    def is_urgent_content(self, text: str) -> bool:
        """Check if text contains urgent keywords."""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.get_urgent_keywords())
