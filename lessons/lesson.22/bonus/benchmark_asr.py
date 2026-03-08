"""
Бенчмарк ASR: Faster-Whisper (tiny..large-v3), GigaAM-v3 (только CPU), Voxtral-Mini.
"""
import argparse
import logging
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, List, Tuple

if sys.version_info < (3, 10):
    print("Ошибка: нужен Python 3.10+ (сейчас %s)." % sys.version.split()[0], file=sys.stderr)
    sys.exit(1)

_BONUS_DIR = Path(__file__).resolve().parent
_LESSON22_SCRIPTS = _BONUS_DIR.parent / "scripts"
if str(_LESSON22_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_LESSON22_SCRIPTS))

logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "WARNING").upper(), logging.WARNING),
    format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
log = logging.getLogger("benchmark_asr")

DEFAULT_AUDIO = _BONUS_DIR.parent / "audio_samples" / "001.ogg"
GIGAAM_MODEL_ID = "ai-sage/GigaAM-v3"
GIGAAM_REVISION = "e2e_rnnt"
VOXTRAL_MODEL_ID = "mistralai/Voxtral-Mini-4B-Realtime-2602"


def _ensure_wav(audio_path: Path) -> Path:
    """Возвращает путь к WAV; при необходимости конвертирует OGG во временный WAV."""
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Файл не найден: {audio_path}")
    if audio_path.suffix.lower() == ".wav":
        log.debug("Аудио уже WAV: %s", audio_path)
        return audio_path
    if audio_path.suffix.lower() in (".ogg", ".oga"):
        from audio_convert import ogg_to_wav
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp.close()
        log.info("Конвертация OGG→WAV: %s -> %s", audio_path, tmp.name)
        ogg_to_wav(audio_path, tmp.name)
        return Path(tmp.name)
    raise ValueError(f"Неожиданное расширение: {audio_path.suffix}")

WHISPER_SIZES = ("tiny", "base", "small", "medium", "large-v3")


def _run_whisper(wav_path: Path, device: str, model_size: str = "small") -> Tuple[float, str]:
    log.info("Faster-Whisper (%s) на %s: загрузка модели", model_size, device)
    from faster_whisper import WhisperModel
    compute_type = "int8" if device == "cpu" else "float16"
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    t0 = time.perf_counter()
    segments, _ = model.transcribe(str(wav_path), language="ru", beam_size=5)
    text = " ".join(s.text.strip() for s in segments if s.text.strip())
    elapsed = time.perf_counter() - t0
    log.info("Faster-Whisper (%s, %s): %.2f с, %d символов", model_size, device, elapsed, len(text or ""))
    return elapsed, text or "(пусто)"

