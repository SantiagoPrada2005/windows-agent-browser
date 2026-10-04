from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración del asistente cargada desde variables de entorno o archivo .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Asistente Guiador de Ofimática"
    app_version: str = "0.1.0"
    debug: bool = False

    # Proveedores de IA
    groq_api_key: str = ""
    groq_model: str = "qwen/qwen3.8-27b"
    openrouter_api_key: str = ""
    vision_model: str = "deepseek/deepseek-v4.1-flash"

    # Parámetros de detección de cambios de pantalla
    screen_change_threshold: float = 0.03
    screen_check_width: int = 640
    screen_check_height: int = 360
    screen_watch_interval_seconds: float = 1.0
    screen_structural_change_threshold: float = 0.12
    enable_background_screen_watcher: bool = True

    # Audio y Wake word
    wake_word: str = "Sofia"
    stt_language: str = "es"
    wake_word_energy_threshold: float = 0.008
