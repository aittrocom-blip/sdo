from openai import OpenAI

from app.config.settings import settings

_client = OpenAI(base_url=settings.nvidia_base_url, api_key=settings.nvidia_api_key)

MODEL = "meta/llama-3.1-8b-instruct"


def chat(messages: list[dict], tools: list[dict] | None = None) -> dict:
    kwargs: dict = dict(model=MODEL, messages=messages, temperature=0.2, max_tokens=600)
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"
    response = _client.chat.completions.create(**kwargs)
    message = response.choices[0].message
    return {
        "content": message.content,
        "tool_calls": [
            {"id": tc.id, "name": tc.function.name, "arguments": tc.function.arguments}
            for tc in (message.tool_calls or [])
        ],
    }
