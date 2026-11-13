import requests
from redscope.fetch import fetch, fetchresult
from unittest.mock import MagicMock, patch
from redscope.config import ScanConfig

def test_fetch():
    res = fetch("http://domain-does-not-exist-xyz987654.invalid")
    assert res.status_code == 0
    assert res.error != ""


def test_fetch_mock():
    res_mock = MagicMock()
    res_mock.status_code = 200
    res_mock.headers = {"Content-Type" : "text/html; charset = utf-8"}
    res_mock.is_redirect = False
    res_mock.encoding = "utf-8"
    res_mock.iter_content.return_value = [b"<html>hello redscope</html>"]
    with patch("requests.get", return_value=res_mock):
        res = fetch("http://example.com/page")
        assert res.status_code == 200
        assert res.content_type == "text/html"
        assert "hello redscope" in res.text
        assert res.is_rdrct is False
        assert res.error == ""

        
def test_fetch_rdrct():
    res_mock = MagicMock()
    res_mock.status_code = 301
    res_mock.is_redirect = True
    res_mock.headers = {"Location" : "/dashboard"}
    res_mock.iter_content.return_value = []
    with patch("requests.get", return_value = res_mock):
        res = fetch("http://example.com")
        assert res.is_rdrct is True
        assert res.rdrct_url == "http://example.com/dashboard"



def test_fetch_timeout():
    with patch("requests.get", side_effect = requests.exceptions.Timeout("Time out")):
        res = fetch("http://example.com/slow")
        assert res.status_code == 0
        assert "timeout" in res.error.lower()

def test_fetch_size():
    res_mock = MagicMock()
    res_mock.status_code = 200 
    res_mock.headers = {"Content-Type" : "text/plain"}
    res_mock.is_redirect = False
    res_mock.encoding = "utf-8"
    res_mock.iter_content.return_value = [b"A"*50, b"B"*50, b"C"*50]
    scan = ScanConfig(max_response_size = 100)
    with patch("requests.get", return_value = res_mock):
        res = fetch("http://example.com/huge", config = scan)
        assert len(res.text) == 100
        assert "C" not in res.text 



