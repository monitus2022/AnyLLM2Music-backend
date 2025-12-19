from ..services.llm import llm_service
from fastapi import Query
from typing import Optional

def llm_health(model: Optional[str] = Query(default=None, description="LLM model to check")):
    """
    Health check endpoint for any model in LLM service.

    :param model: model name to check
    """
    return llm_service.health_check(model=model)