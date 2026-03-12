from __future__ import annotations

import argparse
import hashlib
import os
import sys
import time
from pathlib import Path

_LESSON_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS_DIR = _LESSON_ROOT / "scripts"
for _p in (_SCRIPTS_DIR, _LESSON_ROOT):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

BONUS_DIR = Path(__file__).resolve().parent
DEFAULT_TEXT_FILE = BONUS_DIR / "sample_text.txt"
YANDEX_CHUNK_CHARS = 250
OUTPUT_DIR = BONUS_DIR / "benchmark_output"
OUTPUT_DIR.mkdir(exist_ok=True)


def load_text(path: Path, max_chars: int | None) -> str:
    text = path.read_text(encoding="utf-8").strip()
    if max_chars is not None and len(text) > max_chars:
        text = text[:max_chars]
    return text


def run_silero(text: str, device: str) -> tuple[float, str | None]:
    from tts_pipeline import synthesize

    dev = "cuda" if device == "gpu" else "cpu"
    out_path = OUTPUT_DIR / f"silero_{device}.wav"
    t0 = time.perf_counter()
    synthesize(text, output_path=out_path, use_cache=False, device=dev)
    elapsed = time.perf_counter() - t0
    return elapsed, str(out_path)


def _flash_attn_available() -> bool:
    try:
        import flash_attn  # noqa: F401
        return True
    except Exception:
        return False


def _get_qwen_model(device: str):
    import torch
    try:
        from qwen_tts import Qwen3TTSModel
    except ImportError as e:
        raise RuntimeError(f"qwen-tts not installed: {e}") from e

    device_map = "cuda:0" if device == "gpu" else "cpu"
    kwargs = {"device_map": device_map, "dtype": torch.float32}
    if device == "gpu" and torch.cuda.is_available():
        kwargs["dtype"] = torch.bfloat16
        if _flash_attn_available():
            kwargs["attn_implementation"] = "flash_attention_2"
    try:
        return Qwen3TTSModel.from_pretrained(
            "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice",
            **kwargs,
        )
    except Exception:
        kwargs.pop("attn_implementation", None)
        return Qwen3TTSModel.from_pretrained(
            "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice",
            **kwargs,
        )


def run_qwen(text: str, device: str) -> tuple[float, str | None]:
    import soundfile as sf

    model = _get_qwen_model(device)
    out_path = OUTPUT_DIR / f"qwen_{device}.wav"
    t0 = time.perf_counter()
    wavs, sr = model.generate_custom_voice(
        text=text,
        language="Russian",
        speaker="Vivian",
        instruct="",
    )
    elapsed = time.perf_counter() - t0
    if wavs and len(wavs) > 0:
        sf.write(out_path, wavs[0], sr)
        return elapsed, str(out_path)
    return elapsed, None


def _yandex_cache_path(text: str) -> Path:
    key = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    return OUTPUT_DIR / f"yandex_{key}.wav"


