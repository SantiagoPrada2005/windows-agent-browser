# Módulo de Visión y Captura (`src/asistente_guiador/vision`)

El módulo `vision` proporciona los mecanismos de captura de la pantalla del usuario y optimización de costo/latencia mediante detección local de cambios de cuadro.

---

## 🗂️ Componentes y Archivos

- **[`capture.py`](file:///Users/santiago/proyectos/windows-agent-browser/src/asistente_guiador/vision/capture.py)**: Captura de pantalla de ultra baja latencia:
  - `MSSScreenCapturer`: Implementa `ScreenCapturer` utilizando la librería nativa multiplataforma `mss`.
  - Captura monitores específicos en memoria sin escribir archivos temporales en disco y convierte el búfer BGRA a objetos `PIL.Image.Image`.
- **[`change_detector.py`](file:///Users/santiago/proyectos/windows-agent-browser/src/asistente_guiador/vision/change_detector.py)**: Detector diferencial de cambios visuales:
  - `ScreenChangeDetector`: Compara frames sucesivos utilizando `cv2.absdiff` y umbralización binaria en una resolución reducida (`640x360`).
  - Proporciona `compute_change_ratio` para distinguir cambios menores (parpadeo de cursor/tecleo) de cambios estructurales mayores (>12%).
  - Permite al orquestador saber si la pantalla sigue estática para reutilizar coordenadas en caché y **evitar llamadas redundantes a APIs de visión multimodal**, reduciendo costos y tiempo de respuesta a 0 ms para pantallas sin modificaciones.
- **[`window_detector.py`](file:///Users/santiago/proyectos/windows-agent-browser/src/asistente_guiador/vision/window_detector.py)**: Detección de ventana activa en primer plano:
  - `ActiveWindowDetector`: Contrato abstracto para obtener el título de ventana activa del sistema operativo.
  - `WindowsActiveWindowDetector`: Integración nativa Win32 mediante `ctypes` (`GetForegroundWindow`, `GetWindowTextW`).
  - `FallbackActiveWindowDetector`: Implementación multiplataforma para pruebas y entornos macOS/Linux.
- **[`watcher.py`](file:///Users/santiago/proyectos/windows-agent-browser/src/asistente_guiador/vision/watcher.py)**: Observador continuo en segundo plano:
  - `ScreenContextWatcher`: Tarea asíncrona periódica (~1.0s) que muestrea la pantalla en RAM, consulta la ventana activa y detecta cambios estructurales.
  - Aplica *debouncing* (1.0s de estabilidad visual) antes de disparar la actualización asíncrona del resumen semántico global con el modelo de visión, manteniendo siempre fresco el contexto visual sin sobrecostos.

