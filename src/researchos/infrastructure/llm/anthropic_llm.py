from collections.abc import AsyncIterator

from anthropic import AsyncAnthropic

from researchos.config import settings
from researchos.domain.exceptions import GenerationError
from researchos.domain.models import Message


class AnthropicLLM:
    """Anthropic Claude implementation of the LLMProvider protocol.

    Wraps the async Anthropic SDK client, reading model configuration
    from application settings. Supports both single-shot generation and
    token-by-token streaming.
    """

    def __init__(self):
        """Initialize the client using credentials and defaults from settings."""
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model_id = settings.default_model
        self.temperature = settings.temperature
        self.max_tokens = settings.max_tokens

    def _format_messages(self, messages: list[Message]) -> tuple[str | None, list[dict]]:
        """Split out the system prompt and convert messages to the Anthropic wire format.

        Args:
            messages: Conversation history including optional system message.

        Returns:
            A tuple of (system_prompt, formatted_messages) where system_prompt is
            the content of the first system-role message (or None), and
            formatted_messages is the remaining messages as dicts.
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
        """Generate a complete response from a conversation history.

        Args:
            messages: Conversation history. A system-role message, if present,
                is extracted and sent as the Anthropic ``system`` parameter.

        Returns:
            The text content of the first content block in the response.

        Raises:
            GenerationError: If the model returns an empty response.
            anthropic.APIError: On network or API-level failures.
        """

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
        """Stream a response token by token from a conversation history.

        Args:
            messages: Conversation history. A system-role message, if present,
                is extracted and sent as the Anthropic ``system`` parameter.

        Yields:
            Successive text chunks as they arrive from the model.

        Raises:
            anthropic.APIError: On network or API-level failures.
        """

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
