import argparse
import base64
import re
import subprocess
from pathlib import Path

from sha256_impl import sha256


def pem_to_der(data: bytes) -> bytes:
    text = data.decode("ascii")
    match = re.search(
        r"-----BEGIN CERTIFICATE-----\s*(.*?)\s*-----END CERTIFICATE-----",
        text,
        re.S,
    )
    if not match:
        raise ValueError("PEM certificate block was not found")
    return base64.b64decode(re.sub(r"\s+", "", match.group(1)))


def load_certificate_der(path: Path) -> bytes:
    data = path.read_bytes()
    if data.startswith(b"-----BEGIN CERTIFICATE-----"):
        return pem_to_der(data)
    return data


def format_fingerprint(digest: bytes) -> str:
    return ":".join(f"{byte:02X}" for byte in digest)


def openssl_fingerprint(path: Path) -> str:
    result = subprocess.run(
        ["openssl", "x509", "-noout", "-fingerprint", "-sha256", "-in", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip().split("=", 1)[1]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute a certificate SHA-256 fingerprint over its DER encoding."
    )
    parser.add_argument("certificate", type=Path)
    args = parser.parse_args()

    der = load_certificate_der(args.certificate)
    own = format_fingerprint(sha256(der))

    print(f"certificate: {args.certificate}")
    print(f"DER length:  {len(der)} bytes")
    print(f"own SHA256:  {own}")
    print(f"openssl:     {openssl_fingerprint(args.certificate)}")


if __name__ == "__main__":
    main()
