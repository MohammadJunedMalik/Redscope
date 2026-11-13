from redscope.evidence import Evidence, explain_confidence, evi_from_page
from redscope.extracter import Extracterpage
import pytest
def test_evi():
    evi = Evidence("http://example.com/target")
    assert evi.target_url 
    assert evi.source_url == "" 
    assert evi.discovery_method == "href"
    assert evi.details == {} 


def test_explain_confi():
    assert "confirm" in explain_confidence("observed")
    assert "reference" in explain_confidence("referenced")
    assert "deduced" in explain_confidence("inferred")
    assert "unknown" in explain_confidence("fake")

def test_evi_page():
    page = Extracterpage( url="http://example.com",
                        links={"http://example.com/page1"},
                        scripts={"http://example.com/app.js"},
                        stylesheets={"http://example.com/theme.css"},
                        forms={"http://example.com/contact"},
                        )
    rec = evi_from_page("http://example.com", page)
    method = {item.discovery_method for item in rec}
    assert len(rec)==4
    assert all(item.source_url == "http://example.com" for item in rec)
    assert "script" in method
    assert "form" in method



