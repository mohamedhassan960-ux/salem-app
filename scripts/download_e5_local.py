"""
Direct model downloader for intfloat/multilingual-e5-small into local directory.
Avoids Windows symlink / lock stalling issues.
"""

import os
import sys
import time
import urllib.request

REPO = "intfloat/multilingual-e5-small"
BASE_URL = f"https://huggingface.co/{REPO}/resolve/main"
TARGET_DIR = r"C:\Users\moham\OneDrive\Apps\اوكسجين\data\models\multilingual-e5-small"

FILES = [
    "config.json",
    "modules.json",
    "sentence_bert_config.json",
    "config_sentence_transformers.json",
    "special_tokens_map.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "model.safetensors",
]


def download_file(filename: str):
    url = f"{BASE_URL}/{filename}"
    dest = os.path.join(TARGET_DIR, filename)

    if os.path.exists(dest) and os.path.getsize(dest) > 100:
        print(f"[SKIP] {filename} already exists ({os.path.getsize(dest) // 1024} KB).", flush=True)
        return

    print(f"[DOWNLOADING] {filename} from {url} ...", flush=True)
    t0 = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    try:
        with urllib.request.urlopen(req, timeout=60) as response, open(dest, "wb") as out_file:
            total_size = int(response.headers.get("Content-Length", 0))
            downloaded = 0
            chunk_size = 1024 * 1024  # 1MB chunks
            last_print = time.time()

            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                out_file.write(chunk)
                downloaded += len(chunk)
                if time.time() - last_print > 3.0:
                    pct = (downloaded / total_size * 100) if total_size > 0 else 0
                    print(f"  -> {filename}: {downloaded // (1024*1024)}MB / {total_size // (1024*1024)}MB ({pct:.1f}%)", flush=True)
                    last_print = time.time()

        elapsed = time.time() - t0
        print(f"[DONE] {filename} ({os.path.getsize(dest) // 1024} KB) in {elapsed:.2f}s.", flush=True)
    except Exception as e:
        if "404" in str(e):
            print(f"[OPTIONAL SKIP] {filename} not found on repo (404), skipping.", flush=True)
            if os.path.exists(dest):
                os.remove(dest)
        else:
            print(f"[ERROR] Failed to download {filename}: {e}", flush=True)
            if os.path.exists(dest):
                os.remove(dest)
            raise e


def main():
    os.makedirs(TARGET_DIR, exist_ok=True)
    print(f"Downloading {REPO} into {TARGET_DIR} ...", flush=True)
    for f in FILES:
        download_file(f)
    print("\nAll files downloaded successfully!", flush=True)


if __name__ == "__main__":
    main()
