from unittest.mock import AsyncMock

import pytest
from PIL import Image

from asistente_guiador.core.coordinator import AssistanceCoordinator
from asistente_guiador.core.interfaces import (
    LLMProvider,
    ScreenCapturer,
    TTSProvider,
    VisionProvider,
)
from asistente_guiador.core.models import (
    BoundingBox,
    GuidanceResponse,
    IntentResult,
    IntentType,
    VisualElementResult,
)


class DummyCapturer(ScreenCapturer):
    def __init__(self, color=(255, 255, 255)):
        self.color = color

    def capture_active_screen(self) -> Image.Image:
        return Image.new("RGB", (800, 600), color=self.color)


@pytest.mark.asyncio
async def test_coordinator_locate_element_flow():
    # Mocks
    mock_llm = AsyncMock(spec=LLMProvider)
    mock_vision = AsyncMock(spec=VisionProvider)
    mock_tts = AsyncMock(spec=TTSProvider)
    capturer = DummyCapturer()

    mock_llm.classify_intent.return_value = IntentResult(
        intent=IntentType.LOCATE_ELEMENT,
        target="Guardar",
        requires_visual_context=True,
    )
    mock_vision.analyze_screen.return_value = VisualElementResult(
        found=True,
        application="Word",
        target="Guardar",
        bbox=BoundingBox(x=0.1, y=0.1, width=0.05, height=0.05),
        spatial_description="Arriba a la izquierda",
    )
    mock_llm.generate_response.return_value = GuidanceResponse(
        spoken_text="El botón Guardar está arriba a la izquierda con forma de disquete.",
        visual_highlight=BoundingBox(x=0.1, y=0.1, width=0.05, height=0.05),
        spatial_description="Arriba a la izquierda",
    )

    coordinator = AssistanceCoordinator(
        llm_provider=mock_llm,
        vision_provider=mock_vision,
        screen_capturer=capturer,
        tts_provider=mock_tts,
    )

    response = await coordinator.handle_user_request("¿Dónde guardo este documento?")

    assert "disquete" in response.spoken_text
    assert response.visual_highlight is not None
    mock_vision.analyze_screen.assert_awaited_once()
    mock_tts.speak.assert_awaited_once()


@pytest.mark.asyncio
async def test_coordinator_repeat_instruction():
    mock_llm = AsyncMock(spec=LLMProvider)
    mock_vision = AsyncMock(spec=VisionProvider)
    mock_tts = AsyncMock(spec=TTSProvider)
    capturer = DummyCapturer()

    coordinator = AssistanceCoordinator(
        llm_provider=mock_llm,
        vision_provider=mock_vision,
        screen_capturer=capturer,
        tts_provider=mock_tts,
    )

    # Simular una respuesta previa en sesión
    coordinator.session.last_guidance = GuidanceResponse(spoken_text="Haz clic en Insertar")

    response = await coordinator.handle_user_request("Repíteme el paso")

    assert response.spoken_text == "Haz clic en Insertar"
    # No debe llamar al LLM clasificador para repetición inmediata
    mock_llm.classify_intent.assert_not_awaited()
    mock_tts.speak.assert_awaited_once_with("Haz clic en Insertar")
