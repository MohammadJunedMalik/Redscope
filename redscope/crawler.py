# don't get confused here by seeing these much imports 
from collections import deque
from dataclasses import dataclass, field
import time
from typing import Optional, List, Set, Dict
from redscope.config import ScanConfig
from redscope.urls import normalize
from redscope.scope import in_scope, valid_target
from redscope.fetch import fetchresult, fetch
from redscope.extracter import extract_page

#scan  report tracking pages , crawled counts, visited urls discovered sets(links, scripts, forms, stylesheets) and captured errors
@dataclass
class Crawl:
    target_url: str = ""
    pages_crawled: int = 0
    visited_urls: set[str] = field(default_factory=set)
    all_links: set[str] = field(default_factory=set)
    all_scripts: set[str] = field(default_factory=set)
    all_stylesheets: set[str] = field(default_factory=set)
    all_forms: set[str] = field(default_factory=set)
    errors: set[str] = field(default_factory=set)

# it's main hub that coordinates discovery
def crawl(target_url: str, config: Optional[ScanConfig] = None) -> Crawl :
    if config is None:
        config = ScanConfig()
    result = Crawl(target_url=target_url)
    ok, origin = valid_target(target_url)
    if not ok : 
        result.errors.add(origin)
        return result
    
    start_url = normalize(target_url)
    deq = deque([(start_url, 0)])
    while deq:
        if result.pages_crawled >= config.max_pages:
            break
        current_url, current_depth = deq.popleft()
        if current_url in result.visited_urls:
            continue
        result.visited_urls.add(current_url)
        if config.request_delay > 0:
            time.sleep(config.request_delay)
        res = fetch(current_url, config)
        result.pages_crawled += 1
        if res.error:
            result.errors.add(res.error)
        
        if "text/html" in res.content_type and res.text:
            page = extract_page(res.text, current_url)
            result.all_links.update(page.links)
            result.all_scripts.update(page.scripts)
            result.all_stylesheets.update(page.stylesheets)
            result.all_forms.update(page.forms)

            if current_depth < config.max_depth:
                for e in page.links:
                    if in_scope(origin, e) and e not in result.visited_urls:
                        deq.append((e, current_depth+1))
    return result 






