from unittest.mock import MagicMock
from redscope.api import Apioperation, ApiSpec, parse_api
def test_parse_api():
    dic = {"info" : {"title" : "Shop API", "version" : "1.0.0" }, "servers" : [{"url" : "https://api.example.com"}], "paths" : {"/items" : { "get" : {"summary" : "List items"}, "post" : {"summary" : "Create item"}}}}
    parse = parse_api(dic)
    assert parse.title == "Shop API"
    assert parse.version == "1.0.0"
    assert parse.base_url == "https://api.example.com"
    assert len(parse.operations) == 2
    op_1 = parse.operations[0]
    op_2 = parse.operations[1]
    assert op_1.path == "/items"
    assert op_1.method == "GET"
    assert op_1.summary == "List items"
    assert op_2.path == "/items"
    assert op_2.method == "POST"
    assert op_2.summary == "Create item" 

   

def test_parse_basepath():
    dic = {"info" : {"title" : "Shop Api", "version" : "1.0.0"}, "basePath" : "/api/v2", "paths" : {"/status" : { "get" : {"summary" : "List items"}}}}
    parse = parse_api(dic)
    assert parse.base_url == "/api/v2"
    assert len(parse.operations) == 1
    op_1 = parse.operations[0]
    assert op_1.path == "/status"
    assert op_1.method == "GET"


def test_non_http():
    dic = {"info" : {"title" : "Shop Api", "version" : "1.0.0"}, "paths" : {"/users" : {"get" : {"summary" : "Get users"}, "parameter" : ["filter"]}}}
    parse = parse_api(dic)
    assert len(parse.operations) == 1
    op_1 = parse.operations[0]
    assert op_1.path == "/users"
    assert op_1.method == "GET"


