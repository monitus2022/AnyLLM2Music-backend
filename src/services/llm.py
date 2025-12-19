from openai import OpenAI
from openai.types.chat import ChatCompletion
from ..config import app_settings
from ..prompts.base import HEALTH_CHECK_PROMPT
from ..logger import app_logger
from typing import Optional


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

    def prompt_llm(self, user_messages: str, system_messages: str, kwargs: dict, model: Optional[str] = None):
        app_logger.debug(f"Prompting LLM with model: {model}")
        if not model:
            app_logger.debug(f"No model specified, using default model: {app_settings.openrouter_default_free_model}")
            model = app_settings.openrouter_default_free_model
        if self.llm_provider == "openrouter":
            response: ChatCompletion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": user_messages},
                    {"role": "system", "content": system_messages},
                ],
                **kwargs,
            )
            app_logger.debug(f"LLM response preview: {response.choices[0].message.content}")
            return response
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

    def health_check(self, model: Optional[str] = None):
        app_logger.info(f"Performing health check for model: {model}")
        try:
            self.prompt_llm(
                user_messages=HEALTH_CHECK_PROMPT,
                system_messages="",
                model=model,
                kwargs={},
            )
            app_logger.info(f"Health check successful for model: {model}")
            return {
                "model": model,
                "status": "healthy"
                }
        except Exception as e:
            app_logger.error(f"Health check failed for model {model}: {e}")
            return {
                "model": model,
                "status": "unhealthy", 
                "error": str(e)
                }

llm_service = LlmService(llm_provider="openrouter")
