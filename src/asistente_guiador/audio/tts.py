import asyncio
import logging
import platform
import shutil
import subprocess

from asistente_guiador.core.interfaces import TTSProvider

logger = logging.getLogger(__name__)


class PiperTTSProvider(TTSProvider):
    """
    Proveedor de síntesis de voz local.
    Diseñado para usar el binario local 'piper' (PRD v2.0).
    Incluye fallback para desarrollo (macOS 'say', Windows SAPI o simulado).
    """

    def __init__(
        self,
        piper_path: str = "piper",
        model_path: str = "models/piper/es_ES-davefx-medium.onnx",
        rate: float = 1.0,
    ):
        self.piper_path = piper_path
        self.model_path = model_path
        self.rate = rate
        self._has_piper = bool(shutil.which(self.piper_path))

    async def speak(self, text: str) -> None:
        """Sintetiza y reproduce el texto de forma no bloqueante."""
        if not text.strip():
            return

        logger.info(f"Sintetizando voz: '{text}'")

        if self._has_piper:
            try:
                proc = await asyncio.create_subprocess_exec(
                    self.piper_path,
                    "--model",
                    self.model_path,
                    "--output_raw",
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                _, stderr = await proc.communicate(input=text.encode("utf-8"))
                if proc.returncode == 0:
                    logger.debug("Audio sintetizado con éxito con Piper.")
                    return
                logger.warning(f"Fallo en Piper: {stderr.decode()}. Usando fallback.")
            except Exception as e:
                logger.warning(f"Error invocando Piper: {e}. Usando fallback.")

        await self._system_fallback_speak(text)

    async def _system_fallback_speak(self, text: str) -> None:
        system = platform.system()
        try:
            if system == "Darwin" and shutil.which("say"):
                proc = await asyncio.create_subprocess_exec("say", "-v", "Paulina", text)
                await proc.wait()
            elif system == "Windows":
                ps_script = (
                    "Add-Type -AssemblyName System.speech; "
                    f"(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{text}')"
                )
                proc = await asyncio.create_subprocess_exec("powershell", "-Command", ps_script)
                await proc.wait()
            else:
                logger.info(f"[AUDIO SIMULADO]: {text}")
        except Exception as e:
            logger.error(f"Error en fallback de voz: {e}")
