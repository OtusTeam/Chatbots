"""
Telegram-бот: распознавание голоса через GigaAM-v3.

Голосовое сообщение: OGG → WAV → GigaAM → ответ текстом.
Требуется BOT_TOKEN в .env (bonus или lesson.22).
"""
import asyncio
import logging
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Optional

if sys.version_info < (3, 10):
    print("Ошибка: нужен Python 3.10+ (сейчас %s)." % sys.version.split()[0], file=sys.stderr)
    sys.exit(1)

_BONUS_DIR = Path(__file__).resolve().parent
_LESSON22_SCRIPTS = _BONUS_DIR.parent / "scripts"
if str(_LESSON22_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_LESSON22_SCRIPTS))

from dotenv import load_dotenv
load_dotenv(_BONUS_DIR / ".env")
load_dotenv(_BONUS_DIR.parent / ".env")

logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO),
    format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
log = logging.getLogger("bot_gigaam")

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message

from audio_convert import ogg_to_wav

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("Задайте BOT_TOKEN в .env", file=sys.stderr)
    sys.exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

_gigaam_model: Any = None
_gigaam_device: Optional[str] = None
_gigaam_dtype: Optional[str] = None

GIGAAM_MODEL_ID = "ai-sage/GigaAM-v3"
GIGAAM_REVISION = "e2e_rnnt"


def _select_device() -> str:
    return "cpu"


def _select_dtype(device: str) -> str:
    dtype_env = (os.getenv("GIGAAM_DTYPE") or "auto").strip().lower()
    if dtype_env in {"float16", "fp16"}:
        return "float16"
    if dtype_env in {"bfloat16", "bf16"}:
        return "bfloat16"
    if dtype_env in {"float32", "fp32"}:
        return "float32"
    return "float16" if device == "cuda" else "float32"


def get_gigaam_model() -> Any:
    global _gigaam_model, _gigaam_device, _gigaam_dtype
    device = _select_device()
    dtype = _select_dtype(device)

    if _gigaam_model is None or _gigaam_device != device or _gigaam_dtype != dtype:
        import torch
        from transformers import AutoModel, modeling_utils

        log.info("Загрузка GigaAM-v3: device=%s, dtype=%s", device, dtype)

        _orig_device = torch.device

        class _DeviceMeta(type):
            def __instancecheck__(cls, instance: object) -> bool:
                return isinstance(instance, _orig_device)

        class _DeviceMetaToCpu(metaclass=_DeviceMeta):
            def __new__(cls, device_arg: str, *args: Any, **kwargs: Any) -> Any:
                if device_arg == "meta":
                    return _orig_device("cpu")
                return _orig_device(device_arg, *args, **kwargs)

        torch.device = _DeviceMetaToCpu
        _orig_set_default = getattr(torch, "set_default_device", None)

        def _set_default_no_meta(dev: Any) -> None:
            if dev == "meta" or (isinstance(dev, _orig_device) and getattr(dev, "type", None) == "meta"):
                dev = "cpu"
            if _orig_set_default is not None:
                _orig_set_default(dev)

        if _orig_set_default is not None:
            torch.set_default_device = _set_default_no_meta

        PreTrained = modeling_utils.PreTrainedModel
        _orig_mark_tied = getattr(PreTrained, "mark_tied_weights_as_initialized", None)
        _orig_move_missing = getattr(PreTrained, "_move_missing_keys_from_meta_to_device", None)

        def _ensure_tied_weights(self: Any) -> None:
            if not hasattr(self, "all_tied_weights_keys"):
                self.all_tied_weights_keys = {}

        if _orig_mark_tied is not None:

            def _mark_tied_safe(self: Any, loading_info: Any = None) -> Any:
                if not hasattr(self, "all_tied_weights_keys"):
                    return None
                return _orig_mark_tied(self, loading_info)

            PreTrained.mark_tied_weights_as_initialized = _mark_tied_safe
        if _orig_move_missing is not None:

            def _move_missing_safe(self: Any, *args: Any, **kwargs: Any) -> Any:
                _ensure_tied_weights(self)
                return _orig_move_missing(self, *args, **kwargs)

            PreTrained._move_missing_keys_from_meta_to_device = _move_missing_safe
        try:
            _gigaam_model = AutoModel.from_pretrained(
                GIGAAM_MODEL_ID,
                revision=GIGAAM_REVISION,
                trust_remote_code=True,
                device_map="cpu",
            )
            log.info("GigaAM-v3 загружена")
        except Exception as e:
            log.exception("Ошибка загрузки GigaAM: %s", e)
            raise
        finally:
            torch.device = _orig_device
            if _orig_set_default is not None:
                torch.set_default_device = _orig_set_default
            if _orig_mark_tied is not None:
                PreTrained.mark_tied_weights_as_initialized = _orig_mark_tied
            if _orig_move_missing is not None:
                PreTrained._move_missing_keys_from_meta_to_device = _orig_move_missing
        torch_dtype = {
            "float16": torch.float16,
            "bfloat16": torch.bfloat16,
            "float32": torch.float32,
        }[dtype]
        if device != "cpu":
            _gigaam_model = _gigaam_model.to(device)
        _gigaam_model = _gigaam_model.to(torch_dtype)
        _gigaam_device = device
        _gigaam_dtype = dtype
    return _gigaam_model


@dp.message(F.voice)
async def on_voice(message: Message) -> None:
    """Голосовое → OGG → WAV → GigaAM → ответ текстом."""
    chat_id = message.chat.id
    file_id = message.voice.file_id
    log.info("Голосовое chat_id=%s", chat_id)

    await message.bot.send_chat_action(chat_id, "typing")
    try:
        file = await message.bot.get_file(file_id)
        file_path = file.file_path
        if not file_path:
            log.warning("Пустой file_path для file_id=%s", file_id)
            await message.reply("Не удалось получить файл.")
            return

        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp_ogg:
            ogg_path = tmp_ogg.name
        try:
            await message.bot.download_file(file_path, ogg_path)
            wav_path = ogg_path.replace(".ogg", ".wav")
            ogg_to_wav(ogg_path, wav_path)

            model = get_gigaam_model()
            text = model.transcribe(wav_path)
            if not isinstance(text, str):
                text = str(text) if text is not None else ""
            text = (text or "").strip()
            log.info("Транскрипт: %d символов", len(text))

            if not text:
                await message.reply("Речь не распознана. Попробуйте записать ещё раз.")
            else:
                await message.reply(f"Распознано (GigaAM-v3):\n\n{text}")
        finally:
            for p in (ogg_path, ogg_path.replace(".ogg", ".wav")):
                if os.path.exists(p):
                    try:
                        os.unlink(p)
                    except OSError:
                        pass
    except Exception as e:
        log.exception("Ошибка обработки голосового: %s", e)
        await message.reply(f"Ошибка: {e!s}")


async def main() -> None:
    log.info("Бот GigaAM запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
