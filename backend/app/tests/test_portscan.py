import pytest

from app.constants import VectorState
from app.normalization.normalize_portscan import normalize_legacy_service


def test_portscan_no_exposed_ports_passes():
    evidence = {
        "host": "example.com",
        "results": [
            {"port": 21, "service": "ftp", "reachable": False, "banner": ""},
            {"port": 23, "service": "telnet", "reachable": False, "banner": ""},
        ],
        "exposed_count": 0,
        "plaintext_count": 0,
        "exposed_ports": [],
    }
    result = normalize_legacy_service(evidence)
    assert result["state"] == VectorState.PASS.value


def test_portscan_plaintext_fails():
    evidence = {
        "host": "example.com",
        "results": [
            {"port": 21, "service": "ftp", "reachable": True, "banner": "220 FTP"},
        ],
        "exposed_count": 1,
        "plaintext_count": 1,
        "exposed_ports": [21],
    }
    result = normalize_legacy_service(evidence)
    assert result["state"] == VectorState.FAIL.value
    assert result["meta"]["exposed_ports"] == [21]


def test_portscan_single_non_plaintext_warns():
    evidence = {
        "host": "example.com",
        "results": [
            {"port": 22, "service": "ssh", "reachable": True, "banner": "SSH-2.0-OpenSSH"},
        ],
        "exposed_count": 1,
        "plaintext_count": 0,
        "exposed_ports": [22],
    }
    result = normalize_legacy_service(evidence)
    assert result["state"] == VectorState.WARN.value
    assert result["meta"]["exposed_ports"] == [22]


def test_portscan_multiple_exposed_fails():
    evidence = {
        "host": "example.com",
        "results": [
            {"port": 22, "service": "ssh", "reachable": True, "banner": ""},
            {"port": 25, "service": "smtp", "reachable": True, "banner": ""},
        ],
        "exposed_count": 2,
        "plaintext_count": 0,
        "exposed_ports": [22, 25],
    }
    result = normalize_legacy_service(evidence)
    assert result["state"] == VectorState.FAIL.value


def test_portscan_error_or_skipped_is_not_applicable():
    assert normalize_legacy_service({"error": "timeout"})["state"] == VectorState.NOT_APPLICABLE.value
    assert normalize_legacy_service({"skipped": True})["state"] == VectorState.NOT_APPLICABLE.value
