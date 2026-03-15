"""
Синтез речи Silero TTS. Пути к voices.json и cache заданы относительно пакета voice.
"""
import hashlib
import io
import json
import subprocess
from pathlib import Path

import numpy as np
import torch
import scipy.io.wavfile

_VOICE_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _VOICE_DIR.parent.parent.parent  # app -> services -> scripts
VOICES_PATH = _VOICE_DIR / "voices.json"
CACHE_DIR = _SCRIPTS_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

_tts_model = None
_tts_lang = None
_tts_speaker_id = None
_tts_device = None


def _load_voices_config() -> dict:
    with open(VOICES_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_preset(preset_id: str | None = None) -> dict:
    cfg = _load_voices_config()
    presets = {p["id"]: p for p in cfg["presets"]}
    pid = preset_id or cfg.get("default") or list(presets.keys())[0]
    return presets[pid]


def _get_model(language: str = "ru", speaker_id: str = "v5_2_ru", device: str | torch.device | None = None):
    global _tts_model, _tts_lang, _tts_speaker_id, _tts_device
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    if isinstance(device, str):
        device = torch.device(device)
    if _tts_model is None or _tts_lang != language or _tts_speaker_id != speaker_id:
        loaded = torch.hub.load(
            repo_or_dir="snakers4/silero-models",
            model="silero_tts",
            language=language,
            speaker=speaker_id,
            trust_repo=True,
        )
        raw = loaded[0] if isinstance(loaded, tuple) else loaded
        if raw is not None and hasattr(raw, "model"):
            inner = getattr(raw, "model", None)
            if inner is not None:
                raw = inner
        if raw is None and isinstance(loaded, tuple) and len(loaded) >= 2:
            candidate = loaded[1]
            if candidate is not None and not isinstance(candidate, str) and hasattr(candidate, "forward"):
                raw = candidate
        _tts_model = raw
        if _tts_model is None or not hasattr(_tts_model, "apply_tts"):
            raise RuntimeError(
                "Silero TTS не вернул модель. Очистите кэш: %USERPROFILE%\\.cache\\torch\\hub\\snakers4_silero-models_*"
            )
        _tts_lang = language
        _tts_speaker_id = speaker_id
        _tts_device = device
        _tts_model.to(device)
    elif _tts_device != device:
        _tts_device = device
        _tts_model.to(device)
    if _tts_model is None or not hasattr(_tts_model, "apply_tts"):
        raise RuntimeError(
            "Silero TTS: модель не загружена. Очистите кэш: %USERPROFILE%\\.cache\\torch\\hub\\snakers4_silero-models_*"
        )
    return _tts_model


def _cache_key(text: str, preset_id: str, speed: float, volume_db: float) -> str:
    return hashlib.sha256(f"{text}|{preset_id}|{speed}|{volume_db}".encode("utf-8")).hexdigest()[:16]


def clear_cache() -> int:
    """Удаляет все файлы в CACHE_DIR. Возвращает число удалённых файлов."""
    if not CACHE_DIR.exists():
        return 0
    n = 0
    for f in CACHE_DIR.iterdir():
        if f.is_file():
            f.unlink()
            n += 1
    return n


def _apply_volume(audio: np.ndarray, volume_db: float) -> np.ndarray:
    if volume_db == 0:
        return audio
    factor = 10 ** (volume_db / 20.0)
    return np.clip(audio * factor, -1.0, 1.0).astype(np.float32)


def _apply_speed_ffmpeg(wav_bytes: bytes, sample_rate: int, speed: float) -> bytes:
    if speed <= 0 or speed == 1.0:
        return wav_bytes
    filters = []
    s = speed
    while s > 2.0:
        filters.append(2.0)
        s /= 2.0
    while s < 0.5:
        filters.append(0.5)
        s /= 0.5
    filters.append(s)
    filter_str = ",".join(f"atempo={f}" for f in filters)
    try:
        r = subprocess.run(
            ["ffmpeg", "-y", "-nostdin", "-i", "pipe:0", "-filter:a", filter_str,
             "-acodec", "pcm_s16le", "-ar", str(sample_rate), "-f", "wav", "pipe:1"],
            input=wav_bytes, capture_output=True, timeout=30, check=False,
        )
        if r.returncode == 0 and r.stdout:
            return r.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return wav_bytes


def synthesize(
    text: str,
    output_path: str | Path | None = None,
    *,
    voice_id: str | None = None,
    speed: float = 1.0,
    volume_db: float = 0.0,
    use_cache: bool = True,
    device: str | torch.device | None = None,
) -> bytes | Path:
    preset = get_preset(voice_id)
    language = preset.get("language", "ru")
    speaker = preset.get("speaker", "xenia")
    sample_rate = int(preset.get("sample_rate", 48000))

    if use_cache and not output_path:
        key = _cache_key(text, preset["id"], speed, volume_db)
        cache_file = CACHE_DIR / f"{key}.wav"
        if cache_file.exists():
            if output_path is None:
                return cache_file.read_bytes()
            Path(output_path).write_bytes(cache_file.read_bytes())
            return Path(output_path)

    model_id = preset.get("model_id", "v5_2_ru")
    model = _get_model(language=language, speaker_id=model_id, device=device)
    audio = model.apply_tts(
        text=text, speaker=speaker, sample_rate=sample_rate,
        put_accent=True, put_yo=True,
    )
    if hasattr(audio, "cpu"):
        audio = audio.cpu().numpy()
    audio = np.asarray(audio, dtype=np.float32)
    audio = _apply_volume(audio, volume_db)
    audio_int = (np.clip(audio, -1, 1) * 32767).astype(np.int16)

    buf = io.BytesIO()
    scipy.io.wavfile.write(buf, sample_rate, audio_int)
    buf.seek(0)
    data = buf.read()

    if speed != 1.0:
        data = _apply_speed_ffmpeg(data, sample_rate, speed)

    if output_path:
        output_path = Path(output_path)
        output_path.write_bytes(data)
        if use_cache:
            (CACHE_DIR / f"{_cache_key(text, preset['id'], speed, volume_db)}.wav").write_bytes(data)
        return output_path

    if use_cache:
        (CACHE_DIR / f"{_cache_key(text, preset['id'], speed, volume_db)}.wav").write_bytes(data)
    return data
