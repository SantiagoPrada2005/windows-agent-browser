# Suite de Pruebas Automatizadas (`tests`)

Este directorio contiene las pruebas unitarias y de integración para asegurar la confiabilidad de cada subsistema y del orquestador. Las pruebas están configuradas con `pytest` y `pytest-asyncio`.

---

## 🗂️ Módulos de Prueba

- **[`test_models.py`](file:///Users/santiago/proyectos/windows-agent-browser/tests/test_models.py)**: Valida restricciones de esquemas Pydantic:
  - Transformación matemática de `BoundingBox` a píxeles en distintas resoluciones.
  - Validación de límites normalizados `[0.0, 1.0]` y excepciones `ValidationError`.
  - Serialización y deserialización de `IntentResult` y `VisualElementResult`.
- **[`test_coordinator.py`](file:///Users/santiago/proyectos/windows-agent-browser/tests/test_coordinator.py)**: Comprueba el flujo orquestado de `AssistanceCoordinator`:
  - Detección reactiva de comandos de repetición ("repite por favor") sin invocar a los modelos.
  - Reutilización de caché visual cuando la pantalla no presenta modificaciones significativas.
  - Integración completa con mocks asíncronos de `LLMProvider`, `VisionProvider` y `TTSProvider`.
- **[`test_ai_providers.py`](file:///Users/santiago/proyectos/windows-agent-browser/tests/test_ai_providers.py)**: Evalúa los adaptadores de IA:
  - Clasificación de intenciones y generación de guía en `GroqLLMProvider`.
  - Manejo de reintentos ante error de cuota `429 Too Many Requests`.
  - Procesamiento y compresión de imagen con `OpenRouterVisionProvider`.
- **[`test_change_detector.py`](file:///Users/santiago/proyectos/windows-agent-browser/tests/test_change_detector.py)**: Comprueba el algoritmo de comparación de pantalla:
  - El primer frame siempre es reportado como cambio.
  - Dos frames idénticos retornan `False`.
  - Cuadros con cambios que superan el umbral porcentual devuelven `True`.
  - Cálculo de porcentaje relativo de cambio con `compute_change_ratio`.
- **[`test_window_detector.py`](file:///Users/santiago/proyectos/windows-agent-browser/tests/test_window_detector.py)**: Comprueba la detección de ventana activa del sistema operativo:
  - Fallback resiliente y seguro en entornos de prueba / no-Windows.
  - Mock de funciones de Win32 API (`GetForegroundWindow`, `GetWindowTextW`).
- **[`test_watcher.py`](file:///Users/santiago/proyectos/windows-agent-browser/tests/test_watcher.py)**: Comprueba el observador continuo en segundo plano:
  - Muestreo periódico de pantalla y actualización de `SessionState.global_screen_state`.
  - Detección de cambio estructural y disparo debounced del resumen semántico.
  - Ciclo de vida asíncrono limpio de inicio y detención.
- **[`test_audio.py`](file:///Users/santiago/proyectos/windows-agent-browser/tests/test_audio.py)**: Verifica los componentes de voz:
  - Activación y pausado del detector de Wake Word.
  - Fallback resiliente en `PiperTTSProvider` cuando no existe el binario en el sistema.
  - Simulación de transcripción con `GroqWhisperSTTProvider`.


---

## 🏃 Ejecución de Pruebas

Para ejecutar la suite completa:

```bash
uv run pytest
```

Para ejecutar un archivo específico con logs detallados:

```bash
uv run pytest tests/test_coordinator.py -v -s
```
