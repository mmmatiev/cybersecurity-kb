#!/usr/bin/env python3
"""Build the reviewed source-note layer for the cryptography course corpus."""

from __future__ import annotations

import json
import re
from pathlib import Path


COURSE = "Криптографические методы защиты информации"
ROOT = Path("07 Sources/Courses") / COURSE
NOTES = ROOT / "Source Notes"


def item(pages: str, destination: str, description: str) -> tuple[str, str, str]:
    return pages, destination, description


COVERAGE: dict[str, list[tuple[str, str, str]]] = {
    "2024_Лекция 01.pdf": [
        item("1–4", "[[History of Cryptography]]; source-only course context", "История шифрования, терминология и вводная рамка курса."),
        item("5–8", "[[Cryptosystem and Security Goals]]; [[Cryptanalysis]]", "Модель криптосистемы, цели защиты и роль криптоанализа."),
        item("9–10", "[[Symmetric-Key Cryptography]]", "Симметричное шифрование и общий секрет."),
        item("11–12", "[[Cryptographic Hash Functions]]", "Хэш-функции и свойства односторонности и коллизионной стойкости."),
        item("13", "[[Message Authentication Codes]]", "Контроль целостности и аутентичности сообщения."),
        item("14–15", "[[Digital Signatures]]", "Назначение и базовая схема электронной подписи."),
    ],
    "2024_Лекция 02.pdf": [item("1–9", "[[Algebraic Structures]]", "Операции, полугруппы, моноиды, группы и поля как язык криптографии.")],
    "2024_Лекция 03.pdf": [item("1–6", "[[Algebraic Structures]]", "Циклические группы, порядок элемента, образующие и подгруппы.")],
    "2024_Лекция 04.pdf": [item("1–8", "[[Permutation Groups]]", "Подстановки, композиция, циклы и порядок перестановки.")],
    "2024_Лекция 05-06.pdf": [
        item("1–10", "[[Rings and Modular Arithmetic]]", "Кольца, идеалы, классы вычетов и обратимые элементы."),
        item("11–16", "[[Polynomial Rings]]", "Кольца многочленов, делимость и неприводимые многочлены."),
    ],
    "2024_Лекция 07.pdf": [item("1–9", "[[Finite Fields]]", "Конечные поля, расширения и представление элементов полиномами.")],
    "2024_Лекция 08.pdf": [item("1–11", "[[Elliptic Curves]]; [[Elliptic Curve Cryptography]]", "Кривые над конечными полями, сложение точек и криптографическая группа.")],
    "2024_Лекция 09.pdf": [
        item("1–7", "[[Euclidean Algorithm]]", "Алгоритм Евклида, расширенный вариант и обратный элемент."),
        item("8–10", "[[Rings and Modular Arithmetic]]", "Линейные сравнения и вычисления по модулю."),
        item("11–13", "[[Euler Totient and Fermat-Euler Theorems]]", "Функция Эйлера и теоремы Ферма–Эйлера."),
    ],
    "2024_Лекция 10.pdf": [
        item("1–4", "[[Modular Exponentiation]]", "Быстрое возведение в степень и модульные вычисления."),
        item("5–6", "[[Chinese Remainder Theorem]]", "Восстановление числа по системе остатков."),
    ],
    "2024_Лекция 11.pdf": [
        item("1–7", "[[Quadratic Residues and Modular Square Roots]]", "Квадратичные вычеты, символ Лежандра и критерии разрешимости."),
        item("8–13", "[[Quadratic Residues and Modular Square Roots]]; [[Modular Exponentiation]]", "Извлечение квадратных корней по простому и составному модулю."),
    ],
    "2024_Лекция 12.pdf": [
        item("1–5", "[[Integer Factorization and Pollard Rho]]", "Сложность факторизации и метод Полларда ρ."),
        item("6–10", "[[Discrete Logarithm and Baby-Step Giant-Step]]", "Дискретный логарифм и алгоритм baby-step giant-step."),
    ],
    "2024_Лекция 13.pdf": [
        item("1–6", "[[Symmetric-Key Cryptography]]; [[Block Cipher Design]]", "Общая модель блочного шифра и сеть Фейстеля."),
        item("7–13", "[[Magma]]; [[Block Cipher Modes]]", "Преобразования Магмы и использование режимов."),
    ],
    "2024_Лекция 14.pdf": [item("1–11", "[[Kuznyechik]]", "S-, R- и L-преобразования, развёртка ключа и раунды Кузнечика.")],
    "2024_Лекция 15.pdf": [item("1–12", "[[Block Cipher Modes]]; [[GOST R 34.13-2015]]", "ECB, CTR, OFB, CBC, CFB и режим выработки имитовставки.")],
    "2024_Лекция 16.pdf": [
        item("1–4", "[[DES and Triple DES]]", "DES, сеть Фейстеля и усиление тройным применением."),
        item("5–12", "[[Advanced Encryption Standard]]", "AES, состояние, раундовые преобразования и ключевое расписание."),
    ],
    "2024_Лекция 17-18.pdf": [
        item("1–5", "[[Asymmetric Cryptography]]; [[Cryptographic Key Management]]", "Открытые и закрытые ключи, постановка задач и управление ключевым материалом."),
        item("6–8", "[[Diffie-Hellman Key Exchange]]; [[Man-in-the-Middle Attack]]", "Согласование ключа и необходимость аутентификации обмена."),
        item("9–17", "[[RSA]]", "Генерация ключей, корректность и операции RSA."),
        item("18–23", "[[Rabin Cryptosystem (Cryptography)|Rabin Cryptosystem]]", "Квадратичные вычеты и неоднозначность расшифрования Рабина."),
        item("24–31", "[[ElGamal Cryptosystem]]", "Шифрование Эль-Гамаля и роль случайного параметра."),
        item("32–35", "[[Primality Testing and Miller-Rabin]]", "Вероятностная проверка простоты и тест Миллера–Рабина."),
    ],
    "2024_Лекция 19.pdf": [
        item("1–6", "[[Cryptographic Hash Functions]]", "Свойства, конструкции и модель итеративного хэширования."),
        item("7–16", "[[Streebog]]", "Структура и преобразования хэш-функции Стрибог."),
    ],
    "2024_Лекция 20.pdf": [
        item("1–5", "[[Message Authentication Codes]]", "Коды аутентификации и контроль целостности."),
        item("6–16", "[[Digital Signatures]]", "Требования к подписи, схемы на базе RSA и Эль-Гамаля."),
    ],
    "2024_Лекция 21.pdf": [item("1–11", "[[GOST R 34.10-2012]]; [[Digital Signatures]]", "Формирование и проверка российской подписи на эллиптических кривых.")],
    "2024_Лекция 22.pdf": [
        item("1–4", "[[Public Key Infrastructure and X.509]]; [[Man-in-the-Middle Attack]]", "Проблема подлинности открытых ключей и доверенная третья сторона."),
        item("5–9", "[[Public Key Infrastructure and X.509]]", "Сертификаты, удостоверяющий центр, отзыв и цепочка доверия."),
    ],
    "2024_Лекция 23.pdf": [
        item("1–12", "[[Quantum Key Distribution]]", "Физические предпосылки квантового распределения ключей."),
        item("13–20", "[[BB84]]", "Кодирование в двух базисах, просеивание и обнаружение перехвата."),
        item("21–23", "[[Quantum Key Distribution]]", "Варианты и практические ограничения QKD."),
        item("24–30", "source-only dated examples (2022–2024)", "Эксперименты и внедрения сохранены как датированный материал курса."),
    ],
    "ГОСТ Р 34.10-2012.pdf": [item("1–33", "[[GOST R 34.10-2012]]", "Полный нормативный текст о формировании и проверке электронной цифровой подписи.")],
    "ГОСТ Р 34.12-2015.pdf": [item("1–25", "[[GOST R 34.12-2015]]; [[Kuznyechik]]; [[Magma]]", "Полный нормативный текст с определениями двух базовых блочных шифров.")],
    "ГОСТ Р 34.13-2015.pdf": [item("1–42", "[[GOST R 34.13-2015]]; [[Block Cipher Modes]]", "Полный нормативный текст режимов работы блочных шифров.")],
    "Семинар 01.pdf": [item("1–3", "[[Algebraic Structures]] — worked example", "Проверка замкнутости, ассоциативности, нейтрального и обратного элементов на нестандартной операции.")],
    "Семинар 02.pdf": [item("1–3", "[[Algebraic Structures]] — worked example", "Исследование циклической группы порядка 18, порядков элементов и подгрупп.")],
    "Семинар 03.pdf": [item("1–2", "[[Permutation Groups]] — worked example", "Разложение подстановок на циклы и сокращение большой степени.")],
    "Семинар 04.pdf": [item("1–3", "[[Rings and Modular Arithmetic]] — worked example", "Единицы и делители нуля в кольце классов вычетов.")],
    "Семинар 05.pdf": [item("1–5", "[[Finite Fields]]; [[Polynomial Rings]] — worked example", "Построение F₃² по неприводимому многочлену и таблицы операций.")],
    "Семинар 06.pdf": [item("1–5", "[[Elliptic Curves]] — worked example", "Построение группы точек эллиптической кривой над конечным полем.")],
    "Семинар 07.pdf": [item("1–2", "[[Euclidean Algorithm]] — worked example", "Расширенный алгоритм Евклида и коэффициенты Безу.")],
    "Семинар 08.pdf": [item("1–2", "[[Rings and Modular Arithmetic]] — worked example", "Решение линейного сравнения и вычисление обратного элемента.")],
    "Семинар 09.pdf": [item("1–2", "[[Chinese Remainder Theorem]] — worked example", "Решение системы сравнений по попарно взаимно простым модулям.")],
    "Семинар 10.pdf": [item("1–2", "[[Quadratic Residues and Modular Square Roots]] — worked example", "Вычисление символа Лежандра через закон квадратичной взаимности.")],
    "Семинар 11.pdf": [item("1–3", "[[Quadratic Residues and Modular Square Roots]]; [[Rabin Cryptosystem (Cryptography)|Rabin Cryptosystem]] — worked example", "Извлечение корней по простому и составному модулям с объединением по CRT.")],
    "Тема №1 Введение(1).docx": [
        item("Основные понятия и история", "[[History of Cryptography]]; [[Cryptosystem and Security Goals]]; [[Cryptanalysis]]", "Терминология, развитие криптографии, цели и методы анализа."),
        item("Российское регулирование и сертификация", "[[Russian Cryptographic Regulation and Certification]] — dated/review", "Нормативные и организационные сведения курса фиксируются с датой 2024 и требуют актуализации перед применением."),
        item("Криптографические и технические атаки", "[[Brute-Force Attack]]; [[Linear Cryptanalysis]]; [[Differential Cryptanalysis]]; [[Side-Channel Attacks]]", "Классы атак, утечки реализации и защитные меры."),
        item("Атаки на протоколы", "[[Man-in-the-Middle Attack]]; [[Cryptographic Protocols and Authenticated Key Exchange]]", "Нарушение аутентификации и активный посредник."),
        item("Таблица и встроенное изображение", "supporting source material", "Сохранены в локальном extract/manifest и учтены при визуальной проверке."),
    ],
    "Тема №2 Блокчейн(1).docx": [
        item("Устройство блокчейна и консенсус", "[[Blockchain and Consensus]]", "Цепочка блоков, распределённый реестр и семейства консенсуса."),
        item("Криптографические механизмы", "[[Blockchain Cryptography]]", "Хэширование, подписи, адреса и связывание блоков."),
        item("Sybil, double-spending и 51%", "[[Blockchain Attacks]]", "Атаки объединены в одну каноническую модель угроз."),
        item("Криптовалюты, smart contracts, IoT и PKI", "merged sections or source-only mentions", "Существенные механизмы включены в тематические заметки; перечисления продуктов оставлены у источника."),
        item("События 2020–2024", "source-only dated examples", "Новостные случаи не превращены в канонические знания."),
    ],
    "Тема №3 Алгоритмы(1).docx": [
        item("Симметричные алгоритмы", "[[Symmetric-Key Cryptography]]; [[Block Cipher Design]]; [[Block Cipher Modes]]", "Блочные конструкции, преобразования и режимы."),
        item("Российские и международные шифры", "[[Magma]]; [[Kuznyechik]]; [[DES and Triple DES]]; [[Advanced Encryption Standard]]", "Структура и назначение алгоритмов."),
        item("Хэширование и имитозащита", "[[Cryptographic Hash Functions]]; [[Streebog]]; [[Message Authentication Codes]]", "Свойства хэш-функций, sponge-подход и MAC."),
        item("Асимметричные алгоритмы и подписи", "[[Asymmetric Cryptography]]; [[RSA]]; [[ElGamal Cryptosystem]]; [[Digital Signatures]]", "Открытые ключи и основные схемы."),
        item("Иллюстрации и headers", "supporting source material", "Схемы алгоритмов проверены визуально и используются как сверка формул."),
    ],
    "Тема №4 ГСЧ(1).docx": [
        item("Источники случайности", "[[Random Number Generation and Entropy]]", "Физические источники, энтропия и сбор начального материала."),
        item("Псевдослучайные генераторы", "[[Random Number Generation and Entropy]]", "Детерминированное растяжение seed и требования к криптографическому ГПСЧ."),
        item("Тестирование и аппаратные реализации", "[[Random Number Generation and Entropy]]; source-only product examples", "Критерии качества включены в каноническую заметку, конкретные изделия оставлены у источника."),
        item("Иллюстрации и headers", "supporting source material", "Схемы источников шума учтены при визуальной проверке."),
    ],
    "Тема №5 Протоколы(1).docx": [
        item("Основные определения и модели", "[[Cryptographic Protocols and Authenticated Key Exchange]]", "Участники, сообщения, противник и цели протокола."),
        item("Протоколы цифровой подписи", "[[Digital Signatures]]; [[Schnorr Signatures]]", "Схемы подписи, nonce и угрозы повторного использования."),
        item("Распределение и управление ключами", "[[Diffie-Hellman Key Exchange]]; [[Cryptographic Key Management]]", "Выработка общего секрета и жизненный цикл ключей."),
        item("PKI и сертификаты", "[[Public Key Infrastructure and X.509]]; [[Certificate Enrollment Protocols]]", "Удостоверяющие центры, сертификаты и протоколы регистрации."),
        item("Интернет-протоколы", "[[TLS (Cryptography)|TLS]]; [[IPsec]]; [[SSH]]", "Применение криптографии в сетевом стеке."),
        item("Анонимные сети", "[[Anonymous Communication Systems]]", "Маршрутизация и сокрытие связи между отправителем и получателем."),
        item("Перечни алгоритмов и продуктов", "source-only mentions", "Короткие перечисления без самостоятельного объяснения не вынесены в отдельные заметки."),
    ],
    "Тема №6 Классы СКЗИ(1).docx": [
        item("Классы и архитектура СКЗИ", "[[Cryptographic Protection Systems]]; [[Cryptographic Service Providers]]", "Программные, аппаратные и программно-аппаратные средства."),
        item("Аппаратура защиты и ключи", "[[Hardware Security Modules]]; [[Cryptographic Key Management]]", "Изоляция операций, хранение и применение ключевого материала."),
        item("Сетевые средства", "[[IPsec]]; [[TLS (Cryptography)|TLS]]; [[SSH]]", "Канальные и сетевые средства защиты."),
        item("Аппаратура квантового распределения ключей", "[[Quantum Key Distribution]]", "Практическая архитектура QKD-устройств."),
        item("Изделия, сертификаты и характеристики", "source-only dated/review", "Состояние конкретных продуктов и сертификатов не переносится в устойчивую часть базы."),
        item("Встроенные изображения и headers", "supporting source material", "Аппаратные схемы и фотографии сохранены и проверены локально."),
    ],
    "Тема №7 Постквантовая криптография(1).docx": [
        item("Квантовые вычисления и алгоритмы", "[[Quantum Computing for Cryptography]] — review", "Модель квантовых вычислений и влияние алгоритмов Шора и Гровера."),
        item("Постквантовая миграция", "[[Post-Quantum Cryptography]] — review", "Классы стойких задач и переходные риски."),
        item("Хэш-подписи", "[[Hash-Based Signatures]] — review", "Lamport, WOTS, Merkle и SPHINCS+ как семейство одной канонической заметки."),
        item("Кодовые схемы", "[[Code-Based Cryptography]]", "McEliece и Niederreiter как разделы кодовой криптографии."),
        item("Решётки", "[[Lattice-Based Cryptography]] — review", "LWE, SIS, Kyber и Dilithium как связанные конструкции."),
        item("Многомерные схемы", "[[Multivariate Cryptography]]", "Криптосистемы на многомерных полиномиальных задачах."),
        item("Параметры и статусы стандартизации", "source-only dated/review", "Все изменяемые сведения привязаны к срезу 2024 года."),
    ],
}


