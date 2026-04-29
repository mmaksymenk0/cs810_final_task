import hashlib
import os
import struct
import time

from sha256_impl import sha256_hex

message = b"give my friend 2 bitcoins for a pizza"
result_file = "pow_result.txt"


def check(prefix):
    h = hashlib.sha256(prefix + message).digest()
    return h[0] == 0 and h[1] == 0 and h[2] == 0 and h[3] == 0


def find_prefix():
    base = os.urandom(12)
    start = time.time()
    count = 0

    while True:
        prefix = base + struct.pack('>Q', count)

        if check(prefix):
            elapsed = time.time() - start
            print(f"\nfound prefix: {prefix.hex()}")
            full_hash = hashlib.sha256(prefix + message).hexdigest()
            print(f"hashlib hash: {full_hash}")
            our_hash = sha256_hex(prefix + message)
            print(f"our sha256:   {our_hash}")
            print(f"match: {full_hash == our_hash}")
            print(f"tries: {count+1:,}  time: {elapsed:.1f}s  rate: {(count+1)/elapsed:,.0f}/s")
            return prefix

        count += 1

        if count % 1_000_000 == 0:
            rate = count / (time.time() - start)
            print(f"  {count // 1_000_000}M hashes, {rate / 1e6:.2f}M/s", end="\r", flush=True)

        if count >= (1 << 32):
            count = 0
            base = os.urandom(12)


if __name__ == "__main__":
    if os.path.exists(result_file):
        with open(result_file) as f:
            prefix_hex = f.read().strip()
        prefix = bytes.fromhex(prefix_hex)
        if check(prefix):
            print(f"loaded saved prefix: {prefix_hex}")
            print(f"hash: {hashlib.sha256(prefix + message).hexdigest()}")
            print("already done. delete pow_result.txt to redo.")
        else:
            print("saved prefix is invalid, searching again...")
            prefix = find_prefix()
            with open(result_file, "w") as f:
                f.write(prefix.hex())
    else:
        print("searching for prefix with 32 leading zero bits...")
        print("will take a while (~4 billion tries in single thread)\n")
        prefix = find_prefix()
        with open(result_file, "w") as f:
            f.write(prefix.hex())
        print(f"\nsaved to {result_file}")
