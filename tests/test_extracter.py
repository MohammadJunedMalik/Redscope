from redscope.extracter import Extracterpage, extract_page

def test_extract_all():
    page = extract_page("", "https://example.com")
    assert page.url == "https://example.com"
    assert len(page.links) == 0
    assert len(page.scripts) == 0

def test_resources():
    html = """
<html>
<title> just testing </title>
<body>
<a href="/about">About</a>
<a href="javascript:alert(1)">Javascript</a>
<script src="/bundle.js"></script>
<link rel="stylesheet" href="/theme.css">
<link rel="icon" href="/icon.png">
<form action="/submit" method="POST"></form>
</html>
"""
    page = extract_page(html, "https://example.com")
    assert "https://example.com/about" in page.links
    assert len(page.links) == 1
    assert "https://example.com/bundle.js" in page.scripts
    assert "https://example.com/theme.css" in page.stylesheets
    assert "/icon.png" not in page.stylesheets
    assert "https://example.com/submit" in page.forms



