# Documentación del Proyecto - Asistente Guiador

Bienvenido a la documentación técnica escalonada de **Asistente Guiador de Ofimática para Adultos Mayores (MVP)**.

Este sistema está diseñado con una arquitectura modular y desacoplada para asistir mediante voz y referencias visuales a usuarios que realizan tareas de ofimática, priorizando la accesibilidad cognitiva, bajo costo operativo y respuestas en tiempo real.

---

## 🗂️ Índice General Escalonado

La documentación se organiza de forma jerárquica con archivos índice (`index.md`) en cada nivel:

- **[Arquitectura Global y Módulos de Código (`src/index.md`)](src/index.md)**  
  Visión integral de la solución, árbol de paquetes y contratos entre capas.
  - ⚙️ **[Configuración (`src/asistente_guiador/config/index.md`)](src/asistente_guiador/config/index.md)**: Variables de entorno, perfiles y configuración centralizada (`Settings`).
  - 🧠 **[Core del Asistente (`src/asistente_guiador/core/index.md`)](src/asistente_guiador/core/index.md)**: Modelos de dominio (`models.py`), estado global de pantalla continuo (`GlobalScreenState`), orquestador (`AssistanceCoordinator`), estado de sesión (`SessionState`) e interfaces (`interfaces.py`).
  - 🤖 **[Inteligencia Artificial y Modelos (`src/asistente_guiador/ai/index.md`)](src/asistente_guiador/ai/index.md)**: Clasificación de intención informada, generación de respuestas empáticas con contexto de interfaz, prompts y proveedores externos (Groq Llama 3.3, OpenRouter / DeepSeek).
  - 🎙️ **[Módulo de Audio (`src/asistente_guiador/audio/index.md`)](src/asistente_guiador/audio/index.md)**: Detección de wakeword, grabación con detector de silencio (VAD simple), transcripción (STT) y síntesis de voz (TTS).
  - 👁️ **[Módulo de Visión y Captura (`src/asistente_guiador/vision/index.md`)](src/asistente_guiador/vision/index.md)**: Captura de pantalla multiplataforma con `mss`, detector nativo de ventana activa (`ActiveWindowDetector`) y observador continuo en memoria (`ScreenContextWatcher`).
- 🧪 **[Suite de Pruebas Automatizadas (`tests/index.md`)](tests/index.md)**  
  Estrategia de testing unitario y de integración, mocks de proveedores y cobertura.

---

## 🚀 Inicio Rápido

### Requisitos
- **Python**: `>=3.11, <3.12`
- **Gestor de paquetes**: [`uv`](https://github.com/astral-sh/uv)

### Instalación y Ejecución

```bash
# Sincronizar dependencias
uv sync

# Ejecutar suite de pruebas
uv run pytest

# Ejecutar el punto de entrada principal
uv run asistente-guiador
```

---

## 📋 Reglas de Mantenimiento

Para asegurar que esta documentación se mantenga sincronizada con el código fuente en cada refactorización o adición, se aplica la regla de proyecto ubicada en:  
👉 **[Regla de Mantenimiento de Documentación (`.agents/rules/documentation_maintenance.md`)](.agents/rules/documentation_maintenance.md)**.
