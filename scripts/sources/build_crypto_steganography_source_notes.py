#!/usr/bin/env python3
"""Build source maps for the Foundations of Cryptography and Steganography course."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


COURSE = "Основы криптографии и стеганографии"
ROOT = Path("07 Sources/Courses") / COURSE
NOTES = ROOT / "Source Notes"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "knowledge"))
from build_crypto_steganography_knowledge import TITLE_MAP  # noqa: E402


REFERENCE_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ("source-only course context", "контекст курса — только в источнике"),
    ("source-only title", "титульная страница — только в источнике"),
    ("Aeneas ruler section within", "раздел о линейке Энея внутри"),
    ("Scytale section within", "раздел о сцитале внутри"),
    ("Jefferson Disk section within", "раздел о дисковом шифраторе Джефферсона внутри"),
    ("tabular gamma section within", "раздел о табличном гаммировании внутри"),
    ("neural embedding section within", "раздел о нейросетевом встраивании внутри"),
    ("source-only architecture example", "архитектурный пример только в источнике"),
    ("linear-algebra section within", "раздел о линейной алгебре внутри"),
    ("error-correction section within", "раздел об исправлении ошибок внутри"),
    ("dated/review examples (2024 course snapshot)", "датированные примеры, требующие проверки (срез курса 2024 года)"),
)


def localize_references(value: str) -> str:
    text = value
    for old in sorted(TITLE_MAP, key=len, reverse=True):
        text = text.replace(f"[[{old}]]", f"[[{TITLE_MAP[old]}]]")
    for old, new in REFERENCE_REPLACEMENTS:
        text = text.replace(old, new)
    return text


def item(pages: str, destination: str, description: str) -> tuple[str, str, str]:
    return pages, destination, description


COVERAGE: dict[int, list[tuple[str, str, str]]] = {
    1: [
        item("1–7", "source-only course context", "Титульный лист, организация курса, преподаватели и оценивание; контакты на страницах 3–4 скрыты."),
        item("8–10", "[[Cryptosystem and Security Goals]]", "Уровни обеспечения информационной безопасности и место криптографии."),
        item("11–14", "[[Classical Cryptography]]; [[Symmetric-Key Cryptography]]", "Определения, задачи криптографии и базовая модель шифрования."),
        item("15–16", "[[Cryptographic Hash Functions]]", "Одностороннее преобразование и контроль случайных искажений."),
        item("17", "[[Message Authentication Codes]]", "Имитовставка как защита целостности и аутентичности."),
        item("18–19", "[[Digital Signatures]]", "Формирование и проверка подписи, защита от отказа от авторства."),
    ],
    2: [
        item("1", "source-only title", "Титульная страница лекции."),
        item("2–3", "[[History of Cryptography]]", "Периоды развития криптографии и исторический контекст."),
        item("4–8", "[[Classical Cryptography]]", "Подстановочные, перестановочные, блочные и гаммирующие шифры."),
        item("9–12", "[[Rings and Modular Arithmetic]]", "Математический аппарат и операции в арифметике остатков."),
    ],
    3: [
        item("1", "source-only title", "Титульная страница лекции."),
        item("2", "Aeneas ruler section within [[Substitution Ciphers]]", "Линейка Энея сохранена как исторический пример внутри общей карточки."),
        item("3–4", "[[Polybius Square]]", "Квадрат Полибия и модификация с паролем."),
        item("5", "[[Substitution Ciphers]]", "Шифр простой замены."),
        item("6–9", "[[Affine Cipher]]", "Аффинный и рекуррентный аффинный шифры с примерами."),
        item("10", "[[Frequency Analysis]]", "Частотный криптоанализ простой замены."),
    ],
    4: [
        item("1", "source-only title", "Титульная страница лекции."),
        item("2", "Scytale section within [[Transposition Ciphers]]", "Сцитала как исторический пример перестановки."),
        item("3–4", "[[Cardan Grille Cipher]]", "Поворотная решётка и пример заполнения."),
        item("5–6", "[[Transposition Ciphers]]", "Блочная перестановка и пример шифрования."),
    ],
    5: [
        item("1", "source-only title", "Титульная страница лекции."),
        item("2–3", "[[Playfair Cipher]]", "Правила подготовки биграмм и преобразования таблицей."),
        item("4", "Jefferson Disk section within [[Classical Cryptography]]", "Дисковый шифратор Джефферсона сохранён как исторический пример."),
        item("5–7", "[[Hill Cipher]]", "Матричное и рекуррентное шифрование Хилла с примером."),
        item("8", "[[Frequency Analysis]]; [[Cryptanalysis]]", "Частотный криптоанализ биграмм блочных шифров."),
    ],
    6: [
        item("1", "source-only title", "Титульная страница лекции."),
        item("2–4", "tabular gamma section within [[Classical Cryptography]]", "Табличное гаммирование и пример сложения символов."),
        item("5–9", "[[Vigenere Cipher]]", "Шифр Виженера, повторение ключа и два варианта самоключа."),
        item("10", "[[Stream Ciphers and One-Time Pad]]", "Шифр Вернама и поразрядное сложение."),
        item("11", "[[Cryptanalysis]]; [[Frequency Analysis]]", "Повторяемость гаммы и индекс совпадений."),
    ],
    7: [
        item("1", "source-only title", "Титульная страница лекции."),
        item("2–4", "[[Perfect Secrecy and Cryptographic Strength]]", "Принцип Керкгоффса, вычислительная и абсолютная стойкость."),
        item("5", "[[Brute-Force Attack]]", "Полный перебор как универсальная базовая атака."),
        item("6–7", "[[Cryptanalysis]]", "Модели доступа атакующего и уязвимость исторических шифров."),
    ],
    8: [
        item("1", "source-only title", "Титульная страница лекции."),
        item("2–5", "[[Information Hiding]]; [[Digital Steganography]]; [[Digital Watermarking]]", "Контейнеры, цели стеганографии и цифровых водяных знаков."),
        item("6–9", "[[Spatial-Domain Image Steganography]]; [[Frequency-Domain Image Steganography]]", "Классификация по области и примеры двух подходов."),
        item("10–13", "[[Steganography Quality Metrics]]; [[Steganalysis]]", "Компромисс незаметности, устойчивости и обнаружимости."),
        item("14", "[[Digital Watermark Attacks]]", "Классы атак на цифровые водяные знаки."),
        item("15–18", "[[Steganography Quality Metrics]]; [[Digital Watermark Attacks]]", "Ёмкость, MSE/PSNR, BER/NCC и пример искажения."),
    ],
    9: [
        item("1", "source-only title", "Титульная страница лекции."),
        item("2–8", "[[Digital Image Fundamentals]]", "Растровые и векторные изображения, типы растров и пикселей."),
        item("9–15", "[[Image Color Models]]", "Восприятие цвета, RGB и YCbCr с формулами преобразования."),
        item("16–21", "[[Digital Image File Formats]]; [[Lossless Image Compression]]", "Форматы BMP, GIF, PNG и другие контейнеры, типы сжатия."),
    ],
    10: [
        item("1", "source-only title", "Титульная страница лекции."),
        item("2", "[[Spatial-Domain Image Steganography]]", "Преимущества и недостатки пространственного встраивания."),
        item("3", "[[LSB Steganography]]", "Замена младших значащих битов."),
        item("4–5", "[[Plus-Minus One Steganography]]", "Случайное изменение значения на единицу и пример."),
        item("6–7", "[[Quantization Index Modulation]]", "Квантование значений по биту сообщения и пример."),
        item("8–10", "[[Pixel Value Differencing]]", "Выбор ёмкости по разности соседних пикселей и пример."),
        item("11–13", "[[Neighbor Mean Interpolation]]", "Интерполяция соседних значений, встраивание и извлечение."),
        item("14–15", "neural embedding section within [[Digital Steganography]]; source-only architecture example", "Два подхода к нейросетевому встраиванию; отдельная карточка не создаётся из-за обзорного объёма."),
    ],
    11: [
        item("1", "source-only title", "Титульная страница лекции."),
        item("2–3", "[[Image Frequency-Domain Transforms]]", "Интуиция разложения сигнала по частотным компонентам."),
        item("4–19", "[[Discrete Fourier and Cosine Transforms for Images]]", "Непрерывное и дискретное преобразования Фурье, спектр, 2D DFT и FFT."),
        item("20–26", "linear-algebra section within [[Image Frequency-Domain Transforms]]", "Линейные пространства, базисы и смена базиса для изображения."),
        item("27–37", "[[Discrete Fourier and Cosine Transforms for Images]]", "DCT, базис, матрица, прямое и обратное преобразование."),
        item("38–44", "[[Walsh-Hadamard Transform]]", "Базис, матрица и примеры прямого и обратного преобразования."),
        item("45–54", "[[Discrete Wavelet Transform]]", "Вейвлет-анализ, 2D DWT, Haar и Daubechies 9/7."),
    ],
    12: [
        item("1", "source-only title", "Титульная страница лекции."),
        item("2–7", "[[Lossless Image Compression]]", "Избыточность данных и общая роль сжатия изображений."),
        item("8–18", "[[JPEG Compression]]", "YCbCr, субдискретизация, ДКП, квантование, зигзагообразный обход и кодирование."),
    ],
    13: [
        item("1", "source-only title", "Титульная страница лекции."),
        item("2–5", "[[Frequency-Domain Image Steganography]]", "Общая схема и свойства частотного встраивания."),
        item("6", "[[Koch-Zhao Method]]", "Сравнение выбранной пары частотных коэффициентов."),
        item("7", "[[Quantization Index Modulation]]", "QIM в частотной области."),
        item("8–9", "error-correction section within [[Frequency-Domain Image Steganography]]", "Ошибки извлечения и итеративное усиление устойчивости."),
        item("10", "[[JPEG Steganography]]", "Переход к квантованным DCT-коэффициентам JPEG."),
        item("11", "[[JSteg]]", "LSB-модификация ненулевых коэффициентов."),
        item("12", "[[Plus-Minus One Steganography]]", "Адаптация PM1 к JPEG-коэффициентам."),
        item("13–14", "[[F3 and F4 JPEG Steganography]]", "Обработка обнуления коэффициентов и знаковое отображение битов."),
        item("15", "[[F5 JPEG Steganography]]", "Матричное кодирование и перестановка коэффициентов."),
    ],
    14: [
        item("1", "source-only title", "Титульная страница лекции."),
        item("2–3", "[[Steganalysis]]", "Постановка задачи обнаружения скрытого вложения."),
        item("4–6", "[[Visual Steganalysis and Bit-Plane Analysis]]", "Битовые плоскости до и после LSB-встраивания."),
        item("7–8", "[[Visual Steganalysis and Bit-Plane Analysis]]; [[JPEG Steganography]]", "DCT-гистограммы JPEG до и после JSteg."),
        item("9", "[[Steganalysis]]", "Эволюция методов обнаружения."),
        item("10–12", "[[Statistical Steganalysis]]", "Парный статистический анализ для LSB."),
        item("13–16", "[[Statistical Steganalysis]]; [[Machine Learning for Steganalysis]]", "Ручные статистические признаки для JPEG."),
        item("17–21", "[[Machine Learning for Steganalysis]]", "k-NN, naive Bayes и закон Бенфорда."),
        item("22–24", "[[Neural Network Steganalysis]]", "Автоматический выбор признаков и основы CNN."),
        item("25–28", "[[Neural Network Steganalysis]] — dated/review examples (2024 course snapshot)", "HUGO/WOW/S-UNIWARD/J-UNIWARD/UED и результаты GNCNN, TLU-CNN, PNet сохранены как датированные примеры курса."),
    ],
}


def page_set(spec: str) -> set[int]:
    result: set[int] = set()
    for part in spec.split(","):
        match = re.fullmatch(r"(\d+)(?:–(\d+))?", part.strip())
        if not match:
            raise ValueError(f"Invalid page scope: {spec}")
        start = int(match.group(1))
        end = int(match.group(2) or start)
        result.update(range(start, end + 1))
    return result


def source_note(record: dict[str, object], manifest: dict[str, object]) -> str:
    number = int(record["lecture"])
    public_name = str(record["public_filename"])
    stem = Path(public_name).stem
    sanitation = record["sanitization"]
    rows = "\n".join(
        f"| {scope} | {localize_references(destination)} | {description} |"
        for scope, destination, description in COVERAGE[number]
    )
    redaction = ""
    if number == 1:
        redaction = " На страницах 3–4 скрыты email и телефон; биографии, имена и публичные профили сохранены."
    return f'''---
type: source
area:
  - Cryptography
  - Computer Science
processing_status: processed
---
# {stem}

## Описание

Лекционные слайды курса [[Course - {COURSE}]], локально обработанные без внешнего OCR, API, векторизации или загрузки содержимого в сторонние сервисы. Нумерация сохранённых страниц совпадает с оригиналом.

## Файлы и целостность

- Публичный PDF: [открыть](<../PDF/{public_name}>).
- Технические данные: [извлечённый текст](<../Processed/{stem}/extracted-text.md>) и [манифест](<../Processed/{stem}/manifest.json>).
- Объём: {manifest["pages"]} публичных страниц из {sanitation["original_pages"]} исходных.
- Исходный SHA-256: `{record["original_sha256"]}`.
- Публичный SHA-256: `{record["public_sha256"]}`.
- Санитаризация: удалена финальная контактная страница оригинала {sanitation["removed_pages"][0]}.{redaction}
- Соответствие страниц: публичные страницы 1–{manifest["pages"]} соответствуют исходным страницам 1–{manifest["pages"]}; исходная страница {sanitation["removed_pages"][0]} не публикуется.

## Матрица покрытия

| Страницы | Назначение | Что учтено |
|---|---|---|
{rows}
| Исходная {sanitation["removed_pages"][0]} | удалено перед публикацией | Финальная контактная страница удалена из публичной копии. |

Для каждой содержательной публичной страницы указано назначение. Формулы и схемы интерпретируются по отрендерованным страницам; автоматически извлечённый текст используется только для поиска.
'''


def main() -> int:
    index = json.loads((ROOT / "source-index.json").read_text(encoding="utf-8"))
    records = index["files"]
    if {int(record["lecture"]) for record in records} != set(COVERAGE):
        raise RuntimeError("Lecture set and coverage map differ")

    NOTES.mkdir(parents=True, exist_ok=True)
    course_rows: list[str] = []
    for record in records:
        number = int(record["lecture"])
        stem = Path(str(record["public_filename"])).stem
        manifest_path = ROOT / "Processed" / stem / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        covered: set[int] = set()
        for scope, _, _ in COVERAGE[number]:
            pages = page_set(scope)
            if covered & pages:
                raise RuntimeError(f"Overlapping coverage in lecture {number:02d}: {scope}")
            covered |= pages
        expected = set(range(1, int(manifest["pages"]) + 1))
        if covered != expected:
            raise RuntimeError(
                f"Incomplete coverage in lecture {number:02d}: missing={sorted(expected-covered)} extra={sorted(covered-expected)}"
            )
        note_path = NOTES / f"Source - {stem}.md"
        note_path.write_text(source_note(record, manifest), encoding="utf-8")

        destinations: list[str] = []
        for _, destination, _ in COVERAGE[number]:
            for link in re.findall(r"\[\[[^]]+\]\]", destination):
                localized_link = localize_references(link)
                if localized_link not in destinations:
                    destinations.append(localized_link)
            if "source-only" in destination and "материал только в источнике" not in destinations:
                destinations.append("материал только в источнике")
            if "dated/review" in destination and "датированный материал, требующий проверки" not in destinations:
                destinations.append("датированный материал, требующий проверки")
        course_rows.append(
            f"| [[Source - {stem}]] | {manifest['pages']} | {'; '.join(destinations)} |"
        )

    course_note = f'''---
type: source
area:
  - Cryptography
  - Computer Science
processing_status: processed
---
# {COURSE}

## О курсе

Курс 2024 года связывает классическую криптографию с обработкой цифровых изображений, стеганографическим встраиванием и стегоанализом. Канонические карточки написаны по-русски своими словами; английские названия методов сохранены для поиска.

Корпус содержит 14 санитаризированных PDF: 256 страниц в оригиналах и 242 публичные страницы. Во всех лекциях удалена финальная контактная страница; в лекции 01 дополнительно скрыты контактные значения на страницах 3–4. Исходные файлы на Desktop не изменялись и проверены по SHA-256. Внешние источники и сервисы не использовались.

## Учебные маршруты

1. Классические шифры и их анализ: [[Классическая криптография]] → [[Шифры подстановки]] и [[Шифры перестановки]] → [[Частотный анализ]] → [[Совершенная секретность и криптографическая стойкость]].
2. Представление изображения: [[Основы цифровых изображений]] → [[Цветовые модели изображений]] → [[Сжатие изображений в JPEG]] → [[Частотные преобразования изображений]].
3. Сокрытие: [[Стеганография]] → пространственные и частотные методы → [[Стегоанализ]].

## Полная матрица покрытия

| Источник | Публичных страниц | Каноническое назначение |
|---|---:|---|
{chr(10).join(course_rows)}

## Правила интерпретации

- Каждая публичная страница отражена в source-note; удалённые контактные страницы отмечены отдельно.
- Сцитала, линейка Энея и дисковый шифратор Джефферсона остаются разделами более общих карточек.
- Формулы шифра Хилла, QIM, PVD, NMI, ДПФ, ДКП, JPEG, вейвлет-преобразований и методов F3–F5 сверяются по локальному рендеру.
- Результаты GNCNN, TLU-CNN, PNet и перечень HUGO/WOW/S-UNIWARD/J-UNIWARD/UED считаются датированным срезом курса 2024 года и требуют проверки перед практическим применением.

## Навигация

- [[Cryptography]] — криптографический маршрут.
- [[Computer Science]] — основы цифровых изображений.
- [[Стеганография]] — самостоятельный маршрут по сокрытию и обнаружению данных.
- [[Sources]] — библиотека источников.
'''
    (ROOT / f"Course - {COURSE}.md").write_text(course_note, encoding="utf-8")
    print(f"Built {len(records)} source notes and one course note; covered {index['public_pages']} public pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
