---
type: concept
area:
  - Networks
---
# SSH

## Суть

Secure Shell (SSH) создаёт защищённый интерактивный или туннельный канал поверх TCP. Transport layer согласует алгоритмы и session keys, server authentication проверяет host key, а user authentication подтверждает клиента; эти этапы имеют разные ключи и доверенные данные.

## Как устроено

- Version exchange и algorithm negotiation предшествуют key exchange.
- Key exchange получает общий secret и hash транскрипта.
- Server подписывает exchange hash host key, который клиент сравнивает с known host или доверенной инфраструктурой.
- После NEWKEYS трафик защищается раздельными ключами направлений.
- User authentication использует public key, пароль или другие методы уже внутри защищённого транспорта.

## Практический разбор

Первое подключение с trust-on-first-use сохраняет host key, но не доказывает его подлинность вне канала. Изменение ключа требует проверки причины, а не автоматического удаления записи known_hosts.

## Ограничения и безопасность

- Отключение host-key verification допускает MITM.
- Agent forwarding переносит возможность подписи и расширяет доверенную границу.
- Слабые legacy algorithms и password authentication следует ограничивать политикой.

## Связи

- [[Cryptographic Protocols and Authenticated Key Exchange]]
- [[Man-in-the-Middle Attack]]
- [[Public Key Infrastructure and X.509]]

## Источники курса

- [[Source - Тема №5 Протоколы(1)]], раздел SSH.
- [[Source - Тема №6 Классы СКЗИ(1)]], раздел сетевых средств.