def run_yandex(text: str, api_key: str) -> tuple[float, str | None]:
    import io
    import struct
    try:
        import requests
    except ImportError as e:
        raise RuntimeError(f"requests not installed: {e}") from e

    cache_path = _yandex_cache_path(text)
    if cache_path.exists():
        return 0.0, str(cache_path)

    url = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
    headers = {"Authorization": f"Api-Key {api_key}"}
    chunks = []
    for i in range(0, len(text), YANDEX_CHUNK_CHARS):
        chunk_text = text[i : i + YANDEX_CHUNK_CHARS]
        data = {
            "text": chunk_text,
            "lang": "ru-RU",
            "voice": "alena",
            "format": "lpcm",
            "sampleRateHertz": "16000",
        }
        t0 = time.perf_counter()
        r = requests.post(url, headers=headers, data=data, timeout=60)
        elapsed = time.perf_counter() - t0
        if not r.ok:
            raise RuntimeError(f"Yandex TTS error {r.status_code}: {r.text[:200]}")
        chunks.append((r.content, elapsed))

    if not chunks:
        return 0.0, None
    total_elapsed = sum(e for _, e in chunks)
    pcm = b"".join(c for c, _ in chunks)
    n_samples = len(pcm) // 2
    buf = io.BytesIO()
    buf.write(b"RIFF")
    buf.write(struct.pack("<I", 36 + n_samples * 2))
    buf.write(b"WAVEfmt ")
    buf.write(struct.pack("<IHHIIHH", 16, 1, 1, 16000, 32000, 2, 16))
    buf.write(b"data")
    buf.write(struct.pack("<I", n_samples * 2))
    buf.write(pcm)
    cache_path.write_bytes(buf.getvalue())
    return total_elapsed, str(cache_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="TTS benchmark: Silero, Qwen 1.7B, Yandex SpeechKit")
    parser.add_argument(
        "text_file",
        nargs="?",
        default=None,
        help=f"Path to UTF-8 text file (default: {DEFAULT_TEXT_FILE.name})",
    )
    parser.add_argument("--text-file", dest="text_file_opt", default=None, help="Path to text file")
    parser.add_argument("--cpu-only", action="store_true", help="Run only CPU (and cloud) runs")
    parser.add_argument("--gpu-only", action="store_true", help="Run only GPU (and cloud) runs")
    parser.add_argument("--max-chars", type=int, default=None, help="Trim text to N characters")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Only Silero + Yandex (fast check that the script runs correctly)",
    )
    args = parser.parse_args()

    text_path = Path(args.text_file_opt or args.text_file or DEFAULT_TEXT_FILE)
    if not text_path.is_absolute():
        text_path = BONUS_DIR / text_path
    if not text_path.exists():
        print(f"Error: text file not found: {text_path}", file=sys.stderr)
        sys.exit(1)

    text = load_text(text_path, args.max_chars)
    if not text:
        print("Error: empty text", file=sys.stderr)
        sys.exit(1)

    use_cpu = not args.gpu_only
    use_gpu = not args.cpu_only
    has_cuda = False
    try:
        import torch
        has_cuda = torch.cuda.is_available()
    except Exception:
        pass

    try:
        from dotenv import load_dotenv
        load_dotenv(BONUS_DIR / ".env")
    except Exception:
        pass
    yandex_key = os.getenv("YANDEX_API_KEY", "").strip()

    results: list[tuple[str, str, float, int, str | None]] = []
    quick = getattr(args, "quick", False)

    if use_cpu:
        try:
            elapsed, out = run_silero(text, "cpu")
            results.append(("Silero", "CPU", elapsed, len(text), out))
        except Exception as e:
            results.append(("Silero", "CPU", -1.0, len(text), f"Error: {e}"))
    if use_gpu and has_cuda:
        try:
            elapsed, out = run_silero(text, "gpu")
            results.append(("Silero", "GPU", elapsed, len(text), out))
        except Exception as e:
            results.append(("Silero", "GPU", -1.0, len(text), f"Error: {e}"))

    if quick:
        if yandex_key:
            try:
                elapsed, out = run_yandex(text, yandex_key)
                results.append(("Yandex SpeechKit", "cloud", elapsed, len(text), out))
            except Exception as e:
                results.append(("Yandex SpeechKit", "cloud", -1.0, len(text), f"Error: {e}"))
        else:
            results.append(("Yandex SpeechKit", "cloud", -1.0, len(text), "skipped (no API key)"))
    else:
        if use_cpu:
            try:
                elapsed, out = run_qwen(text, "cpu")
                results.append(("Qwen3-TTS-1.7B", "CPU", elapsed, len(text), out))
            except Exception as e:
                results.append(("Qwen3-TTS-1.7B", "CPU", -1.0, len(text), f"Error: {e}"))
        if use_gpu and has_cuda:
            try:
                elapsed, out = run_qwen(text, "gpu")
                results.append(("Qwen3-TTS-1.7B", "GPU", elapsed, len(text), out))
            except Exception as e:
                results.append(("Qwen3-TTS-1.7B", "GPU", -1.0, len(text), f"Error: {e}"))

        if yandex_key:
            try:
                elapsed, out = run_yandex(text, yandex_key)
                results.append(("Yandex SpeechKit", "cloud", elapsed, len(text), out))
            except Exception as e:
                results.append(("Yandex SpeechKit", "cloud", -1.0, len(text), f"Error: {e}"))
        else:
            results.append(("Yandex SpeechKit", "cloud", -1.0, len(text), "skipped (no API key)"))

    print("\n--- TTS Benchmark ---")
    print(f"Text length: {len(text)} chars")
    print()
    row_fmt = "{:<20} {:<8} {:>10} {:>10}   {}"
    print(row_fmt.format("Backend", "Device", "Time (s)", "Text len", "Output"))
    print("-" * 72)
    for backend, device, elapsed, n, out in results:
        time_str = f"{elapsed:.2f}" if elapsed >= 0 else "—"
        out_str = str(out) if out else "—"
        if len(out_str) > 36:
            out_str = out_str[:33] + "..."
        print(row_fmt.format(backend, device, time_str, n, out_str))
    print()


if __name__ == "__main__":
    main()
