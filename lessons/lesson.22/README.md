# Урок 22 — Speech-to-Text (распознавание речи)

Обработка голосовых сообщений в Telegram-боте: приём OGG, конвертация в WAV, распознавание через Faster-Whisper, ответ текстом.

## Структура
#### Примеры скриптов
- **scripts/stt_pipeline.py** — загрузка модели (small, CPU, INT8), transcribe, transcribe_with_fallback
- **scripts/audio_convert.py** — конвертация OGG → WAV (16 kHz, моно)
- **scripts/bot_voice_stt.py** — демо-бот: хендлер voice → скачивание → конвертация → STT → ответ текстом
#### Прочее
- **audio_samples/** — папка для тестовых OGG/WAV (см. README внутри)
- **requirements.txt**, **.env.example**
#### Бонусные скрипты
- **bonus/benchmark_asr.py** — бенчмарк скорости работы и качества различных STT моделей
- **bonus/bot_gigaam.py** — пример бота, который использует модель STT gigaam (требует токен бота)

## Запуск

1. Скопировать `.env.example` в `.env`, задать **BOT_TOKEN** (получить у @BotFather).
2. Установить зависимости: `pip install -r requirements.txt`
3. Конвертация (нужен OGG в audio_samples или путь к файлу):
   ```bash
   python scripts/audio_convert.py path/to/voice.ogg [output.wav]
   ```
4. Распознавание (нужен WAV):
   ```bash
   python scripts/stt_pipeline.py path/to/audio.wav
   ```
5. Демо-бот (отвечает на голосовые текстом):
   ```bash
   python scripts/bot_voice_stt.py
   ```

**Примечание:** Для pydub может потребоваться FFmpeg в системе (или установка через пакетный менеджер ОС).
