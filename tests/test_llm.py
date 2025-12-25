import pytest
from unittest.mock import Mock, patch
from src.services.llm import LlmService
from src.services.midi import duration_to_ticks, pitch_to_midi
from src.schemas.openrouter import PromptRequest, CompletionKwargs

@patch.dict('os.environ', {'OPENROUTER_API_KEY': 'fake'})
def test_llm_service_initialization_openrouter():
    service = LlmService(llm_provider="openrouter")
    assert service.llm_provider == "openrouter"
    assert service.client is None

@patch('instructor.from_provider')
@patch.dict('os.environ', {'OPENROUTER_API_KEY': 'fake'})
def test_prompt_llm_openrouter(mock_instructor):
    mock_client = Mock()
    mock_instructor.return_value = mock_client

    service = LlmService(llm_provider="openrouter")
    mocked_response = "Test response"
    mocked_completion = Mock()
    mock_client.create_with_completion.return_value = (mocked_response, mocked_completion)
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

    mock_client.create_with_completion.assert_called_once_with(
        model=mocked_model,
        messages=[
            {"role": "user", "content": mocked_user_messages},
            {"role": "system", "content": mocked_system_messages},
        ],
        response_model=None,
        **mocked_config,
        max_retries=3
    )
    assert response == "Test response"

def test_llm_service_unsupported_provider():
    mocked_provider = "unsupported_llm"
    with pytest.raises(ValueError) as excinfo:
        LlmService(llm_provider=mocked_provider)
    assert str(excinfo.value) == f"Unsupported LLM provider: {mocked_provider}"

def test_duration_to_ticks():
    assert duration_to_ticks("quarter") == 480
    assert duration_to_ticks("sixteenth") == 120
    assert duration_to_ticks("dotted_eighth") == 360
    with pytest.raises(ValueError):
        duration_to_ticks("unknown")

def test_pitch_to_midi():
    assert pitch_to_midi("C4") == 60
    assert pitch_to_midi(60) == 60
    assert pitch_to_midi("rest") == -1
    assert pitch_to_midi("kick", is_percussion=True) == 36
