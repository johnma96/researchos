import pytest

from researchos.domain import Message
from researchos.infrastructure.llm.anthropic_llm import AnthropicLLM


@pytest.mark.integration
@pytest.mark.asyncio
async def test_anthropic_generate_integration():
    llm = AnthropicLLM()

    # 4. Ejecutar
    msgs = [Message(role="user", content="Hola, este es mi primer llamado")]

    result = await llm.generate(messages=msgs)

    # 5. Verificar
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_anthropic_stream_integration():
    llm = AnthropicLLM()

    msgs = [Message(role="user", content="Di hola en una palabra")]

    result = ""
    async for token in llm.stream(messages=msgs):
        result += token

    assert isinstance(result, str)
    assert len(result) > 0
