# Módulo de Audio (`src/asistente_guiador/audio`)

El módulo de audio gestiona la interacción por voz con el usuario, asegurando una experiencia accesible adaptada a pausas y titubeos naturales en adultos mayores.

---

## 🗂️ Componentes y Archivos

- **[`wakeword.py`](file:///Users/santiago/proyectos/windows-agent-browser/src/asistente_guiador/audio/wakeword.py)**: Detección pasiva de activación:
  - `WakeWordDetector`: Contrato abstracto para detección local sin enviar audio constante a la nube (respeto a la privacidad, RF-01).
  - `SimpleWakeWordDetector`: Implementación base no bloqueante con soporte para pausar (`pause()`) y reanudar (`resume()`) la escucha desde el tray de Windows.
- **[`recorder.py`](file:///Users/santiago/proyectos/windows-agent-browser/src/asistente_guiador/audio/recorder.py)**: Grabador de micrófono con detector de silencios adaptable:
  - `VoiceActivityRecorder`: Utiliza `sounddevice` y análisis RMS en fragmentos de 100 ms.
  - Diseñado con tolerancia de silencio prolongado (`silence_duration_seconds=1.8s`) para no interrumpir al adulto mayor mientras piensa o formula su frase.
- **[`stt.py`](file:///Users/santiago/proyectos/windows-agent-browser/src/asistente_guiador/audio/stt.py)**: Transcripción de habla a texto:
  - `GroqWhisperSTTProvider`: Envía fragmentos de audio a la API de Whisper en Groq (`whisper-large-v3-turbo`) logrando transcripciones precisas en español con latencias inferiores a 500 ms.
- **[`tts.py`](file:///Users/santiago/proyectos/windows-agent-browser/src/asistente_guiador/audio/tts.py)**: Síntesis de voz a habla:
  - `PiperTTSProvider`: Implementación orientada al motor local Piper (`es_ES-davefx-medium.onnx`).
  - Cuenta con mecanismo de fallback transparente para entornos de desarrollo y pruebas utilizando comandos nativos del sistema operativo (`say` en macOS, PowerShell SAPI en Windows o síntesis simulada).
