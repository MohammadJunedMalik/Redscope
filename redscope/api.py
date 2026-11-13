from dataclasses import dataclass, field

@dataclass
class Apioperation:
    path: str
    method: str 
    summary: str = ""
    parameters: list[str] = field(default_factory=list)
    auth_required: bool = False

@dataclass
class ApiSpec:
    title: str = ""
    version: str = ""
    base_url: str = ""
    operations: list[Apioperation] = field(default_factory=list)



def parse_api(data: dict )-> ApiSpec:
    base_url = ""
    servers = data.get("servers", [])
    if servers:
        base_url = servers[0].get("url", "")
    else:
        if data.get("basePath", ""): 
            base_url = data.get("basePath", "")

    operation = []
    info = data.get("info", {})
    title = info.get("title", "")
    version = info.get("version", "")
    for p, p_item in data.get("paths", {}).items():
        for method, details in p_item.items():
            http_method = {"get", "post", "put", "delete", "patch", "options", "head"}
            if method.lower() not in http_method:
                continue
            summary = details.get("summary", "")  
            opr = Apioperation(path=p, method=method.upper(), summary=summary)
            operation.append(opr)
    return ApiSpec(title = title, version = version, base_url = base_url, operations = operation)



