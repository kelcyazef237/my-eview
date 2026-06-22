from datetime import datetime, timedelta, timezone

from app.constants import VectorState
from app.normalization.normalize_dns import normalize_dns
from app.normalization.normalize_http import normalize_http
from app.normalization.normalize_assets import normalize_asset_surface
from app.normalization.normalize_portscan import normalize_legacy_service
from app.normalization.normalize_threat import normalize_threat
from app.normalization.normalize_whois import normalize_whois
from app.normalization.normalize_tls import normalize_tls


def test_dns_all_pass():
    result = normalize_dns({
        "spf_present": True,
        "dkim_present": True,
        "dmarc_policy": "reject",
        "dnssec": {"ds": True, "dnskey": True, "rrsig": True},
    })
    assert result["spf_presence"]["state"] == VectorState.PASS.value
    assert result["dkim_presence"]["state"] == VectorState.PASS.value
    assert result["dmarc_enforcement"]["state"] == VectorState.PASS.value
    assert result["dnssec_adoption"]["state"] == VectorState.PASS.value


def test_dns_dmarc_missing_fail():
    result = normalize_dns({
        "spf_present": True,
        "dkim_present": True,
        "dmarc_policy": "absent",
        "dnssec": {"ds": False, "dnskey": False, "rrsig": False},
    })
    assert result["dmarc_enforcement"]["state"] == VectorState.FAIL.value
    assert result["dnssec_adoption"]["state"] == VectorState.FAIL.value


def test_dns_error_returns_not_observed():
    result = normalize_dns({"error": "timeout"})
    for finding in result.values():
        assert finding["state"] == VectorState.NOT_OBSERVED.value


def test_tls_13_and_healthy_cert():
    as_of = datetime.now(timezone.utc)
    expires = (as_of + timedelta(days=120)).isoformat()
    result = normalize_tls({
        "negotiated_version": "TLSv1.3",
        "cert_trusted": True,
        "expires_at": expires,
    }, as_of=as_of)
    assert result["tls_version"]["state"] == VectorState.PASS.value
    assert result["certificate_health"]["state"] == VectorState.PASS.value


def test_tls_12_warn():
    result = normalize_tls({"negotiated_version": "TLSv1.2"})
    assert result["tls_version"]["state"] == VectorState.WARN.value


def test_tls_old_fail():
    result = normalize_tls({"negotiated_version": "TLSv1.0"})
    assert result["tls_version"]["state"] == VectorState.FAIL.value


def test_cert_expired_fail():
    as_of = datetime.now(timezone.utc)
    expires = (as_of - timedelta(days=1)).isoformat()
    result = normalize_tls({
        "negotiated_version": "TLSv1.3",
        "cert_trusted": True,
        "expires_at": expires,
    }, as_of=as_of)
    assert result["certificate_health"]["state"] == VectorState.FAIL.value


def test_http_security_headers_pass():
    result = normalize_http({
        "https_root": {
            "headers": {
                "strict-transport-security": "max-age=31536000",
                "content-security-policy": "default-src 'self'",
                "x-frame-options": "DENY",
                "x-content-type-options": "nosniff",
                "referrer-policy": "strict-origin",
                "permissions-policy": "geolocation=()",
            },
        },
        "redirects": {
            "https": {"reachable": True, "is_https_final": True, "hsts_present": True},
            "http": {"reachable": True, "is_https_final": True},
        },
        "admin_paths": [],
    })
    assert result["security_headers"]["state"] == VectorState.PASS.value
    assert result["https_enforcement"]["state"] == VectorState.PASS.value
    assert result["exposed_admin"]["state"] == VectorState.PASS.value


def test_http_missing_headers_warn():
    result = normalize_http({
        "https_root": {
            "headers": {
                "strict-transport-security": "max-age=31536000",
                "x-frame-options": "DENY",
                "content-security-policy": "default-src 'self'",
                "x-content-type-options": "nosniff",
                "referrer-policy": "strict-origin",
            },
        },
        "redirects": {
            "https": {"reachable": True, "is_https_final": True, "hsts_present": True},
            "http": {"reachable": True, "is_https_final": False},
        },
        "admin_paths": [],
    })
    assert result["security_headers"]["state"] == VectorState.WARN.value
    assert result["https_enforcement"]["state"] == VectorState.WARN.value


def test_http_exposed_admin_fail():
    result = normalize_http({
        "https_root": {"headers": {}},
        "redirects": {"https": {"reachable": True, "is_https_final": True, "hsts_present": True}},
        "admin_paths": [{"path": "/.env", "exposed": True}],
    })
    assert result["exposed_admin"]["state"] == VectorState.FAIL.value


def test_http_eol_tech_fail():
    result = normalize_http({
        "https_root": {
            "headers": {},
            "tech_headers": {"server": "Apache/2.2.34"},
            "tech_html": {},
        },
        "redirects": {"https": {"reachable": True, "is_https_final": True, "hsts_present": True}},
        "admin_paths": [],
    })
    assert result["tech_obsolescence"]["state"] == VectorState.FAIL.value
    assert result["software_version"]["state"] == VectorState.WARN.value


