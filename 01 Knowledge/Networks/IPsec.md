---
type: concept
area:
  - Networks
---
# IPsec

## Суть

IPsec защищает IP-пакеты на сетевом уровне набором протоколов, политик и Security Associations. ESP обеспечивает конфиденциальность и/или целостность полезной нагрузки, а IKE согласует алгоритмы, аутентифицирует стороны и создаёт ключевой материал.

## Как устроено

- Transport mode защищает payload исходного IP-пакета; tunnel mode инкапсулирует исходный пакет в новый.
- Security Association однонаправлена и задаёт SPI, ключи, алгоритмы и lifetime.
- Sequence number и anti-replay window обнаруживают повтор пакетов.
- IKE выполняет authenticated key exchange и создаёт CHILD SAs для трафика.
- Policy определяет, какой трафик обходить, отвергать или защищать.

## Практический разбор

Диагностика разделяет IKE negotiation, аутентификацию peer, установку CHILD SA, маршрутизацию и MTU. Наличие SA не означает, что нужный поток совпал с policy selector и реально проходит через туннель.

## Ограничения и безопасность

- Неправильные selectors создают незашифрованный bypass или black hole.
- Повторное использование PSK и слабая идентификация peer снижают аутентичность.
- Encapsulation увеличивает размер пакета и может вызвать fragmentation.

## Связи

- [[Cryptographic Protocols and Authenticated Key Exchange]]
- [[Diffie-Hellman Key Exchange]]
- [[Cryptographic Key Management]]

## Источники курса

- [[Source - Тема №5 Протоколы(1)]], раздел IPsec.
- [[Source - Тема №6 Классы СКЗИ(1)]], раздел сетевых средств.
