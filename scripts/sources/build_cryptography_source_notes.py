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
        item("18–23", "[[Rabin Cryptosystem]]", "Квадратичные вычеты и неоднозначность расшифрования Рабина."),
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
        item("5–9", "certificate lifecycle within the same [[Public Key Infrastructure and X.509]] section", "Сертификаты, удостоверяющий центр, отзыв и цепочка доверия."),
    ],
    "2024_Лекция 23.pdf": [
        item("1–12", "[[Quantum Key Distribution]]", "Физические предпосылки квантового распределения ключей."),
        item("13–20", "[[BB84]]", "Кодирование в двух базисах, просеивание и обнаружение перехвата."),
        item("21–23", "practical limitations within the same [[Quantum Key Distribution]] section", "Варианты и практические ограничения QKD."),
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
    "Семинар 11.pdf": [item("1–3", "[[Quadratic Residues and Modular Square Roots]]; [[Rabin Cryptosystem]] — worked example", "Извлечение корней по простому и составному модулям с объединением по CRT.")],
    "Тема №1 Введение(1).docx": [
        item("абз. 1–173", "[[History of Cryptography]]; [[Cryptosystem and Security Goals]]; [[Cryptanalysis]]; related foundations", "Введение, терминология, модели шифрования, протоколы, генераторы и оценка защищённости."),
        item("абз. 174–396", "[[Russian Cryptographic Regulation and Certification]] — dated/review", "Нормативные и организационные сведения из DOCX, созданного в апреле 2025 года; перед применением требуется актуализация."),
        item("абз. 397–421", "[[Brute-Force Attack]]; [[Linear Cryptanalysis]]; [[Differential Cryptanalysis]]", "Криптографические классы атак и их базовые модели."),
        item("абз. 422–611", "[[Side-Channel Attacks]]; [[RSA]]", "Побочные излучения, энергопотребление, время, fault-подходы и меры защиты."),
        item("абз. 612–678", "[[Man-in-the-Middle Attack]]; [[Cryptographic Protocols and Authenticated Key Exchange]]", "Активный посредник, replay и трёхэтапный протокол."),
        item("абз. 679–731", "source-only security-channel taxonomy", "Атаки по каналам аппаратуры и скрытые каналы сохранены у источника как смежная классификация."),
    ],
    "Тема №2 Блокчейн(1).docx": [
        item("абз. 1–53", "[[Blockchain and Consensus]]", "Сопоставление базы данных, распределённой сети и блокчейна."),
        item("абз. 54–121", "[[Blockchain and Consensus]]; [[Blockchain Cryptography]]", "Механизмы защиты, типы реестров, консенсус и выбор фиксатора транзакций."),
        item("абз. 122–160", "[[Blockchain Attacks]]; source-only governance details", "Sybil, double-spending, 51% и контекст обновления протокола."),
        item("абз. 161–320", "[[Blockchain Cryptography]]; merged sections and source-only mentions", "Криптовалюты, кошельки, smart contracts, токены и MEV; устойчивые механизмы синтезированы, перечни оставлены у источника."),
        item("абз. 321–363", "[[Public Key Infrastructure and X.509]]; source-only IoT applications", "PKI на блокчейне и применение в IoT."),
        item("абз. 364–387", "source-only dated examples (2020–2024)", "Датированные сообщения об атаках не превращены в канонические знания."),
    ],
    "Тема №3 Алгоритмы(1).docx": [
        item("абз. 1–39", "[[Stream Ciphers and One-Time Pad]]; [[Block Cipher Design]]; [[Linear Cryptanalysis]]; [[Differential Cryptanalysis]]", "Поточные конструкции, LFSR, bent functions и переход к блочным шифрам."),
        item("абз. 40–95", "[[Symmetric-Key Cryptography]]; [[Block Cipher Design]]; [[DES and Triple DES]]; [[Magma]]; [[Kuznyechik]]", "История и параметры блочных шифров, SP-сети, Feistel и итерационная структура."),
        item("абз. 96–139", "[[Block Cipher Modes]]; [[GOST R 34.13-2015]]", "Режимы работы, IV, зацепление и режим счётчика."),
        item("абз. 140–149", "[[Advanced Encryption Standard]]", "Раунд AES и развёртка ключа."),
        item("абз. 150–165", "[[IPsec]]; [[SSH]]; authenticated encryption source context", "Порядок шифрования и аутентификации и режим MGM."),
        item("абз. 166–219", "[[Cryptographic Hash Functions]]; [[Streebog]]; [[Message Authentication Codes]]", "Свойства хэш-функций, birthday bound, итеративные конструкции и HMAC."),
        item("абз. 220–238", "source-only Ascon and sponge overview", "Краткий обзор семейства Ascon и sponge-структуры оставлен у источника до появления самостоятельной заметки."),
    ],
    "Тема №4 ГСЧ(1).docx": [
        item("абз. 1–38", "[[Random Number Generation and Entropy]]", "Назначение ГСЧ, программные источники и детерминированное формирование блоков."),
        item("абз. 39–138", "physical-noise and testing sections within [[Random Number Generation and Entropy]]", "Физические источники, постобработка, контроль работоспособности и методика оценки."),
        item("абз. 139–153", "security section within [[Random Number Generation and Entropy]]; [[Side-Channel Attacks]]", "Атаки на ГСЧ и защита источников случайности."),
        item("абз. 154–207", "[[Cryptographic Key Management]]", "Длина ключа, жизненный цикл, ключевая структура и устройства генерации."),
    ],
    "Тема №5 Протоколы(1).docx": [
        item("абз. 1–104", "[[Cryptographic Protocols and Authenticated Key Exchange]]", "Определения, классификация и цели безопасности протоколов."),
        item("абз. 105–258", "[[Digital Signatures]]; [[Schnorr Signatures]]; [[GOST R 34.10-2012]]", "RSA-, ElGamal-, EC- и Schnorr-подписи, nonce, атаки и мультиподпись."),
        item("абз. 259–312", "[[Diffie-Hellman Key Exchange]]; [[Cryptographic Protocols and Authenticated Key Exchange]]", "Распределение ключей, MTI, STS и EDHOC."),
        item("абз. 313–344", "[[Cryptographic Key Management]]; [[Public Key Infrastructure and X.509]]", "Подмена открытого ключа, доверенная сторона и структура сертификата."),
        item("абз. 345–407", "[[IPsec]]", "Сетевой уровень, AH/ESP/IKE и базы политик/ассоциаций."),
        item("абз. 408–431", "[[TLS]]", "Назначение, архитектура и задачи TLS в объёме курса."),
        item("абз. 432–446", "[[SSH]]", "Защищённая оболочка и место протокола в сетевом стеке."),
        item("абз. 447–478", "[[Public Key Infrastructure and X.509]]; [[Certificate Enrollment Protocols]]", "Компоненты PKI и управление жизненным циклом сертификатов."),
        item("абз. 479–530", "[[Anonymous Communication Systems]]", "Модели нарушителя, системы с большими и малыми задержками."),
    ],
    "Тема №6 Классы СКЗИ(1).docx": [
        item("абз. 1–66", "[[Cryptographic Protection Systems]]; [[Cryptographic Service Providers]]; [[Hardware Security Modules]]", "Программные библиотеки, CSP, HSM и криптографические модули."),
        item("абз. 67–118", "[[IPsec]]; [[TLS]]; [[SSH]]; source-only product examples", "Аппаратура защиты каналов и сетевого уровня."),
        item("абз. 119–215", "[[Cryptographic Protection Systems]]; source-only access-control products", "Средства защиты от НСД, доверенная загрузка и AAA."),
        item("абз. 216–250", "[[Quantum Key Distribution]] — dated/review", "Аппаратура, производители и сети QKD из DOCX, созданного в апреле 2025 года."),
    ],
    "Тема №7 Постквантовая криптография(1).docx": [
        item("абз. 1–8", "[[Post-Quantum Cryptography]]", "Мотивация и границы постквантовой криптографии."),
        item("абз. 9–32", "[[Quantum Computing for Cryptography]]", "Алгоритмы Шора и Гровера и их влияние на криптографические задачи."),
        item("абз. 33–47", "[[Quantum Computing for Cryptography]] — dated/review", "Состояние разработки квантовых компьютеров из DOCX, созданного в апреле 2025 года."),
        item("абз. 48–61", "[[Post-Quantum Cryptography]] — dated/review", "Семейства алгоритмов и состояние стандартизации на момент подготовки DOCX."),
        item("абз. 62–93", "[[Hash-Based Signatures]]", "Lamport, WOTS, Merkle и SPHINCS+ внутри одной канонической заметки."),
        item("абз. 94–120", "[[Code-Based Cryptography]]", "McEliece и Niederreiter внутри кодового семейства."),
        item("абз. 121–151", "[[Lattice-Based Cryptography]]", "SVP/CVP, LWE, SIS, Kyber и Dilithium внутри решёточного семейства."),
        item("абз. 152–157", "[[Multivariate Cryptography]]", "Схемы на трудности решения многомерных нелинейных систем."),
        item("абз. 158–170", "source-only dated/review", "Постквантовые блокчейны и изменяемые параметры оставлены у источника."),
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


def paragraph_set(spec: str) -> set[int]:
    match = re.fullmatch(r"абз\. (\d+)(?:–(\d+))?", spec)
    if not match:
        return set()
    start = int(match.group(1))
    end = int(match.group(2) or start)
    return set(range(start, end + 1))


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
    provenance_line = ""
    if manifest["format"] == "docx":
        metadata = manifest.get("metadata", {})
        created = str(metadata.get("created", "не указано"))[:10]
        modified = str(metadata.get("modified", "не указано"))[:10]
        provenance_line = (
            f'\n- Даты из свойств DOCX: создан `{created}`, изменён `{modified}`. '
            "Это дата файла, а не гарантия актуальности всех упомянутых сведений."
        )
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
- Санитаризация: {sanitation_text}{provenance_line}

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
        else:
            covered_paragraphs: set[int] = set()
            for scope, _, _ in COVERAGE[filename]:
                current = paragraph_set(scope)
                if not current:
                    raise RuntimeError(f"Invalid paragraph coverage scope for {filename}: {scope}")
                if covered_paragraphs & current:
                    raise RuntimeError(f"Overlapping paragraph coverage for {filename}: {scope}")
                covered_paragraphs |= current
            expected_paragraphs = set(range(1, int(manifest["paragraphs"]) + 1))
            if covered_paragraphs != expected_paragraphs:
                missing = sorted(expected_paragraphs - covered_paragraphs)
                raise RuntimeError(f"Incomplete paragraph coverage for {filename}: {missing}")
        note_name = f"Source - {stem}.md"
        (NOTES / note_name).write_text(source_note(record, manifest), encoding="utf-8")
        disposition_items: list[str] = []
        for _, destination, _ in COVERAGE[filename]:
            links = re.findall(r"\[\[[^]]+\]\]", destination)
            for link in links:
                if link not in disposition_items:
                    disposition_items.append(link)
            if "source-only" in destination and "source-only material" not in disposition_items:
                disposition_items.append("source-only material")
            if "dated/review" in destination and "dated/review material" not in disposition_items:
                disposition_items.append("dated/review material")
        disposition = "; ".join(disposition_items)
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
- Регулирование, сертификаты, стандартизация и иные изменяемые сведения отмечены `status: review`. Для лекций используется обозначенный в имени срез 2024 года; DOCX датируются по встроенным свойствам файла (апрель 2025 года).
- Для формул приоритет имеет визуально проверенная страница, а не машинный extract.

## Навигация

- [[Cryptography]] — основной маршрут изучения.
- [[Visual QA - Курс криптографии]] — журнал визуальной сверки формул, таблиц и схем.
- [[Sources]] — вход в библиотеку источников.
'''
    (ROOT / f"Course - {COURSE}.md").write_text(course_note, encoding="utf-8")
    print(f"Built {len(records)} source notes and one course source note")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
