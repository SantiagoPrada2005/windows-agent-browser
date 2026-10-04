import asyncio
import json
import logging

import httpx

from asistente_guiador.ai.prompts import (
    GUIDANCE_RESPONSE_SYSTEM_PROMPT,
    INTENT_ROUTER_SYSTEM_PROMPT,
)
from asistente_guiador.core.interfaces import LLMProvider
from asistente_guiador.core.models import (
    GlobalScreenState,
    GuidanceResponse,
    IntentResult,
    IntentType,
    ResponseStyle,
    VisualElementResult,
)

logger = logging.getLogger(__name__)


class GroqLLMProvider(LLMProvider):
    """Proveedor LLM rápido utilizando la API compatible de Groq (o endpoint OpenAI)."""

    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.1-8b-instant",
        base_url: str = "https://api.groq.com/openai/v1",
        timeout: float = 10.0,
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def _post_chat_completion(
        self,
        messages: list[dict],
        response_format_json: bool = True,
        max_retries: int = 3,
    ) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,
        }
        if response_format_json:
            payload["response_format"] = {"type": "json_object"}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(max_retries):
                resp = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                if resp.status_code == 429 and attempt < max_retries - 1:
                    retry_after = float(resp.headers.get("retry-after", 2.0))
                    logger.warning(
                        f"Límite 429 en Groq. Esperando {retry_after:.1f}s antes de reintentar..."
                    )
                    await asyncio.sleep(retry_after)
                    continue

                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return json.loads(content)

    async def classify_intent(
        self,
        user_query: str,
        session_context: list[dict] | None = None,
        screen_state: GlobalScreenState | None = None,
    ) -> IntentResult:
        messages = [
            {"role": "system", "content": INTENT_ROUTER_SYSTEM_PROMPT},
        ]
        if screen_state:
            screen_info = (
                f"Ventana activa: '{screen_state.active_window_title}'. "
                f"Aplicación: '{screen_state.active_application}'. "
                f"Estado visible: '{screen_state.screen_summary}'."
            )
            messages.append(
                {"role": "system", "content": f"Contexto actual de la pantalla: {screen_info}"}
            )

        if session_context:
            context_summary = json.dumps(session_context[-4:], ensure_ascii=False)
            messages.append({"role": "system", "content": f"Historial previo: {context_summary}"})
        messages.append({"role": "user", "content": user_query})

        try:
            raw_json = await self._post_chat_completion(messages)
            intent_val = IntentType(raw_json.get("intent", "unknown"))
            requires_vision = bool(raw_json.get("requires_visual_context", False))
            # Si el modelo clasificó como locate_element, forzar requires_vision
            if intent_val == IntentType.LOCATE_ELEMENT:
                requires_vision = True

            return IntentResult(
                intent=intent_val,
                target=raw_json.get("target"),
                requires_visual_context=requires_vision,
                response_style=ResponseStyle(raw_json.get("response_style", "short_guidance")),
                confidence=float(raw_json.get("confidence", 1.0)),
                raw_query=user_query,
            )
        except Exception as e:
            logger.error(f"Error clasificando intención con Groq: {e}. Fallback a 'unknown'")
            return IntentResult(
                intent=IntentType.UNKNOWN,
                raw_query=user_query,
                confidence=0.0,
            )

    async def generate_response(
        self,
        intent: IntentResult,
        visual_result: VisualElementResult | None = None,
        conversation_history: list[dict] | None = None,
        initial_context: str | None = None,
        screen_state: GlobalScreenState | None = None,
    ) -> GuidanceResponse:
        messages = [
            {"role": "system", "content": GUIDANCE_RESPONSE_SYSTEM_PROMPT},
        ]

        if screen_state:
            messages.append(
                {
                    "role": "system",
                    "content": (
                        f"Estado en vivo: Ventana '{screen_state.active_window_title}' "
                        f"({screen_state.active_application}). {screen_state.screen_summary}"
                    ),
                }
            )
        elif initial_context:
            messages.append(
                {
                    "role": "system",
                    "content": f"Contexto visual inicial de la pantalla activa: {initial_context}",
                }
            )

        # Inyectar turnos previos de chat para coherencia conversacional
        if conversation_history:
            for turn in conversation_history[-4:]:
                messages.append({"role": "user", "content": turn.get("user", "")})
                messages.append({"role": "assistant", "content": turn.get("assistant", "")})

        context_payload = {
            "current_intent": intent.model_dump(),
            "visual_result": visual_result.model_dump() if visual_result else None,
        }
        user_prompt = (
            f"El usuario dice: '{intent.raw_query}'. "
            f"Datos del turno actual: {json.dumps(context_payload, ensure_ascii=False)}"
        )
        messages.append({"role": "user", "content": user_prompt})

        try:
            raw_json = await self._post_chat_completion(messages)
            highlight = visual_result.bbox if visual_result and visual_result.found else None
            return GuidanceResponse(
                spoken_text=raw_json.get("spoken_text", "Por favor revisa la pantalla."),
                visual_highlight=highlight,
                spatial_description=raw_json.get(
                    "spatial_description",
                    visual_result.spatial_description if visual_result else None,
                ),
                needs_user_click=raw_json.get("needs_user_click", True),
            )
        except Exception as e:
            logger.error(f"Error generando respuesta guiada: {e}")
            fallback_text = "No estoy seguro, por favor mira la barra superior de tu pantalla."
            if visual_result and visual_result.spatial_description:
                fallback_text = f"El elemento se encuentra {visual_result.spatial_description}."
            return GuidanceResponse(
                spoken_text=fallback_text,
                visual_highlight=visual_result.bbox if visual_result else None,
            )
