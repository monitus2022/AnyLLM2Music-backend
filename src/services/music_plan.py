from .llm import llm_service, LlmService
from ..prompts.music_plan import *
from ..prompts.base import BASE_CONTEXT_PROMPT
from typing import Optional
from openai.types.chat import ChatCompletion
from ..logger import app_logger
from ..schemas.openrouter import PromptRequest, CompletionKwargs


class MusicPlanService:
    def __init__(self, llm_service: LlmService):
        self.llm_service = llm_service

    def generate_music_plan_given_description(
        self, description: str, model: str, kwargs: dict
    ) -> Optional[ChatCompletion]:
        app_logger.info("Generating music plan from description")
        if not description:
            description = MUSIC_PLAN_USER_DESCRIPTION
        prompt = DEFINE_MUSIC_PLAN_PROMPT.replace(MUSIC_PLAN_USER_DESCRIPTION, description)
        prompt_request = PromptRequest(
            user_messages=prompt,
            system_messages=BASE_CONTEXT_PROMPT,
            model=model,
            kwargs=CompletionKwargs(**kwargs) if kwargs else CompletionKwargs()
        )
        response = self.llm_service.prompt_llm(prompt_request)
        app_logger.info("Music plan generation completed")
        return response

music_plan_service = MusicPlanService(llm_service=llm_service)