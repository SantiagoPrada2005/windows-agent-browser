import io
import logging

import httpx

from asistente_guiador.core.interfaces import STTProvider

logger = logging.getLogger(__name__)


class GroqWhisperSTTProvider(STTProvider):
    """
    Proveedor STT que utiliza la API de Whisper en Groq (o whisper local mediante interfaz).
    Conforme al PRD RF-02 y sección 7.2 (Groq Whisper como alternativa/fallback sin latencia).
    """

    def __init__(
        self,
        api_key: str,
        model: str = "whisper-large-v3-turbo",
        language: str = "es",
        timeout: float = 15.0,
    ):
        self.api_key = api_key
        self.model = model
        self.language = language
        self.timeout = timeout

    async def transcribe(self, audio_data: bytes) -> str:
        """Transcribe bytes de audio (WAV) a texto."""
        if not audio_data:
            return ""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        files = {
            "file": ("audio.wav", io.BytesIO(audio_data), "audio/wav"),
        }
        data = {
            "model": self.model,
            "language": self.language,
            "response_format": "json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    "https://api.groq.com/openai/v1/audio/transcriptions",
                    headers=headers,
                    files=files,
                    data=data,
                )
                resp.raise_for_status()
                res_json = resp.json()
                return str(res_json.get("text", "")).strip()
        except Exception as e:
            logger.error(f"Error en transcripción STT con Groq Whisper: {e}")
            return ""