SUMMARIES: dict[str, str] = {
    "lecture": "Лекционные слайды курса, интегрированные как источник для канонических заметок.",
    "seminar": "Разобранный учебный пример; решение перенесено в соответствующую теоретическую заметку.",
    "standard": "Нормативный первичный текст, используемый для отдельной заметки типа standard.",
    "docx": "Развёрнутый текстовый материал курса, тематически разложенный по каноническим заметкам.",
}


def page_set(spec: str) -> set[int]:
    result: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        match = re.fullmatch(r"(\d+)(?:–(\d+))?", part)
        if not match:
            continue
        start = int(match.group(1))
        end = int(match.group(2) or start)
        result.update(range(start, end + 1))
    return result


def metrics(manifest: dict[str, object]) -> str:
    if manifest["format"] == "pdf":
        return f'{manifest["pages"]} стр.'
    return (
        f'{manifest["paragraphs"]} абз.; {manifest["tables"]} табл.; '
        f'{manifest["equations"]} формул OOXML; {manifest["embedded_media"]} изображ.'
    )


def source_note(record: dict[str, object], manifest: dict[str, object]) -> str:
    filename = str(record["source"])
    stem = Path(filename).stem
    rows = COVERAGE[filename]
    public_rel = Path("..") / ("Original" if record["kind"] == "docx" else "PDF") / filename
    processed_rel = Path("..") / "Processed" / stem
    sanitization = record["sanitization"]
    action = sanitization["action"]
    if record["kind"] == "lecture":
        sanitation_text = (
            f'Удалена только последняя контактная страница оригинала '
            f'({sanitization["removed_page"]}); публичная копия содержит '
            f'{sanitization["public_pages"]} содержательных страниц.'
        )
    else:
        sanitation_text = "Публичная копия побайтно совпадает с оригиналом; санитаризация не требовалась."
    coverage_lines = "\n".join(
        f'| {scope} | {destination} | {description} |' for scope, destination, description in rows
    )
    return f'''---
type: source
area:
  - Cryptography
processing_status: processed
---
# {stem}

## Описание

{SUMMARIES[str(record["kind"])]} Материал обработан локально без внешнего OCR, API или загрузки содержимого в сторонние сервисы.

## Файлы и целостность

- Курс: [[Course - {COURSE}]].
- Публичный файл: [открыть](<{public_rel.as_posix()}>).
- Технический extract: [текст](<{(processed_rel / "extracted-text.md").as_posix()}>) и [manifest](<{(processed_rel / "manifest.json").as_posix()}>).
- Объём: {metrics(manifest)}
- Исходный SHA-256: `{record["original_sha256"]}`.
- Публичный SHA-256: `{record["public_sha256"]}`.
- Санитаризация: {sanitation_text}

## Матрица покрытия

| Страницы или раздел | Disposition | Что учтено |
|---|---|---|
{coverage_lines}

Каждая содержательная страница PDF либо каждый смысловой раздел DOCX имеет disposition: каноническая заметка, объединённый раздел, source-only mention или dated/review. Формулы, таблицы и схемы дополнительно сверены по локальному рендеру.
'''


