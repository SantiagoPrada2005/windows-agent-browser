from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from asistente_guiador.audio.stt import GroqWhisperSTTProvider
from asistente_guiador.audio.tts import PiperTTSProvider
from asistente_guiador.audio.wakeword import WakeWordAudioListener


@pytest.mark.asyncio
async def test_piper_tts_fallback_speak():
    provider = PiperTTSProvider(piper_path="nonexistent_piper_binary")
    with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
        mock_proc = AsyncMock()
        mock_proc.wait = AsyncMock()
        mock_exec.return_value = mock_proc

        await provider.speak("Hola, bienvenido al asistente.")
        assert mock_exec.called


@pytest.mark.asyncio
async def test_groq_whisper_transcription():
    stt = GroqWhisperSTTProvider(api_key="mock-key")
    dummy_wav = b"RIFF....WAVEfmt ...."

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"text": "¿Cómo guardo este archivo?"}
    mock_resp.raise_for_status.return_value = None

    with patch("httpx.AsyncClient.post", return_value=mock_resp):
        text = await stt.transcribe(dummy_wav)

    assert text == "¿Cómo guardo este archivo?"


@pytest.mark.asyncio
async def test_wakeword_listener_pause_and_resume():
    mock_stt = AsyncMock()
    listener = WakeWordAudioListener(stt_provider=mock_stt, wake_word="hey asistente")

    assert listener.is_listening() is True
    listener.pause()
    assert listener.is_listening() is False

    listener.resume()
    assert listener.is_listening() is True


@pytest.mark.asyncio
async def test_wakeword_detection_match():
    mock_stt = AsyncMock()
    mock_stt.transcribe.return_value = "Hola, hey asistente, por favor"
    listener = WakeWordAudioListener(stt_provider=mock_stt, wake_word="hey asistente")

    with patch.object(listener, "_record_audio_window", return_value=b"fake_wav"):
        detected = await listener.wait_for_wake_word()

    assert detected is True
