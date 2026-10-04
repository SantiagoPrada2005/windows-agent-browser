# Módulo de Configuración (`src/asistente_guiador/config`)

Este módulo centraliza todas las variables de entorno, configuraciones de modelos y parámetros del sistema utilizando [`pydantic-settings`](https://docs.pydantic.dev/latest/concepts/pydantic_settings/).

---

## 📄 Archivos del Módulo

- **[`settings.py`](file:///Users/santiago/proyectos/windows-agent-browser/src/asistente_guiador/config/settings.py)**: Define la clase `Settings`.

---

## ⚙️ Parámetros Principales

| Parámetro | Tipo | Valor por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `app_name` | `str` | `"Asistente Guiador de Ofimática"` | Nombre visible de la aplicación. |
| `app_version` | `str` | `"0.1.0"` | Versión actual del paquete. |
| `debug` | `bool` | `False` | Habilita logs detallados y trazas de depuración. |
| `groq_api_key` | `str` | `""` | API Key para inferencia de LLM y Whisper en Groq. |
| `groq_model` | `str` | `"qwen/qwen3.8-27b"` | Modelo rápido para clasificación y generación de respuestas. |
| `openrouter_api_key` | `str` | `""` | API Key para modelos multimodales a través de OpenRouter. |
| `vision_model` | `str` | `"deepseek/deepseek-v4.1-flash"` | Modelo de visión para análisis de UI en pantalla. |
| `screen_change_threshold` | `float` | `0.03` | Umbral diferencial normalizado de cambio en pantalla. |
| `screen_check_width` | `int` | `640` | Ancho de imagen optimizado para comprobación de cambio visual. |
| `screen_check_height` | `int` | `360` | Alto de imagen optimizado para comprobación de cambio visual. |
| `screen_watch_interval_seconds` | `float` | `1.0` | Intervalo en segundos del muestreo continuo de pantalla en memoria. |
| `screen_structural_change_threshold` | `float` | `0.12` | Umbral de cambio visual extenso (>12%) para actualización del resumen semántico. |
| `enable_background_screen_watcher` | `bool` | `True` | Habilita el hilo de monitoreo continuo de pantalla en segundo plano. |
| `wake_word` | `str` | `"hey asistente"` | Frase de activación por voz. |
| `stt_language` | `str` | `"es"` | Código de lenguaje para transcripción de audio. |


---

## 🔑 Archivo `.env`

El módulo lee automáticamente el archivo `.env` en la raíz del proyecto si existe, respetando valores fijados en el entorno del sistema operativo.
