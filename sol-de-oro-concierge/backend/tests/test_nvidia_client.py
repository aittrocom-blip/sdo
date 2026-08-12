from app.llm.nvidia_client import chat


def test_chat_returns_text_response():
    result = chat(messages=[{"role": "user", "content": "Responde solo con la palabra: listo"}])
    assert "content" in result
    assert isinstance(result["content"], str)
    assert len(result["content"]) > 0
