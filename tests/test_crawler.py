import pytest
from unittest.mock import patch
from redscope.crawler import Crawl, crawl
from redscope.config import ScanConfig
from redscope.fetch import fetchresult, fetch

def test_invalid_target():
    res = crawl("ftp://not-allowed.com") or crawl("")
    assert len(res.errors) > 0
    assert res.pages_crawled == 0
    assert len(res.visited_urls) == 0

def test_max_pages(monkeypatch):
    scan = ScanConfig(max_pages=1, request_delay=0)
    res = crawl("http://example.com", scan)
    assert res.pages_crawled == 1


def fake_fetch(url, config=None):
    if url == "http://example.com/":
        
        return fetchresult(url=url, status_code=200, content_type="text/html", text="""<a href="/page1">link</a>
    <a href="http://evil-external.com">external</a>
    <script src="/app.js"></script>""")
    elif url == "http://example.com/page1":
        return fetchresult(url=url, status_code=200, content_type="text/html", text="<a href='/page2'>page2</a>")
    else:
        return fetchresult(url=url, status_code=404)


    
def test_bfs_scope(monkeypatch):
    monkey_patch = monkeypatch.setattr("redscope.crawler.fetch", fake_fetch)
    scan = ScanConfig(max_depth=1, request_delay=0)
    res = crawl("http://example.com", scan)
    assert res.pages_crawled == 2
    assert "http://evil-external.com/" in res.all_links 
    assert "http://example.com/app.js" in res.all_scripts 
    assert "http://evil-external.com" not in res.visited_urls



