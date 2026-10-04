import asyncio
import io
import logging
import wave

import numpy as np

try:
    import sounddevice as sd
except (ImportError, OSError):
    sd = None

logger = logging.getLogger(__name__)


class VoiceActivityRecorder:
    """
    Grabador de voz con detección de silencios adaptada a adultos mayores (PRD 7.2):
    - Permite pausas de 1.5 a 2.0 segundos antes de considerar finalizada la frase.
    - No corta por titubeos cortos.
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        silence_threshold_energy: float = 0.015,
        silence_duration_seconds: float = 1.8,
        max_duration_seconds: float = 15.0,
    ):
        self.sample_rate = sample_rate
        self.silence_threshold = silence_threshold_energy
        self.silence_duration = silence_duration_seconds
        self.max_duration = max_duration_seconds

    def record_phrase(self) -> bytes:
        """Graba audio hasta detectar silencio prolongado. Devuelve WAV bytes."""
        if sd is None:
            logger.warning("sounddevice no disponible. Retornando audio vacío.")
            return b""

        logger.info("Escuchando al usuario (iniciando grabación)...")
        recorded_chunks: list[np.ndarray] = []
        silence_samples_count = 0
        samples_per_chunk = int(self.sample_rate * 0.1)  # Chunks de 100ms
        max_silence_samples = int(self.silence_duration * self.sample_rate)
        max_total_samples = int(self.max_duration * self.sample_rate)
        total_samples = 0
        has_spoken = False

        with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype="float32") as stream:
            while total_samples < max_total_samples:
                chunk, _ = stream.read(samples_per_chunk)
                recorded_chunks.append(chunk)
                total_samples += len(chunk)

                # Calcular energía RMS del chunk
                energy = float(np.sqrt(np.mean(chunk**2)))

                if energy > self.silence_threshold:
                    has_spoken = True
                    silence_samples_count = 0
                else:
                    if has_spoken:
                        silence_samples_count += len(chunk)
                        if silence_samples_count >= max_silence_samples:
                            logger.info("Silencio prolongado detectado. Grabación finalizada.")
                            break

        if not recorded_chunks:
            return b""

        audio_data = np.concatenate(recorded_chunks, axis=0)
        # Convertir a int16 para formato WAV estándar
        audio_int16 = (audio_data * 32767).astype(np.int16)

        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_int16.tobytes())

        return wav_buffer.getvalue()

    async def record_phrase_async(self) -> bytes:
        """Ejecuta la captura de micrófono en un hilo separado para no bloquear asyncio."""
        return await asyncio.to_thread(self.record_phrase)
