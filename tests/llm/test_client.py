from types import SimpleNamespace

from pydantic import BaseModel

from app.llm.client import OpenAIStructuredClient


class Answer(BaseModel):
    value: int


class Completions:
    def __init__(self) -> None:
        self.calls = 0

    async def create(self, **kwargs: object) -> SimpleNamespace:
        self.calls += 1
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
