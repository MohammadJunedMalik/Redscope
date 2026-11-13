from dataclasses import dataclass, field
from bs4 import BeautifulSoup
from redscope.urls import res_url 

# this one is bucket to hold the page url and 4 sets (link, scripts, stylesheets, forms)
@dataclass
class Extracterpage:
    url: str = ""
    # by writing field(default_factory=set) it will create an new set everytime this class when called
    links: set[str] = field(default_factory=set)
    scripts: set[str] = field(default_factory=set)
    stylesheets: set[str] = field(default_factory=set)
    forms: set[str] = field(default_factory=set)

# this one parses raw htnl into categorized and normalized urls . 
def extract_page(html: str, base_url: str):
    page = Extracterpage(url = base_url)
    if not html:
        return page
    parse = BeautifulSoup(html, "html.parser")
    for h in parse.find_all("a"):
        href = h.get("href")
        if not href:
            continue
        href = href.strip()
        if href.startswith(("javascript:","mailto:","tel:")):
            continue
        res = res_url(base_url, href) # it's to convert relative links/urls to absolute
        if res:
            page.links.add(res)
    for s in parse.find_all("script"):
        src = s.get("src")
        if src:
            src = src.strip()
            res = res_url(base_url, src)
            page.scripts.add(res)

    for l in parse.find_all("link"):
        rel = l.get("rel", [])
        if  "stylesheet" in rel:
            href = l.get("href")
            if href:
                href = href.strip()
                res = res_url(base_url, href)
                if res:
                    page.stylesheets.add(res)

    for f in parse.find_all("form"):
        action = f.get("action")
        res =res_url(base_url, action or "")
        if res:
            page.forms.add(res)
    
    return page








