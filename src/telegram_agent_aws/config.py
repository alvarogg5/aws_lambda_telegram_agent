from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_file_encoding="utf-8")

    OPENAI_API_KEY: str
    ELEVENLABS_API_KEY: str
    QDRANT_API_KEY: str
    QDRANT_URL: str
    COMET_API_KEY: str
    TELEGRAM_BOT_TOKEN: str

    OPENAI_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-large"

    ELEVENLABS_VOICE_ID: str = "T8lgQl6x5PSdhmmWx42m"
    ELEVENLABS_MODEL_ID: str = "eleven_flash_v2_5"

    COMET_PROJECT: str = Field(
        default="telegram_agent_aws",
        description="Project name for Comet ML and Opik tracking.",
    )
    OPIK_CONFIG_PATH: str = "/tmp/.opik.config"

    # Mongo
    MONGODB_CONNECTION_STRING: str
    MONGODB_DATABASE_NAME: str


settings = Settings()