def main() -> int:
    index = json.loads((ROOT / "source-index.json").read_text(encoding="utf-8"))
    records = index["files"]
    names = {record["source"] for record in records}
    if names != set(COVERAGE):
        missing = names - set(COVERAGE)
        extra = set(COVERAGE) - names
        raise RuntimeError(f"Coverage mapping mismatch: missing={missing}, extra={extra}")

    NOTES.mkdir(parents=True, exist_ok=True)
    course_rows: list[str] = []
    for record in records:
        filename = record["source"]
        stem = Path(filename).stem
        manifest_path = ROOT / record["processed_path"].split(f"{ROOT.as_posix()}/", 1)[-1] / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest["format"] == "pdf":
            covered: set[int] = set()
            for scope, _, _ in COVERAGE[filename]:
                covered |= page_set(scope)
            expected = set(range(1, int(manifest["pages"]) + 1))
            if covered != expected:
                raise RuntimeError(f"Incomplete page coverage for {filename}: {sorted(expected - covered)}")
        note_name = f"Source - {stem}.md"
        (NOTES / note_name).write_text(source_note(record, manifest), encoding="utf-8")
        disposition = "; ".join(row[1] for row in COVERAGE[filename])
        course_rows.append(
            f'| [[Source - {stem}]] | {record["kind"]} | {metrics(manifest)} | {disposition} |'
        )

    course_note = f'''---
type: source
area:
  - Cryptography
processing_status: processed
---
# {COURSE}

## О курсе

Локально обработанный комплект учебных материалов по криптографическим методам защиты информации. Канонические заметки написаны по-русски своими словами; названия технологий, алгоритмов и протоколов сохранены в принятой английской форме.

В наборе 42 файла: 21 санитаризированная лекция, 11 семинаров, 3 текста ГОСТ и 7 DOCX. Все оригиналы на Desktop проверяются по SHA-256, а публичные копии и технические manifests хранятся в Vault. Внешние OCR, API, embeddings и веб-источники не использовались.

## Полная матрица покрытия

| Source-note | Вид | Объём | Каноническое назначение |
|---|---:|---:|---|
{chr(10).join(course_rows)}

## Правила интерпретации

- Слайды и главы — источники, а не самостоятельные канонические знания.
- Семинарские решения встроены в теоретические заметки как worked examples.
- Простые упоминания, списки продуктов и конкретные события остаются в source-note.
- Регулирование, сертификаты, стандартизация и иные изменяемые сведения отмечены `status: review` и рассматриваются как срез 2024 года.
- Для формул приоритет имеет визуально проверенная страница, а не машинный extract.

## Навигация

- [[Cryptography]] — основной маршрут изучения.
- [[Sources]] — вход в библиотеку источников.
'''
    (ROOT / f"Course - {COURSE}.md").write_text(course_note, encoding="utf-8")
    print(f"Built {len(records)} source notes and one course source note")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
