"""
Multi-threaded HTTP Range downloader for high-speed weights download.
"""

import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

REPO = "intfloat/multilingual-e5-small"
URL = f"https://huggingface.co/{REPO}/resolve/main/model.safetensors"
DEST = r"C:\Users\moham\OneDrive\Apps\اوكسجين\data\models\multilingual-e5-small\model.safetensors"


def get_file_size(url: str) -> int:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}, method="HEAD")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return int(resp.headers.get("Content-Length", 0))


def download_chunk(url: str, start: int, end: int, part_dest: str):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Range": f"bytes={start}-{end}"})
    with urllib.request.urlopen(req, timeout=60) as resp, open(part_dest, "wb") as f:
        f.write(resp.read())


def fast_download(url: str, dest: str, num_threads: int = 8):
    t0 = time.time()
    total_size = get_file_size(url)
    print(f"Total size to download: {total_size // (1024*1024)} MB using {num_threads} threads...", flush=True)

    chunk_size = total_size // num_threads
    ranges = []
    part_files = []

    for i in range(num_threads):
        start = i * chunk_size
        end = total_size - 1 if i == num_threads - 1 else (i + 1) * chunk_size - 1
        part_dest = f"{dest}.part{i}"
        ranges.append((start, end, part_dest))
        part_files.append(part_dest)

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(download_chunk, url, start, end, part_dest)
            for start, end, part_dest in ranges
        ]
        for idx, fut in enumerate(futures):
            fut.result()
            print(f"  [PART {idx+1}/{num_threads}] Finished.", flush=True)

    print("Merging parts into final destination...", flush=True)
    with open(dest, "wb") as out_f:
        for p in part_files:
            with open(p, "rb") as in_f:
                out_f.write(in_f.read())
            os.remove(p)

    elapsed = time.time() - t0
    print(f"SUCCESS: Downloaded {os.path.getsize(dest) // (1024*1024)} MB in {elapsed:.2f}s! ({total_size / (1024*1024*elapsed):.2f} MB/s)", flush=True)


if __name__ == "__main__":
    fast_download(URL, DEST, num_threads=8)
