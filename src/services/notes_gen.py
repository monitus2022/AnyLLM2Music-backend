from .llm import llm_service, LlmService
from ..prompts.music_plan import *
from ..prompts.base import BASE_CONTEXT_PROMPT
from typing import Optional
from openai.types.chat import ChatCompletion
from ..logger import app_logger
from ..schemas.openrouter import PromptRequest, CompletionKwargs
import json
from ..utils import timeit


class NotesGenService:
    def __init__(self, llm_service: LlmService):
        self.llm_service = llm_service

    def generate_single_channel_notes_given_music_rhythm(
            self, music_plan: dict[str, str], music_rtythm: dict[str, list], model: str = None, kwargs: dict = None
    ):
        pass

    def generate_all_channel_notes(self, music_plan: dict):
        channels = music_plan.get("instruments", [])
        if not channels:
            app_logger.error("No channels info are found in music plan")
