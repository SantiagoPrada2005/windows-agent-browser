from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

from asistente_guiador.audio.stt import GroqWhisperSTTProvider
from asistente_guiador.audio.tts import PiperTTSProvider
from asistente_guiador.audio.wakeword import (
    WakeWordAudioListener,
    check_wake_word_match,
    normalize_text,
)


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


def test_wake_word_normalization_and_matching():
    assert normalize_text("¡Sofía!") == "sofia"
    assert normalize_text("¿Cómo estás?") == "como estas"

    # Verificación con Sofia (con y sin tildes, con prefijos y fonética)
    assert check_wake_word_match("¡Sofía!", "Sofia") is True
    assert check_wake_word_match("Oye Sofía, ¿me ayudas?", "Sofia") is True
    assert check_wake_word_match("Hola Sophia", "Sofia") is True
    assert check_wake_word_match("Hey asistente", "Sofia") is True
    assert check_wake_word_match("Buenos días a todos", "Sofia") is False


@pytest.mark.asyncio
async def test_wakeword_listener_pause_and_resume():
    mock_stt = AsyncMock()
    listener = WakeWordAudioListener(stt_provider=mock_stt, wake_word="Sofia")

    assert listener.is_listening() is True
    listener.pause()
    assert listener.is_listening() is False

    listener.resume()
    assert listener.is_listening() is True

    listener.stop()
    assert listener.is_listening() is False


@pytest.mark.asyncio
async def test_wakeword_detection_match():
    mock_stt = AsyncMock()
    mock_stt.transcribe.return_value = "Hola Sofía, por favor"
    listener = WakeWordAudioListener(stt_provider=mock_stt, wake_word="Sofia")

    with patch.object(listener, "_record_audio_window", return_value=b"fake_wav"):
        detected = await listener.wait_for_wake_word()

    assert detected is True


def test_wakeword_record_audio_with_input_stream():
    mock_stt = AsyncMock()
    listener = WakeWordAudioListener(
        stt_provider=mock_stt,
        wake_word="Sofia",
        sample_rate=16000,
        energy_threshold=0.01,
        window_seconds=1.0,
    )

    # Simular InputStream que devuelve 2 chunks con voz y luego silencios
    voice_chunk = np.ones((1600, 1), dtype=np.float32) * 0.05
    silence_chunk = np.zeros((1600, 1), dtype=np.float32)

    chunks = [voice_chunk, voice_chunk, silence_chunk, silence_chunk, silence_chunk, silence_chunk]
    chunk_iter = iter(chunks)

    mock_stream = MagicMock()
    mock_stream.__enter__.return_value = mock_stream
    mock_stream.__exit__.return_value = False
    mock_stream.read.side_effect = lambda n: (next(chunk_iter, silence_chunk), False)

    with patch("asistente_guiador.audio.wakeword.sd") as mock_sd:
        mock_sd.InputStream.return_value = mock_stream
        wav = listener._record_audio_window()

        assert wav is not None
        assert isinstance(wav, bytes)
        assert wav.startswith(b"RIFF")
