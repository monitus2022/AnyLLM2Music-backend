from ..services import music_plan_service, notes_gen_service
from fastapi import Query
from typing import Optional
from ..schemas.music import MusicNotes, MusicPlan, MusicRhythm
from ..services.midi import json_to_midi_bytes
from pydantic import BaseModel
import base64
import tempfile
import os
from midi2audio import FluidSynth


class GenerateMidiRequest(BaseModel):
    music_plan: MusicPlan
    music_rhythm: MusicRhythm
    model: Optional[str] = None
    kwargs: Optional[dict] = None

class ConvertMidiToAudioRequest(BaseModel):
    midi_data: str


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

    midi_bytes = json_to_midi_bytes(music_notes)
    midi_b64 = base64.b64encode(midi_bytes).decode('utf-8')
    return {"midi_data": midi_b64}


async def convert_midi_to_audio(request: ConvertMidiToAudioRequest):
    """
    Convert MIDI data (base64 encoded) to audio (WAV base64 encoded).

    :param midi_data: Base64 encoded MIDI file data
    """
    try:
        # Decode MIDI data
        midi_bytes = base64.b64decode(request.midi_data)

        # Create temp files
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as midi_file, \
                tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_file:

            midi_file_path = midi_file.name
            wav_file_path = wav_file.name

            # Write MIDI data to temp file
            midi_file.write(midi_bytes)
            midi_file.flush()

            # Convert MIDI to WAV using FluidSynth with custom soundfont
            working_dir = os.path.dirname(os.path.abspath(__file__))
            soundfont_path = os.path.join(working_dir, '..', 'assets', 'soundfonts', '8bit.sf2')
            fs = FluidSynth(sound_font=soundfont_path)
            fs.midi_to_audio(midi_file_path, wav_file_path)

            # Read WAV data
            with open(wav_file_path, 'rb') as f:
                wav_bytes = f.read()

            # Encode to base64
            wav_b64 = base64.b64encode(wav_bytes).decode('utf-8')

        # Clean up temp files
        os.unlink(midi_file_path)
        os.unlink(wav_file_path)

        return {"audio_data": wav_b64}

    except Exception as e:
        return {"error": f"Failed to convert MIDI to audio: {str(e)}"}
