# Asistente Guiador de Ofimática para Adultos Mayores (MVP)

Sistema de asistencia por voz y referencias visuales diseñado para guiar a adultos mayores en tareas de ofimática (Word, Bloc de Notas, etc.), priorizando accesibilidad cognitiva, bajo costo operativo y respuestas en tiempo real.

---

## 📚 Documentación Técnica Escalonada

Este proyecto cuenta con un sistema integral de documentación piramidal con índices estructurados:

- 📖 **[Índice Principal del Proyecto (`index.md`)](index.md)**
- 🏗️ **[Arquitectura y Código Fuente (`src/index.md`)](src/index.md)**
  - ⚙️ **[Configuración (`src/asistente_guiador/config/index.md`)](src/asistente_guiador/config/index.md)**
  - 🧠 **[Core y Orquestación (`src/asistente_guiador/core/index.md`)](src/asistente_guiador/core/index.md)**
  - 🤖 **[Inteligencia Artificial y Modelos (`src/asistente_guiador/ai/index.md`)](src/asistente_guiador/ai/index.md)**
  - 🎙️ **[Audio, Grabación y Síntesis (`src/asistente_guiador/audio/index.md`)](src/asistente_guiador/audio/index.md)**
  - 👁️ **[Visión y Optimización Visual (`src/asistente_guiador/vision/index.md`)](src/asistente_guiador/vision/index.md)**
- 🧪 **[Suite de Pruebas Automatizadas (`tests/index.md`)](tests/index.md)**

---

## 🚀 Requisitos e Instalación

### Requisitos
- **Python**: `>=3.11, <3.12`
- **Gestor**: [`uv`](https://github.com/astral-sh/uv)

### Comandos de uso

```bash
# Sincronizar el entorno de desarrollo
uv sync

# Ejecutar la suite de pruebas unitarias y de integración
uv run pytest

# Iniciar el asistente
uv run asistente-guiador
```

---

## 📜 Reglas de Proyecto

El mantenimiento y la evolución de este repositorio se rigen por las reglas en `.agents/rules/`:
- [Guía de uso de `uv`](.agents/rules/uv_guidelines.md)
- [Regla de Mantenimiento de Documentación](.agents/rules/documentation_maintenance.md)
