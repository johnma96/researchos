from unittest.mock import AsyncMock, MagicMock

import pytest
from src.researchos.domain import Message
from src.researchos.infrastructure.llm.anthropic_llm import AnthropicLLM


@pytest.mark.unit
@pytest.mark.asyncio
async def test_anthropic_generate_unit():
    # 1. Crear la estructura falsa que devuelve Anthropic
    fake_content_block = MagicMock()
    fake_content_block.text = "respuesta falsa"

    fake_response = MagicMock()
    fake_response.content = [fake_content_block]

    # 2. Crear el cliente falso
    mock_client = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=fake_response)

    # 3. Instanciar AnthropicLLM e inyectar el cliente falso
    llm = AnthropicLLM()
    llm.client = mock_client

    # 4. Ejecutar
    msgs = [Message(role="user", content="Hola, este es mi primer llamado")]

    result = await llm.generate(messages=msgs)

    # 5. Verificar
    assert isinstance(result, str)
    assert result == "respuesta falsa"
    assert len(llm.client.messages.create.call_args_list) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_anthropic_stream_unit():
    # 1. Simular el objeto stream con text_stream iterable
    async def fake_text_stream():
        for token in ["hola ", "mundo "]:
            yield token

    mock_stream = MagicMock()
    mock_stream.text_stream = fake_text_stream()
    mock_stream.__aenter__ = AsyncMock(return_value=mock_stream)
    mock_stream.__aexit__ = AsyncMock(return_value=False)

    # 2. Crear el cliente falso
    mock_client = MagicMock()
    mock_client.messages.stream.return_value = mock_stream

    # 3. Instanciar AnthropicLLM e inyectar el cliente falso
    llm = AnthropicLLM()
    llm.client = mock_client

    # 4. Ejecutar y acumular tokens
    msgs = [Message(role="user", content="Hola")]
    result = ""
    async for token in llm.stream(messages=msgs):
        result += token

    # 5. Verificar
    assert isinstance(result, str)
    assert len(result) > 0
