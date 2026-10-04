# Módulo de Inteligencia Artificial (`src/asistente_guiador/ai`)

Este módulo implementa el razonamiento cognitivo, la clasificación de peticiones y el análisis visual multimodal adaptado para adultos mayores.

---

## 🗂️ Estructura

- **[`prompts.py`](file:///Users/santiago/proyectos/windows-agent-browser/src/asistente_guiador/ai/prompts.py)**: Define los system prompts estructurados:
  - `SCREEN_SUMMARY_SYSTEM_PROMPT`: Observador visual de interfaz que produce resúmenes concisos del estado de la pantalla y diálogos modales.
  - `INTENT_ROUTER_SYSTEM_PROMPT`: Clasificador estricto JSON informado con el contexto en tiempo real de la pantalla (`GlobalScreenState`).
  - `VISION_LOCATOR_SYSTEM_PROMPT`: Instrucciones de localización espacial cotidiana ("arriba a la izquierda", "icono de disquete") sin jerga técnica.
  - `GUIDANCE_RESPONSE_SYSTEM_PROMPT`: Generador de instrucciones verbales cortas adaptadas con empatía a la ventana y diálogo activos.
- **`providers/`**: Adaptadores concretos que implementan los contratos de `core/interfaces.py`:
  - **[`groq_provider.py`](file:///Users/santiago/proyectos/windows-agent-browser/src/asistente_guiador/ai/providers/groq_provider.py)**: Implementación de `LLMProvider` mediante la API de Groq (o endpoints compatibles con OpenAI). Inyecta metadatos y resumen de pantalla en `classify_intent` y `generate_response`. Soporta reintentos exponenciales ante `429 (Rate Limit)` y parseo a modelos Pydantic.
  - **[`vision_provider.py`](file:///Users/santiago/proyectos/windows-agent-browser/src/asistente_guiador/ai/providers/vision_provider.py)**: Implementación de `VisionProvider` a través de OpenRouter (`OpenRouterVisionProvider`). Implementa `analyze_screen` (bounding box) y `summarize_screen` (resumen semántico de interfaz). Codifica frames en base64 con compresión y escalado inteligente (`max_image_dimension=1280`).

