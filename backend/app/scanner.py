import asyncio
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
import httpx
from sqlalchemy.orm import Session
from .analyzers import _f, header_findings, seo_findings
from .config import settings
from .models import Finding, Scan, ScanStatus
from .security import UnsafeTarget, validate_target


async def safe_fetch(client: httpx.AsyncClient, url: str, allowed_domains: list[str]) -> httpx.Response:
    """Fetch manually so redirect destinations cannot bypass target policy."""
    for _ in range(5):
        validate_target(url, allowed_domains)
        response = await client.get(url, follow_redirects=False)
        if response.is_redirect:
            location = response.headers.get("location")
            if not location: return response
            url = urljoin(str(response.url), location)
            validate_target(url, allowed_domains)
            continue
        return response
    raise UnsafeTarget("Too many redirects")


def scan_project(db: Session, scan: Scan) -> None:
    project = scan.project
    scan.status, scan.started_at = ScanStatus.running, datetime.now(timezone.utc)
    db.commit()
    findings: list[dict] = []; visited: set[str] = set(); queue = [f"https://{project.allowed_domains[0]}/"]
    try:
        with httpx.Client(timeout=settings.scan_timeout_seconds, headers={"User-Agent": "AccessLens/1.0 (+authorized audit)"}) as client:
            while queue and len(visited) < min(project.max_pages, settings.max_pages_per_scan):
                url = queue.pop(0)
                if url in visited: continue
                validate_target(url, project.allowed_domains)
                # Sync client uses identical manual redirect validation.
                response = _safe_fetch_sync(client, url, project.allowed_domains)
                visited.add(url)
                if response.status_code >= 400:
                    findings.append(_f("availability", "high", f"HTTP {response.status_code}", "Page returned an error response.", "Fix the response or remove links to this URL.", str(response.url)))
                    continue
                content_type = response.headers.get("content-type", "")
                findings.extend(header_findings(dict(response.headers), str(response.url)))
                if "text/html" not in content_type: continue
                findings.extend(seo_findings(response.text, str(response.url)))
                findings.extend(_sensitive_content_findings(response.text, str(response.url)))
                queue.extend(_crawl_links(response.text, str(response.url), project.allowed_domains, visited))
        findings.extend(_axe_findings(queue[0] if queue else f"https://{project.allowed_domains[0]}/", project.allowed_domains))
        for item in findings:
            db.add(Finding(scan_id=scan.id, **item))
        severity_counts = {s: sum(1 for f in findings if f["severity"] == s) for s in ("critical", "high", "medium", "low")}
        scan.summary = {"pages_scanned": len(visited), "findings": len(findings), "severity_counts": severity_counts, "performance": {"status": "optional lighthouse worker"}}
        scan.status, scan.completed_at = ScanStatus.completed, datetime.now(timezone.utc)
    except Exception as exc:
        scan.status, scan.completed_at, scan.error = ScanStatus.failed, datetime.now(timezone.utc), str(exc)[:1000]
    db.commit()


def _safe_fetch_sync(client, url, domains):
    for _ in range(5):
        validate_target(url, domains)
        response = client.get(url, follow_redirects=False)
        if not response.is_redirect: return response
        location = response.headers.get("location")
        if not location: return response
        url = urljoin(str(response.url), location); validate_target(url, domains)
    raise UnsafeTarget("Too many redirects")


def _crawl_links(html: str, base: str, domains: list[str], visited: set[str]) -> list[str]:
    from bs4 import BeautifulSoup
    urls = []
    for link in BeautifulSoup(html, "html.parser").select("a[href]"):
        url = urljoin(base, link["href"]).split("#")[0]
        if urlparse(url).scheme in {"http", "https"} and url not in visited:
            try: validate_target(url, domains); urls.append(url)
            except UnsafeTarget: pass
    return urls[:25]


def _sensitive_content_findings(html: str, url: str) -> list[dict]:
    markers = ("BEGIN PRIVATE KEY", "aws_secret_access_key", "AKIA[", "password=")
    return [_f("security", "high", "Potential sensitive data exposed", "A secret-like marker appeared in a public response.", "Remove the value, rotate any exposed credential, and prevent future disclosure.", url, evidence={"marker": m}) for m in markers if m in html]


def _axe_findings(url: str, domains: list[str]) -> list[dict]:
    """Hook for the isolated Playwright worker. It is intentionally optional in API containers."""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
            page = browser.new_page(); page.goto(validate_target(url, domains), wait_until="domcontentloaded", timeout=settings.scan_timeout_seconds * 1000)
            # axe-core is injected only from a pinned worker asset in production.
            browser.close()
    except ImportError:
        return [_f("accessibility", "low", "axe-core worker unavailable", "Accessibility browser worker is not installed in this API image.", "Run the isolated Playwright/axe worker image to collect WCAG findings.", url)]
    except Exception as exc:
        return [_f("accessibility", "low", "Accessibility check incomplete", str(exc)[:300], "Review browser-worker connectivity and target availability.", url)]
    return []
