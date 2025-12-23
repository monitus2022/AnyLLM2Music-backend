from .llm import llm_service, LlmService
from ..prompts.notes_gen import generate_note_events_prompt, ALL_CHANNELS
from ..prompts.base import BASE_CONTEXT_PROMPT
from typing import Optional, Dict, List
from openai.types.chat import ChatCompletion
from ..logger import app_logger
from ..schemas.openrouter import PromptRequest, CompletionKwargs
from ..schemas.music import MusicPlan, MusicRhythm, SectionNotes, ChannelNotes, MusicNotes, NotesResponse
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
            music_plan: MusicPlan,
            music_rhythm: MusicRhythm,
            model: str = None,
            kwargs: dict = None
    ) -> Optional[ChannelNotes]:
        app_logger.info(f"Generating notes for channel: {channel}")
        prompt = generate_note_events_prompt(
            channel=channel,
            rhythm_input=music_rhythm.model_dump_json(),
            music_plan_input=music_plan.model_dump_json()
        )
        completion_kwargs = CompletionKwargs(
            max_tokens=8192,
            **(kwargs or {})
        )
        prompt_request = PromptRequest(
            user_messages=prompt,
            system_messages=BASE_CONTEXT_PROMPT,
            model=model,
            response_format=NotesResponse,
            kwargs=completion_kwargs,
        )
        response = self.llm_service.prompt_llm(prompt_request)
        if response:
            return ChannelNotes(channel=channel, sections=response.sections)
        return None

    @timeit
    def generate_all_channel_notes(
            self,
            music_plan: MusicPlan,
            music_rhythm: MusicRhythm,
            model: str = None,
            kwargs: dict = None) -> Optional[MusicNotes]:
        channels = [inst.name for inst in music_plan.instruments] if isinstance(
            music_plan.instruments, list) else []
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

        result = MusicNotes(channels=channel_notes)

        with open("music_notes.json", "w") as f:
            json.dump(result, f, indent=4)
        
        return result


notes_gen_service = NotesGenService(llm_service=llm_service)
