"""HTTP collector for security headers, HTTPS enforcement, admin paths, tech banners, SRI."""

import asyncio
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from app.collectors.base import get_bound_httpx_client, with_retry
from app.config import get_settings
from app.constants import ADMIN_PATHS, CRITICAL_SECURITY_HEADERS

settings = get_settings()


def _external_resources_with_integrity(soup: BeautifulSoup, base_url: str) -> dict:
    parsed_base = urlparse(base_url)
    base_host = parsed_base.hostname or ""

    scripts = soup.find_all("script", src=True)
    links = soup.find_all("link", href=True)

    external = []
    for tag in list(scripts) + list(links):
        src = tag.get("src") or tag.get("href")
        if not src:
            continue
        full = urljoin(base_url, src)
        host = urlparse(full).hostname or ""
        if host and host.lower() != base_host.lower():
            external.append({
                "tag": tag.name,
                "url": full,
                "integrity": tag.get("integrity"),
                "has_integrity": bool(tag.get("integrity")),
            })

    total = len(external)
    with_integrity = sum(1 for e in external if e["has_integrity"])
    return {
        "total_external": total,
        "with_integrity": with_integrity,
        "resources": external,
    }


def _tech_from_headers(headers: dict) -> dict:
    return {
        "server": headers.get("server"),
        "x_powered_by": headers.get("x-powered-by"),
        "x_generator": headers.get("x-generator"),
    }


def _tech_from_html(soup: BeautifulSoup) -> dict:
    generators = []
    for meta in soup.find_all("meta", attrs={"name": "generator"}):
        content = meta.get("content")
        if content:
            generators.append(content)
    return {"generator_meta": generators}


async def _probe_admin_path(client: httpx.AsyncClient, base_url: str, path: str) -> dict:
    url = urljoin(base_url, path)
    try:
        r = await client.head(url, follow_redirects=True, timeout=10)
        return {
            "path": path,
            "url": str(r.url),
            "status_code": r.status_code,
            "exposed": r.status_code in (200, 201, 204, 301, 302, 307, 308, 401, 403, 405),
        }
    except httpx.HTTPError:
        return {"path": path, "url": url, "status_code": None, "exposed": False}


async def _collect_root(url: str) -> dict:
    async with get_bound_httpx_client(follow_redirects=True, timeout=15) as client:
        r = await client.get(url, headers={"User-Agent": "MYEVIEW/0.1 (external-trust-intelligence)"})
        headers = {k.lower(): v for k, v in r.headers.items()}
        body = r.text
        soup = BeautifulSoup(body, "html.parser")
        return {
            "url": str(r.url),
            "status_code": r.status_code,
            "headers": headers,
            "tech_headers": _tech_from_headers(headers),
            "tech_html": _tech_from_html(soup),
            "sri": _external_resources_with_integrity(soup, str(r.url)),
            "title": soup.title.string.strip() if soup.title else None,
        }


async def _collect_redirects(domain: str) -> dict:
    async with get_bound_httpx_client(follow_redirects=True, timeout=15) as client:
        http_url = f"http://{domain}/"
        https_url = f"https://{domain}/"
        result = {}
        for url in (http_url, https_url):
            try:
                r = await client.head(url, headers={"User-Agent": "MYEVIEW/0.1"}, follow_redirects=True)
                result[url.split("://")[0]] = {
                    "reachable": True,
                    "final_url": str(r.url),
                    "status_code": r.status_code,
                    "is_https_final": str(r.url).startswith("https://"),
                    "hsts_present": "strict-transport-security" in {k.lower(): v for k, v in r.headers.items()},
                }
            except httpx.HTTPError as exc:
                result[url.split("://")[0]] = {"reachable": False, "error": str(exc)}
        return result


async def _collect_admin_paths(domain: str) -> list[dict]:
    base = f"https://{domain}"
    async with get_bound_httpx_client(follow_redirects=True, timeout=10) as client:
        tasks = [_probe_admin_path(client, base, p) for p in ADMIN_PATHS]
        return list(await asyncio.gather(*tasks, return_exceptions=True))


async def collect(domain: str) -> dict:
    async def _run() -> dict:
        https_root = await _collect_root(f"https://{domain}/")
        redirects = await _collect_redirects(domain)
        admin_paths = await _collect_admin_paths(domain)
        return {
            "domain": domain,
            "https_root": https_root,
            "redirects": redirects,
            "admin_paths": admin_paths,
        }

    result, attempts, error = await with_retry(_run)
    if result is None:
        result = {"domain": domain, "error": str(error)}
    result["attempts"] = attempts
    return result
