from .llm import llm_service, LlmService
from ..prompts.notes_gen import generate_note_events_prompt
from ..prompts.base import BASE_CONTEXT_PROMPT
from typing import Optional, Dict, List
from ..logger import app_logger
from ..schemas.openrouter import PromptRequest, CompletionKwargs
from ..schemas.music import MusicPlan, MusicRhythm, SectionNotes, ChannelNotes, MusicNotes, SectionChannelsResponse
import json
from ..utils import timeit
import concurrent.futures


class NotesGenService:
    def __init__(self, llm_service: LlmService):
        self.llm_service = llm_service

    @timeit
    def generate_section_notes_given_music_rhythm(
            self,
            section_name: str,
            music_plan: MusicPlan,
            music_rhythm: MusicRhythm,
            model: str = None,
            kwargs: dict = None
    ) -> Optional[SectionChannelsResponse]:
        app_logger.info(f"Generating notes for section: {section_name}")
        prompt = generate_note_events_prompt(
            section_name=section_name,
            rhythm_input=music_rhythm.model_dump_json(),
            music_plan_input=music_plan.model_dump_json()
        )
        completion_kwargs = CompletionKwargs(
            max_tokens=8192,
            extra_body={
        "reasoning": {  # https://openrouter.ai/docs/guides/best-practices/reasoning-tokens#controlling-reasoning-tokens
            "effort": "xhigh"
        }},
            **(kwargs or {})
        )
        prompt_request = PromptRequest(
            user_messages=prompt,
            system_messages=BASE_CONTEXT_PROMPT,
            model=model,
            response_format=SectionChannelsResponse,
            kwargs=completion_kwargs,
        )
        response = self.llm_service.prompt_llm(prompt_request)
        if response:
            return response
        return None

    @timeit
    def generate_all_channel_notes(
            self,
            music_plan: MusicPlan,
            music_rhythm: MusicRhythm,
            model: str = None,
            kwargs: dict = None) -> Optional[MusicNotes]:
        sections = [sec.section for sec in music_rhythm.sections]
        app_logger.info(f"Generating notes for sections: {sections}")

        if not sections:
            app_logger.error("No sections found in music rhythm")
            return None

        # Dictionary to accumulate sections per channel
        channel_dict = {}

        def generate_for_section(section_name):
            return self.generate_section_notes_given_music_rhythm(section_name, music_plan, music_rhythm, model, kwargs)

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(sections)) as executor:
            futures = [executor.submit(generate_for_section, section)
                       for section in sections]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    for channel_note in result.channels:
                        channel_name = channel_note.channel
                        if channel_name not in channel_dict:
                            channel_dict[channel_name] = []
                        # Assuming each channel_note has sections with one item
                        if channel_note.sections:
                            channel_dict[channel_name].append(channel_note.sections[0])
                else:
                    app_logger.error("Failed to generate notes for a section")

        if not channel_dict:
            app_logger.error("Failed to generate notes for any section")
            return None

        # Build ChannelNotes
        channel_notes = []
        for channel_name, section_list in channel_dict.items():
            channel_notes.append(ChannelNotes(channel=channel_name, sections=section_list))

        result = MusicNotes(channels=channel_notes)

        with open("music_notes.json", "w") as f:
            json.dump(result.model_dump(), f, indent=4)

        return result


notes_gen_service = NotesGenService(llm_service=llm_service)
