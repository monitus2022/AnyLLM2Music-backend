from ..services import llm_service, music_plan_service, notes_gen_service
from fastapi import Query
from typing import Optional
from ..schemas.music import MusicNotes
from ..services.midi import json_to_midi_bytes

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
    music_plan, rhythm_response = music_plan_service.generate_music_rhythm_given_description(
        description=description, model=model, kwargs=kwargs
    )
    return rhythm_response

def create_music_notes(description: str, model: Optional[str] = None, kwargs: dict = None):
    """
    Create music notes given description (generates full plan first).

    :param description: Text description of the music piece
    :param model: LLM model to use
    :param kwargs: Additional kwargs for LLM prompting
    """
    # First generate the full plan
    music_plan, rhythm_response = music_plan_service.generate_music_rhythm_given_description(
        description=description, model=model, kwargs=kwargs
    )
    if not rhythm_response:
        return None

    return notes_gen_service.generate_all_channel_notes(
        music_plan=music_plan, music_rhythm=rhythm_response, model=model, kwargs=kwargs
    )

def create_music_notes_with_cache(
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

    return notes_gen_service.generate_all_channel_notes(
        music_plan=music_plan_response.music_plan,
        music_rhythm=music_plan_response.music_rhythm,
        model=model, kwargs=kwargs
    )

def generate_midi_from_cache(model: Optional[str] = None, kwargs: dict = None):
    """
    Generate MIDI using cached music_notes.json.
    Only used for testing the MIDI generation part.

    :param model: LLM model to use (not used here)
    :param kwargs: Additional kwargs (not used here)
    """
    import json
    import base64

    with open("music_notes.json", "r") as f:
        music_notes_dict = json.load(f)
    music_notes = MusicNotes.model_validate(music_notes_dict)

    midi_bytes = json_to_midi_bytes(music_notes)
    midi_b64 = base64.b64encode(midi_bytes).decode('utf-8')
    return {"midi_data": midi_b64}

def generate_midi_from_description(description: str, model: Optional[str] = None, kwargs: dict = None):
    """
    Final endpoint: Generate music notes from description and generate MIDI.
    Pierces through all components: plan -> rhythm -> notes -> MIDI.

    :param description: Text description of the music piece
    :param model: LLM model to use
    :param kwargs: Additional kwargs for LLM prompting
    """
    import base64

    music_notes = create_music_notes(description, model, kwargs)
    if not music_notes:
        return {"error": "Failed to generate music notes"}

    midi_bytes = json_to_midi_bytes(music_notes)
    midi_b64 = base64.b64encode(midi_bytes).decode('utf-8')
    return {
        "description": description,
        "midi_data": midi_b64
        }
