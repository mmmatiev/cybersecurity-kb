#!/usr/bin/env python3
"""Build the canonical knowledge layer for the cryptography/steganography course."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re

from crypto_steganography_enrichment import (
    DETAILS,
    EXTERNAL_SOURCES,
    Enrichment,
)
from build_thematic_clusters import replace_navigation
from reviewed_course_math import Formula, FORMULAS as REVIEWED_FORMULAS
from reviewed_course_examples import EXAMPLES
from thematic_clusters import organized_note_path, primary_membership


COURSE = "Основы криптографии и стеганографии"
SOURCE_PREFIX = "Source - Основы криптографии и стеганографии - Лекция"
ATTACHMENT_ROOT = "90 Attachments/Courses/Основы криптографии и стеганографии"
UPDATE_START = "<!-- crypto-stego-course:start -->"
UPDATE_END = "<!-- crypto-stego-course:end -->"
GENERATED_MARKER = "<!-- generated: crypto-stego-course -->"


TITLE_MAP: dict[str, str] = {
    "Classical Cryptography": "Классическая криптография",
    "Substitution Ciphers": "Шифры подстановки",
    "Polybius Square": "Квадрат Полибия",
    "Affine Cipher": "Аффинный шифр",
    "Transposition Ciphers": "Шифры перестановки",
    "Cardan Grille Cipher": "Решётка Кардано",
    "Playfair Cipher": "Шифр Плейфера",
    "Hill Cipher": "Шифр Хилла",
    "Vigenere Cipher": "Шифр Виженера",
    "Frequency Analysis": "Частотный анализ",
    "Perfect Secrecy and Cryptographic Strength": "Совершенная секретность и криптографическая стойкость",
    "Digital Image Fundamentals": "Основы цифровых изображений",
    "Image Color Models": "Цветовые модели изображений",
    "Digital Image File Formats": "Форматы цифровых изображений",
    "Lossless Image Compression": "Сжатие изображений без потерь",
    "JPEG Compression": "Сжатие изображений в JPEG",
    "Image Frequency-Domain Transforms": "Частотные преобразования изображений",
    "Discrete Fourier and Cosine Transforms for Images": "ДПФ и ДКП для изображений",
    "Walsh-Hadamard Transform": "Преобразование Уолша—Адамара",
    "Discrete Wavelet Transform": "Дискретное вейвлет-преобразование",
    "Steganography": "Стеганография",
    "Information Hiding": "Сокрытие информации",
    "Digital Steganography": "Цифровая стеганография",
    "Digital Watermarking": "Цифровые водяные знаки",
    "Steganography Quality Metrics": "Метрики качества стеганографии",
    "Digital Watermark Attacks": "Атаки на цифровые водяные знаки",
    "Spatial-Domain Image Steganography": "Стеганография в пространственной области",
    "LSB Steganography": "LSB-стеганография",
    "Plus-Minus One Steganography": "Метод ±1 в стеганографии",
    "Quantization Index Modulation": "Модуляция индекса квантования (QIM)",
    "Pixel Value Differencing": "Метод разности значений пикселей (PVD)",
    "Neighbor Mean Interpolation": "Интерполяция по среднему значению соседних пикселей (NMI)",
    "Frequency-Domain Image Steganography": "Стеганография в частотной области",
    "Koch-Zhao Method": "Метод Коха—Жао",
    "JPEG Steganography": "Стеганография в JPEG",
    "JSteg": "JSteg",
    "F3 and F4 JPEG Steganography": "Методы F3 и F4 в JPEG",
    "F5 JPEG Steganography": "Метод F5 в JPEG",
    "Steganalysis": "Стегоанализ",
    "Visual Steganalysis and Bit-Plane Analysis": "Визуальный стегоанализ и анализ битовых плоскостей",
    "Statistical Steganalysis": "Статистический стегоанализ",
    "Machine Learning for Steganalysis": "Машинное обучение в стегоанализе",
    "Neural Network Steganalysis": "Нейросетевой стегоанализ",
}


SELF_CHECKS: dict[str, tuple[str, str, str]] = {
    "Classical Cryptography": (
        "Чем подстановка отличается от перестановки?",
        "Как условие D_k(E_k(m))=m выражает корректность шифра?",
        "Почему классические шифры нельзя использовать для современной защиты данных?",
    ),
    "Substitution Ciphers": (
        "Что именно задаёт ключ простой подстановки?",
        "Какие статистические свойства языка сохраняются после подстановки?",
        "Чем многоалфавитная подстановка отличается от одноалфавитной?",
    ),
    "Polybius Square": (
        "Как преобразовать символ в координаты квадрата Полибия и обратно?",
        "Как ключевое слово изменяет заполнение таблицы?",
        "Почему известный квадрат является кодированием, а не стойким шифрованием?",
    ),
    "Affine Cipher": (
        "Почему множитель α должен быть взаимно прост с размером алфавита?",
        "Как получить исходный символ из значения y?",
        "Как пары открытого текста и шифртекста помогают восстановить ключ?",
    ),
    "Transposition Ciphers": (
        "Что меняется и что сохраняется при перестановке символов?",
        "Как обратная перестановка восстанавливает исходный блок?",
        "Какие следы оставляет повторение короткой перестановки?",
    ),
    "Cardan Grille Cipher": (
        "Какому условию должны удовлетворять четыре положения решётки?",
        "В каком порядке записываются и считываются символы?",
        "Что произойдёт при перекрытии или пропуске клеток?",
    ),
    "Playfair Cipher": (
        "Как подготовить пару с одинаковыми буквами или нечётной длиной текста?",
        "Какие три правила применяются к биграмме?",
        "Почему шифр Плейфера всё ещё уязвим для статистического анализа?",
    ),
    "Hill Cipher": (
        "При каком условии матрица ключа обратима по модулю m?",
        "Как зашифровать один векторный блок?",
        "Почему известные пары открытых и зашифрованных блоков опасны для ключа?",
    ),
    "Vigenere Cipher": (
        "Как строится гамма из повторяющегося ключа?",
        "Чем повторение ключа отличается от варианта с автоключом?",
        "Почему обнаружение периода упрощает частотный анализ?",
    ),
    "Frequency Analysis": (
        "Какие частоты следует считать для простой замены, Плейфера и Виженера?",
        "Как анализируется шифр Виженера после определения периода?",
        "Почему короткий шифртекст снижает надёжность вывода?",
    ),
    "Perfect Secrecy and Cryptographic Strength": (
        "Как формально выразить совершенную секретность?",
        "Какие условия делают одноразовый блокнот совершенно секретным?",
        "Чем информационно-теоретическая стойкость отличается от вычислительной?",
    ),
    "Digital Image Fundamentals": (
        "Чем растровое изображение отличается от векторного?",
        "Как вычислить несжатый объём изображения по его размерам, каналам и глубине цвета?",
        "Какие преобразования изображения могут уничтожить скрытые данные?",
    ),
    "Image Color Models": (
        "Как канал и глубина цвета влияют на представление пикселя?",
        "Почему одинаковый цвет имеет разные координаты в разных цветовых моделях?",
        "Как преобразование цветовой модели может повлиять на встроенные данные?",
    ),
    "Digital Image File Formats": (
        "Какие части формата описывают пиксели, палитру и служебные данные?",
        "Почему расширения файла недостаточно для понимания внутреннего представления?",
        "Что может произойти со скрытыми данными при преобразовании формата?",
    ),
    "Lossless Image Compression": (
        "Как сжатие без потерь использует избыточность данных?",
        "Как проверить, что декодирование восстановило исходные значения точно?",
        "Почему повторное сохранение без потерь всё равно может изменить структуру файла?",
    ),
    "JPEG Compression": (
        "Из каких основных этапов состоит JPEG-сжатие?",
        "На каком этапе JPEG необратимо теряет информацию?",
        "Почему повторное JPEG-кодирование опасно для скрытого сообщения?",
    ),
    "Image Frequency-Domain Transforms": (
        "Чем пространственное представление изображения отличается от частотного?",
        "Что описывают низкие и высокие частоты изображения?",
        "Как выбор частотной области связан с заметностью и устойчивостью встраивания?",
    ),
    "Discrete Fourier and Cosine Transforms for Images": (
        "Что показывает коэффициент постоянной составляющей?",
        "Почему двумерные ДПФ и ДКП можно вычислять по строкам и столбцам?",
        "Чем комплексный базис ДПФ отличается от косинусного базиса ДКП?",
    ),
    "Walsh-Hadamard Transform": (
        "Из каких значений состоит базис Уолша—Адамара?",
        "Как матричная форма задаёт прямое и обратное преобразование?",
        "Какие коэффициенты разумно выбирать для менее заметного встраивания?",
    ),
    "Discrete Wavelet Transform": (
        "Какие поддиапазоны образуются после одного уровня вейвлет-разложения?",
        "Как многоуровневое разложение отделяет разные масштабы изображения?",
        "Как выбор поддиапазона влияет на заметность и устойчивость вложения?",
    ),
    "Information Hiding": (
        "Чем стеганография отличается от цифровых водяных знаков?",
        "Какие роли выполняют контейнер, сообщение и ключ?",
        "Какие свойства системы сокрытия информации приходится балансировать?",
    ),
    "Digital Steganography": (
        "Какие данные принимают функции встраивания и извлечения?",
        "Как ключ может определять выбор изменяемых элементов контейнера?",
        "Почему ёмкость, незаметность и устойчивость конфликтуют друг с другом?",
    ),
    "Digital Watermarking": (
        "Чем хрупкий водяной знак отличается от устойчивого?",
        "Как BER и NCC характеризуют восстановление метки?",
        "Почему наличие водяного знака само по себе не доказывает авторство?",
    ),
    "Steganography Quality Metrics": (
        "Что измеряют EC, MSE, PSNR, BER и NCC?",
        "Почему высокий PSNR не гарантирует незаметность для стегоанализа?",
        "Какие условия нужно зафиксировать перед сравнением BER или NCC?",
    ),
    "Digital Watermark Attacks": (
        "Какие преобразования могут ослабить или рассинхронизировать водяной знак?",
        "Как оценивать успех атаки вместе с качеством результирующего изображения?",
        "Почему устойчивость к одному воздействию не гарантирует общей устойчивости системы?",
    ),
    "Spatial-Domain Image Steganography": (
        "Какие элементы изображения изменяются при встраивании в пространственной области?",
        "Почему сжатие с потерями и изменение размера разрушают такое вложение?",
        "Чем последовательный обход отличается от ключевого или адаптивного выбора пикселей?",
    ),
    "LSB Steganography": (
        "Как встроить и извлечь один бит методом LSB?",
        "Как обрабатываются значения на границах допустимого диапазона пикселя?",
        "Почему LSB-встраивание выравнивает частоты пар соседних значений?",
    ),
    "Plus-Minus One Steganography": (
        "Чем метод ±1 отличается от прямой замены младшего бита?",
        "Когда значение пикселя нужно увеличить, уменьшить или оставить без изменения?",
        "Какие статистические следы остаются после случайного выбора знака изменения?",
    ),
    "Quantization Index Modulation": (
        "Что определяет шаг квантования q?",
        "Как две сетки квантования кодируют ноль и единицу?",
        "Как увеличение q влияет на устойчивость и заметность изменений?",
    ),
    "Pixel Value Differencing": (
        "Как диапазон разности двух пикселей определяет число встраиваемых битов?",
        "Как распределить необходимое изменение между пикселями пары?",
        "Почему контрастные области допускают большую ёмкость?",
    ),
    "Neighbor Mean Interpolation": (
        "Как из исходного изображения строится интерполированная матрица?",
        "Какие новые значения используются для размещения сообщения?",
        "Почему последующее масштабирование или интерполяция нарушают извлечение?",
    ),
    "Frequency-Domain Image Steganography": (
        "Какие коэффициенты преобразования выбираются для встраивания?",
        "Почему частотное встраивание может пережить часть последующей обработки?",
        "Как ошибки округления влияют на извлечение сообщения?",
    ),
    "Koch-Zhao Method": (
        "Как соотношение двух коэффициентов ДКП кодирует бит?",
        "За что отвечает параметр силы встраивания?",
        "Как получатель извлекает бит без исходного блока?",
    ),
    "JPEG Steganography": (
        "На каком представлении JPEG выполняется встраивание?",
        "Почему нулевые и малые коэффициенты требуют особой обработки?",
        "Как повторное JPEG-кодирование влияет на сообщение и статистику коэффициентов?",
    ),
    "JSteg": (
        "Какие JPEG-коэффициенты JSteg считает пригодными?",
        "Как изменение младшего бита сохраняет знак коэффициента?",
        "Какой статистический след создаёт выравнивание чётных и нечётных значений?",
    ),
    "F3 and F4 JPEG Steganography": (
        "Когда в F3 или F4 возникает эффект обнуления коэффициента?",
        "Чем правило F4 для отрицательных коэффициентов отличается от F3?",
        "Почему после получения нуля тот же бит нужно встраивать повторно?",
    ),
    "F5 JPEG Steganography": (
        "Сколько коэффициентов требуется для кодирования k битов?",
        "Как проверочные XOR-суммы определяют изменяемый коэффициент?",
        "Почему матричное кодирование уменьшает среднее число изменений?",
    ),
    "Steganalysis": (
        "Какие задачи, кроме обнаружения вложения, решает стегоанализ?",
        "Чем визуальный, статистический и обучаемый подходы отличаются друг от друга?",
        "Как несовпадение источников контейнеров искажает оценку детектора?",
    ),
    "Visual Steganalysis and Bit-Plane Analysis": (
        "Что можно увидеть на младших битовых плоскостях изображения?",
        "Как JSteg меняет гистограмму коэффициентов ДКП?",
        "Почему визуальный признак является гипотезой, а не доказательством?",
    ),
    "Statistical Steganalysis": (
        "Как строятся ожидаемые частоты для пар значений в LSB-анализе?",
        "Что измеряет статистика хи-квадрат в этом тесте?",
        "Почему малая или адаптивная нагрузка усложняет обнаружение?",
    ),
    "Machine Learning for Steganalysis": (
        "Из каких этапов состоит классическая схема машинного стегоанализа?",
        "Почему обучающая и проверочная выборки должны соответствовать одному распределению?",
        "Почему классификатор может плохо переноситься на другой метод встраивания?",
    ),
    "Neural Network Steganalysis": (
        "Зачем перед CNN применяют высокочастотную предобработку?",
        "Как связаны P_FA, P_MD и средняя вероятность ошибки?",
        "Почему результаты GNCNN, TLU-CNN и PNet нельзя сравнивать без условий эксперимента?",
    ),
}


PROSE_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ("feature engineering", "выделение признаков"),
    ("embedding methods", "методы встраивания"),
    ("embedding method", "метод встраивания"),
    ("embedding noise", "шум встраивания"),
    ("embedding capacity", "ёмкость встраивания"),
    ("embedding", "встраивание данных"),
    ("cover/stego", "контейнеры и стегоизображения"),
    ("payload", "скрытые данные"),
    ("pipeline", "цепочка обработки"),
    ("padding", "дополнение"),
    ("shrinkage", "эффект обнуления"),
    ("false positive", "ложное срабатывание"),
    ("source-only", "только в источнике"),
    ("Cardan grille", "решётка Кардано"),
    ("Jefferson Disk", "дисковый шифратор Джефферсона"),
    ("autokey-вариантах", "вариантах с автоключом"),
)


def canonical_title(title: str) -> str:
    return TITLE_MAP.get(title, title)


def localize_prose(value: str, *, introduce: str | None = None) -> str:
    text = value
    for old in sorted(TITLE_MAP, key=len, reverse=True):
        replacement = canonical_title(old)
        text = text.replace(f"[[{old}]]", f"[[{replacement}]]")
        if text.startswith(old):
            text = replacement + text[len(old):]
    for old, replacement in PROSE_REPLACEMENTS:
        text = text.replace(old, replacement)
    if introduce and introduce != canonical_title(introduce) and introduce not in text:
        russian = canonical_title(introduce)
        if not re.search(r"(?:[A-ZА-ЯЁ]{2,}|[A-Z]\d)", russian):
            text = text.replace(russian, f"{russian} ({introduce})", 1)
    return text


@dataclass(frozen=True)
class Note:
    title: str
    folder: str
    note_type: str
    area: tuple[str, ...]
    summary: str
    mechanism: tuple[str, ...]
    formulas: tuple[Formula, ...]
    limitations: tuple[str, ...]
    links: tuple[str, ...]
    sources: tuple[tuple[int, str], ...]
    security: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()
    status: str = "learning"
    visuals: tuple[tuple[str, str, int, int], ...] = ()
    extra: str = ""
    enrichment: Enrichment | None = None

    @property
    def path(self) -> Path:
        title = canonical_title(self.title)
        return organized_note_path(Path(self.folder) / f"{title}.md", title)


NOTES: list[Note] = []


def add(**kwargs: object) -> None:
    title = str(kwargs["title"])
    detail = DETAILS.get(title)
    if detail is None:
        raise RuntimeError(f"Missing enrichment for {title}")
    NOTES.append(Note(**kwargs, formulas=REVIEWED_FORMULAS[title], enrichment=detail))


def source(number: int) -> str:
    return f"[[{SOURCE_PREFIX} {number:02d}]]"


def render(note: Note) -> str:
    if note.enrichment is None:
        raise RuntimeError(f"Missing enrichment for {note.title}")
    detail = note.enrichment
    title = canonical_title(note.title)
    yaml = ["---", f"type: {note.note_type}", "area:"]
    yaml.extend(f"  - {value}" for value in note.area)
    if note.security:
        yaml.append("security:")
        yaml.extend(f"  - {value}" for value in note.security)
    aliases = tuple(
        dict.fromkeys(
            alias
            for alias in (note.title, *note.aliases)
            if alias != title
        )
    )
    if aliases:
        yaml.append("aliases:")
        yaml.extend(f'  - "{value}"' for value in aliases)
    if note.status:
        yaml.append(f"status: {note.status}")
    cluster, study_order = primary_membership()[title]
    yaml.append(f'topic: "[[{cluster.basename}]]"')
    yaml.append(f"study_order: {study_order}")
    yaml.append("---")

    summary = localize_prose(note.summary, introduce=note.title)
    mechanism = "\n".join(
        f"{index}. {localize_prose(line)}"
        for index, line in enumerate(note.mechanism, start=1)
    )
    formulas = "\n\n".join(
        f"$$\n{formula.expression}\n$$\n\n**Обозначения и смысл.** {formula.notation}\n\n**Условия применения.** {formula.conditions}"
        for formula in note.formulas
    )
    example = EXAMPLES[note.title].markdown()
    limitations = "\n".join(
        f"- {localize_prose(line)}" for line in (*note.limitations, *detail.mistakes)
    )
    links = "\n".join(f"- [[{canonical_title(link)}]]" for link in note.links)
    prerequisites = "\n".join(
        f"- [[{canonical_title(link)}]]" for link in detail.prerequisites
    ) or "- Специальные предварительные знания не требуются."
    terms = "\n".join(
        f"| {term} | {definition} |" for term, definition in detail.terms
    )
    verification = "\n".join(
        f"- {localize_prose(item)}" for item in detail.verification
    )
    takeaways = "\n".join(
        f"- {localize_prose(item)}" for item in detail.takeaways
    )
    questions = "\n".join(
        f"{index}. {question}"
        for index, question in enumerate(SELF_CHECKS[note.title], start=1)
    )
    answers = "\n>\n".join(
        f"> {index}. {localize_prose(answer)}"
        for index, answer in enumerate(detail.answers, start=1)
    )
    course_sources = "\n".join(
        f"- {source(number)}, стр. {pages}." for number, pages in note.sources
    )
    external_inline = ", ".join(
        f"[{EXTERNAL_SOURCES[key].title}]({EXTERNAL_SOURCES[key].url})"
        for key in detail.source_keys
    )
    external_sources = "\n".join(
        f"- [{EXTERNAL_SOURCES[key].title}]({EXTERNAL_SOURCES[key].url}) — "
        f"{EXTERNAL_SOURCES[key].authors}, {EXTERNAL_SOURCES[key].year}; "
        f"{EXTERNAL_SOURCES[key].kind}."
        for key in detail.source_keys
    )
    deep_dive = ""
    if detail.deep_dive:
        deep_dive = f"\n\n## Дополнительное понимание\n\n{localize_prose(detail.deep_dive)}"
    study_notes = f"\n\n## Пояснение и границы применения\n\n{localize_prose(detail.study_notes)}"
    diagram = ""
    if detail.diagram:
        diagram = f"\n\n## Схема\n\n```mermaid\n{detail.diagram}\n```"
    visuals = ""
    if note.visuals:
        blocks = []
        for filename, caption, number, page in note.visuals:
            blocks.append(
                f"![[{ATTACHMENT_ROOT}/{filename}]]\n\n"
                f"*Что смотреть:* {localize_prose(caption)} "
                f"*Источник:* {source(number)}, стр. {page}."
            )
        visuals = "\n\n## Иллюстрации из курса\n\n" + "\n\n".join(blocks)

    extra = f"\n\n{localize_prose(note.extra.strip())}" if note.extra.strip() else ""
    foundations = f'''## Что нужно знать заранее

{prerequisites}

## Основные понятия

| Термин | Простое объяснение |
|---|---|
{terms}'''
    if note.note_type == "concept":
        middle = f'''## Зачем это нужно

{localize_prose(detail.purpose)} Подтверждающие материалы: {external_inline}.

{foundations}

## Как это устроено

{localize_prose(detail.intuition)}

{mechanism}

## Формальная модель

{formulas}

## Разобранный пример

{example}

{visuals}{diagram}{deep_dive}{study_notes}{extra}

## Ограничения и типичные ошибки

{limitations}'''
    elif note.note_type == "technique":
        middle = f'''## Где применяется

{localize_prose(detail.purpose)} Подтверждающие материалы: {external_inline}.

## Что нужно знать заранее

{prerequisites}

## Входные данные и результат

{localize_prose(detail.intuition)}

### Основные понятия

| Термин | Простое объяснение |
|---|---|
{terms}

## Пошаговый алгоритм

{mechanism}

## Формулы и обозначения

{formulas}

## Разбор примера

{example}

{visuals}{diagram}{deep_dive}{study_notes}{extra}

## Как проверить результат

{verification}

## Ограничения и ошибки

{limitations}'''
    elif note.note_type == "attack":
        middle = f'''## Предпосылки

{localize_prose(detail.purpose)} Подтверждающие материалы: {external_inline}.

{foundations}

## Как проходит атака

{mechanism}

## Последствия и признаки

{formulas}

## Разбор сценария

{example}

{visuals}{diagram}{deep_dive}{study_notes}{extra}

## Противодействие

{verification}

## Ограничения анализа и ошибки

{limitations}'''
    else:
        raise RuntimeError(f"Unsupported generated note type: {note.note_type}")
    opening = "Цель атаки" if note.note_type == "attack" else "Кратко"
    return "\n".join(yaml) + f'''\n{GENERATED_MARKER}
# {title}

## {opening}

{summary}

{middle}

## Что запомнить

{takeaways}

## Связи

{links}

## Самопроверка

{questions}

> [!answer]- Ответы
{answers}

## Источники

### Материалы курса

{course_sources}

### Дополнительные источники

{external_sources}
'''


# Classical cryptography: ten domain notes and one security technique.
add(
    title="Classical Cryptography", folder="01 Knowledge/Cryptography", note_type="concept",
    area=("Cryptography",), aliases=("Классическая криптография",),
    summary="Классическая криптография объединяет ручные и механические шифры, в которых символы заменяются, переставляются или складываются с гаммой. Эти схемы полезны как прозрачные модели ключа, обратимости и криптоанализа, но не как защита современных данных.",
    mechanism=(
        "Подстановка меняет значение символа, сохраняя его позицию; перестановка меняет позицию, сохраняя значение.",
        "Блочная обработка объединяет несколько символов в один объект, а гаммирование добавляет последовательность ключевых символов по модулю мощности алфавита.",
        "Линейка Энея, сцитала и Jefferson Disk в курсе показывают эволюцию от устройства к формальной функции преобразования.",
    ),
    limitations=("Малое пространство ключей и сохранение статистики естественного языка делают схемы уязвимыми.", "Историческая понятность не означает современной криптографической стойкости; применять эти шифры для защиты нельзя."),
    links=("History of Cryptography", "Substitution Ciphers", "Transposition Ciphers", "Vigenere Cipher", "Cryptanalysis"),
    sources=((1, "10–14"), (2, "4–8"), (3, "2–9"), (4, "2–6"), (5, "2–7"), (6, "2–10")),
)
add(
    title="Substitution Ciphers", folder="01 Knowledge/Cryptography", note_type="concept",
    area=("Cryptography",), aliases=("Подстановочные шифры",),
    summary="Шифры подстановки (Substitution Ciphers) заменяют каждый элемент открытого текста другим элементом или группой элементов. Ключ задаёт обратимое отображение алфавита; позиции символов обычно сохраняются, поэтому статистическая структура текста просачивается в шифртекст.",
    mechanism=("Простая замена использует одну перестановку алфавита на всём сообщении.", "Многоалфавитная замена выбирает разные подстановки по позиции или гамме.", "Линейка Энея и квадрат Полибия показывают два способа физически представить таблицу соответствий."),
    limitations=("Простая замена сохраняет односимвольные и многосимвольные частоты.", "Большой формальный размер ключевого пространства не спасает от языковой избыточности и известных фрагментов текста."),
    links=("Polybius Square", "Affine Cipher", "Playfair Cipher", "Vigenere Cipher", "Frequency Analysis"),
    sources=((2, "4–5"), (3, "2–10")),
)
add(
    title="Polybius Square", folder="01 Knowledge/Cryptography", note_type="technique",
    area=("Cryptography",), aliases=("Квадрат Полибия",),
    summary="Polybius Square кодирует символ координатами строки и столбца в ключевой таблице. Метод превращает алфавит в пары чисел и служит строительным блоком для ручных шифров, но сам по себе почти не скрывает статистику текста.",
    mechanism=("Символы заполняют квадратную таблицу; при нехватке ячеек символы объединяют, как I/J в примере курса.", "Шифрование возвращает координату `(row, column)`, расшифрование выполняет обратный поиск.", "Парольная модификация сначала записывает уникальные символы пароля, затем дополняет таблицу оставшимся алфавитом."),
    limitations=("Без секретной перестановки таблица является кодированием, а не стойким шифрованием.", "Даже парольная таблица сохраняет повторения и частоты координатных пар."),
    links=("Substitution Ciphers", "Frequency Analysis", "Classical Cryptography"),
    sources=((3, "3–4"),),
    visuals=(("OCS - Polybius Square - L03 p03.png", "координатную сетку 5×5 и объединение I/J в одной ячейке.", 3, 3),),
)
add(
    title="Affine Cipher", folder="01 Knowledge/Cryptography", note_type="technique",
    area=("Cryptography",), aliases=("Аффинный шифр",),
    summary="Affine Cipher заменяет номер символа линейной функцией по модулю размера алфавита. Пара `(α, β)` является ключом, причём множитель обязан иметь обратный элемент.",
    mechanism=("Алфавит нумеруется элементами `Z_m`.", "Умножение на `α` переставляет классы вычетов, а `β` циклически сдвигает результат.", "В рекуррентном варианте пары параметров выводятся из двух начальных ключей, но преобразование каждого символа остаётся аффинным."),
    limitations=("Число допустимых ключей невелико: `m·φ(m)`, поэтому перебор дешёв.", "Две согласованные пары открытый текст–шифртекст обычно дают систему сравнений для восстановления ключа."),
    links=("Substitution Ciphers", "Rings and Modular Arithmetic", "Frequency Analysis", "Brute-Force Attack"),
    sources=((3, "6–9"),),
    visuals=(("OCS - Affine Cipher - L03 p06.png", "условие обратимости множителя и прямую/обратную формулы по модулю `m`.", 3, 6),),
)
add(
    title="Transposition Ciphers", folder="01 Knowledge/Cryptography", note_type="concept",
    area=("Cryptography",), aliases=("Перестановочные шифры",),
    summary="Шифры перестановки (Transposition Ciphers) не меняют символы, а переставляют их позиции по ключу. Поэтому частоты отдельных символов сохраняются точно, а скрывается лишь локальный порядок.",
    mechanism=("Сообщение делится на блоки фиксированной длины.", "Ключ — перестановка индексов блока; одна и та же перестановка применяется к каждому полному блоку.", "Сцитала задаёт перестановку геометрией намотки, Cardan grille — порядком заполнения отверстий поворотной маски."),
    limitations=("Односимвольные частоты не меняются, поэтому перестановку распознают статистически.", "Короткий блок и повторное применение одной перестановки оставляют заметные периодические зависимости."),
    links=("Cardan Grille Cipher", "Permutation Groups", "Frequency Analysis", "Classical Cryptography"),
    sources=((2, "6"), (4, "2–6")),
)
add(
    title="Cardan Grille Cipher", folder="01 Knowledge/Cryptography", note_type="technique",
    area=("Cryptography",), aliases=("Шифр Кардано", "Поворотная решётка"),
    summary="Cardan Grille Cipher размещает символы через отверстия поворотной маски. После нескольких поворотов все клетки контейнера заполняются, а без знания исходной ориентации и формы решётки порядок чтения скрыт.",
    mechanism=("Выбирается квадратная решётка и набор отверстий.", "На каждом повороте в открытые клетки последовательно записывается часть сообщения.", "После полного цикла заполненная матрица читается в обычном порядке как шифртекст."),
    limitations=("Перекрытие или непокрытые клетки нарушают обратимость и выдают дефект ключа.", "Регулярная геометрия и малое число возможных масок позволяют перебор; метод исторический."),
    links=("Transposition Ciphers", "Permutation Groups", "Classical Cryptography"),
    sources=((4, "3–4"),),
    visuals=(("OCS - Cardan Grille - L04 p03.png", "четыре поворота маски и требование покрыть каждую клетку ровно один раз.", 4, 3),),
)
add(
    title="Playfair Cipher", folder="01 Knowledge/Cryptography", note_type="technique",
    area=("Cryptography",), aliases=("Шифр Плейфера",),
    summary="Playfair Cipher шифрует не отдельные символы, а биграммы с помощью ключевой таблицы. Это размывает односимвольные частоты, но оставляет структуру пар и правила геометрического преобразования.",
    mechanism=("Текст разбивается на пары; повторяющиеся символы пары разделяются служебным символом.", "Символы одной строки сдвигаются вправо, одного столбца — вниз.", "Для разных строк и столбцов берутся противоположные углы образованного прямоугольника."),
    limitations=("Частоты биграмм и фиксированные правила позволяют статистический анализ при достаточном тексте.", "Служебные символы и правила удаления padding могут делать расшифрование неоднозначным."),
    links=("Substitution Ciphers", "Polybius Square", "Frequency Analysis", "Cryptanalysis"),
    sources=((5, "2–3"),),
    visuals=(("OCS - Playfair Cipher - L05 p02.png", "подготовку биграмм и расположение букв в ключевой таблице.", 5, 2),),
)
add(
    title="Hill Cipher", folder="01 Knowledge/Cryptography", note_type="technique",
    area=("Cryptography",), aliases=("Шифр Хилла",),
    summary="Hill Cipher преобразует блок символов умножением на обратимую матрицу над `Z_m`. Он наглядно связывает блочное шифрование с линейной алгеброй и показывает, почему обратимость ключа является частью корректности.",
    mechanism=("Блок из `n` символов представляется вектором-столбцом.", "Матрица ключа перемешивает все координаты блока за одно умножение.", "Рекуррентный вариант порождает следующие матрицы произведением двух предыдущих."),
    limitations=("Известные линейно независимые пары блоков позволяют восстановить матрицу ключа.", "Необратимая матрица делает корректное расшифрование невозможным; padding и порядок координат должны быть заранее согласованы."),
    links=("Rings and Modular Arithmetic", "Linear Cryptanalysis", "Classical Cryptography", "Cryptanalysis"),
    sources=((5, "5–7"),),
    visuals=(("OCS - Hill Cipher - L05 p05.png", "матричную модель блока и условие существования `K^{-1}` по модулю алфавита.", 5, 5),),
)
add(
    title="Vigenere Cipher", folder="01 Knowledge/Cryptography", note_type="technique",
    area=("Cryptography",), aliases=("Шифр Виженера",),
    summary="Vigenere Cipher складывает символы сообщения с периодической или самосинхронизирующейся гаммой по модулю размера алфавита. Это многоалфавитная замена: одинаковая буква может шифроваться по-разному в разных позициях.",
    mechanism=("Ключ задаёт начальную гамму.", "В варианте с повторением ключ циклически продолжается до длины текста.", "В autokey-вариантах продолжение берётся из открытого текста или уже полученного шифртекста."),
    limitations=("Периодический ключ обнаруживается тестом Касиски или индексом совпадений, после чего столбцы анализируются как сдвиги.", "Повторное использование гаммы связывает несколько шифртекстов и раскрывает комбинацию открытых текстов."),
    links=("Substitution Ciphers", "Stream Ciphers and One-Time Pad", "Frequency Analysis", "Cryptanalysis"),
    sources=((6, "5–9"),),
)
add(
    title="Frequency Analysis", folder="01 Knowledge/Cybersecurity/Security Engineering", note_type="technique",
    area=("Cryptography",), security=("Security Engineering",), aliases=("Частотный анализ",),
    summary="Frequency Analysis сопоставляет статистику шифртекста со статистикой предполагаемого языка или структуры данных. Это повторяемая техника криптоанализа, особенно эффективная против простой замены и коротких периодических гамм.",
    mechanism=("Подсчитываются частоты символов, биграмм или других признаков.", "Наблюдаемое распределение сопоставляется с эталонным с учётом длины текста.", "Для Vigenere сначала оценивается период, затем каждая позиционная группа анализируется отдельно."),
    limitations=("Короткий текст даёт шумную оценку, а неизвестный язык или формат ухудшает сопоставление.", "Сжатие, хорошая современная криптография и одноразовая случайная гамма должны устранять полезную языковую статистику."),
    links=("Cryptanalysis", "Substitution Ciphers", "Vigenere Cipher", "Brute-Force Attack"),
    sources=((3, "10"), (5, "8"), (6, "11")),
)
add(
    title="Perfect Secrecy and Cryptographic Strength", folder="01 Knowledge/Cryptography", note_type="concept",
    area=("Cryptography",), aliases=("Совершенная секретность", "Криптографическая стойкость"),
    summary="Совершенная секретность и криптографическая стойкость (Perfect Secrecy and Cryptographic Strength) описывают разные уровни гарантий. Стойкость оценивает ресурсы, необходимые для нарушения заявленной цели, а совершенная секретность требует, чтобы наблюдение шифртекста не меняло распределение вероятностей открытого текста.",
    mechanism=("Принцип Керкгоффса отделяет публичный алгоритм от секретного ключа.", "Вычислительная стойкость зависит от модели атакующего, времени, памяти и данных.", "Абсолютная стойкость не опирается на ограниченность вычислений; курс связывает её с одноразовой случайной гаммой."),
    limitations=("Совершенная секретность переносит сложность в генерацию, доставку, хранение и однократное использование ключа.", "Заявление о стойкости бессмысленно без модели угроз и конкретных параметров."),
    links=("Cryptosystem and Security Goals", "Stream Ciphers and One-Time Pad", "Brute-Force Attack", "Cryptanalysis"),
    sources=((7, "2–4"),),
)


# Digital-image foundations in Computer Science.
add(
    title="Digital Image Fundamentals", folder="01 Knowledge/Computer Science", note_type="concept",
    area=("Computer Science",), aliases=("Основы цифровых изображений",),
    summary="Основы цифровых изображений (Digital Image Fundamentals) начинаются с их представления как дискретной двумерной сетки элементов, каждый из которых хранит одно или несколько числовых значений. Для стеганографии важно различать вид представления, разрешение, число каналов и глубину цвета: именно эти элементы становятся контейнером.",
    mechanism=("Растровое изображение хранит значения пикселей; векторное — геометрические примитивы и правила их отрисовки.", "Бинарные, полутоновые, палитровые и полноцветные растры различаются количеством допустимых значений пикселя.", "Разрешение `M×N`, число каналов и битовая глубина определяют исходный объём данных."),
    limitations=("Одинаковое визуальное изображение может иметь разное внутреннее представление и разную пригодность для встраивания.", "Изменение палитры, размера или формата может уничтожить скрытые данные."),
    links=("Image Color Models", "Digital Image File Formats", "Lossless Image Compression", "Digital Steganography"),
    sources=((9, "2–8"),),
)
add(
    title="Image Color Models", folder="01 Knowledge/Computer Science", note_type="concept",
    area=("Computer Science",), aliases=("Цветовые модели изображений",),
    summary="Цветовые модели изображений (Image Color Models) задают числовые координаты цвета. RGB описывает интенсивности трёх базовых компонентов, а YCbCr отделяет яркость от цветности, что позволяет по-разному обрабатывать визуально неодинаково значимые компоненты.",
    mechanism=("RGB формирует цвет аддитивным сложением красного, зелёного и синего каналов.", "YCbCr хранит яркость `Y` и две цветоразностные компоненты `Cb`, `Cr`.", "Преобразование линейно, но округление и ограничение диапазонов при практической конвертации могут терять информацию."),
    limitations=("Коэффициенты и диапазоны зависят от принятой реализации; нельзя молча смешивать разные матрицы преобразования.", "Стегоалгоритм, работающий с RGB, может не пережить преобразование в YCbCr и обратно."),
    links=("Digital Image Fundamentals", "JPEG Compression", "Spatial-Domain Image Steganography", "Frequency-Domain Image Steganography"),
    sources=((9, "9–15"), (12, "10–11")),
    visuals=(("OCS - RGB Model - L09 p12.png", "три аддитивных компоненты RGB и их вклад в итоговый цвет.", 9, 12), ("OCS - YCbCr Model - L09 p15.png", "формулы перехода между RGB и яркостно-цветностным представлением.", 9, 15)),
)
add(
    title="Digital Image File Formats", folder="01 Knowledge/Computer Science", note_type="concept",
    area=("Computer Science",), aliases=("Форматы цифровых изображений",),
    summary="Форматы цифровых изображений (Digital Image File Formats) определяют, как упакованы пиксели или графические объекты, метаданные, палитра и сжатые данные. Расширение файла не гарантирует способ хранения: для анализа нужно учитывать фактический контейнер и кодек.",
    mechanism=("BMP в курсе служит примером непосредственного растрового хранения без обязательного сжатия.", "GIF использует палитру и поддерживает последовательность кадров.", "PNG сочетает предиктивные фильтры с алгоритмами без потерь; JPEG хранит результат преобразования и квантования с потерями."),
    limitations=("Метаданные и дополнительные секции могут сохраняться или удаляться при пересохранении независимо от пикселей.", "Для стеганографии существенна вся цепочка декодирование–редактирование–повторное кодирование, а не только исходное расширение."),
    links=("Digital Image Fundamentals", "Lossless Image Compression", "JPEG Compression", "JPEG Steganography"),
    sources=((9, "16–21"),),
)
add(
    title="Lossless Image Compression", folder="01 Knowledge/Computer Science", note_type="concept",
    area=("Computer Science",), aliases=("Сжатие изображений без потерь",),
    summary="Сжатие изображений без потерь (Lossless Image Compression) устраняет статистическую и структурную избыточность так, чтобы исходные значения пикселей восстанавливались точно. Оно отличается от JPEG-квантования, где часть информации намеренно отбрасывается.",
    mechanism=("Предсказание или фильтрация превращает значения в более компактно распределённые остатки.", "Словарное или энтропийное кодирование сокращает повторяющиеся и вероятные последовательности.", "Декодер обращает каждый этап и восстанавливает исходный массив байт."),
    limitations=("Для уже сжатых или шумоподобных данных выигрыш мал.", "Хотя значения пикселей сохраняются после декодирования, пересохранение может изменить расположение байтов контейнера и разрушить файловое, но не пиксельное встраивание."),
    links=("Digital Image File Formats", "JPEG Compression", "Digital Image Fundamentals", "LSB Steganography"),
    sources=((9, "17–21"), (12, "2–7")),
)
add(
    title="JPEG Compression", folder="01 Knowledge/Computer Science", note_type="concept",
    area=("Computer Science",), aliases=("Сжатие JPEG",),
    summary="JPEG в объёме курса — последовательность этапов сжатия с потерями: цвет переводится в YCbCr, цветность прореживается, блоки 8×8 проходят дискретное косинусное преобразование, коэффициенты квантуются, располагаются зигзагообразно и энтропийно кодируются.",
    mechanism=("Пиксели каждого канала группируются в блоки 8×8.", "ДКП концентрирует значимую энергию в низких частотах; DC отражает средний уровень, остальные коэффициенты — AC.", "Квантование делит коэффициенты на элементы таблицы и округляет результат, создавая длинные серии нулей для последующего кодирования."),
    limitations=("Квантование необратимо; повторное сохранение в JPEG добавляет новые ошибки.", "Скрытые изменения коэффициентов ДКП должны учитывать нули, значения ±1, таблицы квантования и повторное кодирование."),
    links=("Image Color Models", "Discrete Fourier and Cosine Transforms for Images", "JPEG Steganography", "Frequency-Domain Image Steganography"),
    sources=((12, "8–18"),),
    visuals=(("OCS - JPEG Pipeline - L12 p09.png", "последовательность RGB→YCbCr, прореживание, ДКП, квантование, зигзагообразный обход и кодирование.", 12, 9),),
)
add(
    title="Image Frequency-Domain Transforms", folder="01 Knowledge/Computer Science", note_type="concept",
    area=("Computer Science",), aliases=("Частотные преобразования изображений",),
    summary="Частотные преобразования изображений (Image Frequency-Domain Transforms) представляют изображение коэффициентами выбранного базиса. Низкочастотные компоненты описывают плавные изменения, высокочастотные — быстрые переходы, мелкие детали и шум.",
    mechanism=("Изображение рассматривается как набор строк и столбцов или как матрица в линейном пространстве.", "Прямое преобразование проецирует данные на базис; обратное собирает изображение из коэффициентов.", "ДПФ и ДКП используют глобальные гармонические базисы, преобразование Уолша—Адамара — знаковые прямоугольные функции, а вейвлет-преобразование — функции, локализованные по положению и масштабу."),
    limitations=("Коэффициенты зависят от базиса, нормировки, размера блока и порядка индексов.", "Округление после обратного преобразования способно изменить встроенные биты даже без внешней атаки."),
    links=("Discrete Fourier and Cosine Transforms for Images", "Walsh-Hadamard Transform", "Discrete Wavelet Transform", "Frequency-Domain Image Steganography"),
    sources=((11, "2–3, 20–26"),),
)
add(
    title="Discrete Fourier and Cosine Transforms for Images", folder="01 Knowledge/Computer Science", note_type="concept",
    area=("Computer Science",), aliases=("DFT and DCT for Images", "ДПФ и ДКП изображений"),
    summary="Дискретное преобразование Фурье (ДПФ, DFT) описывает изображение комплексными гармониками, а дискретное косинусное преобразование (ДКП, DCT) — вещественным косинусным базисом. Двумерные преобразования разделимы: сначала обрабатываются строки, затем столбцы.",
    mechanism=("ДПФ хранит амплитуду и фазу комплексных частотных компонентов.", "ДКП использует косинусный базис и хорошо концентрирует энергию естественных изображений.", "Быстрое преобразование Фурье (FFT) ускоряет вычисление ДПФ, не меняя математический результат."),
    limitations=("Положение нулевой частоты и масштаб коэффициентов зависят от соглашений реализации.", "Глобальное преобразование чувствительно к границам; блочная ДКП создаёт отдельные границы каждого блока."),
    links=("Image Frequency-Domain Transforms", "JPEG Compression", "Frequency-Domain Image Steganography", "Koch-Zhao Method"),
    sources=((11, "4–19, 27–37"), (12, "12–13")),
    visuals=(("OCS - DCT Basis - L11 p28.png", "матричное определение ДКП и косинусные коэффициенты базиса.", 11, 28),),
)
add(
    title="Walsh-Hadamard Transform", folder="01 Knowledge/Computer Science", note_type="concept",
    area=("Computer Science",), aliases=("Преобразование Уолша-Адамара",),
    summary="Преобразование Уолша—Адамара раскладывает данные по ортогональным знаковым функциям. Матрица содержит только `+1` и `−1`, поэтому вычисления сводятся к сложениям и вычитаниям.",
    mechanism=("Матрицы порядка степени двойки строятся рекурсивно.", "Двумерное преобразование применяется к строкам и столбцам.", "Нормировка определяет коэффициент обратного преобразования."),
    limitations=("Размер преобразования обычно должен быть степенью двойки или требовать дополнения.", "Ненормированная матрица масштабирует энергию; это нужно учитывать при обратном ходе и порогах встраивания."),
    links=("Image Frequency-Domain Transforms", "Discrete Fourier and Cosine Transforms for Images", "Discrete Wavelet Transform"),
    sources=((11, "38–44"),),
)
add(
    title="Discrete Wavelet Transform", folder="01 Knowledge/Computer Science", note_type="concept",
    area=("Computer Science",), aliases=("Дискретное вейвлет-преобразование", "DWT"),
    summary="Discrete Wavelet Transform разделяет сигнал на низко- и высокочастотные компоненты с локализацией по положению и масштабу. Для изображения фильтрация и прореживание выполняются последовательно по двум измерениям.",
    mechanism=("Фильтры анализа `H0` и `H1` формируют низкочастотную и высокочастотную ветви, затем данные прореживаются вдвое.", "Повторное разложение низкочастотной части создаёт многоуровневое представление.", "Фильтры синтеза и повышение частоты выполняют обратное преобразование."),
    limitations=("Граничная обработка и выбранные фильтры меняют коэффициенты.", "Встраивание в высокочастотные области менее заметно, но такие коэффициенты легче теряются при сглаживании или сжатии."),
    links=("Image Frequency-Domain Transforms", "Walsh-Hadamard Transform", "Frequency-Domain Image Steganography", "Neural Network Steganalysis"),
    sources=((11, "45–54"),),
)


# Steganography: 22 content notes; the MOC is built separately below.
add(
    title="Information Hiding", folder="01 Knowledge/Cybersecurity/Steganography", note_type="concept",
    area=("Computer Science",), security=("Steganography",), aliases=("Сокрытие информации",),
    summary="Information Hiding — общая область методов, которые помещают дополнительные данные в цифровой объект так, чтобы обеспечить требуемое сочетание незаметности, извлекаемости и устойчивости. Стеганография и цифровые водяные знаки используют общий контейнер, но решают разные задачи.",
    mechanism=("Контейнер `C` преобразуется с учётом сообщения `M` и, при необходимости, ключа `K`.", "Получатель извлекает сообщение или проверяет наличие метки по стегообъекту `S`.", "Свойства системы оцениваются по ёмкости, визуальному искажению, устойчивости и обнаружимости."),
    limitations=("Секретность алгоритма не заменяет ключ: анализ предполагает известный метод.", "Оптимизация одного свойства обычно ухудшает другое: большая ёмкость повышает искажение и обнаружимость."),
    links=("Digital Steganography", "Digital Watermarking", "Steganography Quality Metrics", "Steganalysis"),
    sources=((8, "2–5"),),
)
add(
    title="Digital Steganography", folder="01 Knowledge/Cybersecurity/Steganography", note_type="concept",
    area=("Computer Science",), security=("Steganography",), aliases=("Цифровая стеганография",),
    summary="Digital Steganography скрывает сам факт передачи сообщения внутри цифрового контейнера. В отличие от шифрования, цель состоит не только в недоступности содержания, но и в снижении вероятности обнаружения вложения.",
    mechanism=("Процедура встраивания выбирает элементы контейнера и кодирует в них биты сообщения.", "Стеганографический ключ может определять порядок выбора позиций или параметры изменения.", "Извлечение может быть слепым, когда исходный контейнер не нужен, либо опираться на оригинал."),
    limitations=("Незаметность для глаза не равна статистической неразличимости.", "Перекодирование, масштабирование, фильтрация и обрезка могут уничтожить вложение; требования к каналу задаются заранее."),
    links=("Information Hiding", "Spatial-Domain Image Steganography", "Frequency-Domain Image Steganography", "Steganalysis"),
    sources=((8, "2–13"), (10, "14–15")),
)
add(
    title="Digital Watermarking", folder="01 Knowledge/Cybersecurity/Steganography", note_type="concept",
    area=("Computer Science",), security=("Steganography",), aliases=("Цифровые водяные знаки",),
    summary="Digital Watermarking — это встраивание метки, связанной с объектом, владельцем или событием обработки. В отличие от скрытого сообщения, водяной знак часто проектируется так, чтобы сохраняться после допустимых преобразований контейнера.",
    mechanism=("Метка генерируется из идентификатора или проверяемого утверждения.", "Встраивание распределяет её по выбранным пикселям или коэффициентам.", "Проверка оценивает совпадение извлечённой метки с ожидаемой и принимает решение по порогу."),
    limitations=("Устойчивая метка обычно вносит больше искажений, чем хрупкая.", "Водяной знак не доказывает авторство сам по себе: важны ключ, протокол регистрации и доверенная проверка."),
    links=("Information Hiding", "Steganography Quality Metrics", "Digital Watermark Attacks", "Frequency-Domain Image Steganography"),
    sources=((8, "5, 10–18"),),
)
add(
    title="Steganography Quality Metrics", folder="01 Knowledge/Cybersecurity/Steganography", note_type="concept",
    area=("Computer Science",), security=("Steganography",), aliases=("Метрики качества стеганографии",),
    summary="Метрики качества стеганографии (Steganography Quality Metrics) измеряют разные свойства системы: ёмкость — сколько данных помещается в контейнер, MSE и PSNR — насколько он изменён, BER и NCC — насколько точно восстанавливается вложение. Ни одна метрика не описывает безопасность целиком.",
    mechanism=("Ёмкость нормируется на число пикселей, чтобы сравнивать изображения разного размера.", "MSE и PSNR сравнивают исходный и стегообъект на уровне значений пикселей.", "BER и NCC сравнивают исходную и извлечённую битовые последовательности после воздействия."),
    limitations=("Высокий PSNR не гарантирует низкую статистическую обнаружимость.", "Сравнивать BER/NCC корректно только при одинаковом сообщении, атаке и процедуре синхронизации."),
    links=("Digital Steganography", "Digital Watermarking", "Digital Watermark Attacks", "Steganalysis"),
    sources=((8, "10–13, 15–18"),),
)
add(
    title="Digital Watermark Attacks", folder="01 Knowledge/Cybersecurity/Steganography", note_type="attack",
    area=("Computer Science",), security=("Steganography",), aliases=("Атаки на цифровые водяные знаки",),
    summary="Digital Watermark Attacks изменяют контейнер или процедуру проверки, чтобы удалить метку, ухудшить её извлечение или создать ложное решение. В курсе атаки рассматриваются через их влияние на устойчивость метки и визуальное качество контейнера.",
    mechanism=("Сжатие и фильтрация ослабляют выбранные компоненты сигнала.", "Геометрические преобразования нарушают синхронизацию позиций.", "Комбинированные воздействия могут сохранить приемлемое изображение, но увеличить ошибки извлечения."),
    limitations=("Устойчивость проверяют при сжатии, фильтрации, обрезке, изменении масштаба, повороте и сочетании этих воздействий.", "Порог BER или NCC оценивают вместе с полезностью и визуальным качеством результирующего объекта."),
    links=("Digital Watermarking", "Steganography Quality Metrics", "JPEG Compression", "Steganalysis"),
    sources=((8, "14, 18"),),
)
add(
    title="Spatial-Domain Image Steganography", folder="01 Knowledge/Cybersecurity/Steganography", note_type="concept",
    area=("Computer Science",), security=("Steganography",), aliases=("Пространственная стеганография",),
    summary="Spatial-Domain Image Steganography изменяет значения пикселей непосредственно. Методы просты и ёмки, но изменения могут быть уничтожены обработкой изображения или выявлены статистикой соседних значений.",
    mechanism=("Изображение обходится по выбранному ключом порядку.", "Для каждого элемента кодируется один или несколько битов через замену, изменение чётности или адаптивную разность.", "Получатель повторяет порядок и восстанавливает биты из значений пикселей."),
    limitations=("Сжатие с потерями, изменение размера и цветовая коррекция меняют пиксели и разрушают вложение.", "Последовательное заполнение и большой объём вложения создают выраженные статистические следы."),
    links=("LSB Steganography", "Plus-Minus One Steganography", "Pixel Value Differencing", "Neighbor Mean Interpolation", "Statistical Steganalysis"),
    sources=((8, "6–9"), (10, "2–13")),
)
add(
    title="LSB Steganography", folder="01 Knowledge/Cybersecurity/Steganography", note_type="technique",
    area=("Computer Science",), security=("Steganography",), aliases=("LSB-встраивание",),
    summary="LSB Steganography заменяет один или несколько младших битов значения пикселя битами сообщения. Изменение младшего бита не превышает единицы, поэтому обычно визуально незаметно, но создаёт характерные статистические пары значений.",
    mechanism=("Пиксель представляется двоичным словом.", "Младший бит заменяется очередным битом сообщения; при извлечении читается чётность.", "Для цветного изображения канал и порядок пикселей должны быть согласованы."),
    limitations=("Последовательный LSB уязвим к визуальному анализу битовых плоскостей и тесту пар значений.", "Повторное JPEG-кодирование и другие изменения пикселей обычно уничтожают вложение."),
    links=("Spatial-Domain Image Steganography", "Plus-Minus One Steganography", "Visual Steganalysis and Bit-Plane Analysis", "Statistical Steganalysis"),
    sources=((10, "3"),),
    visuals=(("OCS - LSB Embedding - L10 p03.png", "замену последних битов RGB-компонент и минимальный масштаб изменения пикселя.", 10, 3),),
)
add(
    title="Plus-Minus One Steganography", folder="01 Knowledge/Cybersecurity/Steganography", note_type="technique",
    area=("Computer Science",), security=("Steganography",), aliases=("PM1 Steganography", "Стеганография плюс-минус один"),
    summary="Plus-Minus One Steganography кодирует бит чётностью значения, но при несовпадении случайно увеличивает или уменьшает элемент на единицу. В отличие от прямой LSB-замены, направление изменения не детерминировано.",
    mechanism=("Если чётность уже совпадает с битом, значение не меняется.", "Иначе случайный бит выбирает `+1` или `−1` с учётом допустимого диапазона.", "В JPEG-версии операция применяется к пригодным квантованным коэффициентам."),
    limitations=("Границы 0 и 255 требуют отдельного правила, иначе возможен выход из диапазона.", "Изменение гистограммы остаётся статистически обнаружимым, особенно при большой заполненности."),
    links=("LSB Steganography", "Spatial-Domain Image Steganography", "JPEG Steganography", "Statistical Steganalysis"),
    sources=((10, "4–5"), (13, "12")),
    visuals=(("OCS - PM1 Embedding - L10 p05.png", "пары исходной и изменённой матриц и выбор изменения на единицу.", 10, 5),),
)
add(
    title="Quantization Index Modulation", folder="01 Knowledge/Cybersecurity/Steganography", note_type="technique",
    area=("Computer Science",), security=("Steganography",), aliases=("QIM", "Модуляция индекса квантования"),
    summary="Quantization Index Modulation кодирует бит выбором одного из двух сдвинутых квантователей. Одинаковая идея применяется к значениям пикселей и к частотным коэффициентам.",
    mechanism=("Шаг `q` задаёт расстояние между допустимыми уровнями.", "Нулевой и единичный биты отображаются в разные подрешётки уровней.", "Извлечение моделирует оба кандидата и выбирает ближайший."),
    limitations=("Большой `q` повышает устойчивость, но увеличивает искажение.", "Округление и последующее квантование могут переместить значение к другому классу и вызвать BER."),
    links=("Spatial-Domain Image Steganography", "Frequency-Domain Image Steganography", "Steganography Quality Metrics", "Koch-Zhao Method"),
    sources=((10, "6–7"), (13, "7")),
    visuals=(("OCS - QIM Embedding - L10 p07.png", "работу `q=4` на конкретной матрице и два семейства квантованных уровней.", 10, 7),),
)
add(
    title="Pixel Value Differencing", folder="01 Knowledge/Cybersecurity/Steganography", note_type="technique",
    area=("Computer Science",), security=("Steganography",), aliases=("PVD Steganography", "Метод разности значений пикселей"),
    summary="Pixel Value Differencing подстраивает объём вложения под локальный контраст: пара соседних пикселей переносит больше битов, если их разность попадает в широкий диапазон. Необходимое изменение распределяется между двумя пикселями.",
    mechanism=("Изображение разбивается на непересекающиеся пары и вычисляется `d=P_i-P_{i+1}`.", "Модуль разности выбирает диапазон `[l_k,u_k]` и число встраиваемых битов.", "Фрагмент сообщения задаёт новую разность, после чего оба пикселя корректируются в противоположных направлениях."),
    limitations=("Нужно контролировать underflow/overflow и не менять принадлежность пары диапазону.", "Таблица диапазонов и порядок пар являются частью формата; ошибки синхронизации ломают извлечение."),
    links=("Spatial-Domain Image Steganography", "Neighbor Mean Interpolation", "Steganography Quality Metrics", "Statistical Steganalysis"),
    sources=((10, "8–10"),),
    visuals=(("OCS - PVD Embedding - L10 p10.png", "переход от разности 9 к 11 и симметричное изменение пары пикселей.", 10, 10),),
)
add(
    title="Neighbor Mean Interpolation", folder="01 Knowledge/Cybersecurity/Steganography", note_type="technique",
    area=("Computer Science",), security=("Steganography",), aliases=("NMI Steganography", "Интерполяция среднего соседей"),
    summary="Neighbor Mean Interpolation сначала увеличивает изображение, создавая интерполированные пиксели, а затем использует разность между прогнозом и опорным значением как пространство для вложения.",
    mechanism=("Из исходной сетки `m×n` строится сетка `2m×2n`; исходные пиксели становятся опорными.", "Новые значения вычисляются как средние соседей.", "В каждый интерполированный пиксель добавляется числовое представление фрагмента сообщения; извлечение повторяет интерполяцию и берёт разность."),
    limitations=("Ёмкость зависит от допустимых разностей и правил округления.", "Масштабирование или повторная интерполяция меняют предсказанные значения и нарушают извлечение."),
    links=("Spatial-Domain Image Steganography", "Pixel Value Differencing", "Digital Image Fundamentals", "Steganography Quality Metrics"),
    sources=((10, "11–13"),),
    visuals=(("OCS - NMI Embedding - L10 p13.png", "исходную, интерполированную и стегоматрицу вместе с первыми расчётами объёма вложения.", 10, 13),),
)
add(
    title="Frequency-Domain Image Steganography", folder="01 Knowledge/Cybersecurity/Steganography", note_type="concept",
    area=("Computer Science",), security=("Steganography",), aliases=("Частотная стеганография",),
    summary="Frequency-Domain Image Steganography встраивает данные в коэффициенты преобразования, после чего выполняется обратное преобразование. Такие методы обычно устойчивее к части последующей обработки, но сложнее и чувствительны к ошибкам округления.",
    mechanism=("Контейнер преобразуется с помощью ДКП, ДПФ, преобразования Уолша—Адамара или вейвлет-преобразования.", "При встраивании выбранные коэффициенты изменяются с учётом частотной области и заданной силы.", "После обратного преобразования пиксели округляются; получатель снова вычисляет спектр и извлекает биты."),
    limitations=("Выбор слишком низких частот заметен, слишком высоких — хрупок.", "Реализация должна учитывать нормировку преобразования и повторное целочисленное округление."),
    links=("Image Frequency-Domain Transforms", "Koch-Zhao Method", "Quantization Index Modulation", "JPEG Steganography", "Steganalysis"),
    sources=((8, "6–8"), (13, "2–9")),
)
add(
    title="Koch-Zhao Method", folder="01 Knowledge/Cybersecurity/Steganography", note_type="technique",
    area=("Computer Science",), security=("Steganography",), aliases=("Метод Коха и Жао",),
    summary="Метод Коха—Жао кодирует один бит соотношением двух среднечастотных коэффициентов ДКП. Порог `p` задаёт минимальную разность между ними и тем самым управляет компромиссом между заметностью и устойчивостью.",
    mechanism=("В каждом блоке ДКП выбираются два согласованных AC-коэффициента.", "Для бита 0 модуль первого делают больше модуля второго как минимум на `p`; для бита 1 — наоборот.", "При извлечении сравниваются абсолютные значения выбранной пары."),
    limitations=("Малый `p` даёт ошибки после округления, большой создаёт заметное искажение.", "Позиции коэффициентов и порядок блоков должны быть известны извлекателю и защищены ключом."),
    links=("Frequency-Domain Image Steganography", "Discrete Fourier and Cosine Transforms for Images", "Steganography Quality Metrics", "Steganalysis"),
    sources=((13, "6"),),
    visuals=(("OCS - Koch Zhao - L13 p06.png", "два среднечастотных коэффициента, порог `p` и противоположные неравенства для 0 и 1.", 13, 6),),
)
add(
    title="JPEG Steganography", folder="01 Knowledge/Cybersecurity/Steganography", note_type="concept",
    area=("Computer Science",), security=("Steganography",), aliases=("Стеганография JPEG",),
    summary="JPEG Steganography изменяет квантованные коэффициенты ДКП внутри процесса JPEG-кодирования. Методы должны сохранять корректную структуру файла и учитывать особую роль нулей, значений ±1, а также DC- и AC-коэффициентов.",
    mechanism=("JPEG декодируется до квантованных коэффициентов, не обязательно до пикселей.", "Пригодные AC-коэффициенты выбираются по правилам метода и порядку ключа.", "После модификации коэффициенты снова энтропийно кодируются."),
    limitations=("Повторное полное JPEG-кодирование меняет коэффициенты и может уничтожить скрытые данные.", "Изменение нулей и малых коэффициентов сильно влияет на длины серий, размер файла и статистическую обнаружимость."),
    links=("JPEG Compression", "JSteg", "F3 and F4 JPEG Steganography", "F5 JPEG Steganography", "Statistical Steganalysis"),
    sources=((13, "10–15"), (14, "7–8, 14–16")),
)
add(
    title="JSteg", folder="01 Knowledge/Cybersecurity/Steganography", note_type="technique",
    area=("Computer Science",), security=("Steganography",), aliases=("JSteg JPEG Steganography",),
    summary="JSteg переносит идею LSB на квантованные коэффициенты ДКП в JPEG: младший бит модуля пригодного коэффициента заменяется битом сообщения. Значения −1, 0 и 1 исключаются, чтобы не создавать неоднозначность.",
    mechanism=("Коэффициенты обходятся в согласованном порядке.", "Непригодные значения пропускаются.", "Для остальных меняется младший бит абсолютного значения, знак сохраняется."),
    limitations=("Регулярное выравнивание чётных и нечётных коэффициентов оставляет статистический след.", "Пропуски требуют точного совпадения порядка коэффициентов у отправителя и получателя."),
    links=("JPEG Steganography", "LSB Steganography", "F3 and F4 JPEG Steganography", "Statistical Steganalysis"),
    sources=((13, "11"),),
    visuals=(("OCS - JSteg - L13 p11.png", "исключение малых коэффициентов и LSB-замену с сохранением знака.", 13, 11),),
)
add(
    title="F3 and F4 JPEG Steganography", folder="01 Knowledge/Cybersecurity/Steganography", note_type="technique",
    area=("Computer Science",), security=("Steganography",), aliases=("F3", "F4", "F3 and F4"),
    summary="F3 и F4 уменьшают модуль ненулевого JPEG-коэффициента, когда его отображаемый бит не совпадает с сообщением. F4 меняет правило интерпретации отрицательных коэффициентов, чтобы уменьшить асимметрию знаков.",
    mechanism=("Нули пропускаются.", "F3 при необходимости уменьшает модуль; если получается ноль, коэффициент считается обнулённым, а тот же бит переносится дальше.", "F4 использует противоположное соответствие чётности для отрицательных значений и также повторяет встраивание после обнуления."),
    limitations=("Обнуление коэффициентов меняет число нулей и длину обхода.", "Даже исправление знаковой асимметрии не устраняет все статистические зависимости."),
    links=("JPEG Steganography", "JSteg", "F5 JPEG Steganography", "Statistical Steganalysis"),
    sources=((13, "13–14"),),
    visuals=(("OCS - F3 F4 - L13 p14.png", "условия F4 для положительных и отрицательных коэффициентов и повторное встраивание после обнуления.", 13, 14),),
)
add(
    title="F5 JPEG Steganography", folder="01 Knowledge/Cybersecurity/Steganography", note_type="technique",
    area=("Computer Science",), security=("Steganography",), aliases=("F5 Steganography",),
    summary="F5 JPEG Steganography применяет матричное кодирование к группам коэффициентов: В группе без обнуления несколько битов можно встроить, изменив не более одного коэффициента. При обнулении группа перестраивается, и изменений может потребоваться больше. Поэтому на каждый бит сообщения приходится меньше изменений.",
    mechanism=("Пригодные ненулевые коэффициенты собираются в группы.", "Группа из `2^k−1` коэффициентов кодирует `k` битов через проверочные XOR-суммы.", "Если проверочные значения не совпадают, уменьшается модуль одного выбранного коэффициента; при его обнулении встраивание повторяется."),
    limitations=("Матричное кодирование снижает число изменений, но не гарантирует неразличимость.", "Корректная обработка нулей и синхронизация перестановки обязательны для извлечения."),
    links=("JPEG Steganography", "F3 and F4 JPEG Steganography", "Steganography Quality Metrics", "Statistical Steganalysis"),
    sources=((13, "15"),),
    visuals=(("OCS - F5 - L13 p15.png", "матрицу вложения для двух битов и выбор единственного изменяемого коэффициента.", 13, 15),),
)
add(
    title="Steganalysis", folder="01 Knowledge/Cybersecurity/Steganography", note_type="concept",
    area=("Computer Science",), security=("Steganography", "DFIR"), aliases=("Стегоанализ",),
    summary="Steganalysis исследует наличие, тип или параметры скрытого вложения в цифровом объекте. Базовая задача курса — бинарная классификация: определить, является изображение чистым контейнером или стегообъектом.",
    mechanism=("Визуальные методы исследуют битовые плоскости, спектры и гистограммы.", "Статистические методы проверяют ожидаемые распределения и зависимости.", "Машинное обучение строит признаки или извлекает их автоматически и обучает классификатор на чистых и модифицированных примерах."),
    limitations=("Детектор может запомнить особенности камеры, цепочки обработки или источника данных вместо следа встраивания.", "Результаты нельзя переносить на другой объём вложения, формат или распределение изображений без новой проверки."),
    links=("Visual Steganalysis and Bit-Plane Analysis", "Statistical Steganalysis", "Machine Learning for Steganalysis", "Neural Network Steganalysis", "Digital Steganography"),
    sources=((8, "12"), (14, "2–28")),
)
add(
    title="Visual Steganalysis and Bit-Plane Analysis", folder="01 Knowledge/Cybersecurity/Steganography", note_type="technique",
    area=("Computer Science",), security=("Steganography", "DFIR"), aliases=("Визуальный стегоанализ", "Анализ битовых плоскостей"),
    summary="Визуальный стегоанализ и анализ битовых плоскостей (Visual Steganalysis and Bit-Plane Analysis) делают слабые регулярные изменения заметнее на отдельных битовых плоскостях, гистограммах значений и спектрах ДКП. Это быстрый способ сформировать гипотезу, но не доказательство.",
    mechanism=("Каждый разряд пикселей визуализируется отдельным бинарным изображением.", "Сравниваются структура младших плоскостей и ожидаемый шум.", "Для JPEG анализируются гистограммы коэффициентов ДКП до и после предполагаемого встраивания."),
    limitations=("Оценка человеком субъективна и зависит от масштаба, палитры и содержимого.", "Адаптивные методы могут не давать видимого артефакта; вывод нужно подтверждать статистикой."),
    links=("LSB Steganography", "JPEG Steganography", "Statistical Steganalysis", "Steganalysis"),
    sources=((14, "4–8"),),
    visuals=(("OCS - Bit Planes - L14 p05.png", "изменение младших битовых плоскостей после LSB-встраивания.", 14, 5), ("OCS - DCT Histogram - L14 p08.png", "деформацию распределения коэффициентов ДКП после JSteg.", 14, 8)),
)
add(
    title="Statistical Steganalysis", folder="01 Knowledge/Cybersecurity/Steganography", note_type="technique",
    area=("Computer Science",), security=("Steganography", "DFIR"), aliases=("Статистический стегоанализ",),
    summary="Statistical Steganalysis проверяет, нарушило ли встраивание ожидаемые частоты и зависимости элементов изображения. В простейшем LSB-анализе пары значений, различающиеся младшим битом, после заполнения стремятся к одинаковым частотам.",
    mechanism=("Значения группируются в пары `(2j,2j+1)`.", "Из общего числа элементов пары вычисляется ожидаемая частота после LSB-встраивания.", "Хи-квадрат сопоставляет наблюдаемое и ожидаемое распределения; для JPEG используются гистограммы и межблочные зависимости."),
    limitations=("Тест рассчитан на конкретный алгоритм и способ заполнения; малый или адаптивно распределённый объём вложения может остаться незамеченным.", "Обычная обработка изображения тоже меняет статистику и может вызвать ложное срабатывание."),
    links=("LSB Steganography", "Visual Steganalysis and Bit-Plane Analysis", "Machine Learning for Steganalysis", "Steganalysis"),
    sources=((14, "10–16"),),
    visuals=(("OCS - Pairs of Values - L14 p12.png", "формирование пар, ожидаемые частоты и различие результатов для чистого и заполненного изображения.", 14, 12),),
)
add(
    title="Machine Learning for Steganalysis", folder="01 Knowledge/Cybersecurity/Steganography", note_type="technique",
    area=("Computer Science", "AI & ML"), security=("Steganography", "DFIR"), aliases=("Машинное обучение для стегоанализа",),
    summary="Machine Learning for Steganalysis рассматривает обнаружение как задачу классификации по статистическим признакам изображения. В классической схеме признаки вычисляются отдельно, а затем используются для обучения k-NN, наивного байесовского классификатора, SVM, логистической регрессии или другой модели.",
    mechanism=("Из чистых и стегоизображений строятся сопоставимые обучающие выборки.", "Для каждого объекта вычисляется вектор пространственных или JPEG-признаков.", "Классификатор обучается и проверяется на независимой выборке из того же операционного распределения."),
    limitations=("Для каждого изображения обучающей выборки должны быть вычислены признаки и известен правильный класс.", "Качество зависит от того, совпадают ли тип контейнера и метод встраивания в обучающей и исследуемой выборках."),
    links=("Statistical Steganalysis", "Neural Network Steganalysis", "Steganalysis", "JPEG Steganography"),
    sources=((14, "13–22"),),
    visuals=(("OCS - Classification Pipeline - L14 p14.png", "три этапа анализа: вычисление признаков, подготовку обучающей выборки и работу классификатора.", 14, 14),),
)
add(
    title="Neural Network Steganalysis", folder="01 Knowledge/Cybersecurity/Steganography", note_type="technique",
    area=("Computer Science", "AI & ML"), security=("Steganography", "DFIR"), aliases=("Нейросетевой стегоанализ",), status="review",
    summary="Neural Network Steganalysis использует глубокие модели для поиска слабых следов встраивания непосредственно в изображениях или их остаточных представлениях. В курсе этот подход противопоставляется ручному выделению признаков, а конкретные архитектуры и результаты отражают состояние материала на 2024 год.",
    mechanism=("Высокочастотная предобработка или первые слои подавляют содержание изображения и усиливают шум встраивания.", "CNN обучается различать чистые контейнеры и стегоизображения на парных или сбалансированных наборах.", "Качество оценивается отдельно для конкретного метода встраивания, объёма вложения и источника изображений."),
    limitations=("`status: review`: результаты GNCNN, TLU-CNN, PNet и список HUGO/WOW/S-UNIWARD/J-UNIWARD/UED датированы курсом 2024 года.", "Пример PNet показывает, насколько ошибка зависит от присутствия исследуемого метода встраивания в обучающей выборке."),
    links=("Machine Learning for Steganalysis", "Statistical Steganalysis", "Discrete Wavelet Transform", "JPEG Steganography", "Steganalysis"),
    sources=((14, "22–28"),),
    visuals=(("OCS - GNCNN - L14 p26.png", "архитектуру GNCNN и условия приведённого эксперимента, а не только процент ошибки.", 14, 26), ("OCS - PNet - L14 p28.png", "зависимость результата PNet от совпадения метода встраивания при обучении и проверке.", 14, 28)),
    extra="""## Датированный материал курса

