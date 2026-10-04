# Módulo de Inteligencia Artificial (`src/asistente_guiador/ai`)

Este módulo implementa el razonamiento cognitivo, la clasificación de peticiones y el análisis visual multimodal adaptado para adultos mayores.

---

## 🗂️ Estructura

- **[`prompts.py`](file:///Users/santiago/proyectos/windows-agent-browser/src/asistente_guiador/ai/prompts.py)**: Define los system prompts estructurados:
  - `INTENT_ROUTER_SYSTEM_PROMPT`: Clasificador estricto JSON que determina la intención y si se requiere visión.
  - `VISION_LOCATOR_SYSTEM_PROMPT`: Instrucciones de localización espacial cotidiana ("arriba a la izquierda", "icono de disquete") sin jerga técnica.
  - `GUIDANCE_RESPONSE_SYSTEM_PROMPT`: Generador de instrucciones verbales cortas (máximo 2 oraciones), claras y pausadas.
- **`providers/`**: Adaptadores concretos que implementan los contratos de `core/interfaces.py`:
  - **[`groq_provider.py`](file:///Users/santiago/proyectos/windows-agent-browser/src/asistente_guiador/ai/providers/groq_provider.py)**: Implementación de `LLMProvider` mediante la API de Groq (o endpoints compatibles con OpenAI). Soporta reintentos exponenciales ante código de estado `429 (Rate Limit)` y parseo seguro a modelos Pydantic.
  - **[`vision_provider.py`](file:///Users/santiago/proyectos/windows-agent-browser/src/asistente_guiador/ai/providers/vision_provider.py)**: Implementación de `VisionProvider` a través de OpenRouter (`OpenRouterVisionProvider`). Codifica frames en base64 con compresión y escalado inteligente (`max_image_dimension=1280`) para minimizar latencia y consumo de tokens.
