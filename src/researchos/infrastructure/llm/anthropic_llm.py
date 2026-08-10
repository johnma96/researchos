"""Anthropic LLM provider — Concrete implementation of the ``LLMProvider`` Protocol.

Wraps the ``anthropic`` async SDK to implement both one-shot generation and
token-by-token streaming.  All configuration (model, temperature, max_tokens)
is read from :data:`~researchos.config.settings` so no constructor arguments
are required at call sites.

Example:
    >>> from researchos.infrastructure.llm.anthropic_llm import AnthropicLLM
    >>> from researchos.domain.models import Message
    >>> llm = AnthropicLLM()
    >>> answer = await llm.generate([Message(role="user", content="Hello")])
"""

from collections.abc import AsyncIterator

from anthropic import AsyncAnthropic

from researchos.config import settings
from researchos.domain.exceptions import GenerationError
from researchos.domain.models import Message


class AnthropicLLM:
    """Anthropic Claude implementation of the LLMProvider protocol.

    Reads model configuration from :data:`~researchos.config.settings` and
    delegates to the official ``anthropic`` async SDK.  Supports both
    single-response generation and streaming.

    Attributes:
        client: Authenticated :class:`anthropic.AsyncAnthropic` instance.
        model_id: Claude model identifier (e.g. ``claude-haiku-4-5-20251001``).
        temperature: Sampling temperature forwarded to the API.
        max_tokens: Maximum number of tokens in the generated response.
    """

    def __init__(self) -> None:
        """Initialise the provider from application settings.

        No arguments are required; all credentials and parameters are read
        from :data:`~researchos.config.settings` (populated from ``.env``).
        """
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model_id = settings.default_model
        self.temperature = settings.temperature
        self.max_tokens = settings.max_tokens

    def _format_messages(self, messages: list[Message]) -> tuple[str | None, list[dict]]:
        """Separate the system prompt and format messages for the Anthropic API.

        The Anthropic API expects the system prompt as a top-level ``system``
        parameter rather than as an element of the ``messages`` list.  This
        method extracts the first ``role=="system"`` message (if any) and
        converts the remaining messages to the ``{role, content}`` dict schema.

        Args:
            messages: List of :class:`~researchos.domain.models.Message`
                objects in the conversation so far.

        Returns:
            A tuple of ``(system_prompt, formatted_messages)`` where
            ``system_prompt`` is the system instruction string or ``None``
            if no system message was provided, and ``formatted_messages`` is
            the list of dicts for the Anthropic ``messages`` parameter.
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
        """Generate a complete response from the Claude API.

        Sends the conversation to the Anthropic ``messages.create`` endpoint
        and returns the first text block of the response.

        Args:
            messages: Ordered list of :class:`~researchos.domain.models.Message`
                objects representing the conversation history.  May include a
                leading ``role=="system"`` message.

        Returns:
            The model's reply as a plain string.

        Raises:
            GenerationError: If the API returns an empty ``content`` list.
            anthropic.APIError: For network or API-level errors propagated from
                the SDK.
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
        """Stream the model response token by token.

        Uses the Anthropic streaming context manager so that each text delta
        is yielded immediately as it arrives.  Suitable for real-time UIs
        (e.g. Telegram bot with progressive message updates).

        Args:
            messages: Ordered list of :class:`~researchos.domain.models.Message`
                objects.  Same format as :meth:`generate`.

        Yields:
            Successive text fragments (tokens or token groups) from the model
            response, in order.

        Raises:
            anthropic.APIError: For network or API-level errors propagated from
                the SDK.
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
