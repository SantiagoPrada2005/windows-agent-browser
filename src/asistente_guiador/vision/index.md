# Módulo de Visión y Captura (`src/asistente_guiador/vision`)

El módulo `vision` proporciona los mecanismos de captura de la pantalla del usuario y optimización de costo/latencia mediante detección local de cambios de cuadro.

---

## 🗂️ Componentes y Archivos

- **[`capture.py`](file:///Users/santiago/proyectos/windows-agent-browser/src/asistente_guiador/vision/capture.py)**: Captura de pantalla de ultra baja latencia:
  - `MSSScreenCapturer`: Implementa `ScreenCapturer` utilizando la librería nativa multiplataforma `mss`.
  - Captura monitores específicos en memoria sin escribir archivos temporales en disco y convierte el búfer BGRA a objetos `PIL.Image.Image`.
- **[`change_detector.py`](file:///Users/santiago/proyectos/windows-agent-browser/src/asistente_guiador/vision/change_detector.py)**: Detector diferencial de cambios visuales:
  - `ScreenChangeDetector`: Compara frames sucesivos utilizando `cv2.absdiff` y umbralización binaria en una resolución reducida (`640x360`).
  - Permite al orquestador saber si la pantalla sigue estática para reutilizar coordenadas en caché y **evitar llamadas redundantes a APIs de visión multimodal**, reduciendo costos y tiempo de respuesta a 0 ms para pantallas sin modificaciones.
