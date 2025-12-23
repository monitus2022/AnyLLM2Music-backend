from openai import OpenAI
from openai.types.chat import ChatCompletion
from ..config import app_settings
from ..prompts.base import HEALTH_CHECK_PROMPT
from ..logger import app_logger
from ..schemas.openrouter import PromptRequest
from typing import Optional, Union
import instructor
from pydantic import BaseModel


class LlmService:
    def __init__(self, llm_provider: str):
        # Init LLM Client
        self.free_model_only = False if app_settings.openrouter_default_model else True
        self.llm_provider = llm_provider
        if self.llm_provider != "openrouter":
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
        self.client = None

    def prompt_llm(
        self,
        prompt_request: PromptRequest,
    ) -> Union[str, ChatCompletion]:
        """
        Prompt LLM with Request body, optional to return everything in response

        :param prompt_request: Prompt Request body
        :param return_full_response: Return additional info from response body or not
        :return: Response text only or full completion
        """

        # Define Model
        model = prompt_request.model

        app_logger.debug(f"Prompting LLM with model: {model}")
        if not model:
            if self.free_model_only:
                model = app_settings.openrouter_default_free_model
                app_logger.debug(
                    f"No model specified, using default free model: {model}"
                )
            else:
                model = app_settings.openrouter_default_model
                app_logger.debug(
                    f"No model specified, using default model: {model}"
                )

        if self.llm_provider != "openrouter":
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

        # Define output format
        response_format = prompt_request.response_format or None

        # Other params
        kwargs_dict = prompt_request.kwargs.model_dump(exclude_unset=True)

        # Init client
        self.client = OpenAI(
            base_url=app_settings.openrouter_api_key,
            api_key=app_settings.openrouter_url
        )

        # Wrap with instructor client
        self.client: instructor.Instructor = instructor.from_provider(
            model="openrouter/" + model,
            api_key=app_settings.openrouter_api_key,
            base_url=app_settings.openrouter_url,
            async_client=False
        )

        try:
            response, chat_completion_message = self.client.create_with_completion(
                model=model,
                messages=[
                    {"role": "user", "content": prompt_request.user_messages},
                    {"role": "system", "content": prompt_request.system_messages},
                ],
                response_model=response_format,
                **kwargs_dict,
                max_retries=3
            )
            app_logger.debug(f"LLM response: {response}")
            app_logger.debug(
                f"LLM resource usage: {chat_completion_message.usage}")
            return response
        except Exception as e:
            app_logger.error(f"Error parsing LLM response: {e}")
            raise e

    def health_check(self, model: Optional[str] = None):
        app_logger.info(f"Performing health check for model: {model}")
        try:
            prompt_request = PromptRequest(
                user_messages=HEALTH_CHECK_PROMPT, system_messages="", model=model, kwargs={}
            )
            self.prompt_llm(prompt_request)
            app_logger.info(f"Health check successful for model: {model}")
            return {"model": model, "status": "healthy"}
        except Exception as e:
            app_logger.error(f"Health check failed for model {model}: {e}")
            return {"model": model, "status": "unhealthy", "error": str(e)}


llm_service = LlmService(llm_provider="openrouter")
