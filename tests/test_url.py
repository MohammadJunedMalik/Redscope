#it's a test to check the url
import pytest
from redscope.urls import normalize, res_url, take_origin

#this  one url checked by normalize function i created in urls.py
def test_norm():
    assert normalize("http://example.com:80/about/") == "http://example.com/about"
    assert normalize("https://example.com:443/docs/") == "https://example.com/docs"
    assert normalize("http://example.com:8080/api/") == "http://example.com:8080/api"

#this one also check url by res_url function i created in urls.py
def test_res():
    base = "http://example.com/sub/index.html"
    assert res_url(base, "/contact") == "http://example.com/contact"
    assert res_url(base, "details") == "http://example.com/sub/details"
    assert res_url(base, "javascript:void(0)") == ""
    assert res_url(base, "mailto:admin@example.com") == ""

#again this one also check url by take_origin i have created in urls.py 
def test_take_Or():
    assert take_origin("http://example.com/path?query=1") == "http://example.com"
    assert take_origin("https://api.example.com:8443/v1") == "https://api.example.com:8443"
    assert take_origin("") == ""

