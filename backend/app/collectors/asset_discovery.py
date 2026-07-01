"""Certificate Transparency asset discovery via crt.sh with a free
fallback source (hackertarget hostsearch) for when crt.sh 5xxs out.
"""

import httpx

from app.collectors.base import get_bound_httpx_client, with_retry


async def _discover_crtsh(domain: str) -> list[str]:
    """crt.sh certificate transparency lookup. The canonical source — more
    comprehensive than hackertarget, but historically flaky (502/504/timeout).
    """
    async with get_bound_httpx_client(timeout=30, follow_redirects=True) as client:
        r = await client.get(
            f"https://crt.sh/?q=%25.{domain}&output=json",
            headers={"User-Agent": "MYEVIEW/0.1"},
        )
        r.raise_for_status()
        data = r.json()

    assets = set()
    for entry in data:
        raw_names = entry.get("name_value", "")
        for name in raw_names.replace("\n", ",").split(","):
            name = name.strip().lower()
            name = name.removeprefix("*.")
            if name and name.endswith(f".{domain}") and name != domain:
                assets.add(name)
            elif name == domain:
                assets.add(name)
    return sorted(assets)


async def _discover_hackertarget(domain: str) -> list[str]:
    """hackertarget.com hostsearch — free, no API key, returns
    CT+DNS-derived subdomains. Used as a fallback when crt.sh is down.
    Format: one "host,ip" line per subdomain.
    """
    async with get_bound_httpx_client(timeout=30, follow_redirects=True) as client:
        r = await client.get(
            f"https://search.hackertarget.com/hostsearch/?q={domain}",
            headers={"User-Agent": "MYEVIEW/0.1"},
        )
        r.raise_for_status()
        text = r.text

    assets = set()
    for line in text.splitlines():
        host = line.strip().lower().split(",")[0]
        if host and host.endswith(f".{domain}") and host != domain:
            assets.add(host)
    return sorted(assets)


async def discover(domain: str) -> dict:
    """Return discovered subdomains for a domain.

    Tries crt.sh first (more comprehensive CT coverage). On a 5xx,
    timeout, or transport error from crt.sh, falls back to hackertarget
    so the asset_visibility vectors don't silently go NOT_OBSERVED.
    """

    async def _run() -> dict:
        try:
            assets = await _discover_crtsh(domain)
            return {
                "domain": domain,
                "discovered_assets": assets,
                "count": len(assets),
                "source": "crt.sh",
            }
        except (
            httpx.HTTPStatusError,
            httpx.TimeoutException,
            httpx.TransportError,
        ) as primary_exc:
            # crt.sh 5xx/timeout/connection-refused. Try the fallback
            # so we don't lose the whole asset_visibility category.
            try:
                assets = await _discover_hackertarget(domain)
                return {
                    "domain": domain,
                    "discovered_assets": assets,
                    "count": len(assets),
                    "source": "hackertarget",
                    "primary_error": (
                        f"{type(primary_exc).__name__}: {primary_exc}"
                    ),
                }
            except Exception:
                # Both failed. Re-raise the original crt.sh error so
                # the retry layer (and the diagnostic) see the right
                # root cause.
                raise primary_exc

    result, attempts, error = await with_retry(_run)
    if result is None:
        result = {
            "domain": domain,
            "error": f"{type(error).__name__}: {error}" if error else "unknown failure",
        }
    result["attempts"] = attempts
    return result
