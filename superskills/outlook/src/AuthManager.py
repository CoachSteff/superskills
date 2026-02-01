"""
AuthManager - OAuth2 token handling for Microsoft Graph API
"""
import json
import logging
import os
from pathlib import Path
from typing import Optional, TYPE_CHECKING

try:
    import msal
    MSAL_AVAILABLE = True
except ImportError:
    MSAL_AVAILABLE = False
    if TYPE_CHECKING:
        import msal

from superskills.core.credentials import load_credentials, get_credential

logger = logging.getLogger(__name__)


class AuthManager:
    """Manage OAuth2 authentication for Microsoft Graph API using MSAL."""
    
    SCOPES = [
        "Mail.Read",
        "Mail.ReadWrite", 
        "Mail.Send",
        "User.Read"
    ]
    
    def __init__(self):
        """Initialize AuthManager with credentials."""
        if not MSAL_AVAILABLE:
            raise ImportError(
                "MSAL library not installed. Install with: pip install msal"
            )
        
        load_credentials(skill_name="outlook")
        
        client_id = get_credential("MICROSOFT_CLIENT_ID", required=False)
        if not client_id:
            client_id = get_credential("MICROSOFT_APPLICATION_ID", required=True)
        
        self.client_id = client_id
        self.client_secret = get_credential("MICROSOFT_CLIENT_SECRET", required=True)
        self.tenant_id = get_credential("MICROSOFT_TENANT_ID", required=True)
        self.redirect_uri = get_credential("MICROSOFT_REDIRECT_URI", default="http://localhost:8000")
        
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        
        self.token_cache_path = self._get_token_cache_path()
        self.token_cache = self._load_token_cache()
        
        self.app = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=self.authority,
            token_cache=self.token_cache
        )
        
        logger.info("AuthManager initialized")
    
    def _get_token_cache_path(self) -> Path:
        """Get path to token cache file."""
        cache_dir = Path.home() / ".superskills" / "tokens"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        cache_file = cache_dir / "outlook_token.bin"
        
        if cache_file.exists():
            os.chmod(cache_file, 0o600)
        
        return cache_file
    
    def _load_token_cache(self):
        """Load token cache from disk."""
        cache = msal.SerializableTokenCache()
        
        if self.token_cache_path.exists():
            try:
                with open(self.token_cache_path, 'r') as f:
                    cache.deserialize(f.read())
                logger.debug("Token cache loaded from disk")
            except Exception as e:
                logger.warning(f"Failed to load token cache: {e}")
        
        return cache
    
    def _save_token_cache(self):
        """Save token cache to disk."""
        if self.token_cache.has_state_changed:
            try:
                with open(self.token_cache_path, 'w') as f:
                    f.write(self.token_cache.serialize())
                
                os.chmod(self.token_cache_path, 0o600)
                logger.debug("Token cache saved to disk")
            except Exception as e:
                logger.warning(f"Failed to save token cache: {e}")
    
    def acquire_token(self) -> str:
        """
        Acquire access token using device code flow.
        
        Returns:
            Access token string
            
        Raises:
            ValueError: If token acquisition fails
        """
        accounts = self.app.get_accounts()
        
        if accounts:
            logger.debug("Found cached account, attempting silent token acquisition")
            result = self.app.acquire_token_silent(
                scopes=self.SCOPES,
                account=accounts[0]
            )
            
            if result and "access_token" in result:
                self._save_token_cache()
                logger.info("Token acquired silently from cache")
                return result["access_token"]
        
        logger.info("No cached token found, initiating device code flow")
        
        flow = self.app.initiate_device_flow(scopes=self.SCOPES)
        
        if "user_code" not in flow:
            raise ValueError(
                f"Failed to create device flow: {flow.get('error_description', 'Unknown error')}"
            )
        
        print("\n" + "="*60)
        print("Microsoft Authentication Required")
        print("="*60)
        print(f"\n{flow['message']}")
        print("\nWaiting for authentication...")
        print("="*60 + "\n")
        
        result = self.app.acquire_token_by_device_flow(flow)
        
        if "access_token" not in result:
            error_desc = result.get("error_description", "Unknown error")
            raise ValueError(f"Authentication failed: {error_desc}")
        
        self._save_token_cache()
        logger.info("Token acquired via device code flow")
        
        return result["access_token"]
    
    def get_access_token(self) -> str:
        """
        Get current access token (acquire if needed).
        
        Returns:
            Valid access token string
        """
        return self.acquire_token()
    
    def clear_cache(self):
        """Clear token cache (force re-authentication)."""
        if self.token_cache_path.exists():
            self.token_cache_path.unlink()
            logger.info("Token cache cleared")
        
        self.token_cache = msal.SerializableTokenCache()
