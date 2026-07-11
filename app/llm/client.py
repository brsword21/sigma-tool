import asyncio
from typing import Any

from openai import AsyncOpenAI
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
                beta = getattr(self._client, "beta", None)
                parse = (
                    getattr(
                        getattr(getattr(beta, "chat", None), "completions", None),
                        "parse",
                        None,
                    )
                    if beta is not None
                    else None
                )
                if parse is not None:
                    response = await asyncio.wait_for(
                        parse(
                            model=self._model,
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": prompt},
                            ],
                            response_format=response_model,
                        ),
                        timeout=self._timeout,
                    )
                    parsed = response.choices[0].message.parsed
                    if parsed is None:
                        raise ValueError("empty or refused structured response")
                    return response_model.model_validate(parsed)
                response = await asyncio.wait_for(
                    self._client.chat.completions.create(
                        model=self._model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt},
                        ],
                        response_format={
                            "type": "json_schema",
                            "json_schema": {
                                "name": response_model.__name__.lower(),
                                "strict": True,
                                "schema": response_model.model_json_schema(),
                            },
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
                    "Zwróć wyłącznie dane zgodne ze schematem."
                )
        raise StructuredOutputError("LLM returned invalid structured output twice") from last_error


def validated_model(model: type[BaseModel], value: Any) -> BaseModel:
    return model.model_validate(value)