Перечень адаптивных методов встраивания и результаты трёх CNN сохранены для понимания эволюции подходов. Внешние первичные публикации уточняют общую методику проверки, но не превращают несопоставимые результаты курса в рейтинг современных архитектур.""",
)


STEGANOGRAPHY_MOC = rf'''---
type: moc
area:
  - Cybersecurity
security:
  - Steganography
aliases:
  - "Steganography"
---
{GENERATED_MARKER}
# Стеганография

Стеганография (Steganography) — самостоятельный маршрут по сокрытию данных в цифровых изображениях, устойчивости вложения и его обнаружению. Основы криптографии и стеганографии изучаются рядом, но решают разные задачи: криптография скрывает содержание, стеганография — наличие канала.

## Как изучать

1. [[Сокрытие информации]] задаёт общую модель, после чего [[Цифровая стеганография]] и [[Цифровые водяные знаки]] разделяют цели тайной связи и маркирования.
2. [[Основы цифровых изображений]] → [[Цветовые модели изображений]] → [[Форматы цифровых изображений]] объясняют, какие данные фактически изменяет алгоритм.
3. [[Стеганография в пространственной области]] → [[LSB-стеганография]] → адаптивные методы показывают путь от простого изменения бита к выбору позиции по свойствам изображения.
4. [[Частотные преобразования изображений]] → [[Стеганография в частотной области]] → [[Стеганография в JPEG]] переносят встраивание к коэффициентам и реальной цепочке кодека.
5. [[Стегоанализ]] связывает визуальные, статистические и обучаемые детекторы и объясняет, как честно проверять обнаружимость.

## Основы и метрики

- [[Сокрытие информации]] — цели, участники и общий компромисс системы.
- [[Цифровая стеганография]] — скрытый канал, ключ и модель наблюдателя.
- [[Цифровые водяные знаки]] → [[Атаки на цифровые водяные знаки]] — маркирование и проверка устойчивости.
- [[Метрики качества стеганографии]] — MSE, PSNR, BER, NCC и ошибки детектора.
- [[Основы цифровых изображений]], [[Цветовые модели изображений]], [[Сжатие изображений в JPEG]] — необходимая техническая основа.

## Встраивание в пространственной области

- [[Стеганография в пространственной области]]
  - [[LSB-стеганография]] — прямая замена младшего бита.
  - [[Метод ±1 в стеганографии]] — согласование бита случайным изменением значения.
  - [[Модуляция индекса квантования (QIM)]] — выбор одной из решёток квантования.
  - [[Метод разности значений пикселей (PVD)]] — ёмкость по локальному контрасту.
  - [[Интерполяция по среднему значению соседних пикселей (NMI)]] — вложение в интерполированные значения.

## Встраивание в частотной области и JPEG

- [[Стеганография в частотной области]]
  - [[Метод Коха—Жао]] — кодирование сравнением пары коэффициентов.
  - [[Модуляция индекса квантования (QIM)]] — перенос решёток в пространство коэффициентов.
- [[Стеганография в JPEG]]
  - [[JSteg]] — последовательная LSB-подобная модификация.
  - [[Методы F3 и F4 в JPEG]] — движение коэффициентов к нулю и проблема обнуления.
  - [[Метод F5 в JPEG]] — перестановка и матричное кодирование.

## Стегоанализ

- [[Стегоанализ]]
  - [[Визуальный стегоанализ и анализ битовых плоскостей]] — быстрый поиск явных структур.
  - [[Статистический стегоанализ]] — проверка распределений и зависимостей.
  - [[Машинное обучение в стегоанализе]] — ручные признаки и классификатор.
  - [[Нейросетевой стегоанализ]] — обучение признаков вместе с моделью; результаты курса 2024 года имеют `status: review`.

## Формальная модель

$$
S=Embed(C,M,K),\qquad \hat M=Extract(S,K),\qquad Detect(S)\rightarrow\{{cover,stego\}}
$$

Здесь `C` — исходный контейнер, `M` — сообщение, `K` — ключ, а `S` — полученный стегообъект.

## Источник курса

- [[Course - {COURSE}]]

Вернуться к [[Cybersecurity]] и [[Cryptography]].
'''


# Keep the generated MOC on the shared thematic route. Content notes are unchanged.
STEGANOGRAPHY_MOC = replace_navigation("stego", STEGANOGRAPHY_MOC)


EXISTING_UPDATES: dict[Path, str] = {
    Path("01 Knowledge/Cryptography/History of Cryptography.md"): f'''## Дополнение из курса «{COURSE}»

Курс делит развитие криптографии на донаучный этап ручных устройств и преобразований, классический этап формализации подстановок и перестановок и современный этап вычислительных алгоритмов. Линейка Энея, сцитала и дисковый шифратор Джефферсона сохранены как исторические примеры внутри [[Classical Cryptography]], а не как отдельные карточки.

- {source(2)}, стр. 2–3.
- {source(3)}, стр. 2.
- {source(4)}, стр. 2.
- {source(5)}, стр. 4.''',
    Path("01 Knowledge/Cryptography/Cryptosystem and Security Goals.md"): f'''## Дополнение из курса «{COURSE}»

Материал связывает криптографические преобразования с разными задачами защиты: шифрование обеспечивает конфиденциальность, хеш-функция помогает обнаружить случайные изменения, код аутентификации сообщения (MAC) подтверждает целостность и знание общего секрета, а цифровая подпись позволяет проверить автора и защищает от отказа от авторства. Эти механизмы не заменяют друг друга.

- {source(1)}, стр. 8–19.''',
    Path("01 Knowledge/Cryptography/Cryptanalysis.md"): f'''## Дополнение из курса «{COURSE}»

Исторические примеры помогают выбрать модель атаки: простая замена сохраняет частоты символов, шифры Плейфера и Хилла переносят статистические зависимости на биграммы и блоки, а для шифра Виженера с повторяющимся ключом сначала определяют период с помощью теста Касиски или индекса совпадений. В лекции 07 отдельно разобраны атаки только по шифртексту (ciphertext-only), с известным открытым текстом (known-plaintext), с выбранным открытым текстом (chosen-plaintext) и с выбранным шифртекстом (chosen-ciphertext).

- {source(3)}, стр. 10.
- {source(5)}, стр. 8.
- {source(6)}, стр. 11.
- {source(7)}, стр. 6–7.''',
    Path("01 Knowledge/Cryptography/Rings and Modular Arithmetic.md"): f'''## Дополнение из курса «{COURSE}»

Арифметика остатков служит общим языком классических формул: аффинный шифр требует обратимости множителя по модулю алфавита, шифр Хилла — обратимости определителя матрицы, а шифр Виженера — сложения и вычитания символов в `Z_m`. Перед ручным расчётом нужно явно зафиксировать нумерацию алфавита.

- {source(2)}, стр. 9–12.
- {source(3)}, стр. 6–9.
- {source(5)}, стр. 5–7.
- {source(6)}, стр. 5–10.''',
    Path("01 Knowledge/Cryptography/Symmetric-Key Cryptography.md"): f'''## Дополнение из курса «{COURSE}»

Курс показывает общий секрет на самых прозрачных схемах: одна и та же ключевая информация задаёт прямое и обратное преобразование. Исторические подстановки и перестановки полезны для понимания модели, но не наследуют стойкость современных блочных и потоковых примитивов.

- {source(1)}, стр. 13–14.
- {source(2)}, стр. 4–8.''',
    Path("01 Knowledge/Cryptography/Stream Ciphers and One-Time Pad.md"): f'''## Дополнение из курса «{COURSE}»

Шифр Вернама записан как сложение по модулю 2. Совершенная секретность относится только к одноразовой случайной гамме длины сообщения; повторение гаммы превращает XOR двух шифртекстов в XOR открытых текстов и создаёт основу восстановления.

- {source(6)}, стр. 10–11.
- {source(7)}, стр. 4.''',
    Path("01 Knowledge/Cryptography/Cryptographic Hash Functions.md"): f'''## Дополнение из курса «{COURSE}»

Во вводной лекции хеш-функция используется для контроля случайных искажений: отправитель и получатель сравнивают хеш-значения. Для защиты от активного противника одной публичной хеш-функции недостаточно — требуется [[Message Authentication Codes|код аутентификации сообщения]] или [[Digital Signatures|цифровая подпись]].

- {source(1)}, стр. 15–16.''',
    Path("01 Knowledge/Cryptography/Message Authentication Codes.md"): f'''## Дополнение из курса «{COURSE}»

Имитовставка отличается от обычной хеш-функции наличием общего секретного ключа. Проверяющая сторона вычисляет тег заново: совпадение подтверждает целостность и знание ключа, но не обеспечивает публичную неотказуемость.

- {source(1)}, стр. 17.''',
    Path("01 Knowledge/Cryptography/Digital Signatures.md"): f'''## Дополнение из курса «{COURSE}»

Базовая схема курса разделяет ключ подписи и ключ проверки: подписывается сообщение или его хеш-значение, а получатель проверяет результат открытым ключом. Защита от изменения и отказа от авторства работает только при корректной привязке открытого ключа к владельцу.

- {source(1)}, стр. 18–19.''',
    Path("01 Knowledge/Cybersecurity/Security Engineering/Brute-Force Attack.md"): f'''## Дополнение из курса «{COURSE}»

Полный перебор представлен как универсальный метод, не использующий внутреннюю структуру шифра. Его стоимость определяется числом допустимых ключей и скоростью проверки кандидата; поэтому длину ключа оценивают вместе с моделью проверки, параллелизмом и ценностью защищаемых данных.

- {source(7)}, стр. 5.''',
}

EXISTING_UPDATES = {
    organized_note_path(path, path.stem): block
    for path, block in EXISTING_UPDATES.items()
}


def update_existing(path: Path, block: str) -> None:
    content = path.read_text(encoding="utf-8")
    wrapped = f"{UPDATE_START}\n{block.strip()}\n{UPDATE_END}"
    if UPDATE_START in content:
        before, rest = content.split(UPDATE_START, 1)
        _, after = rest.split(UPDATE_END, 1)
        content = before.rstrip() + "\n\n" + wrapped + after
    else:
        content = content.rstrip() + "\n\n" + wrapped + "\n"
    path.write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--overwrite-generated",
        action="store_true",
        help="Replace only files carrying this builder's generated marker",
    )
    return parser.parse_args()


def write_generated(path: Path, content: str, overwrite: bool) -> None:
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if not overwrite or GENERATED_MARKER not in existing:
            raise RuntimeError(f"Refusing to overwrite existing note: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    args = parse_args()
    titles = [canonical_title(note.title) for note in NOTES]
    note_keys = {note.title for note in NOTES}
    if len(NOTES) != 42 or len(set(titles)) != 42:
        raise RuntimeError(f"Expected 42 unique content notes, found {len(NOTES)}")
    if note_keys != set(SELF_CHECKS) or note_keys | {"Steganography"} != set(TITLE_MAP):
        raise RuntimeError("Localization maps do not match the generated note set")
    # Validate the MOC before writing any course content. Keep user additions
    # outside the navigation block even during a full course regeneration.
    moc_path = Path("01 Knowledge/Cybersecurity/Steganography/Стеганография.md")
    updated_moc = STEGANOGRAPHY_MOC
    if moc_path.exists():
        existing_moc = moc_path.read_text(encoding="utf-8")
        if not args.overwrite_generated or GENERATED_MARKER not in existing_moc:
            raise RuntimeError(f"Refusing to overwrite existing note: {moc_path}")
        updated_moc = replace_navigation("stego", existing_moc)
    for note in NOTES:
        write_generated(note.path, render(note), args.overwrite_generated)
    if not moc_path.exists() or updated_moc != moc_path.read_text(encoding="utf-8"):
        moc_path.write_text(updated_moc, encoding="utf-8")
    for path, block in EXISTING_UPDATES.items():
        update_existing(path, localize_prose(block))

    print(
        f"Built {len(NOTES) + 1} new canonical notes "
        f"and updated {len(EXISTING_UPDATES)} existing notes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
