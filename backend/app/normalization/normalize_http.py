"""Convert HTTP raw evidence into scoring-engine findings."""

import re

from app.constants import CRITICAL_SECURITY_HEADERS, VectorState


SENSITIVE_ADMIN_PATHS = {"/phpmyadmin", "/pma", "/adminer", "/.env", "/config", "/console"}


def _f(state: VectorState, meta: dict | None = None) -> dict:
    return {"state": state.value, "meta": meta or {}}


def _https_root(evidence: dict) -> dict:
    return evidence.get("https_root", {}) or {}


def _redirects(evidence: dict) -> dict:
    return evidence.get("redirects", {}) or {}


def normalize_security_headers(evidence: dict) -> dict:
    root = _https_root(evidence)
    headers = {k.lower(): v for k, v in (root.get("headers") or {}).items()}
    if not headers:
        return _f(VectorState.NOT_OBSERVED)

    missing = [h for h in CRITICAL_SECURITY_HEADERS if h not in headers or not headers[h].strip()]
    if not missing:
        return _f(VectorState.PASS)
    if len(missing) <= 2:
        return _f(VectorState.WARN, {"missing_headers": missing})
    return _f(VectorState.FAIL, {"missing_headers": missing})


def normalize_https_enforcement(evidence: dict) -> dict:
    redirects = _redirects(evidence)
    https_info = redirects.get("https", {})
    http_info = redirects.get("http", {})

    if not https_info.get("reachable"):
        return _f(VectorState.FAIL, {"reason": "https_unreachable"})

    https_final_is_https = https_info.get("is_https_final", False)
    hsts_present = https_info.get("hsts_present", False)
    http_reaches_https = http_info.get("is_https_final", False) if http_info.get("reachable") else False

    if https_final_is_https and hsts_present and http_reaches_https:
        return _f(VectorState.PASS, {"hsts": True, "http_redirects": True})
    if https_final_is_https and (hsts_present or http_reaches_https):
        return _f(VectorState.WARN, {"hsts": hsts_present, "http_redirects": http_reaches_https})
    return _f(VectorState.FAIL, {"hsts": False, "http_redirects": False})


def normalize_exposed_admin(evidence: dict) -> dict:
    paths = evidence.get("admin_paths") or []
    exposed = [p for p in paths if isinstance(p, dict) and p.get("exposed")]
    if not exposed:
        return _f(VectorState.PASS)

    sensitive = [p for p in exposed if p.get("path") in SENSITIVE_ADMIN_PATHS]
    path_list = [p.get("path") for p in exposed]
    if len(sensitive) >= 1 or len(exposed) >= 2:
        return _f(VectorState.FAIL, {"exposed_paths": path_list})
    return _f(VectorState.WARN, {"exposed_paths": path_list})


def _parse_version(text: str | None) -> tuple[str, str] | None:
    if not text:
        return None
    m = re.search(r"(\d+(?:\.\d+)*)", text)
    if not m:
        return None
    return text.split("/")[0] if "/" in text else text, m.group(1)


def _is_eol_tech(name: str, version: str) -> bool:
    """Very conservative EOL/heuristically-old detection for MVP."""
    name_lower = name.lower()
    parts = [int(p) for p in version.split(".") if p.isdigit()]
    major = parts[0] if parts else 0
    minor = parts[1] if len(parts) > 1 else 0

    if "apache" in name_lower and major == 2 and minor < 4:
        return True
    if "nginx" in name_lower and major < 1:
        return True
    if "nginx" in name_lower and major == 1 and minor < 18:
        return True
    if "php" in name_lower and major < 8:
        return True
    if "wordpress" in name_lower and major < 5:
        return True
    if "iis" in name_lower and major < 8:
        return True
    return False


def normalize_tech_obsolescence(evidence: dict) -> dict:
    root = _https_root(evidence)
    tech_headers = root.get("tech_headers") or {}
    tech_html = root.get("tech_html") or {}

    candidates = []
    server = tech_headers.get("server")
    if server:
        candidates.append(server)
    x_powered = tech_headers.get("x_powered_by")
    if x_powered:
        candidates.append(x_powered)
    for g in tech_html.get("generator_meta") or []:
        candidates.append(g)

    if not candidates:
        return _f(VectorState.NOT_APPLICABLE)

    has_eol = False
    has_version = False
    detected = []
    for c in candidates:
        parsed = _parse_version(c)
        if parsed:
            has_version = True
            name, version = parsed
            detected.append({"name": name, "version": version})
            if _is_eol_tech(name, version):
                has_eol = True

    if has_eol:
        return _f(VectorState.FAIL, {"detected": detected})
    if has_version:
        return _f(VectorState.PASS, {"detected": detected})
    return _f(VectorState.NOT_APPLICABLE)


def normalize_software_version_currency(evidence: dict) -> dict:
    """MVP: mirrors tech_obsolescence because no CVE feed is wired by default."""
    obsolescence = normalize_tech_obsolescence(evidence)
    if obsolescence["state"] == VectorState.FAIL.value:
        return _f(VectorState.WARN, obsolescence.get("meta", {}))
    if obsolescence["state"] == VectorState.PASS.value:
        return _f(VectorState.PASS, obsolescence.get("meta", {}))
    return _f(VectorState.NOT_APPLICABLE)


def normalize_sri_adoption(evidence: dict) -> dict:
    root = _https_root(evidence)
    sri = root.get("sri") or {}
    total = sri.get("total_external", 0)
    if total == 0:
        return _f(VectorState.NOT_APPLICABLE)
    with_integrity = sri.get("with_integrity", 0)
    ratio = with_integrity / total
    if with_integrity == total:
        return _f(VectorState.PASS, {"total": total, "with_integrity": with_integrity})
    if ratio >= 0.5:
        return _f(VectorState.WARN, {"total": total, "with_integrity": with_integrity, "ratio": ratio})
    return _f(VectorState.FAIL, {"total": total, "with_integrity": with_integrity, "ratio": ratio})


def normalize_http(evidence: dict) -> dict:
    return {
        "security_headers": normalize_security_headers(evidence),
        "https_enforcement": normalize_https_enforcement(evidence),
        "exposed_admin": normalize_exposed_admin(evidence),
        "tech_obsolescence": normalize_tech_obsolescence(evidence),
        "software_version": normalize_software_version_currency(evidence),
        "sri_adoption": normalize_sri_adoption(evidence),
    }
