from fastapi import APIRouter
from .llm import llm_health, create_music_plan, create_music_rhythm, create_music_notes, create_music_notes_with_cache, generate_plan, generate_chords, generate_rhythm, generate_notes
from .midi import generate_midi_from_cache, generate_midi_from_description, generate_midi

router = APIRouter()

@router.get("/")
def read_root():
    return {"app": "AnyLLM2Music"}

@router.get("/health")
def health_check():
    return {"status": "healthy"}

for r in [
    llm_health,
    create_music_plan,
    create_music_rhythm,
    create_music_notes,
    create_music_notes_with_cache,
    generate_midi_from_cache,
    generate_midi_from_description,
    generate_plan,
    generate_chords,
    generate_rhythm,
    generate_notes,
    generate_midi
    ]:
    method = ["POST"] if r.__name__ in ["generate_plan", "generate_chords", "generate_rhythm", "generate_notes", "generate_midi"] else ["GET"]
    router.add_api_route(
        path="/" + r.__name__,
        endpoint=r,
        methods=method,
        tags=["LLM Service"],
    )