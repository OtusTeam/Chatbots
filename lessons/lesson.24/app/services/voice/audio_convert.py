"""
Конвертация OGG (голосовые сообщения Telegram) в WAV 16 kHz моно
и WAV в OGG для отправки голосовых сообщений.
Требуется для Faster-Whisper (STT) и отправки ответа голосом (TTS → OGG).
"""
from pathlib import Path
from io import BytesIO
from typing import Union, Optional

from pydub import AudioSegment

# Параметры, ожидаемые Faster-Whisper (16 kHz моно улучшают распознавание)
WAV_SAMPLE_RATE = 16000
WAV_CHANNELS = 1


def ogg_to_wav(
    input_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    *,
    sample_rate: int = WAV_SAMPLE_RATE,
    channels: int = WAV_CHANNELS,
) -> Union[str, Path]:
    """
    Конвертирует OGG-файл в WAV с заданной частотой и числом каналов.
    """
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Файл не найден: {input_path}")

    if output_path is None:
        output_path = input_path.with_suffix(".wav")
    else:
        output_path = Path(output_path)

    audio = AudioSegment.from_file(str(input_path), format="ogg")
    audio = audio.set_frame_rate(sample_rate).set_channels(channels)
    audio.export(str(output_path), format="wav")
    return output_path


def ogg_bytes_to_wav(
    ogg_data: bytes,
    output_path: Optional[Union[str, Path]] = None,
    *,
    sample_rate: int = WAV_SAMPLE_RATE,
    channels: int = WAV_CHANNELS,
) -> Union[bytes, Path]:
    """
    Конвертирует OGG из байтов в WAV (файл или байты).
    """
    buffer = BytesIO(ogg_data)
    audio = AudioSegment.from_file(buffer, format="ogg")
    audio = audio.set_frame_rate(sample_rate).set_channels(channels)

    if output_path is not None:
        output_path = Path(output_path)
        audio.export(str(output_path), format="wav")
        return output_path

    out = BytesIO()
    audio.export(out, format="wav")
    out.seek(0)
    return out.read()


def wav_to_ogg_bytes(wav_data: bytes) -> bytes:
    """
    Конвертирует WAV (байты) в OGG для отправки голосового сообщения в Telegram.
    """
    seg = AudioSegment.from_file(BytesIO(wav_data), format="wav")
    out = BytesIO()
    seg.export(out, format="ogg", codec="libopus")
    out.seek(0)
    return out.read()
