# Documentación de Arquitectura y Código Fuente (`src`)

El directorio [`src/`](file:///Users/santiago/proyectos/windows-agent-browser/src) alberga el paquete principal del sistema: `asistente_guiador`. Está estructurado siguiendo principios de arquitectura limpia y separación estricta de responsabilidades.

---

## 🏗️ Diagrama de Módulos y Flujo de Dependencias

```mermaid
graph TD
    Entrypoint[app.py / main.py] --> Coordinator[core / AssistanceCoordinator]
    Entrypoint --> Watcher[vision / ScreenContextWatcher]
    
    Coordinator --> Interfaces[core / Interfaces]
    Coordinator --> Models[core / Models]
    Coordinator --> Session[core / SessionState]
    Coordinator --> ChangeDetector[vision / ScreenChangeDetector]
    Coordinator --> WinDetector[vision / ActiveWindowDetector]
    
    Watcher --> ScreenCapturer[vision / MSSScreenCapturer]
    Watcher --> ChangeDetector
    Watcher --> WinDetector
    Watcher --> Session
    Watcher -.-> VisionImpl[ai / OpenRouterVisionProvider]
    
    Interfaces <|.. LLMImpl[ai / GroqLLMProvider]
    Interfaces <|.. VisionImpl
    Interfaces <|.. ScreenCapturer
    Interfaces <|.. TTSImpl[audio / PiperTTSProvider]
    Interfaces <|.. STTImpl[audio / GroqWhisperSTTProvider]
    
    Coordinator --> Config[config / Settings]
    Watcher --> Config
    LLMImpl --> Config
    VisionImpl --> Config
    TTSImpl --> Config
    STTImpl --> Config
```

---

## 🗂️ Subíndices por Módulo

1. **[⚙️ Configuración (`src/asistente_guiador/config/index.md`)](asistente_guiador/config/index.md)**  
   Manejo de variables de entorno y configuración tipada mediante `pydantic-settings`.
2. **[🧠 Core y Dominio (`src/asistente_guiador/core/index.md`)](asistente_guiador/core/index.md)**  
   Entidades, `GlobalScreenState`, contratos abstractos, orquestador e historial de sesión.
3. **[🤖 Inteligencia Artificial (`src/asistente_guiador/ai/index.md`)](asistente_guiador/ai/index.md)**  
   Modelos de lenguaje, prompts con contexto de pantalla vivo, detección de intenciones y proveedores de visión multimodal.
4. **[🎙️ Audio (`src/asistente_guiador/audio/index.md`)](asistente_guiador/audio/index.md)**  
   Detección de activación ("Sofia" / "hey asistente"), grabación de audio interactiva, STT y TTS.
5. **[👁️ Visión (`src/asistente_guiador/vision/index.md`)](asistente_guiador/vision/index.md)**  
   Captura de pantalla con `mss`, detector de ventana activa del SO (`ActiveWindowDetector`) y observador continuo en segundo plano (`ScreenContextWatcher`).

