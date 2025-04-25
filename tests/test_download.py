import downloader

from Param.Download import parse, download_file, download_sequential, download_multithread, main

class MockResponse:
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

    def parse_single_test():
        urls = parse(["https://example.com/file.txt"])
        assert urls == ["https://example.com/file.txt"]
        
    def parse_multiple_test(): 
        inputs = [
        "https://foo.com/a.png",
        "https://bar.org/b.jpg",
        "http://baz.net/c.zip"
    ]
        assert parse(inputs) == inputs

    def test_download_file(tmp_path, monkeypatch):
    # Prepare a dummy response with known content
        dummy = DummyResponse(b"hello world")
        monkeypatch.setattr(downloader.requests, "get", lambda url, stream=True: dummy)
        out = download_file("https://example.com/f.txt", output_dir=str(tmp_path))
        assert os.path.exists(out)
        with open(out, "rb") as f:
            data = f.read()
        assert data == b"hello world"

    def test_download_sequential(monkeypatch):
        calls = []
        def fake_download(url, output_dir="."):
            calls.append(url)
            return f"/tmp/{os.path.basename(url)}"

        monkeypatch.setattr(downloader, "download_file", fake_download)

        urls = ["u1", "u2", "u3"]
        saved = download_sequential(urls, output_dir="/out")
        assert saved == ["/tmp/u1", "/tmp/u2", "/tmp/u3"]
        assert calls == urls  # sequential order  
 
    def test_download_multithreaded(monkeypatch):
        calls = []
    def fake_download(url, output_dir="."):
        calls.append(url)
        return f"/tmp/{os.path.basename(url)}"
        monkeypatch.setattr(downloader, "download_file", fake_download)

    urls = ["uA", "uB", "uC", "uD"]
    saved = download_multithread(urls, output_dir="/out")
    assert set(calls) == set(urls)
    assert set(saved) == {"/tmp/uA", "/tmp/uB", "/tmp/uC", "/tmp/uD"}

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