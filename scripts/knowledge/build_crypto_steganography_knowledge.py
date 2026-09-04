#!/usr/bin/env python3
"""Build the canonical knowledge layer for the cryptography/steganography course."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


COURSE = "Основы криптографии и стеганографии"
SOURCE_PREFIX = "Source - Основы криптографии и стеганографии - Лекция"
ATTACHMENT_ROOT = "90 Attachments/Courses/Основы криптографии и стеганографии"
UPDATE_START = "<!-- crypto-stego-course:start -->"
UPDATE_END = "<!-- crypto-stego-course:end -->"
GENERATED_MARKER = "<!-- generated: crypto-stego-course -->"


@dataclass(frozen=True)
class Note:
    title: str
    folder: str
    note_type: str
    area: tuple[str, ...]
    summary: str
    mechanism: tuple[str, ...]
    formulas: tuple[str, ...]
    example: str
    limitations: tuple[str, ...]
    links: tuple[str, ...]
    sources: tuple[tuple[int, str], ...]
    security: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()
    status: str = "learning"
    visuals: tuple[tuple[str, str, int, int], ...] = ()
    extra: str = ""

    @property
    def path(self) -> Path:
        return Path(self.folder) / f"{self.title}.md"


NOTES: list[Note] = []


def add(**kwargs: object) -> None:
    NOTES.append(Note(**kwargs))


def source(number: int) -> str:
    return f"[[{SOURCE_PREFIX} {number:02d}]]"


def render(note: Note) -> str:
    yaml = ["---", f"type: {note.note_type}", "area:"]
    yaml.extend(f"  - {value}" for value in note.area)
    if note.security:
        yaml.append("security:")
        yaml.extend(f"  - {value}" for value in note.security)
    if note.aliases:
        yaml.append("aliases:")
        yaml.extend(f'  - "{value}"' for value in note.aliases)
    if note.status:
        yaml.append(f"status: {note.status}")
    yaml.append("---")

    mechanism = "\n".join(f"- {line}" for line in note.mechanism)
    formulas = "\n\n".join(f"$$\n{formula}\n$$" for formula in note.formulas)
    limitations = "\n".join(f"- {line}" for line in note.limitations)
    links = "\n".join(f"- [[{link}]]" for link in note.links)
    sources = "\n".join(
        f"- {source(number)}, стр. {pages}." for number, pages in note.sources
    )
    visuals = ""
    if note.visuals:
        blocks = []
        for filename, caption, number, page in note.visuals:
            blocks.append(
                f"![[{ATTACHMENT_ROOT}/{filename}]]\n\n"
                f"*Что смотреть:* {caption} *Источник:* {source(number)}, стр. {page}."
            )
        visuals = "\n\n## Иллюстрации из курса\n\n" + "\n\n".join(blocks)

    extra = f"\n\n{note.extra.strip()}" if note.extra.strip() else ""
    return "\n".join(yaml) + f'''\n{GENERATED_MARKER}
# {note.title}

## Суть

{note.summary}

## Как устроено

{mechanism}

## Формулы и критерии

{formulas}

## Пример из курса

{note.example}{visuals}{extra}

## Ограничения и безопасность

{limitations}

## Связи

{links}

## Самопроверка

1. Сформулируйте назначение {note.title} и назовите входные данные.
2. Воспроизведите основной алгоритм или критерий без подсказки.
3. Объясните, какое ограничение первым проявится в практической системе.

## Источники курса

{sources}
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
    formulas=(r"E_k:\mathcal M\rightarrow\mathcal C,\qquad D_k(E_k(m))=m", r"y_i=(x_i+\gamma_i)\bmod |A|"),
    example="Курс классифицирует исторические схемы по операции над сообщением, а затем использует слово `CRYPTOGRAPHY` как единый тестовый текст для сравнения нескольких шифров.",
    limitations=("Малое пространство ключей и сохранение статистики естественного языка делают схемы уязвимыми.", "Историческая понятность не означает современной криптографической стойкости; применять эти шифры для защиты нельзя."),
    links=("History of Cryptography", "Substitution Ciphers", "Transposition Ciphers", "Vigenere Cipher", "Cryptanalysis"),
    sources=((1, "10–14"), (2, "4–8"), (3, "2–9"), (4, "2–6"), (5, "2–7"), (6, "2–10")),
)
add(
    title="Substitution Ciphers", folder="01 Knowledge/Cryptography", note_type="concept",
    area=("Cryptography",), aliases=("Подстановочные шифры",),
    summary="Подстановочный шифр заменяет каждый элемент открытого текста другим элементом или группой элементов. Ключ задаёт обратимое отображение алфавита; позиции символов обычно сохраняются, поэтому статистическая структура текста просачивается в шифртекст.",
    mechanism=("Простая замена использует одну перестановку алфавита на всём сообщении.", "Многоалфавитная замена выбирает разные подстановки по позиции или гамме.", "Линейка Энея и квадрат Полибия показывают два способа физически представить таблицу соответствий."),
    formulas=(r"y_i=\pi(x_i),\qquad x_i=\pi^{-1}(y_i)", r"|\mathcal K|=|A|!\quad\text{для произвольной простой замены}"),
    example="Для `CRYPTOGRAPHY` лекция сравнивает простую замену с аффинным вариантом: разные ключевые правила дают разные шифртексты, но сохраняют длину и посимвольную структуру.",
    limitations=("Простая замена сохраняет односимвольные и многосимвольные частоты.", "Большой формальный размер ключевого пространства не спасает от языковой избыточности и известных фрагментов текста."),
    links=("Polybius Square", "Affine Cipher", "Playfair Cipher", "Vigenere Cipher", "Frequency Analysis"),
    sources=((2, "4–5"), (3, "2–10")),
)
add(
    title="Polybius Square", folder="01 Knowledge/Cryptography", note_type="technique",
    area=("Cryptography",), aliases=("Квадрат Полибия",),
    summary="Polybius Square кодирует символ координатами строки и столбца в ключевой таблице. Метод превращает алфавит в пары чисел и служит строительным блоком для ручных шифров, но сам по себе почти не скрывает статистику текста.",
    mechanism=("Символы заполняют квадратную таблицу; при нехватке ячеек символы объединяют, как I/J в примере курса.", "Шифрование возвращает координату `(row, column)`, расшифрование выполняет обратный поиск.", "Парольная модификация сначала записывает уникальные символы пароля, затем дополняет таблицу оставшимся алфавитом."),
    formulas=(r"E(a)=(r,c)\iff T_{r,c}=a", r"D(r,c)=T_{r,c}"),
    example="В таблице курса буква `A` расположена в ячейке `(2,3)`, поэтому её представление — пара координат, а не другой символ алфавита.",
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
    formulas=(r"y_i=(\alpha x_i+\beta)\bmod m,\qquad \gcd(\alpha,m)=1", r"x_i=\alpha^{-1}(y_i-\beta)\bmod m"),
    example="Для алфавита из 26 символов курс использует ключ `(3,10)` и получает из `CRYPTOGRAPHY` шифртекст `QJEDPACJKDFE`.",
    limitations=("Число допустимых ключей невелико: `m·φ(m)`, поэтому перебор дешёв.", "Две согласованные пары открытый текст–шифртекст обычно дают систему сравнений для восстановления ключа."),
    links=("Substitution Ciphers", "Rings and Modular Arithmetic", "Frequency Analysis", "Brute-Force Attack"),
    sources=((3, "6–9"),),
    visuals=(("OCS - Affine Cipher - L03 p06.png", "условие обратимости множителя и прямую/обратную формулы по модулю `m`.", 3, 6),),
)
add(
    title="Transposition Ciphers", folder="01 Knowledge/Cryptography", note_type="concept",
    area=("Cryptography",), aliases=("Перестановочные шифры",),
    summary="Перестановочный шифр не меняет символы, а переставляет их позиции по ключевой перестановке. Поэтому частоты отдельных символов сохраняются точно, а скрывается лишь локальный порядок.",
    mechanism=("Сообщение делится на блоки фиксированной длины.", "Ключ — перестановка индексов блока; одна и та же перестановка применяется к каждому полному блоку.", "Сцитала задаёт перестановку геометрией намотки, Cardan grille — порядком заполнения отверстий поворотной маски."),
    formulas=(r"y_i=x_{\pi(i)},\qquad \pi\in S_n", r"x_i=y_{\pi^{-1}(i)}"),
    example="В блочном примере курса слово `CRYPTOGRAPHY` разбивается и переставляется ключом, который задаётся двумя строками соответствующих позиций.",
    limitations=("Односимвольные частоты не меняются, поэтому перестановку распознают статистически.", "Короткий блок и повторное применение одной перестановки оставляют заметные периодические зависимости."),
    links=("Cardan Grille Cipher", "Permutation Groups", "Frequency Analysis", "Classical Cryptography"),
    sources=((2, "6"), (4, "2–6")),
)
add(
    title="Cardan Grille Cipher", folder="01 Knowledge/Cryptography", note_type="technique",
    area=("Cryptography",), aliases=("Шифр Кардано", "Поворотная решётка"),
    summary="Cardan Grille Cipher размещает символы через отверстия поворотной маски. После нескольких поворотов все клетки контейнера заполняются, а без знания исходной ориентации и формы решётки порядок чтения скрыт.",
    mechanism=("Выбирается квадратная решётка и набор отверстий.", "На каждом повороте в открытые клетки последовательно записывается часть сообщения.", "После полного цикла заполненная матрица читается в обычном порядке как шифртекст."),
    formulas=(r"\bigcup_{j=0}^{3}R^j(H)=\Omega,\qquad R^i(H)\cap R^j(H)=\varnothing\;(i\ne j)",),
    example="На слайдах четыре положения одной решётки последовательно раскрывают разные клетки, формируя единый заполненный блок.",
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
    formulas=(r"E(a,b)=\begin{cases}(R(a),R(b)),&row(a)=row(b)\\(D(a),D(b)),&col(a)=col(b)\\(T_{row(a),col(b)},T_{row(b),col(a)}),&\text{иначе}\end{cases}",),
    example="Лекция показывает подготовку биграмм и применение трёх правил к ключевой таблице; именно разделение одинаковых букв обеспечивает однозначную обработку пары.",
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
    formulas=(r"Y=KX\pmod m,\qquad X=K^{-1}Y\pmod m", r"\gcd(\det K,m)=1"),
    example="Для `CRYPTOGRAPHY` курс использует блоки длины 4 и матрицу с определителем `19 ∈ Z*_{26}`; первый блок преобразуется в вектор, соответствующий `SZUC`.",
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
    formulas=(r"y_i=(x_i+\gamma_i)\bmod m,\qquad x_i=(y_i-\gamma_i)\bmod m", r"\gamma_i=k_{((i-1)\bmod r)+1}\quad\text{для повторяющегося ключа}"),
    example="`CRYPTOGRAPHY` и повторяемый ключ `KEY` дают гамму `KEYKEYKEYKEY` и шифртекст `MVWZXMQVYZLW` в нумерации A=0.",
    limitations=("Периодический ключ обнаруживается тестом Касиски или индексом совпадений, после чего столбцы анализируются как сдвиги.", "Повторное использование гаммы связывает несколько шифртекстов и раскрывает комбинацию открытых текстов."),
    links=("Substitution Ciphers", "Stream Ciphers and One-Time Pad", "Frequency Analysis", "Cryptanalysis"),
    sources=((6, "5–9"),),
)
add(
    title="Frequency Analysis", folder="01 Knowledge/Cybersecurity/Security Engineering", note_type="technique",
    area=("Cryptography",), security=("Security Engineering",), aliases=("Частотный анализ",),
    summary="Frequency Analysis сопоставляет статистику шифртекста со статистикой предполагаемого языка или структуры данных. Это повторяемая техника криптоанализа, особенно эффективная против простой замены и коротких периодических гамм.",
    mechanism=("Подсчитываются частоты символов, биграмм или других признаков.", "Наблюдаемое распределение сопоставляется с эталонным с учётом длины текста.", "Для Vigenere сначала оценивается период, затем каждая позиционная группа анализируется отдельно."),
    formulas=(r"\hat p(a)=\frac{n_a}{N}", r"\chi^2=\sum_a\frac{(n_a-Np_a)^2}{Np_a}"),
    example="В лекции гистограмма простой замены сохраняет характерные пики английского языка; в блочном случае анализ переносится на частоты биграмм.",
    limitations=("Короткий текст даёт шумную оценку, а неизвестный язык или формат ухудшает сопоставление.", "Сжатие, хорошая современная криптография и одноразовая случайная гамма должны устранять полезную языковую статистику."),
    links=("Cryptanalysis", "Substitution Ciphers", "Vigenere Cipher", "Brute-Force Attack"),
    sources=((3, "10"), (5, "8"), (6, "11")),
)
add(
    title="Perfect Secrecy and Cryptographic Strength", folder="01 Knowledge/Cryptography", note_type="concept",
    area=("Cryptography",), aliases=("Совершенная секретность", "Криптографическая стойкость"),
    summary="Криптографическая стойкость описывает ресурсы, необходимые для нарушения заявленной цели. Совершенная секретность — более сильное информационно-теоретическое свойство: наблюдение шифртекста не меняет распределение вероятностей открытого текста.",
    mechanism=("Принцип Керкгоффса отделяет публичный алгоритм от секретного ключа.", "Вычислительная стойкость зависит от модели атакующего, времени, памяти и данных.", "Абсолютная стойкость не опирается на ограниченность вычислений; курс связывает её с одноразовой случайной гаммой."),
    formulas=(r"P(M=m\mid C=c)=P(M=m)", r"H(K)\ge H(M)\quad\text{для совершенной секретности}"),
    example="Для конечного алфавита одноразовая случайная гамма той же длины, использованная ровно один раз, делает каждый допустимый открытый текст совместимым с наблюдаемым шифртекстом.",
    limitations=("Совершенная секретность переносит сложность в генерацию, доставку, хранение и однократное использование ключа.", "Заявление о стойкости бессмысленно без модели угроз и конкретных параметров."),
    links=("Cryptosystem and Security Goals", "Stream Ciphers and One-Time Pad", "Brute-Force Attack", "Cryptanalysis"),
    sources=((7, "2–4"),),
)


# Digital-image foundations in Computer Science.
add(
    title="Digital Image Fundamentals", folder="01 Knowledge/Computer Science", note_type="concept",
    area=("Computer Science",), aliases=("Основы цифровых изображений",),
    summary="Цифровое изображение — дискретная двумерная сетка элементов, каждый из которых хранит одно или несколько числовых значений. Для стеганографии важно различать вид представления, разрешение, число каналов и глубину цвета: именно эти элементы становятся контейнером.",
    mechanism=("Растровое изображение хранит значения пикселей; векторное — геометрические примитивы и правила их отрисовки.", "Бинарные, полутоновые, палитровые и полноцветные растры различаются количеством допустимых значений пикселя.", "Разрешение `M×N`, число каналов и битовая глубина определяют исходный объём данных."),
    formulas=(r"I:\{0,\ldots,M-1\}\times\{0,\ldots,N-1\}\rightarrow\{0,\ldots,2^b-1\}^{c}", r"S_{raw}=M\,N\,b\,c\ \text{бит}"),
    example="Курс сравнивает растровое хранение отдельных пикселей с векторным описанием объектов и показывает, почему масштабирование по-разному влияет на эти два вида.",
    limitations=("Одинаковое визуальное изображение может иметь разное внутреннее представление и разную пригодность для встраивания.", "Изменение палитры, ресэмплинг или конвертация формата могут уничтожить скрытые данные."),
    links=("Image Color Models", "Digital Image File Formats", "Lossless Image Compression", "Digital Steganography"),
    sources=((9, "2–8"),),
)
add(
    title="Image Color Models", folder="01 Knowledge/Computer Science", note_type="concept",
    area=("Computer Science",), aliases=("Цветовые модели изображений",),
    summary="Цветовая модель задаёт числовые координаты цвета. RGB описывает интенсивности трёх базовых компонентов, а YCbCr отделяет яркость от цветности, что позволяет по-разному обрабатывать визуально неодинаково значимые компоненты.",
    mechanism=("RGB формирует цвет аддитивным сложением красного, зелёного и синего каналов.", "YCbCr хранит яркость `Y` и две цветоразностные компоненты `Cb`, `Cr`.", "Преобразование линейно, но округление и ограничение диапазонов при практической конвертации могут терять информацию."),
    formulas=(r"Y=0.299R+0.587G+0.114B", r"Cb=128-0.169R-0.331G+0.5B,\quad Cr=128+0.5R-0.419G-0.081B"),
    example="Лекция показывает, что глаз чувствительнее к яркостной составляющей; JPEG использует это при прореживании цветности перед блочным DCT.",
    limitations=("Коэффициенты и диапазоны зависят от принятой реализации; нельзя молча смешивать разные матрицы преобразования.", "Стегоалгоритм, работающий с RGB, может не пережить преобразование в YCbCr и обратно."),
    links=("Digital Image Fundamentals", "JPEG Compression", "Spatial-Domain Image Steganography", "Frequency-Domain Image Steganography"),
    sources=((9, "9–15"), (12, "10–11")),
    visuals=(("OCS - RGB Model - L09 p12.png", "три аддитивных компоненты RGB и их вклад в итоговый цвет.", 9, 12), ("OCS - YCbCr Model - L09 p15.png", "формулы перехода между RGB и яркостно-цветностным представлением.", 9, 15)),
)
add(
    title="Digital Image File Formats", folder="01 Knowledge/Computer Science", note_type="concept",
    area=("Computer Science",), aliases=("Форматы цифровых изображений",),
    summary="Формат изображения определяет, как упакованы пиксели или графические объекты, metadata, палитра и сжатые данные. Расширение файла не гарантирует способ хранения: для анализа нужно учитывать фактический контейнер и кодек.",
    mechanism=("BMP в курсе служит примером непосредственного растрового хранения без обязательного сжатия.", "GIF использует палитру и поддерживает последовательность кадров.", "PNG сочетает предиктивные фильтры с алгоритмами без потерь; JPEG хранит результат преобразования и квантования с потерями."),
    formulas=(r"file=header\parallel metadata\parallel palette?\parallel encoded\_data", r"CR=\frac{S_{raw}}{S_{file}}"),
    example="Слайды сопоставляют BMP, GIF, PNG и другие форматы по представлению цвета, сжатию и поддерживаемым возможностям.",
    limitations=("Metadata и дополнительные секции могут переживать или не переживать пересохранение независимо от пикселей.", "Для стеганографии существенна вся цепочка декодирование–редактирование–повторное кодирование, а не только исходное расширение."),
    links=("Digital Image Fundamentals", "Lossless Image Compression", "JPEG Compression", "JPEG Steganography"),
    sources=((9, "16–21"),),
)
add(
    title="Lossless Image Compression", folder="01 Knowledge/Computer Science", note_type="concept",
    area=("Computer Science",), aliases=("Сжатие изображений без потерь",),
    summary="Сжатие без потерь устраняет статистическую и структурную избыточность так, чтобы исходные значения пикселей восстанавливались точно. Оно отличается от JPEG-квантования, где часть информации намеренно отбрасывается.",
    mechanism=("Предсказание или фильтрация превращает значения в более компактно распределённые остатки.", "Словарное или энтропийное кодирование сокращает повторяющиеся и вероятные последовательности.", "Декодер обращает каждый этап и восстанавливает исходный массив байт."),
    formulas=(r"Decode(Encode(I))=I", r"CR=\frac{|I_{raw}|}{|I_{compressed}|}"),
    example="PNG в курсе приводится как формат, использующий сочетание LZ77 и кодирования Хаффмана; пространственная избыточность объясняет возможность уменьшения размера.",
    limitations=("Для уже сжатых или шумоподобных данных выигрыш мал.", "Хотя значения пикселей сохраняются после декодирования, пересохранение может изменить расположение байтов контейнера и разрушить файловое, но не пиксельное встраивание."),
    links=("Digital Image File Formats", "JPEG Compression", "Digital Image Fundamentals", "LSB Steganography"),
    sources=((9, "17–21"), (12, "2–7")),
)
add(
    title="JPEG Compression", folder="01 Knowledge/Computer Science", note_type="concept",
    area=("Computer Science",), aliases=("Сжатие JPEG",),
    summary="JPEG в объёме курса — конвейер сжатия с потерями: цвет переводится в YCbCr, цветность прореживается, блоки 8×8 преобразуются DCT, коэффициенты квантуются, упорядочиваются zig-zag и энтропийно кодируются.",
    mechanism=("Пиксели каждого канала группируются в блоки 8×8.", "DCT концентрирует значимую энергию в низких частотах; DC отражает средний уровень, остальные коэффициенты — AC.", "Квантование делит коэффициенты на таблицу и округляет, создавая длинные серии нулей для последующего кодирования."),
    formulas=(r"G_{ij}=\frac14C_iC_j\sum_{x=0}^{7}\sum_{y=0}^{7}p_{xy}\cos\frac{(2y+1)j\pi}{16}\cos\frac{(2x+1)i\pi}{16}", r"\hat G_{ij}=round\!\left(\frac{G_{ij}}{Q_{ij}}\right)"),
    example="В блоке курса DC-коэффициент около `907.86` после квантования становится `57`, а большинство высокочастотных AC-коэффициентов обращается в ноль.",
    limitations=("Квантование необратимо; повторное JPEG-сохранение добавляет новые ошибки.", "Скрытые изменения DCT-коэффициентов должны учитывать нули, значения ±1, таблицы квантования и повторное кодирование."),
    links=("Image Color Models", "Discrete Fourier and Cosine Transforms for Images", "JPEG Steganography", "Frequency-Domain Image Steganography"),
    sources=((12, "8–18"),),
    visuals=(("OCS - JPEG Pipeline - L12 p09.png", "последовательность RGB→YCbCr, прореживание, DCT, квантование, zig-zag и кодирование.", 12, 9),),
)
add(
    title="Image Frequency-Domain Transforms", folder="01 Knowledge/Computer Science", note_type="concept",
    area=("Computer Science",), aliases=("Частотные преобразования изображений",),
    summary="Частотное преобразование представляет изображение коэффициентами выбранного базиса. Низкочастотные компоненты описывают плавные изменения, высокочастотные — быстрые переходы, мелкие детали и шум.",
    mechanism=("Изображение рассматривается как набор строк/столбцов или матрица в линейном пространстве.", "Прямое преобразование проецирует данные на базис; обратное собирает изображение из коэффициентов.", "DFT/DCT дают глобальные синусоидальные базисы, Walsh–Hadamard — знаковые прямоугольные, wavelet — локализованные по масштабу."),
    formulas=(r"G=TPT^{\mathsf T}", r"P=T^{-1}G(T^{-1})^{\mathsf T}"),
    example="В лекции один и тот же блок пикселей преобразуется DFT, DCT и Walsh–Hadamard, после чего визуально сравниваются спектр и восстановление.",
    limitations=("Коэффициенты зависят от базиса, нормировки, размера блока и порядка индексов.", "Округление после обратного преобразования способно изменить встроенные биты даже без внешней атаки."),
    links=("Discrete Fourier and Cosine Transforms for Images", "Walsh-Hadamard Transform", "Discrete Wavelet Transform", "Frequency-Domain Image Steganography"),
    sources=((11, "2–3, 20–26"),),
)
add(
    title="Discrete Fourier and Cosine Transforms for Images", folder="01 Knowledge/Computer Science", note_type="concept",
    area=("Computer Science",), aliases=("DFT and DCT for Images", "ДПФ и ДКП изображений"),
    summary="DFT описывает изображение комплексными гармониками, а DCT — вещественными косинусными базисами. Двумерные преобразования сепарабельны: сначала обрабатываются строки, затем столбцы.",
    mechanism=("DFT хранит амплитуду и фазу комплексных частотных компонент.", "DCT использует косинусный базис и хорошо концентрирует энергию естественных изображений.", "FFT ускоряет вычисление DFT, не меняя математический результат."),
    formulas=(r"F(u,v)=\frac1{MN}\sum_{x=0}^{M-1}\sum_{y=0}^{N-1}f(x,y)e^{-2\pi i(ux/M+vy/N)}", r"G=CPC^{\mathsf T},\qquad C^{-1}=C^{\mathsf T}"),
    example="Для матрицы 8×8 курс вычисляет `G=CPC^T`: большой DC в левом верхнем углу и небольшие AC показывают концентрацию энергии.",
    limitations=("Положение нулевой частоты и масштаб коэффициентов зависят от соглашений реализации.", "Глобальное преобразование чувствительно к границам; блочная DCT создаёт отдельные границы каждого блока."),
    links=("Image Frequency-Domain Transforms", "JPEG Compression", "Frequency-Domain Image Steganography", "Koch-Zhao Method"),
    sources=((11, "4–19, 27–37"), (12, "12–13")),
    visuals=(("OCS - DCT Basis - L11 p28.png", "матричное определение DCT и косинусные коэффициенты базиса.", 11, 28),),
)
add(
    title="Walsh-Hadamard Transform", folder="01 Knowledge/Computer Science", note_type="concept",
    area=("Computer Science",), aliases=("Преобразование Уолша-Адамара",),
    summary="Walsh–Hadamard Transform раскладывает данные по ортогональным знаковым функциям. Матрица содержит только `+1` и `−1`, поэтому преобразование удобно реализуется сложениями и вычитаниями.",
    mechanism=("Матрицы порядка степени двойки строятся рекурсивно.", "Двумерное преобразование применяется к строкам и столбцам.", "Нормировка определяет коэффициент обратного преобразования."),
    formulas=(r"H_{2n}=\begin{bmatrix}H_n&H_n\\H_n&-H_n\end{bmatrix},\qquad H_1=[1]", r"H_nH_n^{\mathsf T}=nI"),
    example="Курс строит матрицы `H2`, `H4`, затем показывает прямое и обратное преобразование изображения и отдельного блока пикселей.",
    limitations=("Размер преобразования обычно должен быть степенью двойки или требовать дополнения.", "Ненормированная матрица масштабирует энергию; это нужно учитывать при обратном ходе и порогах встраивания."),
    links=("Image Frequency-Domain Transforms", "Discrete Fourier and Cosine Transforms for Images", "Discrete Wavelet Transform"),
    sources=((11, "38–44"),),
)
add(
    title="Discrete Wavelet Transform", folder="01 Knowledge/Computer Science", note_type="concept",
    area=("Computer Science",), aliases=("Дискретное вейвлет-преобразование", "DWT"),
    summary="Discrete Wavelet Transform разделяет сигнал на низко- и высокочастотные компоненты с локализацией по положению и масштабу. Для изображения фильтрация и прореживание выполняются последовательно по двум измерениям.",
    mechanism=("Фильтры анализа `H0` и `H1` формируют низкочастотную и высокочастотную ветви, затем данные прореживаются вдвое.", "Повторное разложение низкочастотной части создаёт многоуровневое представление.", "Фильтры синтеза и повышение частоты выполняют обратное преобразование."),
    formulas=(r"a_k=\sum_n x_nh_0[n-2k],\qquad d_k=\sum_n x_nh_1[n-2k]", r"LL,LH,HL,HH=DWT_2(I)"),
    example="Лекция сопоставляет Haar и Daubechies 9/7, затем показывает четыре поддиапазона двумерного преобразования и обратную сборку.",
    limitations=("Граничная обработка и выбранные фильтры меняют коэффициенты.", "Встраивание в высокочастотные области менее заметно, но такие коэффициенты легче теряются при сглаживании или сжатии."),
    links=("Image Frequency-Domain Transforms", "Walsh-Hadamard Transform", "Frequency-Domain Image Steganography", "Neural Network Steganalysis"),
    sources=((11, "45–54"),),
)


# Steganography: 22 content notes; the MOC is built separately below.
add(
    title="Information Hiding", folder="01 Knowledge/Cybersecurity/Steganography", note_type="concept",
    area=("Computer Science",), security=("Steganography",), aliases=("Сокрытие информации",),
    summary="Information Hiding — общая область методов, которые помещают дополнительные данные в цифровой объект так, чтобы обеспечить требуемое сочетание незаметности, извлекаемости и устойчивости. Стеганография и цифровые водяные знаки используют общий контейнер, но решают разные задачи.",
    mechanism=("Контейнер `C` преобразуется с учётом сообщения `M` и, при необходимости, ключа `K`.", "Получатель извлекает сообщение или проверяет наличие метки по стегообъекту `S`.", "Свойства системы оцениваются по ёмкости, визуальному искажению, робастности и обнаружимости."),
    formulas=(r"S=Embed(C,M,K)", r"\hat M=Extract(S,K)"),
    example="Курс рассматривает изображения как основной контейнер и разделяет сокрытие сообщения от внедрения водяного знака для подтверждения происхождения или целостности.",
    limitations=("Секретность алгоритма не заменяет ключ: анализ предполагает известный метод.", "Оптимизация одного свойства обычно ухудшает другое: большая ёмкость повышает искажение и обнаружимость."),
    links=("Digital Steganography", "Digital Watermarking", "Steganography Quality Metrics", "Steganalysis"),
    sources=((8, "2–5"),),
)
add(
    title="Digital Steganography", folder="01 Knowledge/Cybersecurity/Steganography", note_type="concept",
    area=("Computer Science",), security=("Steganography",), aliases=("Цифровая стеганография",),
    summary="Digital Steganography скрывает сам факт передачи сообщения внутри цифрового контейнера. В отличие от шифрования, цель состоит не только в недоступности содержания, но и в снижении вероятности обнаружения вложения.",
    mechanism=("Embedding выбирает элементы контейнера и кодирует в них биты сообщения.", "Stego key может определять порядок выбора позиций или параметры модификации.", "Extraction бывает blind, когда исходный контейнер не нужен, или использует оригинал как опору."),
    formulas=(r"S=E(C,M,K),\qquad \hat M=D(S,K)", r"P(Detect(S)=1)\rightarrow\min"),
    example="Лекция сопоставляет пространственное изменение пикселей и частотное изменение коэффициентов, а нейросетевое встраивание оставляет как обзор двух архитектурных подходов.",
    limitations=("Незаметность для глаза не равна статистической неразличимости.", "Перекодирование, масштабирование, фильтрация и обрезка могут уничтожить вложение; требования к каналу задаются заранее."),
    links=("Information Hiding", "Spatial-Domain Image Steganography", "Frequency-Domain Image Steganography", "Steganalysis"),
    sources=((8, "2–13"), (10, "14–15")),
)
add(
    title="Digital Watermarking", folder="01 Knowledge/Cybersecurity/Steganography", note_type="concept",
    area=("Computer Science",), security=("Steganography",), aliases=("Цифровые водяные знаки",),
    summary="Digital Watermarking внедряет метку, связанную с объектом, владельцем или событием обработки. В отличие от скрытого сообщения, водяной знак часто проектируется так, чтобы переживать допустимые преобразования контейнера.",
    mechanism=("Метка генерируется из идентификатора или проверяемого утверждения.", "Встраивание распределяет её по выбранным пикселям или коэффициентам.", "Проверка оценивает совпадение извлечённой метки с ожидаемой и принимает решение по порогу."),
    formulas=(r"S=Embed(C,W,K)", r"accept\iff NCC(W,\hat W)\ge\tau"),
    example="Курс демонстрирует один водяной знак после JPEG-сжатия с разными уровнями качества и сравнивает результат через BER и NCC.",
    limitations=("Робастная метка обычно вносит больше искажений, чем хрупкая.", "Водяной знак не доказывает авторство сам по себе: важны ключ, протокол регистрации и доверенная проверка."),
    links=("Information Hiding", "Steganography Quality Metrics", "Digital Watermark Attacks", "Frequency-Domain Image Steganography"),
    sources=((8, "5, 10–18"),),
)
add(
    title="Steganography Quality Metrics", folder="01 Knowledge/Cybersecurity/Steganography", note_type="concept",
    area=("Computer Science",), security=("Steganography",), aliases=("Метрики качества стеганографии",),
    summary="Метрики стеганографии измеряют разные свойства системы: embedding capacity — сколько данных помещено, MSE/PSNR — насколько изменён контейнер, BER/NCC — насколько точно восстанавливается вложение. Ни одна метрика не описывает безопасность целиком.",
    mechanism=("Ёмкость нормируется на число пикселей, чтобы сравнивать изображения разного размера.", "MSE и PSNR сравнивают исходный и стегообъект на уровне значений пикселей.", "BER и NCC сравнивают исходную и извлечённую битовые последовательности после воздействия."),
    formulas=(r"EC=\frac{B}{MN}\ \text{bpp},\quad MSE=\frac1{MN}\sum_{i=1}^{MN}(C_i-S_i)^2", r"PSNR=10\log_{10}\frac{255^2}{MSE},\quad BER=\frac{B_e}{B}"),
    example="В курсе JPEG-атака последовательно снижает качество: при росте BER от 0 к 0.3105 NCC падает от 1 к 0.7142.",
    limitations=("Высокий PSNR не гарантирует низкую статистическую обнаружимость.", "Сравнивать BER/NCC корректно только при одинаковом сообщении, атаке и процедуре синхронизации."),
    links=("Digital Steganography", "Digital Watermarking", "Digital Watermark Attacks", "Steganalysis"),
    sources=((8, "10–13, 15–18"),),
)
add(
    title="Digital Watermark Attacks", folder="01 Knowledge/Cybersecurity/Steganography", note_type="attack",
    area=("Computer Science",), security=("Steganography",), aliases=("Атаки на цифровые водяные знаки",),
    summary="Digital Watermark Attacks изменяют контейнер или процедуру проверки, чтобы удалить метку, ухудшить её извлечение или создать ложное решение. В курсе атаки рассматриваются через воздействие на робастность и визуальное качество.",
    mechanism=("Сжатие и фильтрация ослабляют выбранные компоненты сигнала.", "Геометрические преобразования нарушают синхронизацию позиций.", "Комбинированные воздействия могут сохранить приемлемое изображение, но увеличить ошибки извлечения."),
    formulas=(r"S'=A(S),\qquad \hat W=Extract(S',K)", r"success(A)\iff BER(W,\hat W)>\tau_{BER}\ \lor\ NCC(W,\hat W)<\tau_{NCC}"),
    example="Серия JPEG-перекодирований на слайде показывает плавный переход от полностью читаемой метки к заметно разрушенной при уменьшении качества.",
    limitations=("Сила атаки должна оцениваться вместе с полезностью и качеством результирующего объекта.", "Защита от одного преобразования не означает устойчивость к обрезке, масштабу, повороту или их комбинации."),
    links=("Digital Watermarking", "Steganography Quality Metrics", "JPEG Compression", "Steganalysis"),
    sources=((8, "14, 18"),),
)
add(
    title="Spatial-Domain Image Steganography", folder="01 Knowledge/Cybersecurity/Steganography", note_type="concept",
    area=("Computer Science",), security=("Steganography",), aliases=("Пространственная стеганография",),
    summary="Spatial-Domain Image Steganography изменяет значения пикселей непосредственно. Методы просты и ёмки, но изменения могут быть уничтожены обработкой изображения или выявлены статистикой соседних значений.",
    mechanism=("Изображение обходится по выбранному ключом порядку.", "Для каждого элемента кодируется один или несколько битов через замену, изменение чётности или адаптивную разность.", "Получатель повторяет порядок и восстанавливает биты из значений пикселей."),
    formulas=(r"P_i'=P_i+\Delta(P_i,m_i,K)", r"\hat m_i=Decode(P_i',K)"),
    example="Курс начинает с LSB, затем уменьшает регулярность через PM1 и повышает адаптивность через PVD и NMI.",
    limitations=("Сжатие с потерями, ресэмплинг и цветовая коррекция меняют пиксели и разрушают вложение.", "Последовательное заполнение и высокая payload дают выраженные статистические следы."),
    links=("LSB Steganography", "Plus-Minus One Steganography", "Pixel Value Differencing", "Neighbor Mean Interpolation", "Statistical Steganalysis"),
    sources=((8, "6–9"), (10, "2–13")),
)
add(
    title="LSB Steganography", folder="01 Knowledge/Cybersecurity/Steganography", note_type="technique",
    area=("Computer Science",), security=("Steganography",), aliases=("LSB-встраивание",),
    summary="LSB Steganography заменяет один или несколько младших битов значения пикселя битами сообщения. Изменение младшего бита не превышает единицы, поэтому обычно визуально незаметно, но создаёт характерные статистические пары значений.",
    mechanism=("Пиксель представляется двоичным словом.", "Младший бит заменяется очередным битом сообщения; при извлечении читается чётность.", "Для цветного изображения канал и порядок пикселей должны быть согласованы."),
    formulas=(r"P_i'=P_i-(P_i\bmod2)+m_i", r"\hat m_i=P_i'\bmod2"),
    example="На слайде три RGB-байта меняют только последние разряды: два значения корректируются на единицу, одно уже совпадает с нужным битом.",
    limitations=("Последовательный LSB уязвим к визуальному анализу битовых плоскостей и pairs-of-values test.", "JPEG-перекодирование и другие изменения пикселей обычно уничтожают вложение."),
    links=("Spatial-Domain Image Steganography", "Plus-Minus One Steganography", "Visual Steganalysis and Bit-Plane Analysis", "Statistical Steganalysis"),
    sources=((10, "3"),),
    visuals=(("OCS - LSB Embedding - L10 p03.png", "замену последних битов RGB-компонент и минимальный масштаб изменения пикселя.", 10, 3),),
)
add(
    title="Plus-Minus One Steganography", folder="01 Knowledge/Cybersecurity/Steganography", note_type="technique",
    area=("Computer Science",), security=("Steganography",), aliases=("PM1 Steganography", "Стеганография плюс-минус один"),
    summary="Plus-Minus One Steganography кодирует бит чётностью значения, но при несовпадении случайно увеличивает или уменьшает элемент на единицу. В отличие от прямой LSB-замены, направление изменения не детерминировано.",
    mechanism=("Если чётность уже совпадает с битом, значение не меняется.", "Иначе случайный бит выбирает `+1` или `−1` с учётом допустимого диапазона.", "В JPEG-версии операция применяется к пригодным квантованным коэффициентам."),
    formulas=(r"P_i'=\begin{cases}P_i+(-1)^r,&P_i\bmod2\ne m_i\\P_i,&\text{иначе}\end{cases}", r"\hat m_i=P_i'\bmod2"),
    example="Для 4×4 блока и сообщения `0001101111001011` слайд показывает, какие элементы сохранились, а какие сдвинулись на единицу.",
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
    formulas=(r"P_i'=q\left\lfloor\frac{P_i}{q}\right\rfloor+\frac q2m_i", r"\hat m_i=\arg\min_{e\in\{0,1\}}|P_i'-Q_e(P_i')|"),
    example="При `q=4` курс преобразует 4×4 блок: пиксель 124 с битом 1 становится 126, а 117 с битом 0 — 116.",
    limitations=("Большой `q` повышает устойчивость, но увеличивает искажение.", "Округление и последующее квантование могут переместить значение к другому классу и вызвать BER."),
    links=("Spatial-Domain Image Steganography", "Frequency-Domain Image Steganography", "Steganography Quality Metrics", "Koch-Zhao Method"),
    sources=((10, "6–7"), (13, "7")),
    visuals=(("OCS - QIM Embedding - L10 p07.png", "работу `q=4` на конкретной матрице и два семейства квантованных уровней.", 10, 7),),
)
add(
    title="Pixel Value Differencing", folder="01 Knowledge/Cybersecurity/Steganography", note_type="technique",
    area=("Computer Science",), security=("Steganography",), aliases=("PVD Steganography", "Метод разности значений пикселей"),
    summary="Pixel Value Differencing адаптирует payload к локальному контрасту: пара соседних пикселей переносит больше битов, когда их разность попадает в широкий диапазон. Изменения распределяются между двумя элементами пары.",
    mechanism=("Изображение разбивается на непересекающиеся пары и вычисляется `d=P_i-P_{i+1}`.", "Модуль разности выбирает диапазон `[l_k,u_k]` и число внедряемых битов.", "Фрагмент сообщения задаёт новую разность, после чего оба пикселя корректируются в противоположных направлениях."),
    formulas=(r"n_k=\log_2(u_k-l_k+1),\qquad d_k^*=sign(d_k)(l_k+m_k)", r"m_k=|P_i'-P_{i+1}'|-l_k"),
    example="Для пары `(124,115)` разность 9 попадает в `[8,15]`, поэтому встраиваются три бита `011`, новая разность становится 11, а пара — `(125,114)`.",
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
    formulas=(r"P_{12}=\left\lfloor\frac{P_{11}+P_{13}}2\right\rfloor,\quad P_{21}=\left\lfloor\frac{P_{11}+P_{31}}2\right\rfloor", r"P_{ij}'=P_{ij}+m_k,\qquad \hat m_k=P_{ij}'-P_{ij}"),
    example="Из 2×2 матрицы курс строит 4×4 интерполированную матрицу и внедряет `0001101111001011`; первый фрагмент меняет 119 на 122.",
    limitations=("Ёмкость зависит от допустимых разностей и правил округления.", "Масштабирование или повторная интерполяция меняют предсказанные значения и нарушают извлечение."),
    links=("Spatial-Domain Image Steganography", "Pixel Value Differencing", "Digital Image Fundamentals", "Steganography Quality Metrics"),
    sources=((10, "11–13"),),
    visuals=(("OCS - NMI Embedding - L10 p13.png", "исходную, интерполированную и стегоматрицу вместе с первыми расчётами payload.", 10, 13),),
)
add(
    title="Frequency-Domain Image Steganography", folder="01 Knowledge/Cybersecurity/Steganography", note_type="concept",
    area=("Computer Science",), security=("Steganography",), aliases=("Частотная стеганография",),
    summary="Frequency-Domain Image Steganography внедряет данные в коэффициенты преобразования, а затем выполняет обратное преобразование. Она обычно устойчивее к части постобработки, но сложнее и подвержена ошибкам округления.",
    mechanism=("Контейнер преобразуется DCT, DFT, WHT или DWT.", "Embedding изменяет выбранные коэффициенты с учётом частотной зоны и силы.", "После обратного преобразования пиксели округляются; получатель снова вычисляет спектр и извлекает биты."),
    formulas=(r"F=T(C),\quad F'=Embed(F,M,K),\quad S=T^{-1}(F')", r"\hat M=Extract(T(S),K)"),
    example="Схема курса показывает, что даже без внешнего воздействия округление вещественных пикселей может дать `BER>0`; предлагается итеративно проверять и повторять встраивание.",
    limitations=("Выбор слишком низких частот заметен, слишком высоких — хрупок.", "Реализация должна учитывать нормировку преобразования и повторное целочисленное округление."),
    links=("Image Frequency-Domain Transforms", "Koch-Zhao Method", "Quantization Index Modulation", "JPEG Steganography", "Steganalysis"),
    sources=((8, "6–8"), (13, "2–9")),
)
add(
    title="Koch-Zhao Method", folder="01 Knowledge/Cybersecurity/Steganography", note_type="technique",
    area=("Computer Science",), security=("Steganography",), aliases=("Метод Коха и Жао",),
    summary="Koch–Zhao Method кодирует один бит отношением двух среднечастотных DCT-коэффициентов блока. Порог `p` задаёт минимальную разницу и тем самым управляет компромиссом между заметностью и устойчивостью.",
    mechanism=("В каждом DCT-блоке выбираются два согласованных AC-коэффициента.", "Для бита 0 первый по модулю делается больше второго минимум на `p`; для бита 1 — наоборот.", "Извлечение сравнивает абсолютные значения выбранной пары."),
    formulas=(r"m_i=0:\ |AC_1|-|AC_2|>p", r"m_i=1:\ |AC_1|-|AC_2|<-p"),
    example="Слайд курса помещает один бит в одну пару среднечастотных коэффициентов и показывает симметричное правило решения по их сравнению.",
    limitations=("Малый `p` даёт ошибки после округления, большой создаёт заметное искажение.", "Позиции коэффициентов и порядок блоков должны быть известны извлекателю и защищены ключом."),
    links=("Frequency-Domain Image Steganography", "Discrete Fourier and Cosine Transforms for Images", "Steganography Quality Metrics", "Steganalysis"),
    sources=((13, "6"),),
    visuals=(("OCS - Koch Zhao - L13 p06.png", "два среднечастотных коэффициента, порог `p` и противоположные неравенства для 0 и 1.", 13, 6),),
)
add(
    title="JPEG Steganography", folder="01 Knowledge/Cybersecurity/Steganography", note_type="concept",
    area=("Computer Science",), security=("Steganography",), aliases=("Стеганография JPEG",),
    summary="JPEG Steganography изменяет квантованные DCT-коэффициенты внутри JPEG-конвейера. Методы должны сохранять синтаксическую корректность и учитывать особую роль нулей, ±1, DC и AC-коэффициентов.",
    mechanism=("JPEG декодируется до квантованных коэффициентов, не обязательно до пикселей.", "Пригодные AC-коэффициенты выбираются по правилам метода и порядку ключа.", "После модификации коэффициенты снова энтропийно кодируются."),
    formulas=(r"\hat G_{uv}=round(G_{uv}/Q_{uv})", r"\hat G_{uv}'=Embed(\hat G_{uv},m_i)"),
    example="Курс последовательно рассматривает JSteg, PM1, F3, F4 и F5 как ответы на статистические следы и shrinkage при изменении квантованных коэффициентов.",
    limitations=("Повторное полное JPEG-перекодирование меняет коэффициенты и может уничтожить payload.", "Изменение нулей и малых коэффициентов сильно влияет на длины серий, размер файла и статистическую обнаружимость."),
    links=("JPEG Compression", "JSteg", "F3 and F4 JPEG Steganography", "F5 JPEG Steganography", "Statistical Steganalysis"),
    sources=((13, "10–15"), (14, "7–8, 14–16")),
)
add(
    title="JSteg", folder="01 Knowledge/Cybersecurity/Steganography", note_type="technique",
    area=("Computer Science",), security=("Steganography",), aliases=("JSteg JPEG Steganography",),
    summary="JSteg переносит идею LSB в квантованные DCT-коэффициенты JPEG: младший бит модуля пригодного коэффициента заменяется битом сообщения. Значения −1, 0 и 1 исключаются, чтобы не создавать неоднозначность.",
    mechanism=("Коэффициенты обходятся в согласованном порядке.", "Непригодные значения пропускаются.", "Для остальных меняется младший бит абсолютного значения, знак сохраняется."),
    formulas=(r"C'=sign(C)\left(|C|-(|C|\bmod2)+m_i\right)", r"\hat m_i=|C'|\bmod2"),
    example="Слайд явно исключает `−1,0,1` и показывает изменение последнего двоичного разряда модуля коэффициента.",
    limitations=("Регулярное выравнивание чётных и нечётных коэффициентов оставляет статистический след.", "Пропуски требуют точного совпадения порядка коэффициентов у отправителя и получателя."),
    links=("JPEG Steganography", "LSB Steganography", "F3 and F4 JPEG Steganography", "Statistical Steganalysis"),
    sources=((13, "11"),),
    visuals=(("OCS - JSteg - L13 p11.png", "исключение малых коэффициентов и LSB-замену с сохранением знака.", 13, 11),),
)
add(
    title="F3 and F4 JPEG Steganography", folder="01 Knowledge/Cybersecurity/Steganography", note_type="technique",
    area=("Computer Science",), security=("Steganography",), aliases=("F3", "F4", "F3 and F4"),
    summary="F3 и F4 уменьшают модуль ненулевого JPEG-коэффициента, когда его отображаемый бит не совпадает с сообщением. F4 меняет правило интерпретации отрицательных коэффициентов, чтобы уменьшить асимметрию знаков.",
    mechanism=("Нули пропускаются.", "F3 при необходимости уменьшает модуль; если получается ноль, возникает shrinkage и тот же бит переносится дальше.", "F4 использует противоположное соответствие чётности для отрицательных значений, сохраняя то же правило повторного встраивания после shrinkage."),
    formulas=(r"F3:\ C'=sign(C)(|C|-1)\ \text{если }|C|\bmod2\ne m_i", r"F4:\ C'=\begin{cases}C+1,&C<0\ \land\ |C|\bmod2=m_i\\C-1,&C>0\ \land\ |C|\bmod2\ne m_i\\C,&\text{иначе}\end{cases}"),
    example="Курс отдельно показывает случай `C'=0`: коэффициент пропускается, а не считается успешно закодированным символом.",
    limitations=("Shrinkage меняет распределение нулей и длину обхода.", "Даже исправление знаковой асимметрии не устраняет все статистические зависимости."),
    links=("JPEG Steganography", "JSteg", "F5 JPEG Steganography", "Statistical Steganalysis"),
    sources=((13, "13–14"),),
    visuals=(("OCS - F3 F4 - L13 p14.png", "условия F4 для положительных и отрицательных коэффициентов и повтор после shrinkage.", 13, 14),),
)
add(
    title="F5 JPEG Steganography", folder="01 Knowledge/Cybersecurity/Steganography", note_type="technique",
    area=("Computer Science",), security=("Steganography",), aliases=("F5 Steganography",),
    summary="F5 JPEG Steganography применяет матричное кодирование к группам коэффициентов, чтобы внедрять несколько битов изменением не более одного коэффициента в группе. Это снижает число модификаций на бит payload.",
    mechanism=("Пригодные ненулевые коэффициенты собираются в группы.", "Группа из `2^k−1` коэффициентов кодирует `k` битов через проверочные XOR-суммы.", "Если проверочные значения не совпадают, уменьшается модуль одного выбранного коэффициента; shrinkage обрабатывается повторно."),
    formulas=(r"n=2^k-1", r"k=2:\ x_1=a_1\oplus a_3,\quad x_2=a_2\oplus a_3"),
    example="Для двух битов курс использует тройку коэффициентов: в зависимости от двух несовпадений меняется `a1`, `a2`, `a3` или ни один.",
    limitations=("Матричное кодирование снижает число изменений, но не гарантирует неразличимость.", "Корректная обработка нулей и синхронизация перестановки обязательны для извлечения."),
    links=("JPEG Steganography", "F3 and F4 JPEG Steganography", "Steganography Quality Metrics", "Statistical Steganalysis"),
    sources=((13, "15"),),
    visuals=(("OCS - F5 - L13 p15.png", "матрицу вложения для двух битов и выбор единственного изменяемого коэффициента.", 13, 15),),
)
add(
    title="Steganalysis", folder="01 Knowledge/Cybersecurity/Steganography", note_type="concept",
    area=("Computer Science",), security=("Steganography", "DFIR"), aliases=("Стегоанализ",),
    summary="Steganalysis исследует наличие, тип или параметры скрытого вложения в цифровом объекте. Базовая задача курса — двухклассовое решение между чистым контейнером и стегообъектом.",
    mechanism=("Визуальные методы исследуют битовые плоскости, спектры и гистограммы.", "Статистические методы проверяют ожидаемые распределения и зависимости.", "Машинное обучение строит признаки или извлекает их автоматически и обучает классификатор на чистых и модифицированных примерах."),
    formulas=(r"\delta(I)\in\{cover,stego\}", r"P_e=P(\delta(C)=stego)+P(\delta(S)=cover)"),
    example="Лекция проходит путь от просмотра LSB-плоскостей до CNN и подчёркивает необходимость выборки, соответствующей конкретным контейнерам и методам внедрения.",
    limitations=("Детектор может выучить камеру, pipeline обработки или источник данных вместо следа embedding.", "Результаты нельзя переносить на другой payload, формат или распределение изображений без новой проверки."),
    links=("Visual Steganalysis and Bit-Plane Analysis", "Statistical Steganalysis", "Machine Learning for Steganalysis", "Neural Network Steganalysis", "Digital Steganography"),
    sources=((8, "12"), (14, "2–28")),
)
add(
    title="Visual Steganalysis and Bit-Plane Analysis", folder="01 Knowledge/Cybersecurity/Steganography", note_type="technique",
    area=("Computer Science",), security=("Steganography", "DFIR"), aliases=("Визуальный стегоанализ", "Анализ битовых плоскостей"),
    summary="Visual Steganalysis выделяет представления, где слабые регулярные изменения становятся заметнее: отдельные битовые плоскости, гистограммы значений и DCT-спектры. Это быстрый способ сформировать гипотезу, но не доказательство.",
    mechanism=("Каждый разряд пикселей визуализируется отдельным бинарным изображением.", "Сравниваются структура младших плоскостей и ожидаемый шум.", "Для JPEG анализируются гистограммы DCT-коэффициентов до и после предполагаемого embedding."),
    formulas=(r"B_k(x,y)=\left\lfloor\frac{I(x,y)}{2^k}\right\rfloor\bmod2", r"h(c)=|\{(u,v):G_{uv}=c\}|"),
    example="После LSB-встраивания младшая плоскость на слайдах теряет естественную структуру; JSteg выравнивает отдельные столбцы гистограммы DCT.",
    limitations=("Оценка человеком субъективна и зависит от масштаба, палитры и содержимого.", "Адаптивные методы могут не давать видимого артефакта; вывод нужно подтверждать статистикой."),
    links=("LSB Steganography", "JPEG Steganography", "Statistical Steganalysis", "Steganalysis"),
    sources=((14, "4–8"),),
    visuals=(("OCS - Bit Planes - L14 p05.png", "изменение младших битовых плоскостей после LSB-встраивания.", 14, 5), ("OCS - DCT Histogram - L14 p08.png", "деформацию распределения DCT-коэффициентов после JSteg.", 14, 8)),
)
add(
    title="Statistical Steganalysis", folder="01 Knowledge/Cybersecurity/Steganography", note_type="technique",
    area=("Computer Science",), security=("Steganography", "DFIR"), aliases=("Статистический стегоанализ",),
    summary="Statistical Steganalysis проверяет, нарушил ли embedding ожидаемые частоты и зависимости элементов изображения. В простейшем LSB-анализе пары значений, отличающиеся младшим битом, после заполнения стремятся к одинаковым частотам.",
    mechanism=("Значения группируются в пары `(2j,2j+1)`.", "Из общего числа элементов пары вычисляется ожидаемая частота после LSB-встраивания.", "Хи-квадрат сопоставляет наблюдаемое и ожидаемое распределения; для JPEG используются гистограммы и межблочные зависимости."),
    formulas=(r"E_{2j}=E_{2j+1}=\frac{n_{2j}+n_{2j+1}}2", r"\chi^2=\sum_i\frac{(O_i-E_i)^2}{E_i}"),
    example="Курс сравнивает результат pairs-of-values test для чистого и наполовину заполненного изображения, затем перечисляет 23 JPEG-признака классического подхода.",
    limitations=("Тест предполагает конкретный алгоритм и способ заполнения; низкий или адаптивный payload может его обойти.", "Естественная обработка изображения тоже меняет статистику и создаёт false positive."),
    links=("LSB Steganography", "Visual Steganalysis and Bit-Plane Analysis", "Machine Learning for Steganalysis", "Steganalysis"),
    sources=((14, "10–16"),),
    visuals=(("OCS - Pairs of Values - L14 p12.png", "формирование пар, ожидаемые частоты и различие результатов для чистого и заполненного изображения.", 14, 12),),
)
add(
    title="Machine Learning for Steganalysis", folder="01 Knowledge/Cybersecurity/Steganography", note_type="technique",
    area=("Computer Science", "AI & ML"), security=("Steganography", "DFIR"), aliases=("Машинное обучение для стегоанализа",),
    summary="Machine Learning for Steganalysis формулирует обнаружение как классификацию по статистическим признакам изображения. Классический pipeline отделяет построение признаков от обучения k-NN, naive Bayes, SVM, logistic regression или другого классификатора.",
    mechanism=("Из чистых и стегоизображений строятся сопоставимые обучающие выборки.", "Для каждого объекта вычисляется вектор пространственных или JPEG-признаков.", "Классификатор обучается и проверяется на независимой выборке из того же операционного распределения."),
    formulas=(r"\hat y=\arg\max_{y\in\{cover,stego\}}P(y)\prod_iP(x_i\mid y)", r"\hat y_{kNN}=mode\{y_j:j\in N_k(x)\}"),
    example="Курс описывает 23 JPEG-признака, затем сравнивает k-NN и naive Bayes; закон Бенфорда приведён как простой дополнительный статистический признак.",
    limitations=("Для каждого изображения обучающей выборки должны быть вычислены признаки и известен правильный класс.", "Качество зависит от того, совпадают ли тип контейнера и метод embedding в обучающей и исследуемой выборках."),
    links=("Statistical Steganalysis", "Neural Network Steganalysis", "Steganalysis", "JPEG Steganography"),
    sources=((14, "13–22"),),
    visuals=(("OCS - Classification Pipeline - L14 p14.png", "трёхэтапный pipeline: признаки, обучающая выборка и классификатор.", 14, 14),),
)
add(
    title="Neural Network Steganalysis", folder="01 Knowledge/Cybersecurity/Steganography", note_type="technique",
    area=("Computer Science", "AI & ML"), security=("Steganography", "DFIR"), aliases=("Нейросетевой стегоанализ",), status="review",
    summary="Neural Network Steganalysis обучает глубокую модель выделять слабые следы embedding непосредственно из изображений или их остаточных представлений. В курсе это развитие ручного feature engineering, а конкретные архитектуры и цифры являются срезом 2024 года.",
    mechanism=("Высокочастотная предобработка или первые слои подавляют содержание и усиливают слабый embedding noise.", "CNN обучается различать cover/stego на парных или сбалансированных наборах.", "Оценка проводится отдельно для метода embedding, payload и источника изображений."),
    formulas=(r"\theta^*=\arg\min_\theta\sum_i CE(f_\theta(I_i),y_i)", r"P_e=\tfrac12(P_{FA}+P_{MD})"),
    example="Слайды приводят GNCNN (ошибка 33.6% в обозначенном эксперименте), TLU-CNN (24%) и PNet (7% при согласованном J-UNIWARD, 27% без него). Эти числа нельзя сравнивать вне их датасетов и условий.",
    limitations=("`status: review`: результаты GNCNN, TLU-CNN, PNet и список HUGO/WOW/S-UNIWARD/J-UNIWARD/UED датированы курсом 2024 года.", "Пример PNet показывает зависимость ошибки от того, присутствовал ли исследуемый embedding method в обучении."),
    links=("Machine Learning for Steganalysis", "Statistical Steganalysis", "Discrete Wavelet Transform", "JPEG Steganography", "Steganalysis"),
    sources=((14, "22–28"),),
    visuals=(("OCS - GNCNN - L14 p26.png", "архитектуру GNCNN и условия приведённого эксперимента, а не только процент ошибки.", 14, 26), ("OCS - PNet - L14 p28.png", "зависимость результата PNet от совпадения embedding method в обучении и проверке.", 14, 28)),
    extra="""## Датированный материал курса

