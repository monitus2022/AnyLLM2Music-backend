from ..services import llm_service, music_plan_service
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