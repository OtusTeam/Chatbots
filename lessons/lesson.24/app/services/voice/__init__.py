"""
Голосовые сервисы: конвертация OGG/WAV, STT (Faster-Whisper), TTS (Silero).
"""
from .audio_convert import (
    ogg_to_wav,
    ogg_bytes_to_wav,
    wav_to_ogg_bytes,
    WAV_SAMPLE_RATE,
    WAV_CHANNELS,
)
from .stt_pipeline import (
    load_model as load_stt_model,
    transcribe,
    transcribe_with_fallback,
)
from .tts_pipeline import synthesize, clear_cache as tts_clear_cache

__all__ = [
    "ogg_to_wav",
    "ogg_bytes_to_wav",
    "wav_to_ogg_bytes",
    "WAV_SAMPLE_RATE",
    "WAV_CHANNELS",
    "load_stt_model",
    "transcribe",
    "transcribe_with_fallback",
    "synthesize",
    "tts_clear_cache",
]
