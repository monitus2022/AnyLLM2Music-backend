from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    openrouter_url: str = Field(alias="OPENROUTER_URL", default="https://openrouter.ai/api/v1")
    openrouter_api_key: str = Field(alias="OPENROUTER_API_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
