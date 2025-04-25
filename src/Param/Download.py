import argparse
import os
import threading
import time
from urllib.parse import urlparse
import requests

"""
    Parse command-line arguments and return a list of URLs.
"""

def parse(arvg=None):
   parser = argparse.ArgumentParser(
        description="Download one or more files by URL, each on its own thread."
    )
   parser.add_argument(
        "urls",
        metavar="URL",
        nargs='+',
        help="HTTP(S) URL of the file to download",
    )
   return parser.parse(argv).urls

"""
    Download a single file from the given URL and save it into output_dir.
    Returns the path to the saved file.
"""

def download_file(url, output_dir='.'):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    # Derive a filename from the URL; fallback to 'download' if none
    path = urlparse(url).path
    filename = os.path.basename(path) or 'download'
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return filepath

"""
    Download each URL in the list one after the other (sequentially).
    Returns a list of saved file paths.
"""

def download_sequential(urls, output_dir='.'):
     saved = []
     for url in urls:
         saved.append(download_file(url, output_dir))
         return saved        
     
"""
    Download all URLs in the list concurrently, each in its own thread.
    Returns a list of saved file paths (order may vary).
"""

def download_multithread(urls, output_dir='.'):
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