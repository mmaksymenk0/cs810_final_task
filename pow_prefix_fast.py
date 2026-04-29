# same as pow_prefix.py but multitasking ==> faster

import hashlib
import os
import struct
import time
import multiprocessing as mp

message = b"give my friend 2 bitcoins for a pizza"
result_file = "pow_result.txt"


def worker(worker_id, result_queue):
    base = os.urandom(12)
    count = 0

    while True:
        prefix = base + struct.pack('>Q', count)
        h = hashlib.sha256(prefix + message).digest()

        if h[0] == 0 and h[1] == 0 and h[2] == 0 and h[3] == 0:
            result_queue.put(prefix)
            return

        count += 1
        if count >= (1 << 32):
            count = 0
            base = os.urandom(12)


if __name__ == "__main__":
    if os.path.exists(result_file):
        with open(result_file) as f:
            prefix_hex = f.read().strip()
        prefix = bytes.fromhex(prefix_hex)
        h = hashlib.sha256(prefix + message).hexdigest()
        if h.startswith("00000000"):
            print(f"loaded saved prefix: {prefix_hex}")
            print(f"hash: {h}")
            print("delete pow_result.txt to recompute.")
            exit()

    n = mp.cpu_count()
    print(f"starting pow with {n} workers...")

    result_q = mp.Queue()
    start = time.time()

    workers = [mp.Process(target=worker, args=(i, result_q)) for i in range(n)]
    for p in workers:
        p.start()

    while result_q.empty():
        time.sleep(5)
        elapsed = time.time() - start
        if not result_q.empty():
            break
        print(f"  running {elapsed:.0f}s", end="\r", flush=True)

    prefix = result_q.get()

    for p in workers:
        p.terminate()
    for p in workers:
        p.join()

    elapsed = time.time() - start
    h = hashlib.sha256(prefix + message).hexdigest()
    print(f"\nfound prefix: {prefix.hex()}")
    print(f"hash: {h}")
    print(f"time: {elapsed:.1f}s, workers: {n}")

    from sha256_impl import sha256_hex
    our = sha256_hex(prefix + message)
    print(f"our sha256: {our}")
    print(f"match: {h == our}")

    with open(result_file, "w") as f:
        f.write(prefix.hex())
    print(f"saved to {result_file}")
