from openai import OpenAI
from openai.types.chat import ChatCompletion
from ..config import app_settings
from ..prompts.base import HEALTH_CHECK_PROMPT
from ..logger import app_logger
from ..schemas.openrouter import PromptRequest
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

    def prompt_llm(self, prompt_request: PromptRequest, return_full_response: bool = False) -> ChatCompletion:
        model = prompt_request.model
        app_logger.debug(f"Prompting LLM with model: {model}")
        if not model:
            app_logger.debug(
                f"No model specified, using default model: {app_settings.openrouter_default_free_model}"
            )
            model = app_settings.openrouter_default_free_model
        if self.llm_provider == "openrouter":
            kwargs_dict = prompt_request.kwargs.dict(exclude_unset=True)
            response: ChatCompletion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt_request.user_messages},
                    {"role": "system", "content": prompt_request.system_messages},
                ],
                **kwargs_dict,
            )
            app_logger.debug(f"LLM response preview: {response.choices[0].message.content}")
            if return_full_response:
                return response
            else:
                return response.choices[0].message.content
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

    def health_check(self, model: Optional[str] = None):
        app_logger.info(f"Performing health check for model: {model}")
        try:
            prompt_request = PromptRequest(
                user_messages=HEALTH_CHECK_PROMPT,
                system_messages="",
                model=model,
                kwargs={}
            )
            self.prompt_llm(prompt_request)
            app_logger.info(f"Health check successful for model: {model}")
            return {"model": model, "status": "healthy"}
        except Exception as e:
            app_logger.error(f"Health check failed for model {model}: {e}")
            return {"model": model, "status": "unhealthy", "error": str(e)}


llm_service = LlmService(llm_provider="openrouter")
