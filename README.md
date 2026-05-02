# Практичне завдання #3-4
## Реалізація цифрового підпису та сертифікатів

## Setup

Python-скрипти для RSA-PSS та RSA-OAEP використовують пакет `cryptography`:

```bash
python3 -m pip install -r requirements.txt
```



## Завдання 1 - SHA-256 з нуля

Реалізував алгоритм SHA-256 вручну по FIPS 180-4. Повідомлення розбивається на 64 байтові блоки, кожен блок обробляється через 64 раунди стискання з використанням констант k та початкових значень h0.

Алгоритм:
1. паддинг - додаємо байт 0x80, нулі і довжину повідомлення в кінці
2. розширення блоку до 64 слів (message schedule)
3. 64 раунди стискання з функціями Ch, Maj, sigma

Файл: `sha256_impl.py`

### Тестові вектори

Перевіряв результати порівнянням з hashlib.sha256.

| Вхід | SHA-256 |
|------|---------|
| `""` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `"abc"` | `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad` |
| `"hello world"` | `b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9` |
| `"give my friend 2 bitcoins for a pizza"` | `4941a019ff6dae9c05ce621111b74576be6a4eb4669ed0096ea28c3de63c5cc7` |
| `"follow the white rabbit"` | `bfc6f97e4dfa5e6535c1de0af2f687e1767b2873dc0219dd6aa16e60d7534434` |
| `"u" * 55` | `0ca01ee60257d2191b570046a2bcab086c75ebab545f8d690840265385594699` |
| `"u" * 56` | `8715318f741444913b0c10e87db38ad144fc37b5b9b07162516269d1c2c7deec` |

Результат тестування: 8/8 passed



## Завдання 2 - Proof of Work

Потрібно знайти 20 байтовий префікс P такий що:


SHA-256(P || "give my friend 2 bitcoins for a pizza")


починається з 32 нулів у бітовому представленні (тобто перші 4 байти хешу = 00 00 00 00).

Ймовірність одного успіху: 1/2^32 = 1/4 млрд.

Беремо 12 випадкових байт як сіль, далі додаємо 8-ми байтовий лічильник. Для прискорення запустив паралельно на всіх ядрах через multiprocessing - кожне ядро має свою окрему сіль, тому не перетинаються.

Файли: pow_prefix.py - однопотоковий, pow_prefix_fast.py - багатопотоковий

### Результат


prefix: 959c2277ea3e515c062422e5000000000deae369
hash:   000000003503ff9418de77afcb1e7dbb9b522fa8e19713699471ad6db7fc3f31


Перевірка: перші 4 байти хешу 00 00 00 00 => 32 нулі + 
Верифікував також власною реалізацією SHA-256 — збіглось.

Час пошуку: ~683 секунди на 12 ядрах (~13 млн хешів/сек сумарно).



## Завдання 3 - RSA-PSS підпис

Файл: `rsa_pss_sign.py`

### Чому textbook RSA небезпечний

Textbook RSA підпис виглядає так: `s = m^d mod n`, де `m` — це просто байти повідомлення як число.

Проблем декілька:

1. детермінованість. Одне й те ж повідомлення завжди дає один і той же підпис. Якщо атакуючий побачив підпис один раз — він знає підпис назавжди.
2. мультиплікативність. Підпис має властивість: `sign(m1) * sign(m2) = sign(m1 * m2) mod n`. Це дозволяє підробляти підписи без знання приватного ключа. Наприклад, атакуючий просить підписати два нешкідливих числа, а потім перемножує результати і отримує підпис довільного повідомлення.
3. немає хешування. Можна підписувати будь-яке число, зокрема й спеціально підібране.

### RSA-PSS

PSS вирішує ці проблеми: Спочатку хешуємо повідомлення через SHA-256, додаємо випадкову сіль до хешу, кодуємо через MGF1, тільки потім підписуємо RSA

Тому два підписи одного повідомлення завжди різні, і підробити підпис без приватного ключа практично неможливо.

### Результат

message:   give my friend 2 bitcoins for a pizza
sig len:   256 bytes (2048-bit key)

verify correct message: pass
verify tampered message: fail (expected)
signatures differ (pss is random): True
both verify: True




## Завдання 4 - RSA через key.pub

Файл: `rsa_encrypt.py`

Використав відкритий ключ з файлу key.pub (8192 біт). Для шифрування використав OAEP padding з SHA 256, аналогічно до PSS але для шифрування.


key size: 8192 bits
message:  give my friend 2 bitcoins for a pizza
ciphertext (1024 bytes): saved to encrypted.bin

Розшифрувати може тільки власник відповідного приватного ключа.


## Завдання 5 - OpenSSL ключ, CSR та self-signed certificate

Файли: `certs/server.key`, `certs/server.pub`, `certs/server.csr`, `certs/server.crt`

Для сертифікатної частини згенеровано окремий RSA ключ розміром 8192 біт:

```bash
openssl genpkey -algorithm RSA -out certs/server.key -pkeyopt rsa_keygen_bits:8192
```

CSR створено з subject з умови:

```bash
openssl req -new -key certs/server.key -out certs/server.csr \
  -subj "/C=UA/L=Kyiv/O=KSE/CN=www.crypto.kse.ua/emailAddress=tpovshyk@kse.org.ua" \
  -nodes
```

Вміст CSR перевірявся командою:

```bash
openssl req -text -noout -in certs/server.csr
```

Текстовий dump у `certs/server_csr_text.txt`.

Self-signed certificate:

```bash
openssl x509 -req -sha256 -in certs/server.csr -signkey certs/server.key -out certs/server.crt
```

Первірка вмісту сертифіката:

```bash
openssl x509 -text -noout -in certs/server.crt
```

