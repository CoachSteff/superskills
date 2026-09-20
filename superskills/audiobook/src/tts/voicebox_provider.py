"""
Voicebox TTS provider implementation.

Voicebox is a local AI voice studio (Chatterbox Multilingual) running on this
machine. It replaced ElevenLabs on 20 September 2026: no cloud, no API key, no
per-character cost, and Steff's own cloned voice in both Dutch and English.

The server listens on http://127.0.0.1:17493 and is normally spawned by
/Applications/Voicebox.app. The development checkout at ~/Developer/voicebox
binds the same port under `just dev`, so only one of the two runs at a time.

This provider returns **MP3** bytes so the audiobook pipeline's one-MP3-per-chapter
contract still holds: Voicebox streams WAV, and ffmpeg transcodes it here.
"""
import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request
from typing import Iterator

from .base import TTSProvider, TTSConfig


def _language_of(extra: dict) -> str:
    """Resolve the two-letter code Chatterbox wants.

    Profiles carry both `language_code` ("nl") and a human `language` ("Dutch"),
    and _build_tts_config passes every profile key through, so accept either.
    """
    code = (extra.get("language_code") or extra.get("language") or "nl").strip().lower()
    return {"dutch": "nl", "nederlands": "nl", "flemish": "nl", "vlaams": "nl",
            "english": "en", "engels": "en"}.get(code, code)


DEFAULT_BASE_URL = "http://127.0.0.1:17493"

# Locked narration preset, signed off by Steff on 2026-09-08 for the Steff NL
# profile. Applies to both languages; only `language` changes. The defaults
# (cfg_weight ~0.5) clamp her melody flat, which is why cfg_weight sits low.
PRESET = {"exaggeration": 1.2, "cfg_weight": 0.3, "temperature": 0.95}


class VoiceboxError(RuntimeError):
    """Raised when the local Voicebox server cannot serve a request."""


class VoiceboxProvider(TTSProvider):
    """Local Voicebox (Chatterbox Multilingual) TTS provider."""

    # Chatterbox can rush and drop the tail of a very long line. The server
    # auto-chunks, but keeping requests modest makes a bad take cheap to re-roll.
    CHARACTER_LIMIT = 2000

    def __init__(self, api_key: str = "", base_url: str = None):
        """Initialize the provider.

        Args:
            api_key: Ignored. Voicebox is local and needs no credential. The
                parameter exists only to match the factory's signature.
            base_url: Override the server address (default 127.0.0.1:17493).
        """
        self.base_url = (base_url or os.getenv("VOICEBOX_URL") or DEFAULT_BASE_URL).rstrip("/")

    # ------------------------------------------------------------------ helpers

    def _get(self, path: str, timeout: int = 10):
        with urllib.request.urlopen(f"{self.base_url}{path}", timeout=timeout) as resp:
            return json.loads(resp.read().decode())

    def is_healthy(self) -> bool:
        try:
            return self._get("/health").get("status") == "healthy"
        except Exception:
            return False

    def list_profiles(self) -> list:
        """Voice profiles currently in Voicebox. Never hardcode-trust an ID."""
        data = self._get("/profiles")
        return data.get("profiles", data) if isinstance(data, dict) else data

    def _require_server(self):
        if self.is_healthy():
            return
        raise VoiceboxError(
            f"No healthy Voicebox server at {self.base_url}. Start it with "
            "`open -a Voicebox`, or `cd ~/Developer/voicebox && just dev` for the "
            "development build (they bind the same port, so run only one)."
        )

    @staticmethod
    def _wav_to_mp3(wav: bytes) -> bytes:
        """Transcode the streamed WAV to MP3.

        320 kbps is requested but LAME will cap it: Chatterbox streams 24 kHz mono,
        and MPEG-2 Layer III tops out at 160 kbps there. That is already well past
        transparent for this source, so the cap costs nothing audible. The narration
        profile's "MP3 320 kbps" gate assumes a 44.1 kHz master and does not apply.
        """
        if not shutil.which("ffmpeg"):
            raise VoiceboxError("ffmpeg is required to write MP3 chapters. `brew install ffmpeg`.")
        proc = subprocess.run(
            ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
             "-i", "pipe:0", "-codec:a", "libmp3lame", "-b:a", "320k", "-f", "mp3", "pipe:1"],
            input=wav, capture_output=True,
        )
        if proc.returncode != 0 or not proc.stdout:
            raise VoiceboxError(f"ffmpeg failed to transcode: {proc.stderr.decode()[:300]}")
        return proc.stdout

    # ---------------------------------------------------------------- interface

    def get_character_limit(self) -> int:
        return self.CHARACTER_LIMIT

    def validate_config(self, config: TTSConfig) -> None:
        if not config.voice_id:
            raise ValueError(
                "Voicebox needs a profile_id as voice_id. List them with "
                "`curl -s http://127.0.0.1:17493/profiles`; the profile set changes "
                "whenever Steff re-clones, so never hardcode-trust an ID."
            )
        extra = config.extra_settings or {}
        lang = _language_of(extra)
        if lang not in ("nl", "en"):
            raise ValueError(f"Voicebox language must be 'nl' or 'en', got '{lang}'.")
        if not (0.7 <= config.speed <= 1.2):
            raise ValueError(f"speed must be between 0.7 and 1.2, got {config.speed}.")

    def generate_speech(self, text: str, config: TTSConfig) -> Iterator[bytes]:
        """Generate one chapter of speech.

        Yields MP3 bytes in a single chunk. Voicebox streams a complete WAV
        rather than incremental audio, so there is nothing to stream through.
        """
        self.validate_config(config)
        self._require_server()

        extra = config.extra_settings or {}
        payload = {
            "profile_id": config.voice_id,
            "text": text,
            "language": _language_of(extra),
            # Always chatterbox. Turbo, qwen, luxtts and tada are not for narration,
            # and bracket tags like [laugh] are read aloud literally on this engine.
            "engine": "chatterbox",
            "exaggeration": extra.get("exaggeration", PRESET["exaggeration"]),
            "cfg_weight": extra.get("cfg_weight", PRESET["cfg_weight"]),
            "temperature": extra.get("temperature", PRESET["temperature"]),
        }
        if extra.get("seed") is not None:
            payload["seed"] = extra["seed"]

        req = urllib.request.Request(
            f"{self.base_url}/generate/stream",
            method="POST",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "Expect": ""},
        )
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                wav = resp.read()
        except urllib.error.HTTPError as e:
            raise VoiceboxError(
                f"Voicebox returned HTTP {e.code}: {e.read()[:300].decode(errors='replace')}"
            ) from e
        except urllib.error.URLError as e:
            raise VoiceboxError(f"Cannot reach Voicebox at {self.base_url}: {e.reason}") from e

        if len(wav) < 1024:
            raise VoiceboxError(
                f"Voicebox returned only {len(wav)} bytes — treat that as a failed take, "
                "not a short chapter. Re-roll with a different seed or lower temperature."
            )

        mp3 = self._wav_to_mp3(wav)

        # `speed` is applied by the pipeline's own post-processing if it needs to;
        # Chatterbox has no speed field, atempo is the only real pace control.
        yield mp3

    def check_quota(self, estimated_characters: int) -> dict:
        """Local and free, so quota is never the constraint."""
        return {
            "sufficient": True,
            "available": -1,
            "required": estimated_characters,
            "provider_supports_check": False,
        }
