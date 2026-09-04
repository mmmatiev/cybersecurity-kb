---
type: source
area:
  - Cryptography
  - Computer Science
processing_status: processed
---
# Основы криптографии и стеганографии

## О курсе

Курс 2024 года связывает классическую криптографию с обработкой цифровых изображений, стеганографическим встраиванием и стегоанализом. Канонические карточки написаны по-русски своими словами; английские названия методов сохранены для поиска.

Корпус содержит 14 санитаризированных PDF: 256 страниц в оригиналах и 242 публичные страницы. Во всех лекциях удалена финальная контактная страница; в лекции 01 дополнительно скрыты контактные значения на страницах 3–4. Исходные файлы на Desktop не изменялись и проверены по SHA-256. Внешние источники и сервисы не использовались.

## Учебные маршруты

1. Классические шифры и их анализ: [[Classical Cryptography]] → [[Substitution Ciphers]] и [[Transposition Ciphers]] → [[Frequency Analysis]] → [[Perfect Secrecy and Cryptographic Strength]].
2. Представление изображения: [[Digital Image Fundamentals]] → [[Image Color Models]] → [[JPEG Compression]] → [[Image Frequency-Domain Transforms]].
3. Сокрытие: [[Steganography]] → пространственные и частотные методы → [[Steganalysis]].

## Полная матрица покрытия

| Source-note | Публичных страниц | Каноническое назначение |
|---|---:|---|
| [[Source - Основы криптографии и стеганографии - Лекция 01]] | 19 | source-only material; [[Cryptosystem and Security Goals]]; [[Classical Cryptography]]; [[Symmetric-Key Cryptography]]; [[Cryptographic Hash Functions]]; [[Message Authentication Codes]]; [[Digital Signatures]] |
| [[Source - Основы криптографии и стеганографии - Лекция 02]] | 12 | source-only material; [[History of Cryptography]]; [[Classical Cryptography]]; [[Rings and Modular Arithmetic]] |
| [[Source - Основы криптографии и стеганографии - Лекция 03]] | 10 | source-only material; [[Substitution Ciphers]]; [[Polybius Square]]; [[Affine Cipher]]; [[Frequency Analysis]] |
| [[Source - Основы криптографии и стеганографии - Лекция 04]] | 6 | source-only material; [[Transposition Ciphers]]; [[Cardan Grille Cipher]] |
| [[Source - Основы криптографии и стеганографии - Лекция 05]] | 8 | source-only material; [[Playfair Cipher]]; [[Classical Cryptography]]; [[Hill Cipher]]; [[Frequency Analysis]]; [[Cryptanalysis]] |
| [[Source - Основы криптографии и стеганографии - Лекция 06]] | 11 | source-only material; [[Classical Cryptography]]; [[Vigenere Cipher]]; [[Stream Ciphers and One-Time Pad]]; [[Cryptanalysis]]; [[Frequency Analysis]] |
| [[Source - Основы криптографии и стеганографии - Лекция 07]] | 7 | source-only material; [[Perfect Secrecy and Cryptographic Strength]]; [[Brute-Force Attack]]; [[Cryptanalysis]] |
| [[Source - Основы криптографии и стеганографии - Лекция 08]] | 18 | source-only material; [[Information Hiding]]; [[Digital Steganography]]; [[Digital Watermarking]]; [[Spatial-Domain Image Steganography]]; [[Frequency-Domain Image Steganography]]; [[Steganography Quality Metrics]]; [[Steganalysis]]; [[Digital Watermark Attacks]] |
| [[Source - Основы криптографии и стеганографии - Лекция 09]] | 21 | source-only material; [[Digital Image Fundamentals]]; [[Image Color Models]]; [[Digital Image File Formats]]; [[Lossless Image Compression]] |
| [[Source - Основы криптографии и стеганографии - Лекция 10]] | 15 | source-only material; [[Spatial-Domain Image Steganography]]; [[LSB Steganography]]; [[Plus-Minus One Steganography]]; [[Quantization Index Modulation]]; [[Pixel Value Differencing]]; [[Neighbor Mean Interpolation]]; [[Digital Steganography]] |
| [[Source - Основы криптографии и стеганографии - Лекция 11]] | 54 | source-only material; [[Image Frequency-Domain Transforms]]; [[Discrete Fourier and Cosine Transforms for Images]]; [[Walsh-Hadamard Transform]]; [[Discrete Wavelet Transform]] |
| [[Source - Основы криптографии и стеганографии - Лекция 12]] | 18 | source-only material; [[Lossless Image Compression]]; [[JPEG Compression]] |
| [[Source - Основы криптографии и стеганографии - Лекция 13]] | 15 | source-only material; [[Frequency-Domain Image Steganography]]; [[Koch-Zhao Method]]; [[Quantization Index Modulation]]; [[JPEG Steganography]]; [[JSteg]]; [[Plus-Minus One Steganography]]; [[F3 and F4 JPEG Steganography]]; [[F5 JPEG Steganography]] |
| [[Source - Основы криптографии и стеганографии - Лекция 14]] | 28 | source-only material; [[Steganalysis]]; [[Visual Steganalysis and Bit-Plane Analysis]]; [[JPEG Steganography]]; [[Statistical Steganalysis]]; [[Machine Learning for Steganalysis]]; [[Neural Network Steganalysis]]; dated/review material |

## Правила интерпретации

- Каждая публичная страница отражена в source-note; удалённые контактные страницы отмечены отдельно.
- Сцитала, линейка Энея и Jefferson Disk остаются разделами более общих карточек.
- Формулы Hill, QIM, PVD, NMI, Fourier/DCT, JPEG, wavelets, F3–F5 и методы стегоанализа сверяются по локальному рендеру.
- Результаты GNCNN, TLU-CNN, PNet и перечень HUGO/WOW/S-UNIWARD/J-UNIWARD/UED считаются датированным срезом курса 2024 года и требуют review перед практическим применением.

## Навигация

- [[Cryptography]] — криптографический маршрут.
- [[Computer Science]] — основы цифровых изображений.
- [[Steganography]] — самостоятельный маршрут по сокрытию и обнаружению данных.
- [[Sources]] — библиотека источников.
