from types import SimpleNamespace

from pydantic import BaseModel, HttpUrl

from app.llm.client import OpenAIStructuredClient


class Answer(BaseModel):
    value: int


class Completions:
    def __init__(self) -> None:
        self.calls = 0
        self.kwargs: list[dict[str, object]] = []

    async def create(self, **kwargs: object) -> SimpleNamespace:
        self.calls += 1
        self.kwargs.append(kwargs)
        content = '{"wrong": true}' if self.calls == 1 else '{"value": 42}'
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


async def test_invalid_structured_output_is_retried_once() -> None:
    completions = Completions()
    sdk = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    client = OpenAIStructuredClient("test", client=sdk)
    answer = await client.structured_response(
        system_prompt="system", user_prompt="user", response_model=Answer
    )
    assert answer.value == 42
    assert completions.calls == 2
    retry_messages = completions.kwargs[1]["messages"]
    assert "Field required" in retry_messages[1]["content"]


class UrlAnswer(BaseModel):
    url: HttpUrl


class UrlCompletions:
    def __init__(self) -> None:
        self.kwargs: dict[str, object] = {}

    async def create(self, **kwargs: object) -> SimpleNamespace:
        self.kwargs = kwargs
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content='{"url":"https://example.com/item"}')
                )
            ]
        )


def _contains_format(value: object) -> bool:
    if isinstance(value, dict):
        return "format" in value or any(_contains_format(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_format(item) for item in value)
    return False


async def test_strict_schema_omits_unsupported_uri_format_but_validates_url() -> None:
    completions = UrlCompletions()
    sdk = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    client = OpenAIStructuredClient("test", client=sdk)

    answer = await client.structured_response(
        system_prompt="system", user_prompt="user", response_model=UrlAnswer
    )

    response_format = completions.kwargs["response_format"]
    assert not _contains_format(response_format)
    assert str(answer.url) == "https://example.com/item"


class Responses:
    def __init__(self) -> None:
        self.kwargs: dict[str, object] = {}

    async def create(self, **kwargs: object) -> SimpleNamespace:
        self.kwargs = kwargs
        return SimpleNamespace(output_text='{"value":42}')


async def test_responses_api_is_preferred_when_available() -> None:
    responses = Responses()
    sdk = SimpleNamespace(responses=responses)
    client = OpenAIStructuredClient("test", client=sdk)

    answer = await client.structured_response(
        system_prompt="system", user_prompt="user", response_model=Answer
    )

    assert answer.value == 42
    assert responses.kwargs["instructions"] == "system"
    assert responses.kwargs["input"] == "user"
    text_config = responses.kwargs["text"]
    assert not _contains_format(text_config["format"]["schema"])
