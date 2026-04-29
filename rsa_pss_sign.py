# sign and verify a message using rsa-pss

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature

message = b"give my friend 2 bitcoins for a pizza"
key_file = "signing.key"
pub_file = "signing.pub"


def generate_or_load_key():
    try:
        with open(key_file, "rb") as f:
            key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())
        print(f"loaded existing key from {key_file}")
    except FileNotFoundError:
        print("generating 2048-bit rsa key pair...")

        key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
        with open(key_file, "wb") as f:
            f.write(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL, serialization.NoEncryption()))
        with open(pub_file, "wb") as f:
            f.write(key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
        print(f"saved private key to {key_file}")
        print(f"saved public key to {pub_file}")
    return key


def sign_pss(priv_key, msg):
    return priv_key.sign(msg, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())


def verify_pss(pub_key, sig, msg):
    try:
        pub_key.verify(sig, msg, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
        return True
    except InvalidSignature:
        return False


if __name__ == "__main__":
    priv = generate_or_load_key()
    pub = priv.public_key()

    sig = sign_pss(priv, message)
    print(f"\nmessage:   {message.decode()}")
    print(f"signature: {sig.hex()}")
    print(f"sig len:   {len(sig)} bytes")

    ok = verify_pss(pub, sig, message)
    print(f"\nverify correct message: {'pass' if ok else 'fail'}")

    tampered = message + b" NOT"
    ok2 = verify_pss(pub, sig, tampered)
    print(f"verify tampered message: {'pass (bad!)' if ok2 else 'fail (expected)'}")

    sig2 = sign_pss(priv, message)
    print(f"\nsign again: {sig2.hex()}")
    print(f"signatures differ (pss is random): {sig != sig2}")
    print(f"both verify: {verify_pss(pub, sig2, message)}")
