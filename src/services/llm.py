from openai import OpenAI
from ..config import app_settings

class LlmService:
    def __init__(self, llm_provider: str):
        self.llm_provider = llm_provider
        if self.llm_provider == "openrouter":
            self.client = OpenAI(
                base_url=app_settings.openrouter_url,
                api_key=app_settings.openrouter_api_key,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

    def prompt_llm(self, user_messages: str, system_messages: str, model: str, kwargs: dict):
        if self.llm_provider == "openrouter":
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": user_messages},
                    {"role": "system", "content": system_messages},
                ],
                **kwargs,
            )
            return response
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
    