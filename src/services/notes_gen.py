from .llm import llm_service, LlmService
from ..prompts.notes_gen import generate_note_events_prompt, ALL_CHANNELS
from ..prompts.base import BASE_CONTEXT_PROMPT
from typing import Optional, Dict, List
from openai.types.chat import ChatCompletion
from ..logger import app_logger
from ..schemas.openrouter import PromptRequest, CompletionKwargs
from ..schemas.music import SectionNotes, ChannelNotes, MusicNotes
import json
from ..utils import timeit
import concurrent.futures


class NotesGenService:
    def __init__(self, llm_service: LlmService):
        self.llm_service = llm_service

    @timeit
    def generate_single_channel_notes_given_music_rhythm(
            self,
            channel: str,
            music_plan: Dict[str, any],
            music_rhythm: Dict[str, any],
            model: str = None,
            kwargs: dict = None
    ) -> Optional[ChannelNotes]:
        app_logger.info(f"Generating notes for channel: {channel}")
        prompt = generate_note_events_prompt(
            channel, json.dumps(music_rhythm), json.dumps(music_plan))
        
        if not kwargs or not kwargs.get("max_tokens", None):
            kwargs["max_tokens"] = 4096                  # Extend default token size
        completion_kwargs = CompletionKwargs(
            **(kwargs or {})
        )
        prompt_request = PromptRequest(
            user_messages=prompt,
            system_messages=BASE_CONTEXT_PROMPT,
            model=model,
            response_format=ChannelNotes,
            kwargs=completion_kwargs,
        )
        response = self.llm_service.prompt_llm(prompt_request)
        if not response:
            app_logger.error(f"Failed to generate notes for channel {channel}")
            return None
        return response

    @timeit
    def generate_all_channel_notes(
        self, 
        music_plan: Dict[str, any], 
        music_rhythm: Dict[str, any], 
        model: str = None, 
        kwargs: dict = None) -> Optional[MusicNotes]:
        channels = [inst["name"] for inst in music_plan.get("instruments", [])] if isinstance(
            music_plan.get("instruments", []), list) else []
        if not channels:
            channels = ALL_CHANNELS  # fallback
            app_logger.warning(
                "No instruments found in music_plan, using default channels")
        app_logger.info(f"Generating notes for channels: {channels}")

        def generate_for_channel(channel):
            return self.generate_single_channel_notes_given_music_rhythm(channel, music_plan, music_rhythm, model, kwargs)

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(channels)) as executor:
            futures = [executor.submit(generate_for_channel, channel)
                       for channel in channels]
            channel_notes = []
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    channel_notes.append(result)
                else:
                    app_logger.error("Failed to generate notes for a channel")

        if not channel_notes:
            app_logger.error("Failed to generate notes for any channel")
            return None

        return MusicNotes(channels=channel_notes)


notes_gen_service = NotesGenService(llm_service=llm_service)
