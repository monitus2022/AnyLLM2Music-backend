import pytest
from unittest.mock import Mock
from src.services.llm import LlmService
from src.schemas.openrouter import PromptRequest, CompletionKwargs

@pytest.fixture
def mocked_client(monkeypatch):
    mock_client = Mock()
    monkeypatch.setattr("src.services.llm.OpenAI", lambda *args, **kwargs: mock_client)
    return mock_client

def test_llm_service_initialization_openrouter(mocked_client):
    service = LlmService(llm_provider="openrouter")
    assert service.llm_provider == "openrouter"
    assert service.client == mocked_client

def test_prompt_llm_openrouter(mocked_client):
    service = LlmService(llm_provider="openrouter")
    mocked_response = Mock()
    mocked_response.choices = [Mock()]
    mocked_response.choices[0].message = Mock()
    mocked_response.choices[0].message.content = "Test response"
    mocked_client.chat.completions.create.return_value = mocked_response

    mocked_user_messages = "Hello, LLM!"
    mocked_system_messages = "You are a helpful assistant."
    mocked_model = "llama3"
    mocked_config = {"temperature": 0.7}

    prompt_request = PromptRequest(
        user_messages=mocked_user_messages,
        system_messages=mocked_system_messages,
        model=mocked_model,
        kwargs=CompletionKwargs(**mocked_config)
    )

    response = service.prompt_llm(prompt_request)

    mocked_client.chat.completions.create.assert_called_once_with(
        model=mocked_model,
        messages=[
            {"role": "user", "content": mocked_user_messages},
            {"role": "system", "content": mocked_system_messages},
        ],
        **mocked_config
    )
    assert response == "Test response"

def test_llm_service_unsupported_provider():
    mocked_provider = "unsupported_llm"
    with pytest.raises(ValueError) as excinfo:
        LlmService(llm_provider=mocked_provider)
    assert str(excinfo.value) == f"Unsupported LLM provider: {mocked_provider}"
