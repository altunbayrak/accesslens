from bs4 import BeautifulSoup

HEADERS = {
    "strict-transport-security": ("high", "Missing HSTS", "Enable Strict-Transport-Security on HTTPS responses."),
    "content-security-policy": ("medium", "Missing Content-Security-Policy", "Define a restrictive Content-Security-Policy."),
    "x-content-type-options": ("low", "Missing X-Content-Type-Options", "Set X-Content-Type-Options: nosniff."),
    "x-frame-options": ("medium", "Missing clickjacking protection", "Set X-Frame-Options or CSP frame-ancestors."),
    "referrer-policy": ("low", "Missing Referrer-Policy", "Set an explicit Referrer-Policy."),
}


def seo_findings(html: str, url: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser"); findings = []
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    if not title:
        findings.append(_f("seo", "high", "Missing page title", "No <title> element found.", "Add a unique, descriptive title under roughly 60 characters.", url))
    elif len(title) > 60:
        findings.append(_f("seo", "low", "Title may be too long", f"Title is {len(title)} characters.", "Keep the title concise and unique.", url))
    description = soup.select_one('meta[name="description"]')
    if not description or not description.get("content", "").strip():
        findings.append(_f("seo", "medium", "Missing meta description", "No usable meta description found.", "Add a clear 120–160 character description.", url))
    if not soup.select_one('link[rel="canonical"]'):
        findings.append(_f("seo", "low", "Missing canonical URL", "No canonical link found.", "Add a canonical URL where duplicate URLs are possible.", url))
    return findings


def header_findings(headers: dict, url: str) -> list[dict]:
    lowered = {k.lower(): v for k, v in headers.items()}; out = []
    for key, (severity, title, remediation) in HEADERS.items():
        if key not in lowered: out.append(_f("security", severity, title, f"Response does not include {key}.", remediation, url))
    return out


def _f(category, severity, title, detail, remediation, url, selector=None, evidence=None):
    return {"category": category, "severity": severity, "title": title, "detail": detail, "remediation": remediation, "url": url, "selector": selector, "evidence": evidence or {}}
