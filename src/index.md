# Documentación de Arquitectura y Código Fuente (`src`)

El directorio [`src/`](file:///Users/santiago/proyectos/windows-agent-browser/src) alberga el paquete principal del sistema: `asistente_guiador`. Está estructurado siguiendo principios de arquitectura limpia y separación estricta de responsabilidades.

---

## 🏗️ Diagrama de Módulos y Flujo de Dependencias

```mermaid
graph TD
    Entrypoint[main.py] --> Coordinator[core / AssistanceCoordinator]
    Coordinator --> Interfaces[core / Interfaces]
    Coordinator --> Models[core / Models]
    Coordinator --> Session[core / SessionState]
    Coordinator --> ChangeDetector[vision / ScreenChangeDetector]
    
    Interfaces <|.. LLMImpl[ai / GroqLLMProvider]
    Interfaces <|.. VisionImpl[ai / GeminiVisionProvider]
    Interfaces <|.. ScreenImpl[vision / MSSScreenCapturer]
    Interfaces <|.. TTSImpl[audio / EdgeTTSProvider]
    Interfaces <|.. STTImpl[audio / GroqWhisperSTT]
    
    Coordinator --> Config[config / Settings]
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
   Entidades, contratos abstractos, orquestador de ciclo de vida e historial de sesión.
3. **[🤖 Inteligencia Artificial (`src/asistente_guiador/ai/index.md`)](asistente_guiador/ai/index.md)**  
   Modelos de lenguaje, prompts adaptados para adultos mayores y proveedores de visión multimodal.
4. **[🎙️ Audio (`src/asistente_guiador/audio/index.md`)](asistente_guiador/audio/index.md)**  
   Detección de activación ("Oye Asistente"), grabación de audio interactiva, STT y TTS.
5. **[👁️ Visión (`src/asistente_guiador/vision/index.md`)](asistente_guiador/vision/index.md)**  
   Captura de pantalla rápida con `mss` y reducción de costos con algoritmo de cambio visual (`ScreenChangeDetector`).
