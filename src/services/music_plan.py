from .llm import llm_service, LlmService
from ..prompts.music_plan import *
from ..prompts.base import BASE_CONTEXT_PROMPT
from typing import Optional
from openai.types.chat import ChatCompletion
from ..logger import app_logger
from ..schemas.openrouter import PromptRequest, CompletionKwargs
import json


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

    def generate_music_chords_given_plan(
        self, music_plan: str, model: str, kwargs: dict
    ) -> Optional[ChatCompletion]:
        app_logger.info("Generating music chords from music plan")
        prompt = DEFINE_CHORD_PROMPT.replace(MUSIC_PLAN_INPUT, music_plan)
        prompt_request = PromptRequest(
            user_messages=prompt,
            system_messages=BASE_CONTEXT_PROMPT,
            model=model,
            kwargs=CompletionKwargs(**kwargs) if kwargs else CompletionKwargs()
        )
        response = self.llm_service.prompt_llm(prompt_request)
        app_logger.info("Music chords generation completed")
        return response
    
    def generate_music_rhythm_given_chords(
        self, music_chords: str, model: str, kwargs: dict
    ) -> Optional[ChatCompletion]:
        app_logger.info("Generating music rhythm from music chords")
        prompt = DEFINE_RHYTHM_PROMPT.replace(MUSIC_CHORDS_INPUT, music_chords)
        prompt_request = PromptRequest(
            user_messages=prompt,
            system_messages=BASE_CONTEXT_PROMPT,
            model=model,
            kwargs=CompletionKwargs(**kwargs) if kwargs else CompletionKwargs()
        )
        response = self.llm_service.prompt_llm(prompt_request)
        app_logger.info("Music rhythm generation completed")
        return response

    def generate_music_rhythm_given_description(
        self, description: str, model: str, kwargs: dict
    ) -> Optional[ChatCompletion]:
        music_plan = self.generate_music_plan_given_description(
            description=description, model=model, kwargs=kwargs
        )
        if not music_plan:
            app_logger.error("Failed to generate music plan; cannot proceed to rhythm generation")
            return None
        music_chords = self.generate_music_chords_given_plan(
            music_plan=music_plan, model=model, kwargs=kwargs
        )
        if not music_chords:
            app_logger.error("Failed to generate music chords; cannot proceed to rhythm generation")
            return None
        rhythm_response = self.generate_music_rhythm_given_chords(
            music_chords=music_chords, model=model, kwargs=kwargs
        )
        if not rhythm_response:
            app_logger.error("Failed to generate music rhythm")
            return None
        
        with open("music_plan.json", "w") as f:
            json.dump({
                "description": description,
                "music_plan": music_plan,
                "music_chords": music_chords,
                "music_rhythm": rhythm_response
            }, f, indent=4)
        return rhythm_response
    
music_plan_service = MusicPlanService(llm_service=llm_service)