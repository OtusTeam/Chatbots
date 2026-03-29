from __future__ import annotations

import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

from adapters.rates import RatesAdapter
from adapters.weather import WeatherAdapter
from api_client import ApiClient, ApiClientConfig


def build_client() -> ApiClient:
    cfg = ApiClientConfig(
        timeout=float(os.getenv("HTTP_TIMEOUT", "8.0")),
        connect_timeout=float(os.getenv("HTTP_CONNECT_TIMEOUT", "3.0")),
        retries=int(os.getenv("HTTP_RETRIES", "1")),
        backoff_seconds=float(os.getenv("HTTP_BACKOFF_SECONDS", "0.4")),
        cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "120")),
    )
    return ApiClient(cfg)


async def run() -> None:
    load_dotenv()
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN is not set in .env")

    client = build_client()
    weather = WeatherAdapter(client)
    rates = RatesAdapter(client)

    dp = Dispatcher()

    @dp.message(Command("start"))
    async def start_handler(message: Message) -> None:
        await message.answer(
            "Урок 28: надежный клиент внешних API.\n"
            "Команды:\n"
            "/weather <город>\n"
            "/rate <base> <quote>\n"
            "Примеры: /weather Berlin, /rate USD EUR"
        )

    @dp.message(Command("weather"))
    async def weather_handler(message: Message) -> None:
        parts = (message.text or "").split(maxsplit=1)
        if len(parts) < 2:
            await message.answer("Использование: /weather <город>")
            return
        city = parts[1].strip()
        try:
            result = weather.get_current_weather(city)
            await message.answer(
                f"Погода в {result.city}\n"
                f"{result.condition_ru}\n"
                f"Температура: {result.temperature_c} °C\n"
                f"Ветер: {result.wind_speed_ms} м/с\n"
                f"Код WMO: {result.weather_code}"
            )
        except Exception as err:
            await message.answer(f"Не удалось получить погоду: {err}")

    @dp.message(Command("rate"))
    async def rate_handler(message: Message) -> None:
        parts = (message.text or "").split()
        if len(parts) != 3:
            await message.answer("Использование: /rate <base> <quote>")
            return
        base, quote = parts[1], parts[2]
        try:
            result = rates.get_rate(base, quote)
            await message.answer(f"Курс {result.base}->{result.quote}: {result.rate} ({result.date})")
        except Exception as err:
            await message.answer(f"Не удалось получить курс: {err}")

    @dp.message(F.text)
    async def fallback(message: Message) -> None:
        await message.answer("Используйте /weather или /rate")

    bot = Bot(token=token)
    try:
        await dp.start_polling(bot)
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(run())
