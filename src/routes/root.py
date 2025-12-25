from fastapi import APIRouter
from .llm import *

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
    generate_midi_from_description
    ]:
    router.add_api_route(
        path="/" + r.__name__,
        endpoint=r,
        methods=["GET"],
        tags=["LLM Service"],
    )