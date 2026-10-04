import asyncio
import collections
import io
import logging
import re
import unicodedata
import wave

import numpy as np

try:
    import sounddevice as sd
except (ImportError, OSError):
    sd = None

from asistente_guiador.core.interfaces import STTProvider

logger = logging.getLogger(__name__)


def normalize_text(text: str) -> str:
    """Normaliza texto para comparaciones de voz: minúsculas, sin tildes ni puntuación."""
    if not text:
        return ""
    text = text.lower()
    # Eliminar marcas diacríticas (á->a, é->e, í->i, ó->o, ú->u, etc.)
    norm_chars = [c for c in unicodedata.normalize("NFKD", text) if unicodedata.category(c) != "Mn"]
    text = "".join(norm_chars)
    # Eliminar signos de puntuación y símbolos
    text = re.sub(r"[^\w\s]", "", text)
    return " ".join(text.split())


def check_wake_word_match(transcribed_text: str, target_wake_word: str) -> bool:
    """
    Comprueba si el texto transcrito coincide con la palabra de activación o sus variantes.
    Soporta prefijos comunes (hey, oye, hola) y comandos universales de respaldo ("asistente").
    """
    clean_text = normalize_text(transcribed_text)
    clean_target = normalize_text(target_wake_word)

    if not clean_text or not clean_target:
        return False

    targets = {
        clean_target,
        f"hey {clean_target}",
        f"oye {clean_target}",
        f"hola {clean_target}",
        "asistente",
        "hey asistente",
        "oye asistente",
        "hola asistente",
    }

    # Si el target es 'sofia', añadir transcripciones comunes de Whisper ('sophia', 'sofi')
    if "sofia" in clean_target:
        targets.update({
            "sophia",
            "hey sophia",
            "oye sophia",
            "hola sophia",
            "sofi",
            "hey sofi",
            "oye sofi",
        })

    for target in targets:
        # Búsqueda como palabra completa o frase contenida
        pattern = rf"\b{re.escape(target)}\b"
        if re.search(pattern, clean_text) or target in clean_text:
            return True

    return False


class WakeWordAudioListener:
    """
    Detector continuo de Wake Word ("Sofia" / "hey asistente"):
    - Escucha audio local continuo con pre-buffer circular (evita cortar la primera sílaba).
    - Detecta el inicio de voz por umbral de energía RMS y graba la palabra completa.
    - Normaliza acentos y fonética para que "Sofía" coincida con "Sofia".
    - Únicamente tras confirmar el Wake Word, despierta al asistente para capturar la orden.
    """

    def __init__(
        self,
        stt_provider: STTProvider,
        wake_word: str = "Sofia",
        sample_rate: int = 16000,
        energy_threshold: float = 0.008,
        window_seconds: float = 2.0,
    ):
        self.stt = stt_provider
        self.wake_word = wake_word
        self.sample_rate = sample_rate
        self.energy_threshold = energy_threshold
        self.window_samples = int(sample_rate * window_seconds)
        self._is_listening = True
        self._should_stop = False

    def pause(self) -> None:
        """Pausa la detección desde la bandeja."""
        self._is_listening = False
        logger.info("Detector de Wake Word: PAUSADO")

    def resume(self) -> None:
        """Reanuda la detección."""
        self._is_listening = True
        logger.info("Detector de Wake Word: REANUDADO")

    def stop(self) -> None:
        """Detiene permanentemente la escucha."""
        self._is_listening = False
        self._should_stop = True

    def is_listening(self) -> bool:
        return self._is_listening and not self._should_stop

    def _record_audio_window(self) -> bytes | None:
        """
        Escucha el micrófono con pre-buffer circular continuo.
        Detecta el inicio de voz por RMS y empaqueta la palabra completa en WAV.
        """
        if sd is None or not self._is_listening or self._should_stop:
            return None

        samples_per_chunk = int(self.sample_rate * 0.1)  # Chunks de 100ms
        pre_buffer: collections.deque[np.ndarray] = collections.deque(maxlen=4)  # 400ms pre-buffer
        max_silence_chunks = 4  # 0.4s de silencio para finalizar
        max_total_chunks = 25  # 2.5s máximo total para wake word

        try:
            with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype="float32") as stream:
                while self._is_listening and not self._should_stop:
                    chunk, _ = stream.read(samples_per_chunk)
                    energy = float(np.sqrt(np.mean(chunk**2)))
                    pre_buffer.append(chunk)

                    if energy >= self.energy_threshold:
                        logger.info(
                            f"🎤 Voz detectada (RMS: {energy:.4f} >= {self.energy_threshold}). "
                            "Capturando palabra..."
                        )
                        recorded_chunks = list(pre_buffer)
                        silence_chunks = 0

                        while (
                            len(recorded_chunks) < max_total_chunks
                            and self._is_listening
                            and not self._should_stop
                        ):
                            c, _ = stream.read(samples_per_chunk)
                            recorded_chunks.append(c)
                            e = float(np.sqrt(np.mean(c**2)))
                            if e < self.energy_threshold:
                                silence_chunks += 1
                                if silence_chunks >= max_silence_chunks:
                                    break
                            else:
                                silence_chunks = 0

                        # Generar WAV
                        audio_data = np.concatenate(recorded_chunks, axis=0)
                        audio_int16 = (audio_data * 32767).astype(np.int16)
                        wav_buffer = io.BytesIO()
                        with wave.open(wav_buffer, "wb") as wf:
                            wf.setnchannels(1)
                            wf.setsampwidth(2)
                            wf.setframerate(self.sample_rate)
                            wf.writeframes(audio_int16.tobytes())

                        return wav_buffer.getvalue()

            return None
        except Exception as e:
            if self._is_listening and not self._should_stop:
                logger.warning(f"Aviso capturando audio del micrófono: {e}")
            return None

    async def wait_for_wake_word(self) -> bool:
        """
        Bucle asíncrono que evalúa si el usuario pronunció el Wake Word.
        Devuelve True únicamente tras confirmar la palabra clave.
        """
        while self._is_listening and not self._should_stop:
            wav_bytes = await asyncio.to_thread(self._record_audio_window)
            if not wav_bytes or not self._is_listening or self._should_stop:
                await asyncio.sleep(0.05)
                continue

            # Transcribir fragmento para verificar palabra clave
            text = await self.stt.transcribe(wav_bytes)
            if not text or len(text.strip()) < 2:
                continue

            logger.info(f"🎧 Escuchado: '{text}' (buscando wake word: '{self.wake_word}')")

            if check_wake_word_match(text, self.wake_word):
                logger.info(f"✨ ¡WAKE WORD DETECTADO!: '{text}'")
                return True
            else:
                logger.debug(f"Descartado (no coincide con '{self.wake_word}'): '{text}'")

        return False
