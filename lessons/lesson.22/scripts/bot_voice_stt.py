"""
Демо-бот Telegram: при получении голосового сообщения скачивает OGG,
конвертирует в WAV, распознаёт речь через Faster-Whisper и отвечает текстом.

Запуск: задайте BOT_TOKEN в .env, затем
  python bot_voice_stt.py
"""
import asyncio
import os
import sys
import tempfile
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_LESSON_DIR = _SCRIPT_DIR.parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
if str(_LESSON_DIR) not in sys.path:
    sys.path.insert(0, str(_LESSON_DIR))

from dotenv import load_dotenv
load_dotenv(_LESSON_DIR / ".env")

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message

from audio_convert import ogg_to_wav
from stt_pipeline import load_model, transcribe_with_fallback

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("Задайте BOT_TOKEN в .env")
    sys.exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

whisper_model = None


def get_model():
    global whisper_model
    if whisper_model is None:
        whisper_model = load_model()
    return whisper_model


@dp.message(F.voice)
async def on_voice(message: Message) -> None:
    """Обрабатывает голосовое сообщение: скачивает OGG → WAV → STT → ответ текстом."""
    await message.bot.send_chat_action(message.chat.id, "typing")
    file_id = message.voice.file_id
    try:
        file = await message.bot.get_file(file_id)
        file_path = file.file_path
        if not file_path:
            await message.reply("Не удалось получить файл.")
            return
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp_ogg:
            ogg_path = tmp_ogg.name
        try:
            await message.bot.download_file(file_path, ogg_path)
            wav_path = ogg_path.replace(".ogg", ".wav")
            ogg_to_wav(ogg_path, wav_path)
            model = get_model()
            text, lang, err = transcribe_with_fallback(wav_path, model=model, language="ru")
            if err:
                await message.reply(err)
            elif not text:
                await message.reply("Речь не распознана. Попробуйте записать ещё раз.")
            else:
                await message.reply(f"Распознано ({lang or '?'}):\n\n{text}")
        finally:
            for p in (ogg_path, ogg_path.replace(".ogg", ".wav")):
                if os.path.exists(p):
                    try:
                        os.unlink(p)
                    except OSError:
                        pass
    except Exception as e:
        await message.reply(f"Ошибка: {e!s}")


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
