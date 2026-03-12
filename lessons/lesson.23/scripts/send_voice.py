import asyncio
import os
import sys
from pathlib import Path

from pydub import AudioSegment

_SCRIPT_DIR = Path(__file__).resolve().parent
_LESSON_DIR = _SCRIPT_DIR.parent
sys.path.insert(0, str(_SCRIPT_DIR))
sys.path.insert(0, str(_LESSON_DIR))

from dotenv import load_dotenv
load_dotenv(_LESSON_DIR / ".env")

from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ChatAction
from aiogram.types import BufferedInputFile, Message

from tts_pipeline import synthesize

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("Задайте BOT_TOKEN в .env")
    sys.exit(1)

REQUEST_TIMEOUT = 300
session = AiohttpSession(timeout=REQUEST_TIMEOUT)
bot = Bot(token=BOT_TOKEN, session=session)
dp = Dispatcher()

MAX_TEXT_LEN = 1500
VOICE_ID = os.getenv("VOICE_ID", None)  # None = default из voices.json
SPEED = float(os.getenv("TTS_SPEED", "1.0"))
VOLUME_DB = float(os.getenv("TTS_VOLUME_DB", "0.0"))
TTS_DEVICE = os.getenv("TTS_DEVICE", "cuda")


def wav_to_ogg_bytes(wav_data: bytes) -> bytes:
    from io import BytesIO
    seg = AudioSegment.from_file(BytesIO(wav_data), format="wav")
    out = BytesIO()
    seg.export(out, format="ogg", codec="libopus")
    out.seek(0)
    return out.read()


@dp.message(F.text)
async def on_text(message: Message) -> None:
    text = (message.text or "").strip()
    if not text:
        return
    if len(text) > MAX_TEXT_LEN:
        await message.reply(f"Текст слишком длинный (максимум {MAX_TEXT_LEN} символов).")
        return
    await message.bot.send_chat_action(message.chat.id, ChatAction.RECORD_VOICE)
    try:
        device = None if TTS_DEVICE == "auto" else TTS_DEVICE
        wav_bytes = synthesize(
            text, output_path=None,
            voice_id=VOICE_ID, speed=SPEED, volume_db=VOLUME_DB,
            use_cache=True, device=device,
        )
        if isinstance(wav_bytes, Path):
            wav_bytes = wav_bytes.read_bytes()
        ogg_bytes = wav_to_ogg_bytes(wav_bytes)
        await message.reply_voice(voice=BufferedInputFile(ogg_bytes, filename="voice.ogg"))
    except Exception as e:
        await message.reply(f"Ошибка озвучки: {e!s}")


if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
