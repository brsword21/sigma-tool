import asyncio
from typing import Any

from openai import AsyncOpenAI
from openai.lib._pydantic import to_strict_json_schema
from pydantic import BaseModel, ValidationError

from app.services.ports import ResponseT


class StructuredOutputError(RuntimeError):
    pass


class OpenAIStructuredClient:
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        client: AsyncOpenAI | None = None,
        timeout_seconds: float = 30,
    ) -> None:
        self._client = client or AsyncOpenAI(
            api_key=api_key, max_retries=0, timeout=timeout_seconds
        )
        self._model = model
        self._timeout = timeout_seconds

    async def structured_response(
        self, *, system_prompt: str, user_prompt: str, response_model: type[ResponseT]
    ) -> ResponseT:
        last_error: Exception | None = None
        prompt = user_prompt
        for _attempt in range(2):
            try:
                schema_format = {
                    "type": "json_schema",
                    "name": response_model.__name__.lower(),
                    "strict": True,
                    "schema": _openai_strict_schema(response_model),
                }
                responses = getattr(self._client, "responses", None)
                if responses is not None and hasattr(responses, "create"):
                    response = await asyncio.wait_for(
                        responses.create(
                            model=self._model,
                            instructions=system_prompt,
                            input=prompt,
                            text={"format": schema_format},
                        ),
                        timeout=self._timeout,
                    )
                    content = response.output_text
                else:
                    response = await asyncio.wait_for(
                        self._client.chat.completions.create(
                            model=self._model,
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": prompt},
                            ],
                            response_format={
                                "type": "json_schema",
                                "json_schema": schema_format,
                            },
                        ),
                        timeout=self._timeout,
                    )
                    content = response.choices[0].message.content
                if not content:
                    raise ValueError("empty structured response")
                return response_model.model_validate_json(content)
            except (TimeoutError, ValidationError, ValueError, IndexError) as exc:
                last_error = exc
                prompt = (
                    f"{user_prompt}\nPoprzednia odpowiedź była niepoprawna. "
                    "Zwróć wyłącznie dane zgodne ze schematem. "
                    f"Problemy walidacji: {_validation_messages(exc)}"
                )
        raise StructuredOutputError("LLM returned invalid structured output twice") from last_error


def _openai_strict_schema(response_model: type[BaseModel]) -> dict[str, Any]:
    schema = to_strict_json_schema(response_model)
    _remove_unsupported_formats(schema)
    return schema


def _remove_unsupported_formats(value: object) -> None:
    if isinstance(value, dict):
        value.pop("format", None)
        for item in value.values():
            _remove_unsupported_formats(item)
    elif isinstance(value, list):
        for item in value:
            _remove_unsupported_formats(item)


def _validation_messages(error: Exception) -> str:
    if isinstance(error, ValidationError):
        messages = [str(item.get("msg", "invalid value")) for item in error.errors()]
        return "; ".join(messages)[:500]
    return type(error).__name__


def validated_model(model: type[BaseModel], value: Any) -> BaseModel:
    return model.model_validate(value)
