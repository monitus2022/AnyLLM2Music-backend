import uuid
from ..services import llm_service, music_plan_service, notes_gen_service
from ..services.progress import progress_emitter
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
    session_id = str(uuid.uuid4())
    await progress_emitter.emit_progress(session_id, "plan_generation", "Starting plan generation...")

    try:
        result = await music_plan_service.generate_music_plan_given_description(
            description=request.description, model=request.model, kwargs=request.kwargs
        )
        if result:
            await progress_emitter.emit_progress(session_id, "plan_generation", "Plan generated successfully")
            await progress_emitter.emit_complete(session_id, "plan_generation")
        else:
            await progress_emitter.emit_error(session_id, "plan_generation", "Failed to generate music plan")
        return {"result": result, "session_id": session_id}
    except Exception as e:
        await progress_emitter.emit_error(session_id, "plan_generation", f"Error generating plan: {str(e)}")
        return {"result": None, "session_id": session_id}

async def generate_chords(request: GenerateChordsRequest):
    """
    Generate music chords given a music plan.

    :param request: GenerateChordsRequest object
    """
    session_id = str(uuid.uuid4())
    await progress_emitter.emit_progress(session_id, "chords_generation", "Starting chords generation...")

    try:
        result = await music_plan_service.generate_music_chords_given_plan(
            music_plan=request.music_plan, description=request.description, model=request.model, kwargs=request.kwargs
        )
        if result:
            await progress_emitter.emit_progress(session_id, "chords_generation", "Chords generated successfully")
            await progress_emitter.emit_complete(session_id, "chords_generation")
        else:
            await progress_emitter.emit_error(session_id, "chords_generation", "Failed to generate music chords")
        return {"result": result, "session_id": session_id}
    except Exception as e:
        await progress_emitter.emit_error(session_id, "chords_generation", f"Error generating chords: {str(e)}")
        return {"result": None, "session_id": session_id}

async def generate_rhythm(request: GenerateRhythmRequest):
    """
    Generate music rhythm given music chords.

    :param request: GenerateRhythmRequest object
    """
    session_id = str(uuid.uuid4())
    await progress_emitter.emit_progress(session_id, "rhythm_generation", "Starting rhythm generation...")

    try:
        result = await music_plan_service.generate_music_rhythm_given_chords(
            music_chords=request.music_chords, description=request.description, model=request.model, kwargs=request.kwargs
        )
        if result:
            await progress_emitter.emit_progress(session_id, "rhythm_generation", "Rhythm generated successfully")
            await progress_emitter.emit_complete(session_id, "rhythm_generation")
        else:
            await progress_emitter.emit_error(session_id, "rhythm_generation", "Failed to generate music rhythm")
        return {"result": result, "session_id": session_id}
    except Exception as e:
        await progress_emitter.emit_error(session_id, "rhythm_generation", f"Error generating rhythm: {str(e)}")
        return {"result": None, "session_id": session_id}

async def generate_notes(request: GenerateNotesRequest):
    """
    Generate music notes given music plan and rhythm.

    :param request: GenerateNotesRequest object
    """
    session_id = str(uuid.uuid4())
    await progress_emitter.emit_progress(session_id, "notes_generation", "Starting notes generation...")

    try:
        result = await notes_gen_service.generate_all_channel_notes(
            music_plan=request.music_plan, music_rhythm=request.music_rhythm, model=request.model, kwargs=request.kwargs
        )
        if result:
            await progress_emitter.emit_progress(session_id, "notes_generation", "Notes generated successfully")
            await progress_emitter.emit_complete(session_id, "notes_generation")
        else:
            await progress_emitter.emit_error(session_id, "notes_generation", "Failed to generate music notes")
        return {"result": result, "session_id": session_id}
    except Exception as e:
        await progress_emitter.emit_error(session_id, "notes_generation", f"Error generating notes: {str(e)}")
        return {"result": None, "session_id": session_id}

