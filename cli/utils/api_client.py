"""
Anthropic API client wrapper.
"""
import os
import time
from typing import Optional
from anthropic import Anthropic, APIError, APIConnectionError, RateLimitError, AuthenticationError
from cli.utils.model_resolver import ModelResolver


class APIClient:
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-latest", 
                 max_tokens: int = 4000, temperature: float = 0.7):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found in environment.\n"
                "Please set it with:\n"
                "  export ANTHROPIC_API_KEY=your_key_here\n"
                "Or add it to a .env file in your project root."
            )
        
        try:
            self.client = Anthropic(api_key=self.api_key)
        except Exception as e:
            raise ValueError(f"Failed to initialize Anthropic client: {e}")
        
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._resolved_model: Optional[str] = None
    
    def call(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        model = kwargs.get('model', self.model)
        max_tokens = kwargs.get('max_tokens', self.max_tokens)
        temperature = kwargs.get('temperature', self.temperature)
        max_retries = kwargs.get('max_retries', 3)
        
        if self._resolved_model is None:
            self._resolved_model = ModelResolver.resolve(model, self.api_key)
        
        resolved_model = self._resolved_model
        
        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model=resolved_model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ]
                )
                
                return response.content[0].text
            
            except AuthenticationError as e:
                raise ValueError(
                    f"Authentication failed: {e}\n"
                    "Your API key may be invalid or expired.\n"
                    "Please check your ANTHROPIC_API_KEY and try again."
                )
            
            except RateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"Rate limit reached. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise ValueError(
                        f"Rate limit exceeded: {e}\n"
                        "You've made too many requests. Please wait a few moments and try again.\n"
                        "Consider upgrading your API plan if this happens frequently."
                    )
            
            except APIConnectionError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"Network error. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise ValueError(
                        f"Network connection failed: {e}\n"
                        "Please check your internet connection and try again.\n"
                        "If the problem persists, Anthropic's API may be experiencing issues."
                    )
            
            except APIError as e:
                status_code = getattr(e, 'status_code', None)
                if status_code == 400:
                    raise ValueError(
                        f"Invalid request: {e}\n"
                        "The request was malformed. This may be due to:\n"
                        "  - Invalid model name\n"
                        "  - Prompt too long for the model\n"
                        "  - Invalid parameters"
                    )
                elif status_code == 500:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        print(f"Server error. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise ValueError(
                            f"API server error: {e}\n"
                            "Anthropic's API is experiencing issues. Please try again later."
                        )
                else:
                    raise ValueError(f"API error: {e}")
            
            except Exception as e:
                raise ValueError(
                    f"Unexpected error calling Anthropic API: {e}\n"
                    "Please check your configuration and try again."
                )
        
        raise ValueError("Max retries exceeded")
