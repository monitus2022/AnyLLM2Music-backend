from ..services import llm_service, music_plan_service, notes_gen_service
from fastapi import Query
from typing import Optional
from ..schemas.music import MusicPlan, MusicChords, MusicRhythm
from ..schemas.llm import GeneratePlanRequest, GenerateChordsRequest, GenerateRhythmRequest, GenerateNotesRequest


async def llm_health(model: Optional[str] = Query(default=None, description="LLM model to check")):
    """
    Health check endpoint for any model in LLM service.

    :param model: model name to check
    """
    return await llm_service.health_check(model=model)

async def create_music_plan(description: str, model: Optional[str] = None, kwargs: dict = None):
    """
    Create a music plan given a text description.

    :param description: Text description of the music piece
    :param model: LLM model to use
    :param kwargs: Additional kwargs for LLM prompting
    """
    return await music_plan_service.generate_music_plan_given_description(
        description=description, model=model, kwargs=kwargs
    )

async def create_music_rhythm(description: str, model: Optional[str] = None, kwargs: dict = None):
    """
    Create music rhythm given music chords.

    :param description: Text description of the music piece
    :param model: LLM model to use
    :param kwargs: Additional kwargs for LLM prompting
    """
    music_plan, rhythm_response = await music_plan_service.generate_music_rhythm_given_description(
        description=description, model=model, kwargs=kwargs
    )
    return rhythm_response

async def create_music_notes(description: str, model: Optional[str] = None, kwargs: dict = None):
    """
    Create music notes given description (generates full plan first).

    :param description: Text description of the music piece
    :param model: LLM model to use
    :param kwargs: Additional kwargs for LLM prompting
    """
    # First generate the full plan
    music_plan, rhythm_response = await music_plan_service.generate_music_rhythm_given_description(
        description=description, model=model, kwargs=kwargs
    )
    if not rhythm_response:
        return None

    return await notes_gen_service.generate_all_channel_notes(
        music_plan=music_plan, music_rhythm=rhythm_response, model=model, kwargs=kwargs
    )

async def create_music_notes_with_cache(
        model: Optional[str] = None, kwargs: dict = None
):
    """
    Create music notes given description (generates full plan first).
    Using cache json file to skip previous prompting
    Only used in testing purpose

    :param description: Text description of the music piece
    :param model: LLM model to use
    :param kwargs: Additional kwargs for LLM prompting
    """
    import json
    from ..schemas.music import MusicPlanResponse
    with open("music_plan.json", "r") as f:
        music_plan_full_content: dict = json.load(f)
    music_plan_response: MusicPlanResponse = MusicPlanResponse.model_validate(music_plan_full_content)

    return await notes_gen_service.generate_all_channel_notes(
        music_plan=music_plan_response.music_plan,
        music_rhythm=music_plan_response.music_rhythm,
        model=model, kwargs=kwargs
    )

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

