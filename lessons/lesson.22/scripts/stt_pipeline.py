"""
Пайплайн распознавания речи: загрузка модели Faster-Whisper (small, CPU, INT8),
транскрипция с указанием языка и пунктуации, обработка ошибок и длинных сообщений.
"""
from pathlib import Path
from typing import Union, Optional, Tuple, List

from faster_whisper import WhisperModel

# Модель small + CPU + INT8 — компромисс скорость/качество для учебного проекта
DEFAULT_MODEL_SIZE = "small"
DEFAULT_DEVICE = "cpu"
DEFAULT_COMPUTE_TYPE = "int8"
MAX_DURATION_SEC = 120


def load_model(
    model_size: str = DEFAULT_MODEL_SIZE,
    device: str = DEFAULT_DEVICE,
    compute_type: str = DEFAULT_COMPUTE_TYPE,
) -> WhisperModel:
    """
    Загружает модель Whisper для распознавания речи.
    """
    return WhisperModel(model_size, device=device, compute_type=compute_type)


def transcribe(
    audio_path: Union[str, Path],
    model: Optional[WhisperModel] = None,
    *,
    language: Optional[str] = None,
    beam_size: int = 5,
    vad_filter: bool = True,
    without_timestamps: bool = True,
    condition_on_previous_text: bool = False,
) -> Tuple[str, Optional[str]]:
    """
    Транскрибирует аудиофайл в текст.
    """
    if model is None:
        model = load_model()

    segments, info = model.transcribe(
        str(audio_path),
        language=language,
        beam_size=beam_size,
        vad_filter=vad_filter,
        without_timestamps=without_timestamps,
        condition_on_previous_text=condition_on_previous_text,
    )
    text_parts: List[str] = []
    for segment in segments:
        if segment.text.strip():
            text_parts.append(segment.text.strip())
    full_text = " ".join(text_parts) if text_parts else ""
    detected_lang = getattr(info, "language", None)
    return full_text, detected_lang


def transcribe_with_fallback(
    audio_path: Union[str, Path],
    model: Optional[WhisperModel] = None,
    *,
    language: Optional[str] = None,
    max_duration_sec: int = MAX_DURATION_SEC,
) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Транскрипция с обработкой ошибок и ограничением по длительности.
    """
    try:
        path = Path(audio_path)
        if path.exists():
            size_mb = path.stat().st_size / (1024 * 1024)
            if size_mb > 10:  # условно > 5 мин для 16 kHz mono
                return "", None, "Аудио слишком длинное. Отправьте сообщение до 1–2 минут."
        text, lang = transcribe(audio_path, model=model, language=language)
        return text, lang, None
    except Exception as e:
        return "", None, f"Ошибка распознавания: {e!s}"


if __name__ == "__main__":
    import sys
    p = sys.argv[1] if len(sys.argv) > 1 else None
    if not p or not Path(p).exists():
        print("Использование: python stt_pipeline.py <path_to.wav>")
        sys.exit(1)
    model = load_model()
    text, lang, err = transcribe_with_fallback(p, model=model)
    if err:
        print("Ошибка:", err)
    else:
        print("Язык:", lang)
        print("Текст:", text or "(пусто)")
