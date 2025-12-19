from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class BasePromptMessages(BaseModel):
    user_messages: str = Field(..., description="User messages")
    system_messages: str = Field(..., description="System messages")

    def to_list(self) -> List[Dict[str, str]]:
        return [
            {"role": "user", "content": self.user_messages},
            {"role": "system", "content": self.system_messages},
        ]

class CompletionKwargs(BaseModel):
    temperature: Optional[float] = Field(None, description="Sampling temperature between 0 and 2")
    max_tokens: Optional[int] = Field(None, description="Maximum number of tokens to generate")
    top_p: Optional[float] = Field(None, description="Top-p sampling value")
    frequency_penalty: Optional[float] = Field(None, description="Frequency penalty")
    presence_penalty: Optional[float] = Field(None, description="Presence penalty")
    stop: Optional[List[str]] = Field(None, description="Stop sequences")

class PromptRequest(BaseModel):
    user_messages: str = Field(..., description="User messages for the prompt")
    system_messages: str = Field(..., description="System messages for the prompt")
    model: Optional[str] = Field(None, description="Model to use")
    kwargs: CompletionKwargs = Field(default_factory=CompletionKwargs, description="Optional extra kwargs for completion")

class OpenRouterPromptTemplate(BaseModel):
    model: str = Field(..., description="The model to use for the prompt")
    messages : BasePromptMessages = Field(..., description="The prompt messages")