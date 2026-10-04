import base64
import io
import json
import logging

import httpx
from PIL import Image

from asistente_guiador.ai.prompts import VISION_LOCATOR_SYSTEM_PROMPT
from asistente_guiador.core.interfaces import VisionProvider
from asistente_guiador.core.models import BoundingBox, VisualElementResult

logger = logging.getLogger(__name__)


class OpenRouterVisionProvider(VisionProvider):
    """
    Proveedor de visión multimodal usando OpenRouter (o DeepSeek Vision directo).
    Convierte el frame a base64 y solicita la detección estructurada del elemento en pantalla.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "deepseek/deepseek-v4.1-flash",
        base_url: str = "https://openrouter.ai/api/v1",
        timeout: float = 20.0,
        max_image_dimension: int = 1280,
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_image_dimension = max_image_dimension

    def _encode_image(self, image: Image.Image) -> str:
        """Redimensiona si es necesario para controlar costes y convierte a base64 JPEG."""
        img = image.convert("RGB")
        w, h = img.size
        if max(w, h) > self.max_image_dimension:
            scale = self.max_image_dimension / max(w, h)
            img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    async def analyze_screen(
        self,
        image: Image.Image,
        target_description: str,
        context: str | None = None,
    ) -> VisualElementResult:
        b64_image = self._encode_image(image)

        prompt_text = f"Busca el siguiente elemento en la pantalla: '{target_description}'."
        if context:
            prompt_text += f" Contexto adicional: {context}"

        messages = [
            {"role": "system", "content": VISION_LOCATOR_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"},
                    },
                ],
            },
        ]

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/asistente-guiador",
            "X-Title": "Asistente Guiador Ofimatica",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
                raw_text = data["choices"][0]["message"]["content"]
                parsed = json.loads(raw_text)

                bbox_dict = parsed.get("bbox")
                bbox = None
                if bbox_dict and isinstance(bbox_dict, dict):
                    bbox = BoundingBox(
                        x=float(bbox_dict.get("x", 0.0)),
                        y=float(bbox_dict.get("y", 0.0)),
                        width=float(bbox_dict.get("width", 0.0)),
                        height=float(bbox_dict.get("height", 0.0)),
                    )

                return VisualElementResult(
                    found=bool(parsed.get("found", False)),
                    application=str(parsed.get("application", "Unknown")),
                    target=target_description,
                    confidence=float(parsed.get("confidence", 0.0)),
                    bbox=bbox,
                    spatial_description=str(parsed.get("spatial_description", "")),
                    reason=str(parsed.get("reason", "")),
                )
        except Exception as e:
            logger.error(f"Error en inferencia visual con OpenRouter: {e}")
            return VisualElementResult(
                found=False,
                target=target_description,
                confidence=0.0,
                spatial_description="No se pudo analizar la pantalla por un error de conexión.",
                reason=str(e),
            )
