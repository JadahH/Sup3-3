import argparse
import os
import threading
import time
from urllib.parse import urlparse
import requests

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

