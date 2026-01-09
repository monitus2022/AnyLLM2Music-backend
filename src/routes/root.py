from fastapi import APIRouter
from .llm import llm_health, generate_plan, generate_chords, generate_rhythm, generate_notes
from .midi import generate_midi, convert_midi_to_audio

router = APIRouter()


@router.get("/")
def read_root():
    return {"app": "AnyLLM2Music"}


@router.get("/health")
def health_check():
    return {"status": "healthy"}


for r in [
    llm_health,
    generate_plan,
    generate_chords,
    generate_rhythm,
    generate_notes,
    generate_midi,
    convert_midi_to_audio
]:
    method = ["POST"] if r.__name__ in ["generate_plan", "generate_chords",
                                        "generate_rhythm", "generate_notes", "generate_midi", "convert_midi_to_audio"] else ["GET"]
    router.add_api_route(
        path="/" + r.__name__,
        endpoint=r,
        methods=method,
        tags=["LLM Service"],
    )
