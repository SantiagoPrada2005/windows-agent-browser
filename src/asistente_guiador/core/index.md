# Módulo Core (`src/asistente_guiador/core`)

El módulo `core` contiene la lógica central del dominio y la orquestación del asistente. Es agnóstico a las implementaciones concretas de proveedores externos de IA, interfaces gráficas o sistemas operativos.

---

## 📄 Archivos y Responsabilidades

- **[`models.py`](file:///Users/santiago/proyectos/windows-agent-browser/src/asistente_guiador/core/models.py)**: Entidades y DTOs de dominio implementados con `pydantic.BaseModel`.
  - `IntentType`: Enum con intenciones admitidas (`LOCATE_ELEMENT`, `GENERAL_QUESTION`, `EXPLAIN_ACTION`, `REPEAT_INSTRUCTION`, etc.).
  - `BoundingBox`: Coordenadas normalizadas `[0.0, 1.0]` con método de conversión a píxeles `to_pixel_coords()`.
  - `IntentResult`: Resultado del enrutador/clasificador semántico.
  - `VisualElementResult`: Estructura devuelta por el modelo de visión.
  - `GuidanceResponse`: Mensaje hablado final y datos para resaltado visual overlay.
- **[`interfaces.py`](file:///Users/santiago/proyectos/windows-agent-browser/src/asistente_guiador/core/interfaces.py)**: Puertos abstractos (Clean Architecture) basados en `abc.ABC`:
  - `LLMProvider`: Contratos `classify_intent` y `generate_response`.
  - `VisionProvider`: Contrato `analyze_screen`.
  - `STTProvider`: Contrato `transcribe`.
  - `TTSProvider`: Contrato `speak`.
  - `ScreenCapturer`: Contrato `capture_active_screen`.
- **[`session_state.py`](file:///Users/santiago/proyectos/windows-agent-browser/src/asistente_guiador/core/session_state.py)**: Maneja el estado conversacional en memoria y el caché de pantalla:
  - Ventana deslizante de historial (hasta 6 interacciones).
  - Último screenshot analizado con timestamp.
  - Última respuesta de guía para soporte de repetición ("¿puedes repetir?").
- **[`coordinator.py`](file:///Users/santiago/proyectos/windows-agent-browser/src/asistente_guiador/core/coordinator.py)**: Implementa `AssistanceCoordinator`, el motor de orquestación reactivo con inferencia adaptativa:
  1. Detecta solicitud de repetición y responde sin volver a invocar modelos.
  2. Clasifica la intención con LLM de baja latencia.
  3. Si requiere contexto visual, evalúa cambios en pantalla mediante `ScreenChangeDetector`. Si no hay cambios, reutiliza el resultado previo; si los hay, invoca al proveedor de visión.
  4. Genera la guía verbal adaptada para usuarios mayores.
  5. Envía el texto a TTS y actualiza la sesión.
