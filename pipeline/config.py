"""Pipeline configuration via pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    USE_MOCK_PIPELINE: bool = True
    USE_LLAVA: bool = False
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    TOPIC_VISION_EVENTS: str = "sportscast.vision"
    TOPIC_SPEECH_EVENTS: str = "sportscast.speech"
    TOPIC_AUDIO_EVENTS: str = "sportscast.audio"
    TOPIC_FUSED_EVENTS: str = "sportscast.fused"
    TOPIC_REVIEW_QUEUE: str = "sportscast.review"
    CONFIDENCE_THRESHOLD: float = 0.75
    REVIEW_THRESHOLD: float = 0.45
    FRAME_SAMPLE_RATE: int = 2
    SEGMENT_DURATION: int = 10
    FUSION_WINDOW_MS: int = 3000
    DASHBOARD_URL: str = "http://localhost:8000"
    DATABASE_URL: str = "sqlite+aiosqlite:///./sportscast.db"
    CLIPS_DIR: str = "./clips"
    SEGMENTS_DIR: str = "./segments"
    LOG_LEVEL: str = "INFO"


settings = Settings()
