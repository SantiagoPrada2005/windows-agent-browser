import json
from unittest.mock import MagicMock, patch

import httpx
import pytest
from PIL import Image

from asistente_guiador.ai.providers.groq_provider import GroqLLMProvider
from asistente_guiador.ai.providers.vision_provider import OpenRouterVisionProvider
from asistente_guiador.core.models import IntentType


@pytest.mark.asyncio
async def test_groq_classify_intent_success():
    provider = GroqLLMProvider(api_key="mock-key")

    mock_response_json = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "intent": "locate_element",
                            "target": "Guardar",
                            "requires_visual_context": True,
                            "response_style": "short_guidance",
                            "confidence": 0.98,
                        }
                    )
                }
            }
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_response_json
    mock_resp.raise_for_status.return_value = None

    with patch("httpx.AsyncClient.post", return_value=mock_resp):
        res = await provider.classify_intent("¿Dónde guardo este documento?")

    assert res.intent == IntentType.LOCATE_ELEMENT
    assert res.target == "Guardar"
    assert res.requires_visual_context is True
    assert res.confidence == 0.98


@pytest.mark.asyncio
async def test_groq_classify_intent_network_failure():
    provider = GroqLLMProvider(api_key="mock-key")

    with patch("httpx.AsyncClient.post", side_effect=httpx.ConnectError("Connection refused")):
        res = await provider.classify_intent("¿Dónde guardo este documento?")

    assert res.intent == IntentType.UNKNOWN
    assert res.confidence == 0.0


@pytest.mark.asyncio
async def test_vision_provider_success():
    provider = OpenRouterVisionProvider(api_key="mock-key")
    img = Image.new("RGB", (640, 480), color=(200, 200, 200))

    mock_response_json = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "found": True,
                            "application": "Word",
                            "confidence": 0.95,
                            "bbox": {"x": 0.05, "y": 0.02, "width": 0.04, "height": 0.04},
                            "spatial_description": "arriba a la izquierda, icono de disquete",
                            "reason": "icono de disquete visible",
                        }
                    )
                }
            }
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_response_json
    mock_resp.raise_for_status.return_value = None

    with patch("httpx.AsyncClient.post", return_value=mock_resp):
        result = await provider.analyze_screen(img, target_description="Guardar")

    assert result.found is True
    assert result.application == "Word"
    assert result.bbox is not None
    assert result.bbox.x == 0.05
    assert "disquete" in result.spatial_description


@pytest.mark.asyncio
async def test_vision_summarize_screen_success():
    provider = OpenRouterVisionProvider(api_key="mock-key")
    img = Image.new("RGB", (640, 480), color=(100, 150, 200))

    mock_response_json = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "application": "Microsoft Word",
                            "summary": "Documento en blanco de Word con cursor en el inicio.",
                        }
                    )
                }
            }
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_response_json
    mock_resp.raise_for_status.return_value = None

    with patch("httpx.AsyncClient.post", return_value=mock_resp):
        summary = await provider.summarize_screen(img, active_window="Documento 1 - Word")

    assert "Documento en blanco" in summary


@pytest.mark.asyncio
async def test_groq_classify_with_screen_state():
    from asistente_guiador.core.models import GlobalScreenState

    provider = GroqLLMProvider(api_key="mock-key")
    state = GlobalScreenState(
        active_window_title="Guardar como",
        active_application="Word",
        screen_summary="Diálogo de guardar archivo con botón Guardar resaltado.",
    )

    mock_response_json = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "intent": "locate_element",
                            "target": "Guardar",
                            "requires_visual_context": True,
                            "response_style": "short_guidance",
                            "confidence": 0.99,
                        }
                    )
                }
            }
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_response_json
    mock_resp.raise_for_status.return_value = None

    with patch("httpx.AsyncClient.post", return_value=mock_resp) as mock_post:
        res = await provider.classify_intent("¿Dónde le doy?", screen_state=state)

    assert res.intent == IntentType.LOCATE_ELEMENT
    assert res.target == "Guardar"
    # Verificar que el mensaje enviado incluía el contexto de pantalla
    sent_payload = mock_post.call_args[1]["json"]
    system_messages = [m["content"] for m in sent_payload["messages"] if m["role"] == "system"]
    assert any("Guardar como" in msg for msg in system_messages)
