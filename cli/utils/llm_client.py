"""
Unified LLM client for intent parsing.
Supports multiple providers: Gemini, Anthropic, OpenAI
"""
import os
import time
from abc import ABC, abstractmethod
from typing import Optional

from anthropic import Anthropic, APIConnectionError, APIError, AuthenticationError, RateLimitError
from google import genai
from openai import APIError as OpenAIAPIError
from openai import OpenAI


class LLMProvider(ABC):
    """Base class for LLM providers"""

    @abstractmethod
    def call(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """Call the LLM and return response text"""
        pass

    @staticmethod
    def create(provider: str, api_key: Optional[str] = None, model: Optional[str] = None, **kwargs) -> 'LLMProvider':
        """Factory method to create appropriate provider"""
        provider = provider.lower()

        if provider == 'gemini':
            return GeminiProvider(api_key=api_key, model=model, **kwargs)
        elif provider == 'anthropic':
            return AnthropicProvider(api_key=api_key, model=model, **kwargs)
        elif provider == 'openai':
            return OpenAIProvider(api_key=api_key, model=model, **kwargs)
        else:
            raise ValueError(f"Unknown provider: {provider}. Supported: gemini, anthropic, openai")


class GeminiProvider(LLMProvider):
    """Google Gemini provider"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash-exp",
                 max_tokens: int = 2000, temperature: float = 0.3):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in environment.\n"
                "Please set it with:\n"
                "  export GEMINI_API_KEY=your_key_here\n"
                "Or add it to a .env file in your project root."
            )

        try:
            self.client = genai.Client(api_key=self.api_key)
            self.model_name = model
            self.max_tokens = max_tokens
            self.temperature = temperature
        except Exception as e:
            raise ValueError(f"Failed to initialize Gemini client: {e}")

    def call(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """Call Gemini API with retry logic"""
        max_retries = kwargs.get('max_retries', 3)

        # Combine system and user prompts for Gemini
        combined_prompt = f"{system_prompt}\n\n---\n\n{user_prompt}"

        # Build config
        config = {
            "max_output_tokens": kwargs.get('max_tokens', self.max_tokens),
            "temperature": kwargs.get('temperature', self.temperature),
        }

        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=combined_prompt,
                    config=config
                )

                return response.text

            except Exception as e:
                error_msg = str(e).lower()

                # Rate limiting
                if 'rate limit' in error_msg or 'quota' in error_msg:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        print(f"Rate limit reached. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise ValueError(
                            f"Rate limit exceeded: {e}\n"
                            "Please wait a few moments and try again."
                        )

                # Network errors
                elif 'connection' in error_msg or 'network' in error_msg:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        print(f"Network error. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise ValueError(
                            f"Network connection failed: {e}\n"
                            "Please check your internet connection and try again."
                        )

                # Authentication errors
                elif 'api key' in error_msg or 'authentication' in error_msg:
                    raise ValueError(
                        f"Authentication failed: {e}\n"
                        "Your API key may be invalid or expired.\n"
                        "Please check your GEMINI_API_KEY and try again."
                    )

                # Other errors
                else:
                    raise ValueError(f"Gemini API error: {e}")

        raise ValueError("Max retries exceeded")


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider"""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-haiku-20240307",
                 max_tokens: int = 2000, temperature: float = 0.3):
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

    def call(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """Call Anthropic API with retry logic"""
        max_retries = kwargs.get('max_retries', 3)
        model = kwargs.get('model', self.model)
        max_tokens = kwargs.get('max_tokens', self.max_tokens)
        temperature = kwargs.get('temperature', self.temperature)

        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model=model,
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
                        "Please wait a few moments and try again."
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
                        "Please check your internet connection and try again."
                    )

            except APIError as e:
                status_code = getattr(e, 'status_code', None)
                if status_code in [500, 502, 503, 504]:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        print(f"Server error. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                raise ValueError(f"API error: {e}")

            except Exception as e:
                raise ValueError(f"Unexpected error calling Anthropic API: {e}")

        raise ValueError("Max retries exceeded")


class OpenAIProvider(LLMProvider):
    """OpenAI provider"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini",
                 max_tokens: int = 2000, temperature: float = 0.3):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment.\n"
                "Please set it with:\n"
                "  export OPENAI_API_KEY=your_key_here\n"
                "Or add it to a .env file in your project root."
            )

        try:
            self.client = OpenAI(api_key=self.api_key)
        except Exception as e:
            raise ValueError(f"Failed to initialize OpenAI client: {e}")

        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def call(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """Call OpenAI API with retry logic"""
        max_retries = kwargs.get('max_retries', 3)
        model = kwargs.get('model', self.model)
        max_tokens = kwargs.get('max_tokens', self.max_tokens)
        temperature = kwargs.get('temperature', self.temperature)

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )

                return response.choices[0].message.content

            except OpenAIAPIError as e:
                error_msg = str(e).lower()

                if 'rate limit' in error_msg:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        print(f"Rate limit reached. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise ValueError(f"Rate limit exceeded: {e}")

                elif 'authentication' in error_msg or 'api key' in error_msg:
                    raise ValueError(
                        f"Authentication failed: {e}\n"
                        "Your API key may be invalid or expired."
                    )

                raise ValueError(f"OpenAI API error: {e}")

            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"Error occurred. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                raise ValueError(f"Unexpected error calling OpenAI API: {e}")

        raise ValueError("Max retries exceeded")
