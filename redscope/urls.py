# this ones is created to remove the url inconsistency and duplication also turn relative links to absolute links and resolves standard prorts 80 & 443
from urllib.parse import urljoin, urlparse, urlunparse

def normalize(url: str) -> str:
    if not url:
        return ""

    url = url.strip()
    parse = urlparse(url)
    scheme = parse.scheme.lower()
    netloc = parse.netloc.lower()

    if scheme == "http" and netloc.endswith(":80"):
        netloc = netloc[:-3]

    elif scheme == "https" and netloc.endswith(":443"):
        netloc = netloc[:-4]

    path = parse.path
    if not path:
        path = "/"
    elif len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")

    normal = urlunparse((scheme, netloc, path, parse.params, parse.query, ""))

    return normal

def res_url(base_url: str, link: str) -> str:
    if not link:
        return ""
    link = link.strip()
    l_link = link.lower()
    if l_link.startswith("javascript:") or l_link.startswith("mailto:") or l_link.startswith("tel:") or l_link.startswith("data:"):
        return ""
    abs_url = urljoin(base_url, link)
    return normalize(abs_url)


def take_origin(url: str) -> str:
    if not url:
        return ""
    n_url = normalize(url) 
    parse = urlparse(n_url)
    scheme = parse.scheme
    if not scheme:
        return "" 
    netloc = parse.netloc
    if not netloc :
        return ""
    return f"{parse.scheme}://{parse.netloc}"

    

