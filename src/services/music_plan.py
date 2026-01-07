from .llm import llm_service, LlmService
from ..prompts.music_plan import *
from ..prompts.base import BASE_CONTEXT_PROMPT
from typing import Optional
from openai.types.chat import ChatCompletion
from ..logger import app_logger
from ..schemas.openrouter import PromptRequest, CompletionKwargs
from ..schemas.music import MusicPlan, MusicChords, MusicRhythm
import json
from ..utils import timeit


class MusicPlanService:
    def __init__(self, llm_service: LlmService):
        self.llm_service = llm_service

    @timeit
    async def generate_music_plan_given_description(
        self,
        description: str,
        music_parameters: Optional[dict] = None,
        model: str = None,
        kwargs: dict = None,
    ) -> Optional[MusicPlan]:
        """
        Generate a music plan given a text description.
        :param description: Text description of the music piece
        :param music_parameters: Additional music parameters
        :param model: LLM model to use
        :param kwargs: Additional kwargs for LLM prompting
        :return: Generated MusicPlan object
        """
        app_logger.info("Generating music plan from description")
        if not description:
            description = MUSIC_PLAN_USER_DESCRIPTION
        if not music_parameters:
            # TODO: change hard-code to input
            music_parameters = MUSIC_PLAN_USER_PARAMETERS
        prompt = DEFINE_MUSIC_PLAN_PROMPT.replace(MUSIC_PLAN_USER_DESCRIPTION, description).replace(
            MUSIC_PLAN_USER_PARAMETERS, str(music_parameters)
        )
        completion_kwargs = CompletionKwargs(
            **(kwargs or {})
        )
        prompt_request = PromptRequest(
            user_messages=prompt,
            system_messages=BASE_CONTEXT_PROMPT,
            model=model,
            response_format=MusicPlan,
            kwargs=completion_kwargs
        )
        music_plan_response = await self.llm_service.prompt_llm(prompt_request)
        app_logger.info("Music plan generation completed")
        return music_plan_response

    @timeit
    async def generate_music_chords_given_plan(
        self,
        music_plan: MusicPlan,
        description: Optional[str] = None,
        music_parameters: Optional[dict] = None,
        model: str = None,
        kwargs: dict = None
    ) -> Optional[MusicChords]:
        """
        Generate music chords given a music plan.
        :param music_plan: MusicPlan object
        :param music_parameters: Additional music parameters
        :param model: LLM model to use
        :param kwargs: Additional kwargs for LLM prompting
        :return: Generated MusicChords object
        """
        app_logger.info("Generating music chords from music plan")
        if not music_parameters:
            music_parameters = MUSIC_PLAN_USER_PARAMETERS
        description_text = description if description else "<No original description provided>"
        prompt = DEFINE_CHORD_PROMPT.replace(MUSIC_PLAN_INPUT, music_plan.model_dump_json()).replace(
            MUSIC_PLAN_USER_PARAMETERS, str(music_parameters)
        ).replace(MUSIC_DESCRIPTION, description_text)
        completion_kwargs = CompletionKwargs(
            **(kwargs or {})
        )
        prompt_request = PromptRequest(
            user_messages=prompt,
            system_messages=BASE_CONTEXT_PROMPT,
            model=model,
            response_format=MusicChords,
            kwargs=completion_kwargs
        )
        music_chords_response = await self.llm_service.prompt_llm(prompt_request)
        app_logger.info("Music chords generation completed")
        return music_chords_response

    @timeit
    async def generate_music_rhythm_given_chords(
        self,
        music_chords: MusicChords,
        description: Optional[str] = None,
        music_parameters: Optional[dict] = None,
        model: str = None,
        kwargs: dict = None
    ) -> Optional[MusicRhythm]:
        """
        Generate music rhythm given music chords.
        :param music_chords: MusicChords object
        :param music_parameters: Additional music parameters
        :param model: LLM model to use
        :param kwargs: Additional kwargs for LLM prompting
        :return: Generated MusicRhythm object
        """
        app_logger.info("Generating music rhythm from music chords")
        if not music_parameters:
            music_parameters = MUSIC_PLAN_USER_PARAMETERS
        description_text = description if description else "<No original description provided>"
        prompt = DEFINE_RHYTHM_PROMPT.replace(MUSIC_CHORDS_INPUT, music_chords.model_dump_json()).replace(
            MUSIC_PLAN_USER_PARAMETERS, str(music_parameters)
        ).replace(MUSIC_DESCRIPTION, description_text)
        completion_kwargs = CompletionKwargs(
            **(kwargs or {})
        )
        prompt_request = PromptRequest(
            user_messages=prompt,
            system_messages=BASE_CONTEXT_PROMPT,
            model=model,
            response_format=MusicRhythm,
            kwargs=completion_kwargs,
        )
        music_rhythm_response = await self.llm_service.prompt_llm(prompt_request)
        app_logger.info("Music rhythm generation completed")
        return music_rhythm_response

    async def generate_music_rhythm_given_description(
        self,
        description: str,
        music_parameters: Optional[dict] = None,
        music_plan: MusicPlan = None,
        model: str = None,
        kwargs: dict = None
    ) -> tuple[Optional[MusicPlan], Optional[MusicRhythm]]:
        """
        Generate music rhythm given a text description.
        :param description: Text description of the music piece
        :param music_parameters: Additional music parameters
        :param music_plan: Pre-generated MusicPlan object (optional)
        :param model: LLM model to use
        :param kwargs: Additional kwargs for LLM prompting
        :return: Tuple of (MusicPlan, MusicRhythm) objects
        """
        app_logger.info("Generating music rhythm from description")
        music_plan = await self.generate_music_plan_given_description(
            description=description, music_parameters=music_parameters, model=model, kwargs=kwargs
        )
        if not music_plan:
            app_logger.error(
                "Failed to generate music plan; cannot proceed to rhythm generation")
            return None, None
        music_chords = await self.generate_music_chords_given_plan(
            music_plan=music_plan, music_parameters=music_parameters, model=model, kwargs=kwargs
        )
        if not music_chords:
            app_logger.error(
                "Failed to generate music chords; cannot proceed to rhythm generation")
            return music_plan, None
        rhythm_response = await self.generate_music_rhythm_given_chords(
            music_chords=music_chords, music_parameters=music_parameters, model=model, kwargs=kwargs
        )
        if not rhythm_response:
            app_logger.error("Failed to generate music rhythm")
            return None

        # Debug purpose only: save to json file
        # with open("music_plan.json", "w") as f:
        #     json.dump(
        #         {
        #             "description": description,
        #             # Load json string to dict/list
        #             "music_plan": music_plan.model_dump(),
        #             "music_chords": music_chords.model_dump(),
        #             "music_rhythm": rhythm_response.model_dump()
        #         },
        #         f,
        #         indent=4,
        #     )
        return music_plan, rhythm_response


music_plan_service = MusicPlanService(llm_service=llm_service)
