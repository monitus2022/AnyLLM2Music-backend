from fastapi import APIRouter
from .llm import llm_health, create_music_plan

router = APIRouter()

@router.get("/")
def read_root():
    return {"app": "AnyLLM2Music"}

@router.get("/health")
def health_check():
    return {"status": "healthy"}

for r in [
    llm_health,
    create_music_plan
    ]:
    router.add_api_route(
        path="/" + r.__name__,
        endpoint=r,
        methods=["GET"],
        tags=["LLM Service"],
    )