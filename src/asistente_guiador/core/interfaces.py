from abc import ABC, abstractmethod

from PIL import Image

from asistente_guiador.core.models import (
    GuidanceResponse,
    IntentResult,
    VisualElementResult,
)


class LLMProvider(ABC):
    """Puerto para el modelo de lenguaje de clasificación y respuesta."""

    @abstractmethod
    async def classify_intent(
        self,
        user_query: str,
        session_context: str | None = None,
    ) -> IntentResult:
        """Clasifica la petición del usuario en una intención estructurada."""
        pass

    @abstractmethod
    async def generate_response(
        self,
        intent: IntentResult,
        visual_result: VisualElementResult | None = None,
        session_context: str | None = None,
    ) -> GuidanceResponse:
        """Genera la respuesta verbal guiada en lenguaje cotidiano."""
        pass


class VisionProvider(ABC):
    """Puerto para modelos de visión multimodales (DeepSeek / OpenRouter)."""

    @abstractmethod
    async def analyze_screen(
        self,
        image: Image.Image,
        target_description: str,
        context: str | None = None,
    ) -> VisualElementResult:
        """Analiza la captura de pantalla para ubicar un elemento específico."""
        pass


class STTProvider(ABC):
    """Puerto para el reconocimiento de voz a texto."""

    @abstractmethod
    async def transcribe(self, audio_data: bytes) -> str:
        """Convierte fragmento de audio a texto en español."""
        pass


class TTSProvider(ABC):
    """Puerto para síntesis de voz a habla."""

    @abstractmethod
    async def speak(self, text: str) -> None:
        """Sintetiza y reproduce la frase al usuario."""
        pass


class ScreenCapturer(ABC):
    """Puerto para la captura rápida de pantalla."""

    @abstractmethod
    def capture_active_screen(self) -> Image.Image:
        """Obtiene una captura de la pantalla o ventana activa."""
        pass
