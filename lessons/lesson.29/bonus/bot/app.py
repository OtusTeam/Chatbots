from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

from bot.mistral_client import build_mistral_client_from_env
from bot.mcp_client import McpClient

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = ("name", "phone", "email")
FIELD_LABELS = {
    "name": "имя",
    "phone": "телефон",
    "email": "email",
}


def _build_mcp_args(decision: dict[str, Any]) -> dict[str, str]:
    args = decision.get("args") or {}
    if not isinstance(args, dict):
        return {}
    return {
        "name": str(args.get("name", "")).strip(),
        "phone": str(args.get("phone", "")).strip(),
        "email": str(args.get("email", "")).strip(),
        "comment": str(args.get("comment", "")).strip(),
        "source": str(args.get("source", "telegram-mcp-bot")).strip(),
    }


def _merge_non_empty(dst: dict[str, str], src: dict[str, str]) -> None:
    for key in REQUIRED_FIELDS:
        value = (src.get(key) or "").strip()
        if value:
            dst[key] = value
    source = (src.get("source") or "").strip()
    if source:
        dst["source"] = source


def _missing_fields(data: dict[str, str]) -> list[str]:
    missing: list[str] = []
    for key in REQUIRED_FIELDS:
        if not (data.get(key) or "").strip():
            missing.append(key)
    return missing


def _missing_fields_reply(missing: list[str]) -> str:
    readable = ", ".join(FIELD_LABELS[m] for m in missing)
    return f"Пожалуйста, пришлите недостающие данные: {readable}."


async def run() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    load_dotenv()
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN is not set")

    mcp_server_url = os.getenv("MCP_SERVER_URL", "http://mcp-server:8000").strip()
    mcp_client = McpClient(server_url=mcp_server_url)
    llm = build_mistral_client_from_env()
    chat_draft: dict[int, dict[str, str]] = {}
    logger.info("Bot started. MCP_SERVER_URL=%s", mcp_server_url)

    dp = Dispatcher()

    @dp.message(Command("start"))
    async def start_handler(message: Message) -> None:
        await message.answer(
            "Bonus lesson.29: бот с Mistral + MCP.\n"
            "Можно писать свободным текстом, команду /lead использовать не обязательно.\n"
            "Я дружелюбно помогу собрать данные для лида: имя, телефон и email обязательны, комментарий по желанию."
        )

    @dp.message(Command("tools"))
    async def tools_handler(message: Message) -> None:
        try:
            tools = mcp_client.list_tools()
            await message.answer(f"MCP tools: {tools}")
        except Exception as err:
            await message.answer(f"Не удалось получить tools: {err}")

    @dp.message(F.text)
    async def text_handler(message: Message) -> None:
        text = (message.text or "").strip()
        if not text:
            await message.answer("Пришлите текст с данными лида.")
            return
        logger.info("User message chat_id=%s text=%s", message.chat.id, text)

        chat_id = message.chat.id
        draft = chat_draft.get(chat_id, {"source": "telegram-mcp-bot"})
        decision = llm.decide_action(text, current_draft=draft)
        logger.info("Model decision chat_id=%s decision=%s", chat_id, decision)
        args = _build_mcp_args(decision)
        _merge_non_empty(draft, args)
        chat_draft[chat_id] = draft
        logger.info("Current lead draft chat_id=%s draft=%s", chat_id, draft)

        missing = _missing_fields(draft)
        if missing:
            base_reply = str(decision.get("reply", "")).strip()
            if base_reply:
                await message.answer(base_reply)
            else:
                await message.answer(_missing_fields_reply(missing))
            return

        try:
            draft.setdefault("comment", "")
            logger.info("MCP call chat_id=%s tool=create_lead arguments=%s", chat_id, draft)
            tool_result = mcp_client.call_tool("create_lead", draft)
            logger.info("MCP response chat_id=%s result=%s", chat_id, tool_result)
            result = tool_result.get("result", {})
            await message.answer(
                "Лид обработан через MCP tool:\n"
                f"provider={result.get('provider')}\n"
                f"ok={result.get('ok')}\n"
                f"duplicate={result.get('duplicate')}\n"
                f"entity_id={result.get('entity_id')}\n"
                f"message={result.get('message')}"
            )
            chat_draft.pop(chat_id, None)
        except Exception as err:
            logger.exception("MCP call failed chat_id=%s error=%s", chat_id, err)
            await message.answer(f"Ошибка вызова MCP tool: {err}")

    bot = Bot(token=token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run())
