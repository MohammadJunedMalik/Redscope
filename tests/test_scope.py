# so this test is to check the scope.py file and it's functions i have created
import pytest
from redscope.scope import same_origin, in_scope, valid_target

# so this one is for same_origin function
def test_s_o():
    assert same_origin("http://example.com/a", "http://example.com/b/c") is True
    assert same_origin("http://example.com:8080", "http://example.com:8081") is False
    assert same_origin("http://example.com", "https://example.com") is False

#, this one for in_scope function
def test_in_s():
    target = "https://example.com"
    assert in_scope(target, "https://example.com/api/users") is True
    assert in_scope(target, "https://other.com/api/users") is False
    assert in_scope(target, "ftp://example.com/file") is False

#and this one for valid_target function
def test_vt():
    ok, origin =valid_target("https://example.com")
    assert ok is True
    assert origin == "https://example.com"
    ok, error = valid_target("")
    assert origin == "https://example.com"
    ok, error = valid_target("ftp://example.com")
    assert ok is False

    


