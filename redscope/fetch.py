# this one seems complicated even after finishing the code of this file even i got confused in few lines so i'm gonna explain in brief here or if you don't still understand just give the code to the ai bro or even after that u still don't understand then contact me through gmail i will make sure to reply to u as soon as possible , so let's surpass our limits:- 
from dataclasses import dataclass, field 
from typing import Dict, Optional
import time
import requests
from redscope.config import ScanConfig
from redscope.urls import res_url

# here it's like an structured scoreboard, whenever we send the reequest to url, what we want a clean report containing did it succeed?, at what status code, at what headers ? .....etc...etc
@dataclass
class fetchresult:
    url: str
    status_code: int = 0
    hdrs: Dict[str, str] = field(default_factory=dict)
    content_type: str = ""
    text: str = ""
    is_rdrct: bool = False
    rdrct_url: str = ""
    elapsed_ms: float = 0.0
    error: str = ""

#from here if there's no settings r given so here we have created our own default scan with safety limits (5 sec. timeout...etc)
def fetch(url: str, config: Optional[ScanConfig]  = None) -> fetchresult:
    if config is None:
        config = ScanConfig()
    fr = fetchresult(url=url) # it creates an empty url
    req_hdrs = {"User-Agent": config.usr_agnt} # this one build the http header and identify my scanner
    start_t = time.time() # it's starts the  stopwatch
    # here in try block it sends an http request GET if the target bounce us to an exterlink it will not follow that blindfolded
    try:
        rq = requests.get(
                url,  headers = req_hdrs, timeout = config.request_timeout, allow_redirects = False, stream = True)
        fr.elapsed_ms = round((time.time() - start_t )* 1000, 2)  # here stopwatch stops and record it in milisec.
        fr.status_code = rq.status_code
        fr.hdrs = dict(rq.headers)
        fr.content_type = rq.headers.get("Content-Type", "").split(';')[0].strip().lower()
        # here in the location code we convert relative urls to absolute urls 
        if rq.is_redirect or rq.status_code in (301,302,303,307,308):
            fr.is_rdrct = True
            location = rq.headers.get("Location", "")
            if location:
                fr.rdrct_url = res_url(url, location)
        # alr so here if a malicious file is in mb's or in gb's we have set limit to 1mb and it reads per  8kb then track it in bytes then we break it if it hits 1mb and stop downloading
        chunks = []
        bytes_readed = 0 
        for i in rq.iter_content(chunk_size=8192):
            if not i:
                break
            chunks.append(i)
            bytes_readed += len(i)
            if bytes_readed >= config.max_response_size:
                break
        # here we merge chunks together , detect encoding and convert bytes into human readable form
        pure_bytes = b"".join(chunks)
        encode_bytes = rq.encoding or "utf-8"
        fr.text = pure_bytes.decode(encode_bytes, errors="replace")

    # here are i have build exception thay can happen , catches the errors and prints the error and elapsed time 
    except requests.exceptions.Timeout:
        fr.elapsed_ms = round((time.time() - start_t )* 1000, 2)
        fr.error = f"Requests hits the timeout after: {fr.elapsed_ms}"

    except requests.exceptions.RequestException as er:
        fr.elapsed_ms = round((time.time()- start_t)*1000, 2)
        fr.error = f"Request error has been occured after : {er}"

    except Exception as er:
        fr.elapsed_ms = round((time.time()- start_t)*1000, 2)
        fr.error = f"an unexpected/unknown error has been occured : {er}"

    return fr