Текстовий dump у `certs/server_crt_text.txt`.


## Завдання 6 - Підпис CSR іншою командою

Для підпису іншій команді потрібно передавати тільки `certs/server.csr` бо CSR містить відкритий ключ і метадані subject, але не містить приватного ключа.

Перед передачею CSR треба перевірити:

```bash
openssl req -text -noout -in certs/server.csr
```

Критично не передавати `certs/server.key` оскільки витік приватного ключа дозволяє іншій стороні підписувати дані від нашого імені, розшифровувати дані, якщо цей ключ використовується для шифрування, і фактично привласнити ідентичність сертифіката.

Наш CSR `certs/server.csr` був переданий іншій команді для підпису. Приватний ключ `certs/server.key` не передавався.

У відповідь отримано сертифікат `certs/tetiana_signed_by_alona.crt`, підписаний ключем колеги з email `anazarenko1@kse.org.ua`.

Перевірка отриманого сертифіката:

```bash
openssl x509 -noout -subject -issuer -dates -in certs/tetiana_signed_by_alona.crt
```

Результат:

```text
subject=C=UA, L=Kyiv, O=KSE, CN=www.crypto.kse.ua, emailAddress=tpovshyk@kse.org.ua
issuer=C=UA, L=Kyiv, O=KSE, CN=www.crypto.kse.ua emailAddress=anazarenko1@kse.org.ua
notBefore=May  2 10:08:55 2026 GMT
notAfter=May  2 10:08:55 2027 GMT
```

Subject збігається з нашим CSR, а Issuer вказує на сторону, яка підписала сертифікат.


## Завдання 7 - crt.sh для kse.ua

Запит до crt.sh виконувався для `kse.ua` з точним match:

```bash
curl -L "https://crt.sh/?q=kse.ua&match==&output=json"
```

Станом на 2026-05-01 найперший запис для identity `kse.ua`:

| Поле | Значення |
|------|----------|
| crt.sh ID | 619701728 |
| Issuer | COMODO ECC Domain Validation Secure Server CA 2 |
| Common Name | sni55450.cloudflaressl.com |
| SAN / name_value | kse.ua |
| Not Before | 2018-07-25 00:00:00 |
| Not After | 2019-01-31 23:59:59 |

Якщо фільтрувати строго `common_name == "kse.ua"`, то найперший запис:

| Поле | Значення |
|------|----------|
| crt.sh ID | 4725403360 |
| Issuer | cPanel, Inc. Certification Authority |
| Common Name | kse.ua |
| Not Before | 2021-06-19 00:00:00 |
| Not After | 2021-09-17 23:59:59 |

Тут обидва варіанти оскільки crt.sh може показувати сертифікати, де `kse.ua` знаходиться в SAN, але CN має інше значення.


## Завдання 8 - Fingerprint чинного сертифіката kse.ua

Файли: `certs/kse_current.crt`, `cert_fingerprint.py`

Чинний leaf certificate для `kse.ua` отримано через TLS підключення:

```bash
openssl s_client -connect kse.ua:443 -servername kse.ua -showcerts
```

SHA-256 fingerprint сертифіката обчислюється не від PEM-тексту і текстового dump, а від DER encoding усього X.509 сертифіката.

Скрипт `cert_fingerprint.py` бере PEM-сертифікат, декодує base64 в DER bytes і рахує SHA-256 через нашу реалізацію з `sha256_impl.py`.

Результат:

```text
own SHA256:  36:A7:60:17:49:FB:AD:99:5A:97:79:E2:C8:A2:B6:89:1D:03:98:70:FF:40:E3:4B:E2:0D:A3:A4:BF:CC:EB:E0
openssl:     36:A7:60:17:49:FB:AD:99:5A:97:79:E2:C8:A2:B6:89:1D:03:98:70:FF:40:E3:4B:E2:0D:A3:A4:BF:CC:EB:E0
```

Отже, наш fingerprint є SHA-256 hash від DER-представлення чинного leaf certificate `kse.ua`.


## Розподіл роботи

### Максим - Реалізація криптографії

- SHA-256 from scratch за FIPS 180-4.
- Тестові вектори для SHA-256.
- Proof-of-Work prefix search.
- RSA-PSS підпис і перевірка.
- RSA шифрування через `key.pub`.

### Тетяна - OpenSSL, сертифікати та аналіз

- Генерація RSA 8192-bit ключа.
- CSR і self-signed certificate.
- Перевірка CSR та сертифіката через OpenSSL.
- Пояснення безпечного обміну CSR з іншою командою.
- Дослідження crt.sh для `kse.ua`.
- Аналіз SHA-256 fingerprint чинного сертифіката.



## Файли проєкту

| Файл | Опис |
|------|------|
| `sha256_impl.py` | SHA-256 з нуля + тести |
| `pow_prefix.py` | пошук PoW префіксу |
| `pow_prefix_fast.py` | багатопотоковий |
| `pow_result.txt` | знайдений префікс |
| `rsa_pss_sign.py` | RSA-PSS підпис і перевірка |
| `rsa_encrypt.py` | RSA шифрування через key.pub |
| `cert_fingerprint.py` | SHA-256 fingerprint сертифіката через власний SHA-256 |
| `certs/` | OpenSSL ключі, CSR, сертифікати та dumps |
| `certs/tetiana_signed_by_alona.crt` | наш сертифікат, підписаний іншою командою |
| `certs/tetiana_signed_by_alona_text.txt` | текстовий вивід сертифіката, підписаного іншою командою |
| `requirements.txt` | dependency |
| `signing.key` | згенерований приватний ключ |
| `signing.pub` | відповідний публічний ключ |
| `encrypted.bin` | зашифроване повідомлення |
| `key.pub` | наданий відкритий ключ для шифрування |
