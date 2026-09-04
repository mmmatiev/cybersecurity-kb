---
type: concept
area:
  - Cryptography
status: review
---
# Post-Quantum Cryptography

## Суть

Post-Quantum Cryptography (PQC) разрабатывает классические алгоритмы, рассчитанные на противника с крупномасштабным квантовым компьютером. Она отличается от QKD: выполняется на обычных вычислителях и заменяет уязвимые public-key primitives, а не физический канал распределения ключа.

## Как устроено

- Алгоритм Шора угрожает факторизации и дискретному логарифму, следовательно RSA, DH и ECC.
- Алгоритм Гровера даёт квадратичное ускорение поиска и влияет на запас длины симметричных ключей и хэшей.
- Основные семейства курса: hash-based signatures, code-based, lattice-based и multivariate cryptography.
- Миграция может применять hybrid key establishment или подпись, соединяя классический и PQC-компонент.
- Crypto agility требует версии форматов, negotiation и возможности ротации без изменения данных вручную.

## Практический разбор

Инвентаризация начинается с долгоживущих данных и public-key зависимостей: сертификаты, VPN, firmware signing, архивные подписи и протоколы. Затем оценивается риск harvest-now-decrypt-later и возможность гибридного перехода.

## Ограничения и безопасность

- Статусы стандартов, наборы параметров и рекомендации быстро меняются; эта заметка отражает материал курса на 2024 год и требует актуализации перед внедрением.
- Большие ключи и ciphertext/signature меняют MTU, storage, latency и parser attack surface.
- Новая математическая основа не устраняет implementation и side-channel risks.

## Связи

- [[Quantum Computing for Cryptography]]
- [[Hash-Based Signatures]]
- [[Code-Based Cryptography]]
- [[Lattice-Based Cryptography]]
- [[Multivariate Cryptography]]
- [[Quantum Key Distribution]]

## Источники курса

- [[Source - Тема №7 Постквантовая криптография(1)]], все разделы; срез 2024 года.
