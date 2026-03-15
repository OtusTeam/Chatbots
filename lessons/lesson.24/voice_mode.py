"""
Опциональный Telegram-бот (polling) с голосовым режимом: при включённом режиме
принимает voice, распознаёт (STT), формирует ответ (заглушка LLM/RAG), озвучивает (TTS)
и отправляет текст и голос.

Основной бот урока 24 — webhook: main_webhook.py (приём текста и голоса, режим ответа текст/голос).
Зависимости: скрипты уроков 22 и 23 (sys.path). Запуск: BOT_TOKEN в .env, python voice_mode.py
"""
import asyncio
import os
import sys
import tempfile
from pathlib import Path

# Пути к скриптам уроков 22 и 23
_LESSON24 = Path(__file__).resolve().parent.parent
_LESSON22_SCRIPTS = _LESSON24.parent / "lesson.22" / "scripts"
_LESSON23_SCRIPTS = _LESSON24.parent / "lesson.23" / "scripts"
for p in (_LESSON22_SCRIPTS, _LESSON23_SCRIPTS, str(_LESSON24)):
    if p not in sys.path:
        sys.path.insert(0, str(p))

from dotenv import load_dotenv
load_dotenv(_LESSON24 / ".env")

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, BufferedInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command

# Импорты из уроков 22 и 23
try:
    from audio_convert import ogg_to_wav
    from stt_pipeline import load_model as load_stt_model, transcribe_with_fallback
except ImportError:
    audio_convert = None
    stt_pipeline = None

try:
    from tts_pipeline import synthesize
    from pydub import AudioSegment
except ImportError:
    synthesize = None
    AudioSegment = None

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("Задайте BOT_TOKEN в .env")
    sys.exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Включён ли голосовой режим по user_id (в памяти; для продакшена — БД/FSM)
voice_mode: dict[int, bool] = {}
STT_MODEL = None
MAX_VOICE_TEXT_LEN = 500


def get_voice_mode(user_id: int) -> bool:
    return voice_mode.get(user_id, False)


def set_voice_mode(user_id: int, on: bool) -> None:
    voice_mode[user_id] = on


def _get_stt_model():
    global STT_MODEL
    if STT_MODEL is None:
        STT_MODEL = load_stt_model()
    return STT_MODEL


def _llm_stub(user_text: str) -> str:
    """Заглушка вместо LLM/RAG: возвращает короткий ответ по тексту."""
    return f"Вы сказали: «{user_text[:200]}». Это демо голосового режима; для полного ответа подключите LLM или RAG."


def wav_to_ogg_bytes(wav_data: bytes) -> bytes:
    from io import BytesIO
    seg = AudioSegment.from_file(BytesIO(wav_data), format="wav")
    out = BytesIO()
    seg.export(out, format="ogg", codec="libopus")
    out.seek(0)
    return out.read()


@dp.message(Command("voice"))
async def cmd_voice(message: Message) -> None:
    """Команда /voice — переключатель голосового режима."""
    user_id = message.from_user.id if message.from_user else 0
    current = get_voice_mode(user_id)
    set_voice_mode(user_id, not current)
    new_state = get_voice_mode(user_id)
    status = "включён" if new_state else "выключен"
    await message.reply(
        f"Голосовой режим {status}. Отправьте голосовое сообщение — бот распознает его и ответит текстом и голосом.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Вкл/выкл голосовой режим", callback_data="toggle_voice")],
        ]),
    )


@dp.callback_query(F.data == "toggle_voice")
async def cb_toggle_voice(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id if callback.from_user else 0
    set_voice_mode(user_id, not get_voice_mode(user_id))
    status = "включён" if get_voice_mode(user_id) else "выключен"
    await callback.answer(f"Голосовой режим {status}")
    await callback.message.edit_text(f"Голосовой режим {status}. Отправьте голосовое — получите ответ текстом и голосом.")


@dp.message(F.voice)
async def on_voice(message: Message) -> None:
    """Обработка голосового: только если голосовой режим включён."""
    user_id = message.from_user.id if message.from_user else 0
    if not get_voice_mode(user_id):
        await message.reply("Голосовой режим выключен. Включите командой /voice.")
        return
    await message.bot.send_chat_action(message.chat.id, "typing")
    try:
        file = await message.bot.get_file(message.voice.file_id)
        if not file.file_path:
            await message.reply("Не удалось получить файл.")
            return
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            ogg_path = tmp.name
        try:
            await message.bot.download_file(file.file_path, ogg_path)
            wav_path = ogg_path.replace(".ogg", ".wav")
            ogg_to_wav(ogg_path, wav_path)
            model = _get_stt_model()
            text, lang, err = transcribe_with_fallback(wav_path, model=model, language="ru")
            if err:
                await message.reply(err)
                return
            if not text:
                await message.reply("Речь не распознана. Попробуйте ещё раз.")
                return
            answer_text = _llm_stub(text)
            if len(answer_text) > MAX_VOICE_TEXT_LEN:
                answer_text = answer_text[:MAX_VOICE_TEXT_LEN] + "..."
            await message.reply(answer_text)
            try:
                wav_bytes = synthesize(answer_text, output_path=None, use_cache=True)
                if isinstance(wav_bytes, Path):
                    wav_bytes = wav_bytes.read_bytes()
                ogg_bytes = wav_to_ogg_bytes(wav_bytes)
                await message.reply_voice(voice=BufferedInputFile(ogg_bytes, filename="voice.ogg"))
            except Exception as e:
                await message.reply(f"Озвучка не удалась: {e!s}")
        finally:
            for p in (ogg_path, ogg_path.replace(".ogg", ".wav")):
                if os.path.exists(p):
                    try:
                        os.unlink(p)
                    except OSError:
                        pass
    except Exception as e:
        await message.reply(f"Ошибка: {e!s}")


@dp.message(F.text)
async def on_text(message: Message) -> None:
    """Текстовые сообщения: краткий ответ без озвучки (или можно добавить озвучку по кнопке)."""
    text = (message.text or "").strip()
    if not text:
        return
    if get_voice_mode(message.from_user.id if message.from_user else 0):
        await message.reply("Голосовой режим включён. Отправьте голосовое сообщение для ответа голосом и текстом.")
        return
    await message.reply(_llm_stub(text))


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
