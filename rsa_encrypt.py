# encrypt a message using rsa with oaep padding (key.pub)

from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

message = b"give my friend 2 bitcoins for a pizza"
key_file = "key.pub"
out_file = "encrypted.bin"


def load_public_key(path):
    with open(path, "rb") as f:
        return load_pem_public_key(f.read(), backend=default_backend())


def rsa_encrypt(pub_key, msg):
    return pub_key.encrypt(msg,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(), label=None,),)


if __name__ == "__main__":
    pub = load_public_key(key_file)
    print(f"key size: {pub.key_size} bits")
    print(f"message:  {message.decode()}")
    
    ciphertext = rsa_encrypt(pub, message)
    print(f"\nciphertext ({len(ciphertext)} bytes):")
    print(ciphertext.hex())

    with open(out_file, "wb") as f:
        f.write(ciphertext)
    print(f"\nsaved to {out_file}")
