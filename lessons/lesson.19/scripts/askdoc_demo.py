"""
Демо RAG-лайт: один документ (из файла или строка) -> чанки в памяти ->
по запросу поиск по ключевым словам -> сборка ответа через GigaChat с цитатой.
"""
import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_LESSON_DIR = os.path.dirname(_SCRIPT_DIR)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)
if _LESSON_DIR not in sys.path:
    sys.path.insert(0, _LESSON_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(_LESSON_DIR, ".env"))

from chunking import chunk_text, chunk_file
from keyword_search import search_chunks
from answer_builder import get_answer_with_citation


def run_askdoc(doc_source: str, is_path: bool = False) -> None:
    """
    Загружает документ в чанки, в цикле принимает вопросы и выводит ответ с цитатой.

    :param doc_source: путь к файлу или сам текст документа
    :param is_path: True если doc_source — путь к файлу
    """
    if is_path:
        chunks = chunk_file(doc_source)
    else:
        chunks = chunk_text(doc_source)

    if not chunks:
        print("Нет чанков для поиска.")
        return

    print(f"Загружено чанков: {len(chunks)}. Введите вопрос (или пусто для выхода).\n")

    while True:
        try:
            question = input("Вопрос: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not question:
            break

        found = search_chunks(chunks, question, top_n=5)

        for i, chunk in enumerate(found):
            print(chunk)

        if not found:
            print("По контексту ничего не найдено. Ответ: Не знаю.\n")
            continue

        answer, source = get_answer_with_citation(found, question)
        print("Ответ:", answer)
        if source:
            print("Источник:", source)
        print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if os.path.isfile(path):
            run_askdoc(path, is_path=True)
        else:
            run_askdoc(path, is_path=False)
    else:
        sample = (
            "Компания Рога и Копыта. Офис: ул. Ленина, 10. Телефон: +7 495 123-45-67. "
            "Режим работы: понедельник — пятница с 9:00 до 18:00. "
            "Для получения справки направьте запрос на info@example.com."
        )
        #run_askdoc(sample, is_path=False)
        run_askdoc('../docs/book03_chapter09.txt', is_path=True)