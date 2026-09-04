#!/usr/bin/env python3
"""Apply repeatable learning metadata and study aids to the cryptography corpus."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path("01 Knowledge")

ALIASES = {
    "Advanced Encryption Standard": ["AES", "Стандарт расширенного шифрования"],
    "Algebraic Structures": ["Алгебраические структуры"],
    "Anonymous Communication Systems": ["Анонимные системы связи"],
    "Asymmetric Cryptography": ["Асимметричная криптография"],
    "BB84": ["Протокол BB84"],
    "Block Cipher Design": ["Построение блочных шифров"],
    "Block Cipher Modes": ["Режимы работы блочных шифров"],
    "Blockchain Attacks": ["Атаки на блокчейн"],
    "Blockchain Cryptography": ["Криптография блокчейна"],
    "Blockchain and Consensus": ["Блокчейн и консенсус"],
    "Brute-Force Attack": ["Атака полным перебором", "Brute Force"],
    "Certificate Enrollment Protocols": ["Протоколы управления сертификатами"],
    "Chinese Remainder Theorem": ["Китайская теорема об остатках", "CRT"],
    "Code-Based Cryptography": ["Кодовая криптография"],
    "Cryptanalysis": ["Криптоанализ"],
    "Cryptographic Hash Functions": ["Криптографические хэш-функции"],
    "Cryptographic Key Management": ["Управление криптографическими ключами"],
    "Cryptographic Protection Systems": ["Средства криптографической защиты информации", "СКЗИ"],
    "Cryptographic Protocols and Authenticated Key Exchange": ["Криптографические протоколы и аутентифицированный обмен ключами", "AKE"],
    "Cryptographic Service Providers": ["Криптографические провайдеры", "CSP"],
    "Cryptosystem and Security Goals": ["Криптосистема и цели безопасности"],
    "DES and Triple DES": ["DES и Triple DES", "3DES"],
    "Differential Cryptanalysis": ["Дифференциальный криптоанализ"],
    "Diffie-Hellman Key Exchange": ["Обмен ключами Диффи — Хеллмана", "DH"],
    "Digital Signatures": ["Цифровые подписи", "Электронная подпись"],
    "Discrete Logarithm and Baby-Step Giant-Step": ["Дискретный логарифм и Baby-Step Giant-Step", "BSGS"],
    "ElGamal Cryptosystem": ["Криптосистема Эль-Гамаля"],
    "Elliptic Curve Cryptography": ["Криптография на эллиптических кривых", "ECC"],
    "Elliptic Curves": ["Эллиптические кривые"],
    "Euclidean Algorithm": ["Алгоритм Евклида", "Расширенный алгоритм Евклида"],
    "Euler Totient and Fermat-Euler Theorems": ["Функция Эйлера и теоремы Ферма — Эйлера"],
    "Finite Fields": ["Конечные поля", "Поля Галуа"],
    "GOST R 34.10-2012": ["ГОСТ Р 34.10-2012"],
    "GOST R 34.12-2015": ["ГОСТ Р 34.12-2015"],
    "GOST R 34.13-2015": ["ГОСТ Р 34.13-2015"],
    "Hardware Security Modules": ["Аппаратные модули безопасности", "HSM"],
    "Hash-Based Signatures": ["Подписи на основе хэш-функций"],
    "History of Cryptography": ["История криптографии"],
    "IPsec": ["IP Security", "Безопасность IP"],
    "Integer Factorization and Pollard Rho": ["Факторизация и метод Полларда ро"],
    "Kuznyechik": ["Кузнечик"],
    "Lattice-Based Cryptography": ["Решёточная криптография"],
    "Linear Cryptanalysis": ["Линейный криптоанализ"],
    "Magma": ["Магма"],
    "Man-in-the-Middle Attack": ["Атака человек посередине", "MITM"],
    "Message Authentication Codes": ["Коды аутентификации сообщений", "MAC"],
    "Modular Exponentiation": ["Модульное возведение в степень"],
    "Multivariate Cryptography": ["Многомерная криптография"],
    "Permutation Groups": ["Группы подстановок"],
    "Polynomial Rings": ["Кольца многочленов"],
    "Post-Quantum Cryptography": ["Постквантовая криптография", "PQC"],
    "Primality Testing and Miller-Rabin": ["Тесты простоты и Миллер — Рабин"],
    "Public Key Infrastructure and X.509": ["Инфраструктура открытых ключей и X.509", "PKI"],
    "Quadratic Residues and Modular Square Roots": ["Квадратичные вычеты и модульные квадратные корни"],
    "Quantum Computing for Cryptography": ["Квантовые вычисления для криптографии"],
    "Quantum Key Distribution": ["Квантовое распределение ключей", "QKD"],
    "RSA": ["Криптосистема RSA"],
    "Rabin Cryptosystem": ["Криптосистема Рабина"],
    "Random Number Generation and Entropy": ["Генерация случайных чисел и энтропия", "ГСЧ"],
    "Rings and Modular Arithmetic": ["Кольца и модульная арифметика"],
    "Russian Cryptographic Regulation and Certification": ["Российское регулирование и сертификация криптографии"],
    "SSH": ["Secure Shell", "Безопасная оболочка"],
    "Schnorr Signatures": ["Подписи Шнорра"],
    "Side-Channel Attacks": ["Атаки по сторонним каналам"],
    "Stream Ciphers and One-Time Pad": ["Поточные шифры и одноразовый блокнот", "OTP"],
    "Streebog": ["Стрибог", "ГОСТ Р 34.11-2012"],
    "Symmetric-Key Cryptography": ["Симметричная криптография"],
    "TLS": ["Transport Layer Security", "Безопасность транспортного уровня"],
}

REVIEW = {
    "Code-Based Cryptography",
    "Hash-Based Signatures",
    "Lattice-Based Cryptography",
    "Multivariate Cryptography",
    "Post-Quantum Cryptography",
    "Quantum Computing for Cryptography",
    "Quantum Key Distribution",
    "Russian Cryptographic Regulation and Certification",
    "TLS",
}

FORMULAS = {
    "Algebraic Structures": r"Для циклической группы порядка $n$ порядок степени образующего вычисляется как $$\operatorname{ord}(g^k)=\frac{n}{\gcd(n,k)}.$$",
    "Asymmetric Cryptography": r"Корректность пары преобразований выражается равенством $$D_{sk}(E_{pk}(m))=m.$$",
    "Block Cipher Design": r"При фиксированном ключе блочный шифр задаёт обратимую перестановку $$E_K:\{0,1\}^n\rightarrow\{0,1\}^n,\qquad D_K(E_K(P))=P.$$",
    "Block Cipher Modes": r"Для CBC связь блоков задаётся как $$C_i=E_K(P_i\oplus C_{i-1}),\qquad P_i=D_K(C_i)\oplus C_{i-1},\quad C_0=IV.$$ В режиме счётчика поток получают как $O_i=E_K(CTR_i)$, а $C_i=P_i\oplus O_i$.",
    "Brute-Force Attack": r"Для равномерного ключа длины $k$ полный перебор имеет пространство $2^k$ вариантов и в среднем требует примерно $$2^{k-1}$$ проверок.",
    "Chinese Remainder Theorem": r"Для попарно взаимно простых $n_i$ решение можно собрать как $$x\equiv\sum_{i=1}^{r} a_iN_i u_i\pmod N,\quad N=\prod_i n_i,\ N_i=N/n_i,\ u_i=N_i^{-1}\pmod{n_i}.$$",
    "Cryptographic Hash Functions": r"Birthday bound объясняет, почему коллизию для $n$-битного хэша ожидают примерно после $$q\approx 2^{n/2}$$ независимых проб, а поиск прообраза — после порядка $2^n$ проб.",
    "Cryptosystem and Security Goals": r"Функциональная корректность шифрования требует $$D_{k_2}(E_{k_1}(M))=M,$$ где в симметричной схеме обычно $k_1=k_2$, а в асимметричной используются разные ключи пары.",
    "Differential Cryptanalysis": r"Анализ отслеживает распространение разности $$\Delta X=X_0\oplus X_1,\qquad \Delta Y=S(X_0)\oplus S(X_1)$$ и ищет переходы с вероятностью, заметно отличающейся от случайной.",
    "Diffie-Hellman Key Exchange": r"Стороны публикуют $g^x$ и $g^y$, после чего независимо получают один секрет: $$K_A=(g^y)^x=g^{xy}=(g^x)^y=K_B.$$",
    "Digital Signatures": r"Абстрактная схема удовлетворяет условию корректности $$\operatorname{Verify}_{pk}(m,\operatorname{Sign}_{sk}(m))=1.$$",
    "Discrete Logarithm and Baby-Step Giant-Step": r"Задача состоит в поиске $x$ из $g^x=h$ в группе порядка $n$. BSGS представляет $$x=im+j$$ при $m=\lceil\sqrt n\rceil$ и сводит поиск к совпадению baby- и giant-steps.",
    "ElGamal Cryptosystem": r"Для открытого ключа $y=g^x$ и случайного $k$ шифртекст имеет вид $$c_1=g^k,\qquad c_2=m\,y^k,$$ а расшифрование восстанавливает $m=c_2(c_1^x)^{-1}$.",
    "Elliptic Curve Cryptography": r"Открытый ключ получают скалярным умножением $$Q=dP,$$ а стойкость связывают со сложностью восстановления $d$ по точкам $P$ и $Q$.",
    "Elliptic Curves": r"Кривая в короткой форме задаётся как $$y^2=x^3+ax+b,$$ причём условие $4a^3+27b^2\ne0$ исключает особые точки.",
    "Euclidean Algorithm": r"Алгоритм использует инвариант $$\gcd(a,b)=\gcd(b,a\bmod b),$$ а расширенный вариант находит $x,y$ такие, что $ax+by=\gcd(a,b)$.",
    "Euler Totient and Fermat-Euler Theorems": r"Если $\gcd(a,n)=1$, то $$a^{\varphi(n)}\equiv1\pmod n.$$ Для простого $p$ это даёт малую теорему Ферма: $a^{p-1}\equiv1\pmod p$.",
    "Finite Fields": r"Конечное поле имеет порядок $$|\mathbb F_{p^m}|=p^m,$$ а расширение можно представить как $\mathbb F_p[X]/(f)$ для неприводимого многочлена $f$ степени $m$.",
    "Integer Factorization and Pollard Rho": r"Pollard rho строит последовательность $x_{i+1}=f(x_i)\bmod n$ и ищет нетривиальный делитель через $$d=\gcd(|x_i-x_j|,n),\qquad 1<d<n.$$",
    "Lattice-Based Cryptography": r"Решётка, заданная базисом $B=(b_1,\ldots,b_n)$, состоит из целочисленных комбинаций $$\mathcal L(B)=\left\{\sum_i z_i b_i\mid z_i\in\mathbb Z\right\}.$$",
    "Linear Cryptanalysis": r"Линейная аппроксимация полезна, когда её вероятность $$P=\tfrac12+\varepsilon$$ имеет ненулевое смещение $\varepsilon$; накопление статистики позволяет отличать её от случайного соотношения.",
    "Message Authentication Codes": r"Отправитель вычисляет $$t=\operatorname{MAC}_K(m),$$ а получатель принимает сообщение только если независимо вычисленный тег совпадает с переданным.",
    "Modular Exponentiation": r"Двоичное разложение $e=\sum_i e_i2^i$ превращает вычисление в последовательность возведений в квадрат и умножений: $$a^e\equiv\prod_{i:e_i=1}a^{2^i}\pmod n.$$",
    "Permutation Groups": r"Если независимые циклы подстановки имеют длины $l_1,\ldots,l_r$, то её порядок равен $$\operatorname{ord}(\pi)=\operatorname{lcm}(l_1,\ldots,l_r).$$",
    "Polynomial Rings": r"Деление с остатком записывается как $$a(X)=q(X)b(X)+r(X),\qquad \deg r<\deg b.$$ Неприводимый $f$ позволяет построить поле классов $\mathbb F_p[X]/(f)$.",
    "Primality Testing and Miller-Rabin": r"Для нечётного кандидата представляют $$n-1=2^s d,\qquad d\ \text{нечётно},$$ и проверяют последовательность $a^d,a^{2d},\ldots,a^{2^{s-1}d}\pmod n$.",
    "Quadratic Residues and Modular Square Roots": r"Символ Лежандра удовлетворяет критерию Эйлера $$\left(\frac ap\right)\equiv a^{(p-1)/2}\pmod p,$$ принимая значения $1$ или $-1$ для ненулевого $a$.",
    "Rabin Cryptosystem": r"Шифрование использует $$c=m^2\pmod n,\qquad n=pq.$$ При известном разложении сначала находят корни по $p$ и $q$, затем объединяют их по CRT в четыре кандидата.",
    "Random Number Generation and Entropy": r"Для смещённого бита курса $P(X=1)=\tfrac12+\Delta$. XOR двух независимых битов уменьшает смещение: $$P(X_1\oplus X_2=0)=\tfrac12+2\Delta^2.$$",
    "Rings and Modular Arithmetic": r"Класс $a\in\mathbb Z_n$ обратим тогда и только тогда, когда $$\gcd(a,n)=1,$$ и обратный элемент удовлетворяет $aa^{-1}\equiv1\pmod n$.",
    "RSA": r"Для $n=pq$ выбирают $e$ и $d$ так, что $ed\equiv1\pmod{\varphi(n)}$. Тогда $$c=m^e\pmod n,\qquad m=c^d\pmod n.$$",
    "Schnorr Signatures": r"В варианте курса вычисляют $$R=g^r,\quad e=H(R\parallel m),\quad s=r+xe\pmod q,$$ а проверка восстанавливает $R_v=g^sP^e$ при согласованном обозначении открытого ключа.",
    "Stream Ciphers and One-Time Pad": r"Поточное шифрование складывает сообщение с гаммой: $$c_i=m_i\oplus\gamma_i,\qquad m_i=c_i\oplus\gamma_i.$$ Для OTP гамма равномерна, независима и используется ровно один раз.",
    "Symmetric-Key Cryptography": r"Один общий секрет управляет обеими операциями: $$C=E_K(M),\qquad M=D_K(C).$$",
}

DIAGRAMS = {
    "Blockchain and Consensus": """```mermaid
flowchart LR
    T[Транзакции] --> B[Кандидат в блок]
    B --> C{Консенсус}
    C --> L[Принятый журнал]
    L --> H[Ссылка на предыдущий блок]
```""",
    "Block Cipher Modes": """```mermaid
flowchart LR
    IV[IV / nonce] --> M[Режим работы]
    P[Открытые блоки] --> M
    E[Блочный шифр E_K] --> M
    M --> C[Шифртекст]
```""",
    "Cryptographic Protocols and Authenticated Key Exchange": """```mermaid
sequenceDiagram
    participant A as Сторона A
    participant B as Сторона B
    A->>B: параметры и вклад A
    B->>A: вклад B и подтверждение
    A->>B: подтверждение A
    Note over A,B: общий ключ принимается только после аутентификации
```""",
    "Cryptosystem and Security Goals": """```mermaid
flowchart LR
    M[Сообщение M] --> E[Шифрование E]
    K1[Ключ k1] --> E
    E --> C[Шифртекст C]
    C --> D[Расшифрование D]
    K2[Ключ k2] --> D
    D --> M2[Сообщение M]
```""",
    "Hardware Security Modules": """```mermaid
flowchart LR
    A[Приложение] -->|запрос операции| H[Граница HSM]
    H --> C[Криптографический процессор]
    H --> K[Защищённое хранение ключей]
    H --> R[Источник случайности]
    H -->|результат без выдачи ключа| A
```""",
    "Post-Quantum Cryptography": """```mermaid
flowchart TD
    PQC[Post-Quantum Cryptography] --> H[Hash-based]
    PQC --> C[Code-based]
    PQC --> L[Lattice-based]
    PQC --> M[Multivariate]
    H --> HS[Подписи]
    C --> CE[Шифрование / KEM]
    L --> LE[Шифрование и подписи]
    M --> MS[Подписи]
```""",
    "Public Key Infrastructure and X.509": """```mermaid
flowchart LR
    R[Корневой УЦ] -->|подписывает| I[Промежуточный УЦ]
    I -->|подписывает| E[Сертификат субъекта]
    E --> V[Проверяющая сторона]
    V -->|проверяет цепочку и срок| R
```""",
    "TLS": """```mermaid
flowchart TD
    A[Прикладной протокол] --> H[TLS Handshake: параметры, ключи, аутентификация]
    H --> R[TLS Record: защита трафика]
    R --> T[Надёжный транспорт, например TCP]
```""",
}


def add_frontmatter(text: str, title: str) -> str:
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not match:
        raise RuntimeError(f"Missing frontmatter: {title}")
    frontmatter = match.group(1)
    if "\naliases:" not in f"\n{frontmatter}":
        aliases = "\naliases:\n" + "\n".join(f'  - "{alias}"' for alias in ALIASES[title])
        frontmatter += aliases
    if not re.search(r"(?m)^status:", frontmatter):
        status = "review" if title in REVIEW else "learning"
        frontmatter += f"\nstatus: {status}"
    return f"---\n{frontmatter}\n---\n" + text[match.end():]


def self_check(title: str, note_type: str) -> str:
    display = ALIASES[title][0]
    if note_type == "attack":
        questions = [
            f"Какую предпосылку или цель безопасности нарушает {display}?",
            "Воспроизведите цепочку атаки: необходимые условия, действия нарушителя и наблюдаемый результат.",
            "Какие две меры разрывают цепочку на разных этапах и что останется проверить после их внедрения?",
        ]
    elif note_type == "standard":
        questions = [
            f"Какую область и какие преобразования определяет {display}?",
            "Назовите ключевые параметры или требования стандарта, которые нельзя смешивать с соседними ГОСТ.",
            "Что ещё требуется проверить в реализации, даже если она заявляет соответствие стандарту?",
        ]
    else:
        questions = [
            f"Какую задачу решает {display} и какие входные предпосылки для этого нужны?",
            "Воспроизведите основной механизм, вычислительные шаги или поток данных без подсказки.",
            "Назовите главное ограничение или ошибку применения и способ её обнаружить либо предотвратить.",
        ]
    return "## Самопроверка\n\n" + "\n".join(f"{i}. {q}" for i, q in enumerate(questions, 1))


def enrich(path: Path) -> None:
    title = path.stem
    text = path.read_text(encoding="utf-8")
    text = add_frontmatter(text, title)
    note_type = re.search(r"(?m)^type: ([^\n]+)", text).group(1)
    if title in FORMULAS and "## Ключевая формула" not in text:
        block = f"## Ключевая формула\n\n{FORMULAS[title]}\n\n"
        marker = "## Практический разбор\n"
        text = text.replace(marker, block + marker, 1)
    if title in DIAGRAMS and "## Схема" not in text:
        block = f"## Схема\n\n{DIAGRAMS[title]}\n\n"
        marker = "## Практический разбор\n"
        text = text.replace(marker, block + marker, 1)
    if "## Самопроверка" not in text:
        block = self_check(title, note_type) + "\n\n"
        marker = "## Источники курса\n"
        if marker not in text:
            raise RuntimeError(f"Missing source section: {path}")
        text = text.replace(marker, block + marker, 1)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    paths = sorted(path for path in ROOT.rglob("*.md") if path.stem in ALIASES)
    found = {path.stem for path in paths}
    if found != set(ALIASES):
        raise RuntimeError(f"Corpus mismatch: missing={set(ALIASES)-found}, extra={found-set(ALIASES)}")
    for path in paths:
        enrich(path)
    print(f"Enhanced {len(paths)} cryptography-course notes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
