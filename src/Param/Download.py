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

def download_sequential():
    pass