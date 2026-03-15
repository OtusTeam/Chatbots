"""
Обработка текстовых и голосовых сообщений: GigaChat LLM и ответ текстом или голосом по режиму.
"""
import logging
import os
import tempfile
from pathlib import Path

from aiogram import Router, types, F
from aiogram.types import BufferedInputFile

from app.services.response_mode import get_response_mode
from app.services.voice import (
    ogg_to_wav,
    wav_to_ogg_bytes,
    load_stt_model,
    transcribe_with_fallback,
    synthesize,
)
from app.services.llm import get_llm_reply

logger = logging.getLogger(__name__)
router = Router()

MAX_VOICE_TEXT_LEN = 500

_stt_model = None


def _get_stt_model():
    global _stt_model
    if _stt_model is None:
        _stt_model = load_stt_model()
    return _stt_model


async def _send_answer(message: types.Message, answer_text: str, user_id: int) -> None:
    """Отправляет ответ: в режиме «текст» — только текстом, в режиме «голос» — только голосом."""
    if len(answer_text) > MAX_VOICE_TEXT_LEN:
        answer_text = answer_text[:MAX_VOICE_TEXT_LEN] + "..."
    if get_response_mode(user_id) == "voice":
        try:
            wav_bytes = synthesize(answer_text, output_path=None, use_cache=True)
            if isinstance(wav_bytes, Path):
                wav_bytes = wav_bytes.read_bytes()
            ogg_bytes = wav_to_ogg_bytes(wav_bytes)
            await message.reply_voice(voice=BufferedInputFile(ogg_bytes, filename="voice.ogg"))
        except Exception as e:
            logger.warning("TTS failed: %s", e)
            await message.reply("Озвучка не удалась.")
    else:
        await message.reply(answer_text)


@router.message(F.text)
async def on_text(message: types.Message) -> None:
    """Текстовое сообщение → LLM → ответ текстом или текстом + голосом по режиму."""
    text = (message.text or "").strip()
    if not text:
        return
    user_id = message.from_user.id if message.from_user else 0
    await message.bot.send_chat_action(message.chat.id, "typing")
    answer_text = get_llm_reply(text)
    await _send_answer(message, answer_text, user_id)


@router.message(F.voice)
async def on_voice(message: types.Message) -> None:
    """Голосовое сообщение → OGG → WAV → STT → LLM → ответ текстом или текстом + голосом по режиму."""
    user_id = message.from_user.id if message.from_user else 0
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
            text, _lang, err = transcribe_with_fallback(wav_path, model=model, language="ru")
            if err:
                await message.reply(err)
                return
            if not (text and text.strip()):
                await message.reply("Речь не распознана. Попробуйте ещё раз.")
                return
            answer_text = get_llm_reply(text.strip())
            await _send_answer(message, answer_text, user_id)
        finally:
            for p in (ogg_path, ogg_path.replace(".ogg", ".wav")):
                if os.path.exists(p):
                    try:
                        os.unlink(p)
                    except OSError:
                        pass
    except Exception as e:
        logger.exception("Voice handling error")
        await message.reply(f"Ошибка: {e!s}")
