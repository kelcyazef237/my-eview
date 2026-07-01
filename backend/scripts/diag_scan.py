#!/usr/bin/env python3
"""Diagnostic end-to-end scan runner.

Exercises the real backend pipeline against a target domain and logs every
component's pass/fail so we can debug stability issues.

Two passes:
  1. Per-component probe — each collector (DNS, WHOIS, TLS, HTTP, threat
     intel, asset discovery, AXFR) is called individually with a retry
     wrapper. Produces a clean pass/fail matrix.
  2. End-to-end scan — `app.services.scan_orchestrator.run_scan` is called
     inside a SAVEPOINT, the result is reported, then the SAVEPOINT is
     rolled back so no rows are persisted.

Run:
    python scripts/diag_scan.py --domain matrixtelecoms.com
    python scripts/diag_scan.py --domain matrixtelecoms.com --no-e2e
    python scripts/diag_scan.py --domain example.com --no-component

Exit codes:
    0  scan completed and is_complete=True
    1  scan completed but is_complete=False (data holes)
    2  scan raised an unhandled exception
    3  pre-flight check failed
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import socket
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

# ANSI colors — match start.py / create_admin.py style
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

TAG_COLORS = {
    "STAGE":   CYAN,
    "START":   DIM,
    "PASS":    GREEN,
    "FAIL":    RED,
    "DETAIL":  DIM,
    "WARN":    YELLOW,
    "ERROR":   RED,
    "SUMMARY": BOLD + MAGENTA,
    "VECTOR":  DIM,
    "PREFLT":  CYAN,
    "CLEANUP": YELLOW,
    "CLEAN-FAIL": RED,
}


class DiagLogger:
    """Single-line-per-event logger with structured tags.

    Writes plain text to the log file and colored text to stdout.
    Every line is prefixed with a UTC timestamp and a tag, e.g.
        [2026-07-01 14:23:01.234] [PASS] collect(dns) attempts=1 elapsed=1.22s
    """

    def __init__(self, log_path: Path) -> None:
        self.log_path = log_path
        # Truncate (the caller writes the header immediately after construction)
        self._fh = open(log_path, "a", buffering=1)  # line-buffered

    def _stamp(self, tag: str, msg: str) -> str:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S") + f".{int(time.time()*1000) % 1000:03d}"
        return f"[{ts}] [{tag:<7}] {msg}"

    def emit(self, tag: str, msg: str, *, color: bool = True) -> None:
        line = self._stamp(tag, msg)
        # File: plain
        self._fh.write(line + "\n")
        # Stdout: colored
        col = TAG_COLORS.get(tag, "") if color else ""
        print(f"{col}{line}{RESET}", flush=True)

    def close(self) -> None:
        self._fh.close()


def preflight(logger: DiagLogger, db, domain: str) -> bool:
    """Run pre-flight checks. Return True if all critical ones pass."""
    ok = True

    logger.emit("PREFLT", "checking DNS resolver (google.com)")
    t0 = time.perf_counter()
    try:
        socket.gethostbyname("google.com")
        logger.emit("PASS", f"dns_resolver ok elapsed={time.perf_counter()-t0:.2f}s")
    except Exception as exc:
        logger.emit("FAIL", f"dns_resolver err={type(exc).__name__}({exc})")
        ok = False

    logger.emit("PREFLT", "checking database (SELECT 1)")
    t0 = time.perf_counter()
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        logger.emit("PASS", f"database ok elapsed={time.perf_counter()-t0:.2f}s")
    except Exception as exc:
        logger.emit("FAIL", f"database err={type(exc).__name__}({exc})")
        ok = False

    logger.emit("PREFLT", "checking crt.sh reachability (HEAD)")
    t0 = time.perf_counter()
    try:
        import httpx
        with httpx.Client(timeout=5) as c:
            r = c.head("https://crt.sh/", follow_redirects=True)
            r.raise_for_status()
        logger.emit("PASS", f"crt.sh ok elapsed={time.perf_counter()-t0:.2f}s")
    except Exception as exc:
        logger.emit("WARN", f"crt.sh unreachable err={type(exc).__name__}({exc}) — asset_discovery will fail")

    from app.config import get_settings
    settings = get_settings()
    if not settings.otx_api_key:
        logger.emit("WARN", "OTX_API_KEY not set — malware vector will be NOT_OBSERVED")
    else:
        logger.emit("PASS", f"otx_api_key present (len={len(settings.otx_api_key)})")

    logger.emit("PREFLT", f"target domain={domain}")
    return ok


# ---------------------------------------------------------------------------
# Pass 1 — per-component probes
# ---------------------------------------------------------------------------

async def probe_dns(logger: DiagLogger, domain: str) -> dict | None:
    from app.collectors import dns_collector
    logger.emit("STAGE", "dns")
    t0 = time.perf_counter()
    try:
        result = await dns_collector.collect(domain)
        elapsed = time.perf_counter() - t0
        attempts = result.get("attempts", 1)
        if "error" in result:
            logger.emit("FAIL", f"collect(dns) attempts={attempts} elapsed={elapsed:.2f}s err={result['error']}")
            return None
        logger.emit("PASS", f"collect(dns) attempts={attempts} elapsed={elapsed:.2f}s")
        spf = "present" if result.get("spf_present") else "absent"
        dkim = "present" if result.get("dkim_present") else "absent"
        dmarc = result.get("dmarc_policy", "absent")
        dnssec = result.get("dnssec", {})
        dnssec_summary = "+".join(k for k, v in dnssec.items() if v) or "none"
        axfr = result.get("zone_transfer", {})
        axfr_summary = f"refused={len(axfr.get('refused', []))}/{axfr.get('tested', 0)}"
        if axfr.get("allowed"):
            axfr_summary += f" ALLOWED={axfr['allowed']}"
        logger.emit("DETAIL", f"dns.spf={spf} dns.dkim={dkim} dns.dmarc={dmarc} dns.dnssec={dnssec_summary} dns.axfr={axfr_summary}")
        return result
    except Exception as exc:
        elapsed = time.perf_counter() - t0
        logger.emit("FAIL", f"collect(dns) elapsed={elapsed:.2f}s err={type(exc).__name__}({exc})")
        return None


async def probe_axfr(logger: DiagLogger, domain: str) -> dict | None:
    from app.collectors.dns_collector import _zone_transfer_status
    logger.emit("STAGE", "axfr (direct)")
    t0 = time.perf_counter()
    try:
        result = await asyncio.to_thread(_zone_transfer_status, domain)
        elapsed = time.perf_counter() - t0
        tested = result.get("tested", 0)
        allowed = result.get("allowed", [])
        refused = result.get("refused", [])
        logger.emit("PASS", f"_zone_transfer_status elapsed={elapsed:.2f}s tested={tested} allowed={len(allowed)} refused={len(refused)}")
        if allowed:
            logger.emit("WARN", f"AXFR allowed by: {','.join(allowed)} — zone_transfer vector will FAIL")
        return result
    except Exception as exc:
        elapsed = time.perf_counter() - t0
        logger.emit("FAIL", f"_zone_transfer_status elapsed={elapsed:.2f}s err={type(exc).__name__}({exc})")
        return None


async def probe_whois(logger: DiagLogger, domain: str) -> dict | None:
    from app.collectors import whois_collector
    logger.emit("STAGE", "whois")
    t0 = time.perf_counter()
    try:
        result = await whois_collector.collect(domain)
        elapsed = time.perf_counter() - t0
        attempts = result.get("attempts", 1)
        if "error" in result:
            logger.emit("FAIL", f"collect(whois) attempts={attempts} elapsed={elapsed:.2f}s err={result['error']}")
            return None
        logger.emit("PASS", f"collect(whois) attempts={attempts} elapsed={elapsed:.2f}s")
        logger.emit("DETAIL", f"whois.creation_date={result.get('creation_date')} whois.expiration_date={result.get('expiration_date')} whois.registrar={result.get('registrar')}")
        return result
    except Exception as exc:
        elapsed = time.perf_counter() - t0
        logger.emit("FAIL", f"collect(whois) elapsed={elapsed:.2f}s err={type(exc).__name__}({exc})")
        return None


async def probe_tls(logger: DiagLogger, domain: str) -> dict | None:
    from app.collectors import tls_collector
    logger.emit("STAGE", "tls")
    t0 = time.perf_counter()
    try:
        result = await tls_collector.collect(domain, 443)
        elapsed = time.perf_counter() - t0
        attempts = result.get("attempts", 1)
        if "error" in result:
            logger.emit("FAIL", f"collect(tls) attempts={attempts} elapsed={elapsed:.2f}s err={result['error']}")
            return None
        logger.emit("PASS", f"collect(tls) attempts={attempts} elapsed={elapsed:.2f}s")
        supported = result.get("supported_versions", [])
        negotiated = result.get("negotiated_version")
        trusted = result.get("cert_trusted")
        logger.emit("DETAIL", f"tls.negotiated={negotiated} tls.supported={','.join(supported)} tls.trusted={trusted} tls.expires_at={result.get('expires_at')}")
        return result
    except Exception as exc:
        elapsed = time.perf_counter() - t0
        logger.emit("FAIL", f"collect(tls) elapsed={elapsed:.2f}s err={type(exc).__name__}({exc})")
        return None


async def probe_http(logger: DiagLogger, domain: str) -> dict | None:
    from app.collectors import http_collector
    logger.emit("STAGE", "http")
    t0 = time.perf_counter()
    try:
        result = await http_collector.collect(domain)
        elapsed = time.perf_counter() - t0
        attempts = result.get("attempts", 1)
        if "error" in result:
            logger.emit("FAIL", f"collect(http) attempts={attempts} elapsed={elapsed:.2f}s err={result['error']}")
            return None
        logger.emit("PASS", f"collect(http) attempts={attempts} elapsed={elapsed:.2f}s")
        https_root = result.get("https_root", {})
        redirects = result.get("redirects", {})
        admin_paths = result.get("admin_paths", [])
        exposed_admin = [a["path"] for a in admin_paths if a.get("exposed")]
        logger.emit(
            "DETAIL",
            f"http.https_root_status={https_root.get('status_code')} "
            f"http.http_reachable={redirects.get('http', {}).get('reachable')} "
            f"http.https_reachable={redirects.get('https', {}).get('reachable')} "
            f"http.exposed_admin_paths={','.join(exposed_admin) if exposed_admin else 'none'}"
        )
        return result
    except Exception as exc:
        elapsed = time.perf_counter() - t0
        logger.emit("FAIL", f"collect(http) elapsed={elapsed:.2f}s err={type(exc).__name__}({exc})")
        return None


async def probe_asset_discovery(logger: DiagLogger, domain: str) -> dict | None:
    from app.collectors import asset_discovery
    logger.emit("STAGE", "asset_discovery")
    t0 = time.perf_counter()
    try:
        result = await asset_discovery.discover(domain)
        elapsed = time.perf_counter() - t0
        attempts = result.get("attempts", 1)
        if "error" in result:
            logger.emit("FAIL", f"discover(asset_discovery) attempts={attempts} elapsed={elapsed:.2f}s err={result['error']}")
            return None
        count = result.get("count", 0)
        assets = result.get("discovered_assets", [])
        sample = ",".join(assets[:5])
        logger.emit("PASS", f"discover(asset_discovery) attempts={attempts} elapsed={elapsed:.2f}s count={count}")
        logger.emit("DETAIL", f"asset_discovery.sample={sample}")
        return result
    except Exception as exc:
        elapsed = time.perf_counter() - t0
        logger.emit("FAIL", f"discover(asset_discovery) elapsed={elapsed:.2f}s err={type(exc).__name__}({exc})")
        return None


async def probe_threat_intel(logger: DiagLogger, domain: str, db) -> dict | None:
    from app.collectors import threat_intel_collector
    logger.emit("STAGE", "threat_intel")
    t0 = time.perf_counter()
    try:
        result = await threat_intel_collector.collect(domain, db)
        elapsed = time.perf_counter() - t0
        otx = result.get("otx", {})
        otx_summary = (
            "skipped(no_api_key)" if otx.get("skipped")
            else "error" if "error" in otx
            else f"pulses={otx.get('pulse_count', 0)} malware={otx.get('malware_count', 0)}"
        )
        derived = result.get("derived", {})
        logger.emit("PASS", f"collect(threat_intel) elapsed={elapsed:.2f}s")
        logger.emit("DETAIL", f"threat_intel.otx={otx_summary} threat_intel.spam={derived.get('spam_listed_count', 0)} threat_intel.botnet={derived.get('botnet_listed')} threat_intel.blacklist_aggregate={derived.get('blacklist_aggregate_count')}")
        return result
    except Exception as exc:
        elapsed = time.perf_counter() - t0
        logger.emit("FAIL", f"collect(threat_intel) elapsed={elapsed:.2f}s err={type(exc).__name__}({exc})")
        return None


# ---------------------------------------------------------------------------
# Pass 2 — end-to-end orchestrator (in SAVEPOINT, rolled back after)
# ---------------------------------------------------------------------------

async def run_end_to_end(logger: DiagLogger, db, domain: str) -> tuple[int, dict | None]:
    """Run scan_orchestrator.run_scan inside a SAVEPOINT and report the result.

    Returns (exit_code, summary_dict). summary_dict is None on hard failure.
    The SAVEPOINT is always rolled back before returning.
    """
    from app.services.scan_orchestrator import run_scan
    from app.reference_data import CATEGORY_ROWS, VECTOR_ROWS

    logger.emit("STAGE", "end_to_end")
    logger.emit("START", "run_scan via scan_orchestrator (SAVEPOINT)")

    savepoint = db.begin_nested()
    scan_run = None
    t0 = time.perf_counter()
    try:
        scan_run = await run_scan(db, domain, is_full_report=False)
        elapsed = time.perf_counter() - t0
    except Exception as exc:
        elapsed = time.perf_counter() - t0
        logger.emit("ERROR", f"run_scan raised {type(exc).__name__}({exc}) elapsed={elapsed:.2f}s")
        logger.emit("ERROR", "traceback:")
        for line in traceback.format_exc().splitlines():
            logger.emit("ERROR", f"  {line}")
        try:
            savepoint.rollback()
            logger.emit("CLEANUP", "SAVEPOINT rolled back after exception")
        except Exception as cleanup_exc:
            logger.emit("CLEAN-FAIL", f"rollback failed err={type(cleanup_exc).__name__}({cleanup_exc})")
        return 2, None

    # Inspect the result. Note: scan_run is now attached to the savepoint.
    status = scan_run.status
    started = scan_run.started_at
    finished = scan_run.finished_at
    duration = (finished - started).total_seconds() if finished and started else None

    score = scan_run.score
    overall = score.overall_score if score else None
    shield_tier = score.shield_tier if score else None
    outlook = score.outlook if score else None

    # Re-derive is_complete from the persisted vector_findings
    from app.constants import VectorState
    vector_findings = scan_run.vector_findings or []
    not_observed = sum(1 for vf in vector_findings if (vf.state or "").upper() == VectorState.NOT_OBSERVED.value)
    scored = len(VECTOR_ROWS)  # total possible vectors
    not_observed_ratio = not_observed / scored if scored else 0.0
    is_complete = status == "complete" and not_observed_ratio <= 0.15

    logger.emit("SUMMARY", f"scan_run.id={scan_run.id} status={status} duration={duration:.2f}s" if duration else f"scan_run.id={scan_run.id} status={status}")
    logger.emit("SUMMARY", f"overall={overall}/1000 tier={shield_tier} outlook={outlook} is_complete={is_complete} not_observed={not_observed}/{scored} ({not_observed_ratio:.1%})")

    # Per-category breakdown
    cat_by_id = {c["id"]: c for c in CATEGORY_ROWS}
    vec_by_id = {v["id"]: v for v in VECTOR_ROWS}
    state_by_vec_id = {vf.vector_id: vf.state for vf in vector_findings}

    cat_breakdown: list[dict] = []
    for cat_score in (scan_run.category_scores or []):
        cat = cat_by_id.get(cat_score.category_id, {})
        cat_breakdown.append({
            "key": cat.get("key", "?"),
            "name": cat.get("name", "?"),
            "points_total": cat.get("points_total", 0),
            "points_lost": cat_score.points_lost,
            "points_remaining": cat_score.points_remaining,
        })
        logger.emit(
            "DETAIL",
            f"category[{cat.get('key', '?')}] points_lost={cat_score.points_lost}/{cat.get('points_total', 0)} remaining={cat_score.points_remaining}"
        )

    # Per-vector state summary
    vec_states = []
    for vec in VECTOR_ROWS:
        state = state_by_vec_id.get(vec["id"], "MISSING")
        vec_states.append((vec["key"], state))
    vec_summary = " ".join(f"{k}={s}" for k, s in vec_states)
    logger.emit("VECTOR", vec_summary)

    summary = {
        "scan_run_id": str(scan_run.id),
        "status": status,
        "duration": duration,
        "overall": overall,
        "shield_tier": shield_tier,
        "outlook": outlook,
        "is_complete": is_complete,
        "not_observed": not_observed,
        "scored": scored,
        "not_observed_ratio": not_observed_ratio,
        "categories": cat_breakdown,
        "vector_states": dict(vec_states),
    }

    # Roll back the SAVEPOINT — this is the contract: no DB writes persist
    try:
        savepoint.rollback()
        logger.emit("CLEANUP", "SAVEPOINT rolled back — no DB changes persisted")
    except Exception as cleanup_exc:
        logger.emit("CLEAN-FAIL", f"rollback failed err={type(cleanup_exc).__name__}({cleanup_exc})")

    exit_code = 0 if is_complete else 1
    return exit_code, summary


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnostic end-to-end scan runner")
    parser.add_argument("--domain", required=True, help="Target domain to scan")
    parser.add_argument("--no-component", action="store_true", help="Skip pass 1 (per-component probes)")
    parser.add_argument("--no-e2e", action="store_true", help="Skip pass 2 (end-to-end orchestrator)")
    parser.add_argument("--log-dir", default=str(BACKEND_DIR / "logs"), help="Where to write the log file")
    args = parser.parse_args()

    domain = args.domain.lower().strip()
    if not domain or "." not in domain:
        print(f"{RED}invalid domain: {domain!r}{RESET}", file=sys.stderr)
        return 3

    # Set up log file
    log_dir = Path(args.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_domain = domain.replace("/", "_")
    log_path = log_dir / f"diag-{safe_domain}-{ts}.log"

    logger = DiagLogger(log_path)
    # Replace the start marker with one that includes the domain
    with open(log_path, "a") as f:
        f.write(f"# diag_scan domain={domain} pid={os.getpid()} started={ts}\n")
    logger.emit("STAGE", f"diag_scan domain={domain} log={log_path}")
    print(f"{DIM}Log file: {log_path}{RESET}", flush=True)

    # Pre-flight
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        preflight_ok = preflight(logger, db, domain)
        if not preflight_ok:
            logger.emit("ERROR", "pre-flight failed — aborting")
            return 3

        # Pass 1 — per-component probes
        if not args.no_component:
            logger.emit("STAGE", "=== pass 1: per-component probes ===")
            probes = [
                ("dns",            probe_dns,            (logger, domain)),
                ("axfr",           probe_axfr,           (logger, domain)),
                ("whois",          probe_whois,          (logger, domain)),
                ("tls",            probe_tls,            (logger, domain)),
                ("http",           probe_http,           (logger, domain)),
                ("asset_discovery",probe_asset_discovery,(logger, domain)),
                ("threat_intel",   probe_threat_intel,   (logger, domain, db)),
            ]
            for name, fn, fn_args in probes:
                try:
                    asyncio.run(fn(*fn_args))
                except Exception as exc:
                    logger.emit("ERROR", f"probe({name}) raised {type(exc).__name__}({exc})")
                    for line in traceback.format_exc().splitlines():
                        logger.emit("ERROR", f"  {line}")

        # Pass 2 — end-to-end orchestrator
        summary: dict | None = None
        exit_code = 0
        if not args.no_e2e:
            logger.emit("STAGE", "=== pass 2: end-to-end orchestrator ===")
            exit_code, summary = asyncio.run(run_end_to_end(logger, db, domain))
        else:
            logger.emit("STAGE", "=== pass 2 skipped (--no-e2e) ===")

        if summary is not None and isinstance(summary, dict):
            logger.emit("SUMMARY", json.dumps(summary, default=str))
        elif not args.no_e2e:
            logger.emit("SUMMARY", "no summary produced (scan failed)")

        logger.emit("STAGE", f"diag_scan complete exit_code={exit_code}")
        return exit_code
    finally:
        db.close()
        logger.close()


if __name__ == "__main__":
    sys.exit(main())
