from collections.abc import AsyncIterator

from anthropic import AsyncAnthropic

from researchos.config import settings
from researchos.domain.exceptions import GenerationError
from researchos.domain.models import Message


class AnthropicLLM:
    """Contract for Claude provider."""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model_id = settings.default_model
        self.temperature = settings.temperature
        self.max_tokens = settings.max_tokens

    def _format_messages(self, messages: list[Message]) -> tuple[str | None, list[dict]]:
        """
        Separa el system prompt (si existe) y formatea los mensajes
        para el esquema que espera Anthropic.
        """
        system_prompt = None
        formatted = []

        for msg in messages:
            if msg.role == "system":
                system_prompt = msg.content
            else:
                formatted.append({"role": msg.role, "content": msg.content})

        return system_prompt, formatted

    async def generate(self, messages: list[Message]) -> str:
        """Generate a response from a list of messages."""

        system, formatted_msgs = self._format_messages(messages)

        response = await self.client.messages.create(
            model=self.model_id,
            max_tokens=self.max_tokens,
            system=system or "",
            messages=formatted_msgs,
            temperature=self.temperature,
        )

        if response.content and len(response.content) > 0:
            return response.content[0].text
        else:
            raise GenerationError("Claude returned empty response")

    async def stream(self, messages: list[Message]) -> AsyncIterator[str]:
        """Stream a response token by token."""

        system, formatted_msgs = self._format_messages(messages)

        async with self.client.messages.stream(
            model=self.model_id,
            max_tokens=self.max_tokens,
            system=system or "",
            messages=formatted_msgs,
            temperature=self.temperature,
        ) as stream:
            async for text in stream.text_stream:
                yield text
