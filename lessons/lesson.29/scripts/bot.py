from __future__ import annotations

import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

from crm_client import CrmClient
from models import LeadPayload


async def run() -> None:
    load_dotenv()
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN is not set in .env")

    crm_client = CrmClient.from_env()
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def start_handler(message: Message) -> None:
        await message.answer(
            "Урок 29: CRM интеграция.\n"
            "Отправьте команду:\n"
            "/lead <имя>; <телефон>; <email>; <комментарий>\n"
            "Пример:\n"
            "/lead Ivan; +79991112233; ivan@example.com; Хочу консультацию"
        )

    @dp.message(Command("lead"))
    async def lead_handler(message: Message) -> None:
        text = message.text or ""
        body = text[len("/lead") :].strip()
        parts = [p.strip() for p in body.split(";")]
        if len(parts) != 4:
            await message.answer("Неверный формат. Используйте: /lead <имя>; <телефон>; <email>; <комментарий>")
            return

        payload = LeadPayload(name=parts[0], phone=parts[1], email=parts[2], comment=parts[3])
        try:
            result = crm_client.create_lead(payload)
            await message.answer(
                f"CRM: {result.provider}\n"
                f"ok={result.ok}\n"
                f"duplicate={result.duplicate}\n"
                f"entity_id={result.entity_id}\n"
                f"message={result.message}"
            )
        except Exception as err:
            await message.answer(f"Ошибка CRM: {err}")

    @dp.message(F.text)
    async def fallback(message: Message) -> None:
        await message.answer("Используйте /lead для отправки анкеты.")

    bot = Bot(token=token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run())
