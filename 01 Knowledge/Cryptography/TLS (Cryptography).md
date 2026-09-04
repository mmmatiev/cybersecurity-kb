---
type: concept
area:
  - Cryptography
  - Web
---
# TLS

## Суть

Transport Layer Security (TLS) защищает прикладной поток поверх транспорта: согласует версию и алгоритмы, аутентифицирует сервер сертификатом, получает сеансовые ключи и передаёт записи с конфиденциальностью и целостностью. Его безопасность зависит от полного handshake transcript и корректной проверки имени.

## Как устроено

- ClientHello и ServerHello выбирают параметры и несут случайные значения.
- Эфемерный key exchange получает shared secret; сертификат и CertificateVerify связывают его с сервером.
- KDF выводит handshake и application traffic secrets по стадиям транскрипта.
- Finished аутентифицирует накопленный transcript и подтверждает владение ключами.
- Record layer использует раздельные ключи и sequence-dependent nonces для направлений.

## Практический разбор

Диагностика TLS разделяет network reachability, handshake negotiation, certificate validation и application protocol. HTTP 200 не доказывает корректность всех криптографических свойств, а успешный handshake не гарантирует авторизацию приложения.

## Ограничения и безопасность

- Отключение проверки сертификата превращает шифрованный канал в уязвимый к MITM.
- Legacy versions, downgrade и слабые suites требуют явной политики.
- Session resumption и 0-RTT имеют отдельные свойства свежести и replay.

## Связи

- [[Public Key Infrastructure and X.509]]
- [[Cryptographic Protocols and Authenticated Key Exchange]]
- [[Man-in-the-Middle Attack]]

## Источники курса

- [[Source - Тема №5 Протоколы(1)]], раздел TLS.
- [[Source - Тема №6 Классы СКЗИ(1)]], раздел сетевых средств.
