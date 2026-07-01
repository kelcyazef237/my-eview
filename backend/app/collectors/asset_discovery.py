"""Certificate Transparency asset discovery via crt.sh."""

import httpx

from app.collectors.base import get_bound_httpx_client, with_retry


async def discover(domain: str) -> dict:
    """Return discovered subdomains from crt.sh for a domain."""

    async def _run() -> dict:
        url = f"https://crt.sh/?q=%25.{domain}&output=json"
        async with get_bound_httpx_client(timeout=30, follow_redirects=True) as client:
            r = await client.get(url, headers={"User-Agent": "MYEVIEW/0.1"})
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

        return {
            "domain": domain,
            "discovered_assets": sorted(assets),
            "count": len(assets),
        }

    result, attempts, error = await with_retry(_run)
    if result is None:
        result = {
            "domain": domain,
            "error": f"{type(error).__name__}: {error}" if error else "unknown failure",
        }
    result["attempts"] = attempts
    return result
