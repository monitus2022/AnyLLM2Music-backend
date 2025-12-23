from ..services import llm_service, music_plan_service, notes_gen_service
from fastapi import Query
from typing import Optional

def llm_health(model: Optional[str] = Query(default=None, description="LLM model to check")):
    """
    Health check endpoint for any model in LLM service.

    :param model: model name to check
    """
    return llm_service.health_check(model=model)

def create_music_plan(description: str, model: Optional[str] = None, kwargs: dict = None):
    """
    Create a music plan given a text description.

    :param description: Text description of the music piece
    :param model: LLM model to use
    :param kwargs: Additional kwargs for LLM prompting
    """
    return music_plan_service.generate_music_plan_given_description(
        description=description, model=model, kwargs=kwargs
    )

def create_music_rhythm(description: str, model: Optional[str] = None, kwargs: dict = None):
    """
    Create music rhythm given music chords.

    :param description: Text description of the music piece
    :param model: LLM model to use
    :param kwargs: Additional kwargs for LLM prompting
    """
    return music_plan_service.generate_music_rhythm_given_description(
        description=description, model=model, kwargs=kwargs
    )

def create_music_notes(description: str, model: Optional[str] = None, kwargs: dict = None):
    """
    Create music notes given description (generates full plan first).

    :param description: Text description of the music piece
    :param model: LLM model to use
    :param kwargs: Additional kwargs for LLM prompting
    """
    # First generate the full plan
    rhythm_response = music_plan_service.generate_music_rhythm_given_description(
        description=description, model=model, kwargs=kwargs
    )
    if not rhythm_response:
        return None
    # Load the saved plan
    import json
    with open("music_plan.json", "r") as f:
        plan_data = json.load(f)
    music_plan = plan_data["music_plan"]
    music_rhythm = plan_data["music_rhythm"]
    return notes_gen_service.generate_all_channel_notes(
        music_plan=music_plan, music_rhythm=music_rhythm, model=model, kwargs=kwargs
    )