def _run_gigaam(wav_path: Path) -> Tuple[float, str]:
    """GigaAM-v3 только на CPU."""
    import torch
    from transformers import AutoModel, modeling_utils

    log.info("GigaAM-v3 (CPU): загрузка")
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
        try:
            model = AutoModel.from_pretrained(
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
    model = model.to(torch.float32)
    t0 = time.perf_counter()
    try:
        text = model.transcribe(str(wav_path))
    except Exception as e:
        if "transcribe_longform" in str(e) or "too long" in str(e).lower():
            log.info("Длинное аудио, используем transcribe_longform")
            text = model.transcribe_longform(str(wav_path))
        else:
            raise
    elapsed = time.perf_counter() - t0
    text = _normalize_gigaam_text(text)
    log.info("GigaAM-v3 (CPU): %.2f с, %d символов", elapsed, len((text or "").strip()))
    return elapsed, (text or "(пусто)").strip()


def _normalize_gigaam_text(text: Any) -> str:
    if text is None:
        return ""
    if isinstance(text, str):
        return text
    if isinstance(text, (list, tuple)):
        parts = []
        for item in text:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(item["text"])
            else:
                parts.append(str(item))
        return " ".join(p for p in parts if p)
    return str(text)

def _run_voxtral(wav_path: Path, device: str) -> Tuple[float, str]:
    import soundfile as sf
    import torch
    from transformers import VoxtralRealtimeForConditionalGeneration, AutoProcessor

    log.info("Voxtral на %s: загрузка", device)
    processor = AutoProcessor.from_pretrained(VOXTRAL_MODEL_ID)
    if device == "cuda":
        model = VoxtralRealtimeForConditionalGeneration.from_pretrained(
            VOXTRAL_MODEL_ID,
            device_map="cuda:0",
            torch_dtype=torch.float16,
        )
    else:
        model = VoxtralRealtimeForConditionalGeneration.from_pretrained(VOXTRAL_MODEL_ID)
        model = model.to(device)

    audio, _ = sf.read(str(wav_path), dtype="float32")
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    inputs = processor(audio, return_tensors="pt")
    # model может быть загружен через device_map; берём device/dtype по первому параметру
    try:
        p = next(model.parameters())
        model_device = p.device
        model_dtype = p.dtype
    except StopIteration:
        model_device = torch.device("cuda:0" if device == "cuda" else "cpu")
        model_dtype = torch.float16 if device == "cuda" else torch.float32
    inputs = inputs.to(model_device, dtype=model_dtype)

    t0 = time.perf_counter()
    outputs = model.generate(**inputs)
    decoded = processor.batch_decode(outputs, skip_special_tokens=True)
    elapsed = time.perf_counter() - t0
    text = (decoded[0] if decoded else "").strip() or "(пусто)"
    log.info("Voxtral-Mini (%s): %.2f с, %d символов", device, elapsed, len(text))
    return elapsed, text

def main() -> None:
    parser = argparse.ArgumentParser(description="Бенчмарк ASR: Whisper, GigaAM-v3, Voxtral")
    parser.add_argument(
        "--audio",
        type=Path,
        default=DEFAULT_AUDIO,
        help="Путь к аудио (OGG или WAV). По умолчанию: ../audio_samples/002.ogg",
    )
    parser.add_argument("--cpu-only", action="store_true", help="Запускать только на CPU")
    parser.add_argument("--gpu-only", action="store_true", help="Запускать только на GPU")
    args = parser.parse_args()

    wav_path = _ensure_wav(args.audio)
    use_cpu = not args.gpu_only
    use_gpu = not args.cpu_only
    try:
        import torch
        cuda_available = torch.cuda.is_available()
    except Exception as ex:
        log.warning("Не удалось проверить CUDA: %s", ex)
        cuda_available = False
    if use_gpu and not cuda_available:
        use_gpu = False
        log.warning("GPU недоступен, выполняем только на CPU.")
        print("GPU недоступен, выполняем только на CPU.", file=sys.stderr)

    results: List[Tuple[str, str, float, str]] = []

    # Faster-Whisper (несколько размеров модели)
    for model_size in WHISPER_SIZES:
        label = f"Faster-Whisper ({model_size})"
        if use_cpu:
            try:
                elapsed, text = _run_whisper(wav_path, "cpu", model_size)
                results.append((label, "CPU", elapsed, text))
            except Exception as e:
                log.exception("Faster-Whisper %s CPU: %s", model_size, e)
                results.append((label, "CPU", -1.0, f"Ошибка: {e}"))
        if use_gpu:
            try:
                elapsed, text = _run_whisper(wav_path, "cuda", model_size)
                results.append((label, "GPU", elapsed, text))
            except Exception as e:
                log.exception("Faster-Whisper %s GPU: %s", model_size, e)
                results.append((label, "GPU", -1.0, f"Ошибка: {e}"))

    # GigaAM-v3 CPU
    try:
        elapsed, text = _run_gigaam(wav_path)
        results.append(("GigaAM-v3 (e2e_rnnt)", "CPU", elapsed, text))
    except Exception as e:
        log.exception("GigaAM-v3: %s", e)
        results.append(("GigaAM-v3 (e2e_rnnt)", "CPU", -1.0, f"Ошибка: {e}"))

    # Voxtral GPU
    if use_gpu:
        try:
            elapsed, text = _run_voxtral(wav_path, "cuda")
            results.append(("Voxtral-Mini-4B-Realtime", "GPU", elapsed, text))
        except Exception as e:
            log.exception("Voxtral GPU: %s", e)
            results.append(("Voxtral-Mini-4B-Realtime", "GPU", -1.0, f"Ошибка: {e}"))

    # Вывод таблицы
    print("\n" + "=" * 80)
    print("Бенчмарк ASR — аудио:", args.audio)
    print("=" * 80)
    fmt = "| {:<28} | {:<5} | {:>10} | {}"
    print(fmt.format("Модель", "Устр.", "Время (с)", "Транскрипт (начало)"))
    print("-" * 80)
    for model_name, device, elapsed, text in results:
        time_str = f"{elapsed:.2f}" if elapsed >= 0 else "N/A"
        preview = (text[:50] + "…") if len(text) > 50 else text
        print(fmt.format(model_name, device, time_str, preview))
    print("=" * 80)
    print("\nПолные транскрипты:")
    for model_name, device, elapsed, text in results:
        print(f"\n--- {model_name} ({device}) ---")
        print(text)

    if wav_path != Path(args.audio) and wav_path.exists():
        try:
            wav_path.unlink()
        except OSError:
            pass

if __name__ == "__main__":
    main()
