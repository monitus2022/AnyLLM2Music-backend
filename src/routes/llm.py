from ..services import llm_service, music_plan_service, notes_gen_service
from fastapi import Query
from typing import Optional
from ..schemas.llm import GeneratePlanRequest, GenerateChordsRequest, GenerateRhythmRequest, GenerateNotesRequest


async def llm_health(model: Optional[str] = Query(default=None, description="LLM model to check")):
    """
    Health check endpoint for any model in LLM service.

    :param model: model name to check
    """
    return await llm_service.health_check(model=model)

async def generate_plan(request: GeneratePlanRequest):
    """
    Generate a music plan given a text description.

    :param request: GeneratePlanRequest object
    """
    return await music_plan_service.generate_music_plan_given_description(
        description=request.description, model=request.model, kwargs=request.kwargs
    )

async def generate_chords(request: GenerateChordsRequest):
    """
    Generate music chords given a music plan.

    :param request: GenerateChordsRequest object
    """
    return await music_plan_service.generate_music_chords_given_plan(
        music_plan=request.music_plan, description=request.description, model=request.model, kwargs=request.kwargs
    )

async def generate_rhythm(request: GenerateRhythmRequest):
    """
    Generate music rhythm given music chords.

    :param request: GenerateRhythmRequest object
    """
    return await music_plan_service.generate_music_rhythm_given_chords(
        music_chords=request.music_chords, description=request.description, model=request.model, kwargs=request.kwargs
    )

async def generate_notes(request: GenerateNotesRequest):
    """
    Generate music notes given music plan and rhythm.

    :param request: GenerateNotesRequest object
    """
    return await notes_gen_service.generate_all_channel_notes(
        music_plan=request.music_plan, music_rhythm=request.music_rhythm, model=request.model, kwargs=request.kwargs
    )

