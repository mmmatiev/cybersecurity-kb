---
type: moc
area:
  - Cybersecurity
security:
  - Steganography
---
<!-- generated: crypto-stego-course -->
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
S=Embed(C,M,K),\qquad \hat M=Extract(S,K),\qquad Detect(S)\rightarrow\{cover,stego\}
$$

## Источник курса

- [[Course - Основы криптографии и стеганографии]]

Вернуться к [[Cybersecurity]] и [[Cryptography]].
