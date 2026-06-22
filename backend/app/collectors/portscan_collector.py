"""Gated verified-tier light port-scan collector (TCP connect + banner read only)."""

import asyncio
import socket
from typing import Any

from app.collectors.base import _source_address_tuple
from app.config import get_settings
from app.constants import LEGACY_PORTS

settings = get_settings()


def _normalize_banner(data: bytes) -> str:
    try:
        return data.decode("utf-8", errors="replace").strip().replace("\n", " ").replace("\r", "")
    except Exception:
        return ""


async def _probe_port(host: str, port: int, timeout: float = 5.0) -> dict[str, Any]:
    source = _source_address_tuple()
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(
                host,
                port,
                local_addr=source if source else None,
            ),
            timeout=timeout,
        )
        banner = ""
        try:
            data = await asyncio.wait_for(reader.read(256), timeout=2.0)
            banner = _normalize_banner(data)
        except asyncio.TimeoutError:
            pass
        writer.close()
        await writer.wait_closed()
        return {
            "port": port,
            "service": LEGACY_PORTS.get(port, "unknown"),
            "reachable": True,
            "banner": banner,
        }
    except (OSError, asyncio.TimeoutError):
        return {
            "port": port,
            "service": LEGACY_PORTS.get(port, "unknown"),
            "reachable": False,
            "banner": "",
        }


async def collect(host: str) -> dict:
    """Run TCP-connect probes on curated legacy ports."""
    results = await asyncio.gather(*[_probe_port(host, port) for port in LEGACY_PORTS])
    exposed = [r for r in results if r["reachable"]]
    plaintext = [r for r in exposed if r["service"] in ("ftp", "telnet")]
    return {
        "host": host,
        "results": results,
        "exposed_count": len(exposed),
        "plaintext_count": len(plaintext),
        "exposed_ports": [r["port"] for r in exposed],
    }
