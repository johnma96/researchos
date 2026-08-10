"""Telegram bot adapter — delivery channel for the RAG engine."""

import logging
from collections.abc import Awaitable, Callable

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

logger = logging.getLogger(__name__)

AnswerFn = Callable[[str], Awaitable[str]]


class TelegramBot:
    def __init__(self, token: str, answer_fn: AnswerFn) -> None:
        self.token_telegram = token
        self.answer_fn = answer_fn

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        raw_text = update.message.text

        logger.info("Mensaje recibido: %s", raw_text[:80])

        answer_llm = await self.answer_fn(raw_text)
        await update.message.reply_text(answer_llm)

    def run(self) -> None:
        print(self.token_telegram)
        app = ApplicationBuilder().token(self.token_telegram).build()
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))
        app.run_polling()
