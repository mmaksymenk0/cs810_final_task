# OpenSSL сертифікати

## Згенеровані файли

| Файл | Опис |
|------|------|
| `server.key` | приватний RSA-ключ розміром 8192 біт, згенерований через OpenSSL |
| `server.pub` | відкритий ключ, отриманий із `server.key` |
| `server.csr` | запит на формування сертифіката для `www.crypto.kse.ua` |
| `server.crt` | самопідписаний сертифікат, створений на основі `server.csr` |
| `server_csr_text.txt` | текстовий вивід вмісту CSR |
| `server_crt_text.txt` | текстовий вивід вмісту сертифіката |
| `tetiana_signed_by_alona.crt` | наш сертифікат, підписаний іншою командою |
| `tetiana_signed_by_alona_text.txt` | текстовий вивід сертифіката, підписаного іншою командою |
| `kse_current.crt` | чинний TLS leaf certificate домену `kse.ua`, отриманий 2026-05-01 |

## Команди

```bash
openssl genpkey -algorithm RSA -out certs/server.key -pkeyopt rsa_keygen_bits:8192

openssl req -new -key certs/server.key -out certs/server.csr \
  -subj "/C=UA/L=Kyiv/O=KSE/CN=www.crypto.kse.ua/emailAddress=tpovshyk@kse.org.ua" \
  -nodes

openssl req -text -noout -in certs/server.csr

openssl x509 -req -sha256 -in certs/server.csr -signkey certs/server.key -out certs/server.crt

openssl x509 -text -noout -in certs/server.crt
```

## Підпис сертифіката іншою командою

Для завдання з підписом іншою командою потрібно передавати тільки `server.csr`. CSR містить відкритий ключ і метадані власника сертифіката. Файл `server.key` передавати не можна, бо це приватний ключ. Якщо інша сторона отримає приватний ключ, вона зможе видавати себе за власника сертифіката і створювати підписи від імені нашої команди.

Перед тим як приймати сертифікат, підписаний іншою командою, треба перевірити вміст CSR:

```bash
openssl req -text -noout -in certs/server.csr
```

Під час перевірки потрібно переконатися, що subject і відкритий ключ відповідають нашим очікуванням.

Після передачі `server.csr` іншій команді було отримано `tetiana_signed_by_alona.crt`. Перевірка сертифіката:

```bash
openssl x509 -noout -subject -issuer -dates -in certs/tetiana_signed_by_alona.crt
```

Отриманий сертифікат має наш subject з email `tpovshyk@kse.org.ua`, а issuer містить email сторони, яка підписала сертифікат: `anazarenko1@kse.org.ua`.
