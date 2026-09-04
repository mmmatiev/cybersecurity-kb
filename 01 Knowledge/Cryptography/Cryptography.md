---
type: moc
area:
  - Cryptography
---

# Cryptography

Знания о криптографических примитивах, протоколах и их безопасном применении.

## Как работать с разделом

1. Идти сверху вниз: основы → математика → примитивы → протоколы → стандарты → post-quantum.
2. После чтения отвечать на блок «Самопроверка» без подглядывания и разбирать связанные семинарские примеры.
3. Менять `status: learning` на `status: stable`, когда механизм, ограничения и пример воспроизводятся самостоятельно.
4. Заметки со `status: review` не использовать для эксплуатационных решений без актуального источника.

### В работе

```query
path:"01 Knowledge" [status:learning]
```

### Требуют актуализации

```query
path:"01 Knowledge" [status:review]
```

## Foundations

- [[History of Cryptography]]
- [[Cryptosystem and Security Goals]]
- [[Cryptanalysis]]

## Classical cryptography

- [[Classical Cryptography]]
  - [[Substitution Ciphers]] → [[Polybius Square]], [[Affine Cipher]] and [[Playfair Cipher]]
  - [[Transposition Ciphers]] → [[Cardan Grille Cipher]]
  - [[Hill Cipher]] and [[Vigenere Cipher]]
- [[Frequency Analysis]]
- [[Perfect Secrecy and Cryptographic Strength]]

## Mathematics

- [[Algebraic Structures]] → [[Permutation Groups]]
- [[Rings and Modular Arithmetic]] → [[Polynomial Rings]] → [[Finite Fields]]
- [[Elliptic Curves]]
- [[Euclidean Algorithm]]
- [[Euler Totient and Fermat-Euler Theorems]]
- [[Chinese Remainder Theorem]]
- [[Quadratic Residues and Modular Square Roots]]
- [[Modular Exponentiation]]
- [[Integer Factorization and Pollard Rho]]
- [[Discrete Logarithm and Baby-Step Giant-Step]]
- [[Primality Testing and Miller-Rabin]]

## Primitives

- [[Symmetric-Key Cryptography]]
  - [[Block Cipher Design]]
  - [[Stream Ciphers and One-Time Pad]]
  - [[DES and Triple DES]]
  - [[Advanced Encryption Standard|AES]]
  - [[Kuznyechik]] and [[Magma]]
  - [[Block Cipher Modes]]
- [[Cryptographic Hash Functions]] → [[Streebog]]
- [[Message Authentication Codes]]
- [[Asymmetric Cryptography]]
  - [[RSA]] and [[Rabin Cryptosystem]]
  - [[ElGamal Cryptosystem]]
  - [[Diffie-Hellman Key Exchange]]
  - [[Elliptic Curve Cryptography]]
  - [[Digital Signatures]] → [[Schnorr Signatures]]

## Protocols and infrastructure

- [[Random Number Generation and Entropy]]
- [[Cryptographic Key Management]]
- [[Cryptographic Protocols and Authenticated Key Exchange]]
- [[Public Key Infrastructure and X.509]] → [[Certificate Enrollment Protocols]]
- [[Hardware Security Modules]] and [[Cryptographic Service Providers]]
- [[Cryptographic Protection Systems]]
- [[TLS]]

## Standards

- [[GOST R 34.10-2012]] — digital signatures
- [[GOST R 34.12-2015]] — Kuznyechik and Magma
- [[GOST R 34.13-2015]] — block cipher modes

## Quantum and post-quantum cryptography

- [[Quantum Computing for Cryptography]]
- [[Quantum Key Distribution]] → [[BB84]]
- [[Post-Quantum Cryptography]]
  - [[Hash-Based Signatures]]
  - [[Code-Based Cryptography]]
  - [[Lattice-Based Cryptography]]
  - [[Multivariate Cryptography]]

## Security connections

- [[Brute-Force Attack]], [[Linear Cryptanalysis]] and [[Differential Cryptanalysis]]
- [[Man-in-the-Middle Attack]] and [[Side-Channel Attacks]]
- [[Russian Cryptographic Regulation and Certification]]

Стеганография не является веткой криптографии: для сокрытия самого факта передачи используется отдельный маршрут [[Steganography]], который опирается на основы цифровых изображений.

## Course source

- [[Course - Криптографические методы защиты информации]]
- [[Course - Основы криптографии и стеганографии]]

Cryptography является самостоятельной предметной областью и одновременно фундаментом для [[Cybersecurity]], [[AppSec]] и [[Network Security]].

Вернуться на [[Home]].
