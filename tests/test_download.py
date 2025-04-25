from Param.Download import parse, download_file

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
 