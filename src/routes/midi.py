import re
import uuid
from ..services import notes_gen_service
from ..services.progress import progress_emitter
from ..schemas.midi import GenerateMidiRequest, ConvertMidiToAudioRequest
from ..services.midi import json_to_midi_bytes, midi_to_audio


async def generate_midi(request: GenerateMidiRequest):
    """
    Generate MIDI from music plan and rhythm.

    :param request: GenerateMidiRequest object
    """
    import base64

    session_id = str(uuid.uuid4())
    await progress_emitter.emit_progress(session_id, "midi_generation", "Starting MIDI generation...")

    try:
        await progress_emitter.emit_progress(session_id, "midi_generation", "Generating music notes...")
        music_notes = await notes_gen_service.generate_all_channel_notes(
            music_plan=request.music_plan, music_rhythm=request.music_rhythm, model=request.model, kwargs=request.kwargs
        )
        if not music_notes:
            await progress_emitter.emit_error(session_id, "midi_generation", "Failed to generate music notes")
            return {"result": None, "session_id": session_id}

        await progress_emitter.emit_progress(session_id, "midi_generation", "Converting notes to MIDI...")

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
        await progress_emitter.emit_progress(session_id, "midi_generation", "MIDI generated successfully")
        await progress_emitter.emit_complete(session_id, "midi_generation")
        return {"result": {"midi_data": midi_b64}, "session_id": session_id}
    except Exception as e:
        await progress_emitter.emit_error(session_id, "midi_generation", f"Error generating MIDI: {str(e)}")
        return {"result": None, "session_id": session_id}


async def convert_midi_to_audio(request: ConvertMidiToAudioRequest):
    session_id = str(uuid.uuid4())
    await progress_emitter.emit_progress(session_id, "audio_conversion", "Starting MIDI to audio conversion...")

    try:
        result = midi_to_audio(request.midi_data, request.soundfont)
        if result:
            await progress_emitter.emit_progress(session_id, "audio_conversion", "Audio conversion completed successfully")
            await progress_emitter.emit_complete(session_id, "audio_conversion")
        else:
            await progress_emitter.emit_error(session_id, "audio_conversion", "Failed to convert MIDI to audio")
        return {"result": result, "session_id": session_id}
    except Exception as e:
        await progress_emitter.emit_error(session_id, "audio_conversion", f"Error converting MIDI to audio: {str(e)}")
        return {"result": None, "session_id": session_id}
