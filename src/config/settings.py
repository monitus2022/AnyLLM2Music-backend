from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    openrouter_url: str = Field(alias="OPENROUTER_URL", default="https://openrouter.ai/api/v1")
    openrouter_api_key: str = Field(alias="OPENROUTER_API_KEY")
    openrouter_default_free_model: str = Field(alias="OPENROUTER_DEFAULT_FREE_MODEL", default="openai/gpt-oss-120b:free")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
