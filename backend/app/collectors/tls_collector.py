"""TLS collector for TLS version strength and certificate health."""

import socket
import ssl
from datetime import datetime, timezone

from app.collectors.base import _source_address_tuple, with_retry
from app.config import get_settings

settings = get_settings()


_TLS_VERSION_ORDER = [
    ("TLSv1.3", ssl.TLSVersion.TLSv1_3),
    ("TLSv1.2", ssl.TLSVersion.TLSv1_2),
    ("TLSv1.1", ssl.TLSVersion.TLSv1_1),
    ("TLSv1.0", ssl.TLSVersion.TLSv1),
]


def _probe_tls_version(host: str, port: int, version: ssl.TLSVersion) -> bool:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.minimum_version = version
    ctx.maximum_version = version
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    source = _source_address_tuple()
    try:
        with socket.create_connection(
            (host, port),
            timeout=settings.collector_timeout_seconds,
            source_address=source,
        ) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as _:
                return True
    except (socket.timeout, ConnectionRefusedError, OSError, ssl.SSLError):
        return False


def _supported_tls_versions(host: str, port: int) -> list[str]:
    supported = []
    for name, version in _TLS_VERSION_ORDER:
        if _probe_tls_version(host, port, version):
            supported.append(name)
    return supported


def _handshake_info(host: str, port: int) -> dict:
    source = _source_address_tuple()
    ctx = ssl.create_default_context()
    with socket.create_connection(
        (host, port),
        timeout=settings.collector_timeout_seconds,
        source_address=source,
    ) as sock:
        with ctx.wrap_socket(sock, server_hostname=host) as ssock:
            version = ssock.version()
            cipher = ssock.cipher()
            cert = ssock.getpeercert()
            cert_binary = ssock.getpeercert(binary_form=True)
            chain = [cert.get("issuer") for cert in ssock._sslobj.get_unverified_chain()] if hasattr(ssock._sslobj, "get_unverified_chain") else []

            not_after = cert.get("notAfter")
            expires_at = None
            if not_after:
                expires_at = ssl.cert_time_to_seconds(not_after)

            return {
                "negotiated_version": version,
                "cipher": cipher,
                "subject": cert.get("subject"),
                "issuer": cert.get("issuer"),
                "not_after": not_after,
                "expires_at": datetime.fromtimestamp(expires_at, tz=timezone.utc).isoformat() if expires_at else None,
                "subject_alt_names": cert.get("subjectAltName"),
                "chain_issuers": chain,
                "cert_binary_present": bool(cert_binary),
            }


def _cert_trusted(host: str, port: int) -> bool:
    source = _source_address_tuple()
    ctx = ssl.create_default_context()
    try:
        with socket.create_connection(
            (host, port),
            timeout=settings.collector_timeout_seconds,
            source_address=source,
        ) as sock:
            with ctx.wrap_socket(sock, server_hostname=host):
                return True
    except ssl.SSLError:
        return False
    except OSError:
        return False


async def collect(host: str, port: int = 443) -> dict:
    async def _run() -> dict:
        supported = _supported_tls_versions(host, port)
        info = _handshake_info(host, port)
        trusted = _cert_trusted(host, port)
        return {
            "host": host,
            "port": port,
            "supported_versions": supported,
            "negotiated_version": info.get("negotiated_version"),
            "expires_at": info.get("expires_at"),
            "issuer": info.get("issuer"),
            "subject": info.get("subject"),
            "subject_alt_names": info.get("subject_alt_names"),
            "cert_trusted": trusted,
            "cert_valid": trusted,  # alias for normalization
        }

    result, attempts, error = await with_retry(_run)
    if result is None:
        result = {"host": host, "port": port, "error": str(error)}
    result["attempts"] = attempts
    return result