def test_http_sri_pass():
    result = normalize_http({
        "https_root": {
            "headers": {},
            "sri": {"total_external": 3, "with_integrity": 3},
        },
        "redirects": {"https": {"reachable": True, "is_https_final": True, "hsts_present": True}},
        "admin_paths": [],
    })
    assert result["sri_adoption"]["state"] == VectorState.PASS.value


def test_http_sri_fail():
    result = normalize_http({
        "https_root": {
            "headers": {},
            "sri": {"total_external": 4, "with_integrity": 1},
        },
        "redirects": {"https": {"reachable": True, "is_https_final": True, "hsts_present": True}},
        "admin_paths": [],
    })
    assert result["sri_adoption"]["state"] == VectorState.FAIL.value


def test_whois_mature_domain_passes():
    as_of = datetime(2026, 6, 22, tzinfo=timezone.utc)
    created = (as_of - timedelta(days=800)).isoformat()
    expires = (as_of + timedelta(days=180)).isoformat()
    result = normalize_whois({"creation_date": created, "expiration_date": expires}, as_of=as_of)
    assert result["domain_age"]["state"] == VectorState.PASS.value
    assert result["domain_expiration"]["state"] == VectorState.PASS.value


def test_whois_young_domain_warns():
    as_of = datetime(2026, 6, 22, tzinfo=timezone.utc)
    created = (as_of - timedelta(days=200)).isoformat()
    expires = (as_of + timedelta(days=60)).isoformat()
    result = normalize_whois({"creation_date": created, "expiration_date": expires}, as_of=as_of)
    assert result["domain_age"]["state"] == VectorState.WARN.value
    assert result["domain_expiration"]["state"] == VectorState.WARN.value


def test_whois_expiring_soon_fails():
    as_of = datetime(2026, 6, 22, tzinfo=timezone.utc)
    created = (as_of - timedelta(days=1000)).isoformat()
    expires = (as_of + timedelta(days=10)).isoformat()
    result = normalize_whois({"creation_date": created, "expiration_date": expires}, as_of=as_of)
    assert result["domain_age"]["state"] == VectorState.PASS.value
    assert result["domain_expiration"]["state"] == VectorState.FAIL.value


def test_whois_error_returns_not_observed():
    result = normalize_whois({"error": "timeout"})
    assert result["domain_age"]["state"] == VectorState.NOT_OBSERVED.value
    assert result["domain_expiration"]["state"] == VectorState.NOT_OBSERVED.value


def test_assets_small_clean_surface_passes():
    result = normalize_asset_surface({
        "domain": "example.com",
        "discovered_assets": ["www.example.com", "mail.example.com"],
    })
    assert result["asset_count"]["state"] == VectorState.PASS.value
    assert result["shadow_assets"]["state"] == VectorState.PASS.value
    assert result["unmanaged_assets"]["state"] == VectorState.PASS.value


def test_assets_large_count_fails():
    assets = [f"sub{i}.example.com" for i in range(40)]
    result = normalize_asset_surface({"domain": "example.com", "discovered_assets": assets})
    assert result["asset_count"]["state"] == VectorState.FAIL.value


def test_assets_shadow_threshold_warns():
    assets = ["www.example.com"] + [f"shadow{i}.example.com" for i in range(6)]
    result = normalize_asset_surface({"domain": "example.com", "discovered_assets": assets})
    assert result["shadow_assets"]["state"] == VectorState.FAIL.value


def test_assets_error_returns_not_observed():
    result = normalize_asset_surface({"error": "timeout"})
    for finding in result.values():
        assert finding["state"] == VectorState.NOT_OBSERVED.value


def test_threat_clean_passes():
    result = normalize_threat({"derived": {}})
    assert result["malware"]["state"] == VectorState.PASS.value
    assert result["phishing"]["state"] == VectorState.PASS.value
    assert result["spam_blacklist"]["state"] == VectorState.PASS.value
    assert result["botnet"]["state"] == VectorState.PASS.value
    assert result["blacklist_aggregate"]["state"] == VectorState.PASS.value


def test_threat_active_malware_fails():
    result = normalize_threat({"derived": {"malware_activity": "active"}})
    assert result["malware"]["state"] == VectorState.FAIL.value


def test_threat_historical_phishing_warns():
    result = normalize_threat({"derived": {"phishing_activity": "historical"}})
    assert result["phishing"]["state"] == VectorState.WARN.value


def test_threat_multiple_blacklists_fails():
    result = normalize_threat({"derived": {"spam_listed_count": 2, "blacklist_aggregate_count": 5}})
    assert result["spam_blacklist"]["state"] == VectorState.FAIL.value
    assert result["blacklist_aggregate"]["state"] == VectorState.FAIL.value