Перечень адаптивных embedding methods и результаты трёх CNN сохранены для понимания эволюции подходов. Перед выбором актуальной архитектуры или сравнением качества требуется новая проверка по современным источникам; внешняя проверка в рамках этой интеграции намеренно не выполнялась.""",
)


STEGANOGRAPHY_MOC = rf'''---
type: moc
area:
  - Cybersecurity
security:
  - Steganography
---
{GENERATED_MARKER}
# Steganography

Самостоятельный маршрут по сокрытию данных в цифровых изображениях, устойчивости вложения и его обнаружению. Основы криптографии и стеганографии изучаются рядом, но решают разные задачи: криптография скрывает содержание, стеганография — наличие канала.

## Как изучать

1. [[Information Hiding]] → [[Digital Steganography]] и [[Digital Watermarking]].
2. [[Digital Image Fundamentals]] → [[Image Color Models]] → [[Digital Image File Formats]].
3. [[Spatial-Domain Image Steganography]] → [[LSB Steganography]] → адаптивные методы.
4. [[Image Frequency-Domain Transforms]] → [[Frequency-Domain Image Steganography]] → [[JPEG Steganography]].
5. [[Steganalysis]] → визуальные, статистические и обучаемые детекторы.

## Foundations and metrics

- [[Information Hiding]]
- [[Digital Steganography]]
- [[Digital Watermarking]] → [[Digital Watermark Attacks]]
- [[Steganography Quality Metrics]]
- [[Digital Image Fundamentals]], [[Image Color Models]], [[JPEG Compression]]

## Spatial-domain embedding

- [[Spatial-Domain Image Steganography]]
  - [[LSB Steganography]]
  - [[Plus-Minus One Steganography]]
  - [[Quantization Index Modulation]]
  - [[Pixel Value Differencing]]
  - [[Neighbor Mean Interpolation]]

## Frequency-domain and JPEG embedding

- [[Frequency-Domain Image Steganography]]
  - [[Koch-Zhao Method]]
  - [[Quantization Index Modulation]]
- [[JPEG Steganography]]
  - [[JSteg]]
  - [[F3 and F4 JPEG Steganography]]
  - [[F5 JPEG Steganography]]

## Steganalysis

- [[Steganalysis]]
  - [[Visual Steganalysis and Bit-Plane Analysis]]
  - [[Statistical Steganalysis]]
  - [[Machine Learning for Steganalysis]]
  - [[Neural Network Steganalysis]] (`status: review` для результатов курса 2024 года)

## Формальная модель

$$
S=Embed(C,M,K),\qquad \hat M=Extract(S,K),\qquad Detect(S)\rightarrow\{{cover,stego\}}
$$

## Источник курса

- [[Course - {COURSE}]]

Вернуться к [[Cybersecurity]] и [[Cryptography]].
'''


EXISTING_UPDATES: dict[Path, str] = {
    Path("01 Knowledge/Cryptography/History of Cryptography.md"): f'''## Дополнение из курса «{COURSE}»

Курс делит развитие криптографии на донаучный этап ручных устройств и преобразований, классический этап формализации подстановок/перестановок и современный этап вычислительных алгоритмов. Линейка Энея, сцитала и дисковый шифратор Джефферсона сохранены как исторические примеры внутри [[Classical Cryptography]], а не как отдельные карточки.

- {source(2)}, стр. 2–3.
- {source(3)}, стр. 2.
- {source(4)}, стр. 2.
- {source(5)}, стр. 4.''',
    Path("01 Knowledge/Cryptography/Cryptosystem and Security Goals.md"): f'''## Дополнение из курса «{COURSE}»

Материал связывает криптографические преобразования с комплексной защитой: шифрование отвечает за конфиденциальность, hash — за обнаружение случайных изменений, MAC — за целостность и аутентичность при общем секрете, digital signature — за проверяемое авторство и защиту от отказа. Это разные цели и механизмы, их нельзя заменять одним «шифрованием».

- {source(1)}, стр. 8–19.''',
    Path("01 Knowledge/Cryptography/Cryptanalysis.md"): f'''## Дополнение из курса «{COURSE}»

Исторические примеры уточняют выбор модели атаки: простая замена сохраняет частоты символов, Playfair и Hill переносят статистику на биграммы и блоки, Vigenere с повторяющимся ключом сначала раскрывает период через тест Касиски или индекс совпадений. Лекция 07 отдельно различает ciphertext-only, known-plaintext, chosen-plaintext и chosen-ciphertext доступ.

- {source(3)}, стр. 10.
- {source(5)}, стр. 8.
- {source(6)}, стр. 11.
- {source(7)}, стр. 6–7.''',
    Path("01 Knowledge/Cryptography/Rings and Modular Arithmetic.md"): f'''## Дополнение из курса «{COURSE}»

Арифметика остатков используется как единый язык классических формул: Affine Cipher требует обратимости множителя по модулю алфавита, Hill Cipher — обратимости определителя матрицы, Vigenere — сложения и вычитания символов в `Z_m`. Перед ручным расчётом нужно явно зафиксировать нумерацию алфавита.

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

Вводная лекция использует hash для контроля случайных искажений: отправитель и получатель сравнивают digest. Для защиты от активного противника одного публичного hash недостаточно — требуется [[Message Authentication Codes]] или [[Digital Signatures]].

- {source(1)}, стр. 15–16.''',
    Path("01 Knowledge/Cryptography/Message Authentication Codes.md"): f'''## Дополнение из курса «{COURSE}»

Имитовставка в курсе отделена от обычного hash наличием общего секретного ключа. Проверяющая сторона вычисляет тег заново; совпадение подтверждает целостность и знание ключа, но не даёт публичной неотказуемости.

- {source(1)}, стр. 17.''',
    Path("01 Knowledge/Cryptography/Digital Signatures.md"): f'''## Дополнение из курса «{COURSE}»

Базовая схема курса разделяет ключ подписи и ключ проверки: подписывается сообщение или его digest, а получатель проверяет результат открытым ключом. Это защищает от изменения и отказа от авторства только при корректной привязке открытого ключа к владельцу.

- {source(1)}, стр. 18–19.''',
    Path("01 Knowledge/Cybersecurity/Security Engineering/Brute-Force Attack.md"): f'''## Дополнение из курса «{COURSE}»

Полный перебор представлен как универсальный метод, не использующий внутреннюю структуру шифра. Его стоимость определяется числом допустимых ключей и скоростью проверки кандидата; поэтому длину ключа оценивают вместе с моделью проверки, параллелизмом и ценностью защищаемых данных.

- {source(7)}, стр. 5.''',
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
    titles = [note.title for note in NOTES]
    if len(NOTES) != 42 or len(set(titles)) != 42:
        raise RuntimeError(f"Expected 42 unique content notes, found {len(NOTES)}")
    for note in NOTES:
        write_generated(note.path, render(note), args.overwrite_generated)

    moc_path = Path("01 Knowledge/Cybersecurity/Steganography/Steganography.md")
    write_generated(moc_path, STEGANOGRAPHY_MOC, args.overwrite_generated)
    for path, block in EXISTING_UPDATES.items():
        update_existing(path, block)

    print(
        f"Built {len(NOTES) + 1} new canonical notes "
        f"and updated {len(EXISTING_UPDATES)} existing notes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
