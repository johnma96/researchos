"""Telegram bot adapter — delivery channel for the RAG engine."""

import logging
from collections.abc import Awaitable, Callable

from telegram import Update
from telegram.constants import MessageLimit
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

logger = logging.getLogger(__name__)

AnswerFn = Callable[[str], Awaitable[str]]


def _split_message(text: str, limit: int = MessageLimit.MAX_TEXT_LENGTH) -> list[str]:
    """Split text into chunks that fit Telegram's per-message character limit.

    Breaks on the last whitespace before ``limit`` when possible, so words
    aren't cut in half. Falls back to a hard cut if a single token exceeds
    the limit on its own.
    """
    chunks = []
    while len(text) > limit:
        split_at = text.rfind(" ", 0, limit)
        if split_at <= 0:
            split_at = limit
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip()
    chunks.append(text)
    return chunks


class TelegramBot:
    def __init__(self, token: str, answer_fn: AnswerFn) -> None:
        self.token_telegram = token
        self.answer_fn = answer_fn

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        raw_text = update.message.text

        logger.info("Mensaje recibido: %s", raw_text[:80])

        answer_llm = await self.answer_fn(raw_text)
        for chunk in _split_message(answer_llm):
            await update.message.reply_text(chunk)

    def run(self) -> None:
        app = ApplicationBuilder().token(self.token_telegram).build()
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))
        app.run_polling()
