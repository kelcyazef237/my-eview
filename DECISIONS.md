# MYEVIEW — Design Decisions

This document records assumptions and decisions made where the build specification was ambiguous or required reconciliation.

## 1. 1000-Point Reconciliation

The original specification's category table summed to 1100 points (a drafting error). We adopted the normalized allocation from `myeview-holistic-plan-v2.md`:

| Category | Points |
|---|---|
| Email Trust & Authentication | 140 |
| Digital Identity & Domain Governance | 90 |
| Infrastructure Security | 180 |
| Technology Currency | 90 |
| Threat Intelligence Exposure | 270 |
| Asset Visibility & Attack Surface | 140 |
| Ecosystem Trust | 90 |
| Entity Intelligence | 0 |
| **Total scored** | **1000** |

## 2. Vector Count Reconciliation

The specification states "24 underlying risk vectors" but the category table enumerates 27 distinct vectors (including the 4 unscored Entity Intelligence vectors). We implemented all enumerated vectors and seeded 27 rows. The unscored Entity Intelligence vectors are displayed qualitatively and hidden from the default Owner view, consistent with the vector-hiding requirement.

## 3. Vector Scoring Defaults

All vectors follow the spec pattern: `PASS = 0 deduction`, `WARN = partial deduction`, `FAIL = full vector-budget deduction`. `NOT_APPLICABLE` and `NOT_OBSERVED` deduct 0 points. Detailed thresholds are in `backend/config/scoring_rules_v1.yaml`.

## 4. DKIM Probing

DKIM selectors are probed from a curated list of common selectors: `default`, `google`, `selector1`, `selector2`, `mail`. Absence across all probed selectors is scored as FAIL. This is documented because DKIM requires a known selector to query.

## 5. DMARC Interpretation

A domain is considered to have **no DMARC** if there is no valid `v=DMARC1` TXT record at `_dmarc.<domain>`. Invalid or malformed DMARC records are also treated as absent and scored as FAIL (-80).

## 6. TLS Version Baseline

- `TLS 1.3` → PASS  
- `TLS 1.2` → WARN  
- `TLS ≤ 1.1` or SSL → FAIL  

This reflects TLS 1.3 as the trust-score baseline while still tolerating TLS 1.2.

## 7. Domain Age / Asset Count Thresholds

Because first-time assessments have no organization-specific baseline, absolute thresholds are used:

- Domain age: > 12 months PASS, 6–12 months WARN, < 6 months FAIL.
- Internet-facing asset count: 0–10 PASS, 11–30 WARN, 31+ FAIL.

These are tuned for Cameroonian institutions of the size expected in the MVP.

## 8. Certificate Trust

Certificate health uses the system trust store (`certifi`). A certificate is FAIL if it is expired, untrusted, hostname-mismatched, or has fewer than 30 days remaining.

## 9. Legacy Service Exposure Gating

The `Legacy Service Exposure` vector is `NOT_APPLICABLE` by default. It only runs for organizations that have explicitly opted into the gated "Verified" light port-scan tier, in line with the spec's authorization requirement.

## 10. Threat-Intel Timing

- Active vs historical threshold: ≤ 6 months = active, > 6 months = historical.
- Feodo Tracker, PhishTank, and OpenPhish are cached locally and refreshed by Celery beat.
- AlienVault OTX is the only feed requiring an API key; the key is injected at testing/deployment time.

## 11. Regulatory Citations

Authoritative COBAC IT/cybersecurity text was not publicly available during implementation. Reports reference "COBAC operational risk management obligations" as a soft citation, with the standard disclaimer that regulatory determinations require qualified legal and compliance advisors. Concrete citations are provided for ANTIC Law 2010/012 and Data Protection Law 2024/017.

## 12. View-Layer Defaults

- Public / anonymous users see only score, Shield tier, trend, and sector benchmark.
- Owner users see category findings, TIA, and Entity Intelligence but not the 24-vector drill-down.
- Owner-Technical users see everything including raw evidence and vector details after enabling the Technical View toggle.
- Internal Ops users see everything plus raw evidence store, ruleset info, and re-scan triggers.

## 13. Determinism Controls

- All outbound collectors use a single configurable source IP (`COLLECTOR_BIND_ADDRESS`).
- Continuous values are bucketed into discrete states before scoring.
- Raw evidence is append-only and immutable per scan run.
- The scoring engine is a pure function with no live calls or randomness.

## 14. Incomplete Run Threshold

If more than 15% of scored vectors in a run return `NOT_OBSERVED`, the run is marked `incomplete` and no new score is published.

## 15. NOT_OBSERVED Scoring Guard (Fix)

The scoring engine explicitly short-circuits `NOT_OBSERVED` and `NOT_APPLICABLE` states to 0 deduction before evaluating tier rules. Without this guard, meta-based vectors like DMARC (which match on `meta.dmarc_policy` rather than `state`) would fall through to the `match: true` fallback and receive a -80 FAIL deduction when the check couldn't run — silently scoring a failed check as FAIL, violating the spec's determinism guarantee. The guard is in `backend/app/scoring/engine.py:_deduction_for_vector`.

## 16. Subdomain Re-scan Budget

The orchestrator re-runs TLS and HTTP collectors against up to 20 discovered subdomains per scan to populate the `unmanaged_assets` vector. This cap prevents scan-time explosion for organizations with large CT-log footprints while still providing meaningful coverage for the cert-issuer mismatch and banner-comparison heuristics.

## 17. Celery Beat Schedule

- Threat feeds: PhishTank hourly, OpenPhish every 12h, Feodo every 30min.
- Monitoring scans: weekly (Monday 02:17 UTC) — dispatched to all orgs for internal alerting.
- Full report cycles: monthly (1st of month 03:17 UTC) — dispatched to all orgs; only these feed the outlook momentum comparison.

## 18. Evidence Reference Convention

Vector findings store the collector name (e.g. `"dns"`, `"tls"`, `"http"`, `"threat_intel"`) as `evidence_ref`, not a stringified meta dict. This provides a stable link to the raw_evidence rows for the same scan_run + collector_name, enabling traceability without coupling the finding to mutable metadata.
