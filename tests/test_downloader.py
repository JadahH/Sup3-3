import os
import pytest

import Param.downloader as downloader
from Param.downloader import (
    parse_args,
    download_file,
    download_sequential,
    download_multithreaded,
    main,
)


class DummyResponse:
    """A fake requests.Response for testing download_file."""
    def __init__(self, content: bytes, status_code: int = 200):
        self._content = content
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code != 200:
            raise IOError(f"HTTP {self.status_code}")

    def iter_content(self, chunk_size=1):
        # Yield all content in one go
        yield self._content


def test_parse_args_single_url():
    urls = parse_args(["https://example.com/file.txt"])
    assert urls == ["https://example.com/file.txt"]


def test_parse_args_multiple_urls():
    inputs = [
        "https://foo.com/a.png",
        "https://bar.org/b.jpg",
        "http://baz.net/c.zip"
    ]
    assert parse_args(inputs) == inputs


def test_download_file_writes_content(tmp_path, monkeypatch):
    fake = DummyResponse(b"hello world")
    monkeypatch.setattr(downloader.requests, "get", lambda url, stream=True: fake)

    out_path = download_file("https://example.com/f.txt", output_dir=str(tmp_path))
    assert os.path.isfile(out_path)
    with open(out_path, "rb") as f:
        assert f.read() == b"hello world"


def test_download_sequential(monkeypatch):
    calls = []
    def fake_download(url, output_dir="."):
        calls.append(url)
        return f"/tmp/{os.path.basename(url)}"

    monkeypatch.setattr(downloader, "download_file", fake_download)

    urls = ["u1", "u2", "u3"]
    saved = download_sequential(urls, output_dir="/out")

    assert saved == ["/tmp/u1", "/tmp/u2", "/tmp/u3"]
    assert calls == urls


def test_download_multithreaded(monkeypatch):
    calls = []
    def fake_download(url, output_dir="."):
        calls.append(url)
        return f"/tmp/{os.path.basename(url)}"

    monkeypatch.setattr(downloader, "download_file", fake_download)

    urls = ["uA", "uB", "uC", "uD"]
    saved = download_multithreaded(urls, output_dir="/out")

    assert set(calls) == set(urls)
    assert set(saved) == {f"/tmp/{u}" for u in urls}


def test_main_prints_timings(monkeypatch, capsys):
    monkeypatch.setattr(downloader, "parse_args", lambda: ["x1", "x2"])
    monkeypatch.setattr(downloader, "download_sequential", lambda urls: None)
    monkeypatch.setattr(downloader, "download_multithreaded", lambda urls: None)

    times = iter([10.0, 13.0, 20.0, 23.5])
    monkeypatch.setattr(downloader.time, "time", lambda: next(times))

    main()
    captured = capsys.readouterr()
    out = captured.out.strip().splitlines()

    assert out[0] == "Sequential download took 3.00 seconds"
    assert out[1] == "Multithreaded download took 3.50 seconds"