from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import django
from asgiref.sync import sync_to_async
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from botmanager.models import SenderType  # noqa: E402
from botmanager.services import (  # noqa: E402
    append_consultation_message,
    collect_metrics,
    create_enrollment_request,
    find_course_by_id,
    get_active_prompt,
    get_active_prompt_name,
    get_status_label,
    get_or_create_lead,
    get_or_create_open_consultation,
    list_active_courses,
    recent_orders_for_lead,
)


def _user_full_name(message: Message) -> str:
    first_name = message.from_user.first_name if message.from_user else ""
    last_name = message.from_user.last_name if message.from_user else ""
    full_name = f"{first_name} {last_name}".strip()
    return full_name or "Unknown user"


async def _ensure_lead(message: Message):
    if not message.from_user:
        return None
    return await sync_to_async(get_or_create_lead)(
        telegram_id=message.from_user.id,
        username=message.from_user.username or "",
        full_name=_user_full_name(message),
    )


async def run() -> None:
    load_dotenv(BASE_DIR.parent / ".env")
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN is not set in .env")

    dp = Dispatcher()

    @dp.message(Command("start"))
    async def start_handler(message: Message) -> None:
        lead = await _ensure_lead(message)
        if lead is None:
            return
        await message.answer(
            "Бот приёма заявок на обучающие курсы.\n"
            "Команды:\n"
            "/start\n"
            "/catalog\n"
            "/order <id_курса>\n"
            "/my_orders\n"
            "/consult <вопрос>\n"
            "/metrics\n"
            "/active_prompt\n"
            "/help"
        )

    @dp.message(Command("catalog"))
    async def catalog_handler(message: Message) -> None:
        courses = await sync_to_async(list_active_courses)()
        if not courses:
            await message.answer("Каталог временно пуст. Попробуйте позже.")
            return
        lines = ["Доступные курсы:"]
        for course in courses:
            lines.append(f"{course.id}. {course.title} — {course.price_rub} RUB")
        lines.append("\nЧтобы оставить заявку: /order <id_курса>")
        await message.answer("\n".join(lines))

    @dp.message(Command("order"))
    async def order_handler(message: Message) -> None:
        parts = (message.text or "").split(maxsplit=1)
        if len(parts) != 2 or not parts[1].isdigit():
            await message.answer("Использование: /order <id_курса>. Сначала посмотрите /catalog")
            return

        lead = await _ensure_lead(message)
        if lead is None:
            return
        if lead.is_blocked:
            await message.answer("Ваш аккаунт ограничен. Напишите оператору для уточнения.")
            return

        course = await sync_to_async(find_course_by_id)(int(parts[1]))
        if course is None:
            await message.answer("Курс не найден. Проверьте ID в /catalog.")
            return

        order = await sync_to_async(create_enrollment_request)(lead, course, actor="telegram-client")
        consultation = await sync_to_async(get_or_create_open_consultation)(lead, order)
        await sync_to_async(append_consultation_message)(
            consultation, SenderType.CLIENT, f"Оформлена заявка на курс: {course.title}"
        )
        await message.answer(
            "Заявка создана.\n"
            f"Номер заявки: #{order.id}\n"
            f"Курс: {course.title}\n"
            "Для консультации напишите /consult <ваш вопрос>"
        )

    @dp.message(Command("my_orders"))
    async def my_orders_handler(message: Message) -> None:
        lead = await _ensure_lead(message)
        if lead is None:
            return
        orders = await sync_to_async(recent_orders_for_lead)(lead, 5)
        if not orders:
            await message.answer("У вас пока нет заявок. Откройте каталог: /catalog")
            return
        lines = ["Ваши последние заявки:"]
        for order in orders:
            lines.append(f"#{order.id} | {order.course.title} | статус: {get_status_label(order.status)}")
        await message.answer("\n".join(lines))

    @dp.message(Command("consult"))
    async def consult_handler(message: Message) -> None:
        parts = (message.text or "").split(maxsplit=1)
        if len(parts) != 2:
            await message.answer("Использование: /consult <ваш вопрос>")
            return
        lead = await _ensure_lead(message)
        if lead is None:
            return
        consultation = await sync_to_async(get_or_create_open_consultation)(lead)
        await sync_to_async(append_consultation_message)(consultation, SenderType.CLIENT, parts[1])
        active_prompt = await sync_to_async(get_active_prompt)()
        bot_reply = (
            "Спасибо за вопрос. Оператор свяжется с вами и поможет выбрать курс."
            if active_prompt is None
            else f"Принял запрос. Работаем по шаблону: {active_prompt.name}. Оператор скоро ответит."
        )
        await sync_to_async(append_consultation_message)(consultation, SenderType.BOT, bot_reply)
        await message.answer(bot_reply)

    @dp.message(Command("metrics"))
    async def metrics_handler(message: Message) -> None:
        metrics = await sync_to_async(collect_metrics)()
        await message.answer(
            "Метрики:\n"
            f"- новых лидов сегодня: {metrics['new_leads_today']}\n"
            f"- открытых консультаций: {metrics['open_consultations']}\n"
            f"- заявок в ожидании оплаты: {metrics['waiting_payment_orders']}\n"
            f"- оплаченных заявок: {metrics['paid_orders']}\n"
            f"- действий операторов: {metrics['operator_actions']}\n"
            f"- активных промптов: {metrics['active_prompts']}"
        )

    @dp.message(Command("active_prompt"))
    async def active_prompt_handler(message: Message) -> None:
        prompt_name = await sync_to_async(get_active_prompt_name)()
        await message.answer(f"Активный промпт: {prompt_name}")

    @dp.message(Command("help"))
    async def help_handler(message: Message) -> None:
        await start_handler(message)

    @dp.message(F.text)
    async def fallback(message: Message) -> None:
        await message.answer(
            "Доступные команды: /start, /catalog, /order, /my_orders, /consult, /metrics, /active_prompt, /help"
        )

    bot = Bot(token=token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run())
