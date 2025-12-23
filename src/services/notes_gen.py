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
            self, channel: str, music_plan: Dict[str, any], music_rhythm: Dict[str, any], model: str = None, kwargs: dict = None
    ) -> Optional[ChannelNotes]:
        app_logger.info(f"Generating notes for channel: {channel}")
        prompt = generate_note_events_prompt(channel, json.dumps(music_rhythm), json.dumps(music_plan))
        completion_kwargs = CompletionKwargs(
            response_format={"type": "json_object"},
            max_tokens=4096
            )
        if kwargs:
            completion_kwargs = CompletionKwargs(**kwargs, response_format={"type": "json_object"})
        prompt_request = PromptRequest(
            user_messages=prompt,
            system_messages=BASE_CONTEXT_PROMPT,
            model=model,
            kwargs=completion_kwargs,
        )
        response = self.llm_service.prompt_llm(prompt_request)
        if not response:
            app_logger.error(f"Failed to generate notes for channel {channel}")
            return None
        try:
            notes_data = json.loads(response)

            sections = []
            for section_data in notes_data.get("sections", []):
                bars = []
                for bar_data in section_data.get("bars", []):
                    events = []
                    for event_list in bar_data.get("events", []):
                        if len(event_list) == 4:
                            events.append({
                                "beat": event_list[0],
                                "pitch": event_list[1],
                                "duration": event_list[2],
                                "velocity": event_list[3]
                            })
                    bars.append({"bar": bar_data["bar"], "events": events})
                sections.append({"section": section_data["section"], "bars": bars})
            return ChannelNotes(channel=channel, sections=sections)
        except json.JSONDecodeError as e:
            app_logger.error(f"Failed to parse JSON for channel {channel}: {e}")
            return None

    @timeit
    def generate_all_channel_notes(self, music_plan: Dict[str, any], music_rhythm: Dict[str, any], model: str = None, kwargs: dict = None) -> Optional[MusicNotes]:
        channels = [inst["name"] for inst in music_plan.get("instruments", [])] if isinstance(music_plan.get("instruments", []), list) else []
        if not channels:
            channels = ALL_CHANNELS  # fallback
            app_logger.warning("No instruments found in music_plan, using default channels")
        app_logger.info(f"Generating notes for channels: {channels}")
        
        def generate_for_channel(channel):
            return self.generate_single_channel_notes_given_music_rhythm(channel, music_plan, music_rhythm, model, kwargs)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(channels)) as executor:
            futures = [executor.submit(generate_for_channel, channel) for channel in channels]
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
