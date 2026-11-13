# unlike my previous project i have created this as an central safety where there is default limits to pages , depth and timeout  
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class ScanConfig:
    max_depth: int = 2
    max_pages: int = 50
    request_timeout: int = 5
    request_delay : float = 0.1 
    usr_agnt: str = ("RedScope(+https://github.com/authorized-security-assessment)")
    max_response_size: int = 1024*1024


b_drctry = Path(__file__).resolve().parent.parent
instance_drctry = b_drctry / "instance"
db_path = instance_drctry / "redscope.db"
report_drctry = b_drctry / "reports"

