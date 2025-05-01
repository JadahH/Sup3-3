import argparse
import os
import threading
import time
from urllib.parse import urlparse

import requests


def parse_args(argv=None):
    """
    Parse command-line arguments and return a list of URLs.
    """
    parser = argparse.ArgumentParser(
        description="Download one or more files by URL, each on its own thread."
    )
    parser.add_argument(
        "urls",
        metavar="URL",
        nargs="+",
        help="HTTP(S) URL of the file to download",
    )
    # NOTE: use parse_args, not parser.parse!
    return parser.parse_args(argv).urls


def download_file(url, output_dir="."):
    """
    Download a single file from the given URL and save it into output_dir.
    Returns the path to the saved file.
    """
    response = requests.get(url, stream=True)
    response.raise_for_status()

    path = urlparse(url).path
    filename = os.path.basename(path) or "download"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    return filepath


def download_sequential(urls, output_dir="."):
    """
    Download each URL in the list one after the other (sequentially).
    Returns a list of saved file paths.
    """
    saved = []
    for url in urls:
        saved.append(download_file(url, output_dir))
    return saved


def download_multithreaded(urls, output_dir="."):
    """
    Download all URLs in the list concurrently, each in its own thread.
    Returns a list of saved file paths (order may vary).
    """
    saved = []
    lock = threading.Lock()

    def worker(u):
        path = download_file(u, output_dir)
        with lock:
            saved.append(path)

    threads = []
    for url in urls:
        t = threading.Thread(target=worker, args=(url,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return saved


def main():
    urls = parse_args()

    start_seq = time.time()
    download_sequential(urls)
    seq_duration = time.time() - start_seq

    start_mt = time.time()
    download_multithreaded(urls)
    mt_duration = time.time() - start_mt

    print(f"Sequential download took {seq_duration:.2f} seconds")
    print(f"Multithreaded download took {mt_duration:.2f} seconds")


if __name__ == "__main__":
    main()