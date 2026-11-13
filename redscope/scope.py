# so here i am gonna explain here function by function
from redscope.urls import normalize, take_origin
from urllib.parse import urlparse

# here it checks scheme(btw http/https), host and port 
def same_origin(a_url: str, b_url: str) -> bool:
    a_take = take_origin(a_url)
    b_take = take_origin(b_url)
    if not a_take:
        return False
    if not b_take:
        return False
    return a_take == b_take 

# this one checks if a discovered link/url belongs to strictly inside the approved target origin
def in_scope(target_take: str, candidate_url: str) -> bool:
    n_c_url = normalize(candidate_url)
    parse = urlparse(n_c_url)
    scheme = parse.scheme
    if not scheme:
        return False
    netloc = parse.netloc
    if not netloc:
        return False

    if scheme not in ("http","https"):
        return False

    return same_origin(target_take, candidate_url)
#  and lastly it checks pre-flight for to validate the user-supplied target before sending any network traffic
def valid_target(url: str) -> tuple[bool, str]:
    if not url or not url.strip():
        return False, "Url must not be empty"
    n_url = normalize(url)
    parse = urlparse(n_url)
    scheme = parse.scheme
    if scheme not in ("http", "https"):
        return False, "scheme must be http or https"
    netloc = parse.netloc
    if not netloc:
        return False, "Target url must have an host/domain"

    return True, take_origin(n_url)





    


