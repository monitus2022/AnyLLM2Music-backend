import re
from ..services import music_plan_service, notes_gen_service
from typing import Optional
from ..schemas.music import MusicNotes, MusicPlan, MusicRhythm
from ..schemas.midi import GenerateMidiRequest, ConvertMidiToAudioRequest
from ..services.midi import json_to_midi_bytes, midi_to_audio


def generate_midi_from_cache():
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


async def generate_midi_from_description(description: str, model: Optional[str] = None, kwargs: dict = None):
    """
    Final endpoint: Generate music notes from description and generate MIDI.
    Pierces through all components: plan -> rhythm -> notes -> MIDI.

    :param description: Text description of the music piece
    :param model: LLM model to use
    :param kwargs: Additional kwargs for LLM prompting
    """
    import base64

    # First generate the full plan
    music_plan, rhythm_response = await music_plan_service.generate_music_rhythm_given_description(
        description=description, model=model, kwargs=kwargs
    )
    if not rhythm_response:
        return {"error": "Failed to generate music rhythm"}

    music_notes = await notes_gen_service.generate_all_channel_notes(
        music_plan=music_plan, music_rhythm=rhythm_response, model=model, kwargs=kwargs
    )
    if not music_notes:
        return {"error": "Failed to generate music notes"}

    midi_bytes = json_to_midi_bytes(music_notes)
    midi_b64 = base64.b64encode(midi_bytes).decode('utf-8')
    return {
        "description": description,
        "midi_data": midi_b64
    }


async def generate_midi(request: GenerateMidiRequest):
    """
    Generate MIDI from music plan and rhythm.

    :param request: GenerateMidiRequest object
    """
    import base64

    music_notes = await notes_gen_service.generate_all_channel_notes(
        music_plan=request.music_plan, music_rhythm=request.music_rhythm, model=request.model, kwargs=request.kwargs
    )
    if not music_notes:
        return {"error": "Failed to generate music notes"}

    # Extract and validate BPM from music plan
    bpm_value = request.music_plan.tempo_feel.bpm
    try:
        if isinstance(bpm_value, str):
            # Extract the first integer from the string (e.g., "160 bpm" -> 160)
            match = re.search(r'\d+', bpm_value)
            if match:
                bpm = int(match.group())
            else:
                bpm = 120  # Default if no number found
        elif isinstance(bpm_value, int):
            bpm = bpm_value
        else:
            bpm = 120  # Default for unexpected types

        # Validate range
        if not (40 <= bpm <= 200):
            bpm = 120  # Default fallback
    except (AttributeError, TypeError, ValueError):
        bpm = 120  # Default fallback

    midi_bytes = json_to_midi_bytes(music_notes, bpm=bpm)
    midi_b64 = base64.b64encode(midi_bytes).decode('utf-8')
    return {"midi_data": midi_b64}


async def convert_midi_to_audio(request: ConvertMidiToAudioRequest):
    return midi_to_audio(request.midi_data, request.soundfont)
