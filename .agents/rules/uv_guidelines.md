# Directrices de Gestión de Entorno y Dependencias con `uv`

Este proyecto utiliza **`uv`** como el único y canónico gestor de paquetes, entornos virtuales y versiones de Python.

## 1. Reglas Estrictas de Ejecución
- **NUNCA usar `pip install`, `virtualenv` o `python -m venv` directamente.**
- Todas las invocaciones de comandos, scripts y herramientas deben realizarse a través de `uv run`:
  - En lugar de `pytest`: usar `uv run pytest`
  - En lugar de `python main.py`: usar `uv run python main.py`
  - En lugar de `ruff check`: usar `uv run ruff check`

## 2. Gestión de Dependencias
- Para agregar dependencias de producción:
  ```bash
  uv add <paquete>
  ```
- Para agregar dependencias de desarrollo o testing:
  ```bash
  uv add --dev <paquete>
  ```
- Para eliminar dependencias:
  ```bash
  uv remove <paquete>
  ```
- Tras modificar manualmente `pyproject.toml`, sincronizar siempre el entorno y el lockfile:
  ```bash
  uv sync
  ```
- El archivo `uv.lock` **SIEMPRE** debe mantenerse sincronizado y versionado junto a `pyproject.toml`.

## 3. Versión de Python y Entorno
- La versión de Python del proyecto está fijada en **Python 3.11** mediante `.python-version` y `requires-python = ">=3.11,<3.12"`.
- Para garantizar que la versión de Python correcta esté instalada localmente:
  ```bash
  uv python install 3.11
  ```
- Para inspeccionar el entorno o dependencias instaladas:
  ```bash
  uv tree
  ```

## 4. Estilo y Calidad de Código
- Usar `uv run ruff check .` para linting.
- Usar `uv run ruff format .` para formateo de código.
