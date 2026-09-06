from __future__ import annotations
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

class ComplianceBlocked(RuntimeError): pass

def assert_robots_allowed(url: str, user_agent: str, timeout: int = 10) -> None:
    parsed=urlparse(url)
    robots=f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp=RobotFileParser()
    rp.set_url(robots)
    try: rp.read()
    except Exception as exc: raise ComplianceBlocked(f"Cannot verify robots.txt for {parsed.netloc}: {exc}") from exc
    if not rp.can_fetch(user_agent, url):
        raise ComplianceBlocked(f"robots.txt disallows this user agent for {url}")
