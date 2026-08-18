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


def chat_stream(messages: list[dict]):
    """Generador de deltas de texto para la respuesta final (sin tools — esas ya se
    resolvieron antes de llamar acá). No hace streaming de la ronda de tool-calling: esa
    no es texto visible para el huésped, así que no aporta streamear su latencia."""
    stream = _client.chat.completions.create(
        model=MODEL, messages=messages, temperature=0.2, max_tokens=600, stream=True,
    )
    for chunk in stream:
        # Algunos chunks finales (ej. de uso/tokens) llegan sin "choices" — no son texto.
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
