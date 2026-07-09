"""AI-assisted report generation via DeepSeek (default) or Ollama Cloud.

The rule-based scoring engine is deterministic but rigid — it can miss
nuance that a model would catch reading the actual scan evidence. This
module assembles a scan's full evidence trail (raw collector payloads +
vector findings + category scores) into a compact summary, sends it to
an OpenAI-compatible chat completions endpoint, and parses the model's
structured response into a report context that reuses the existing
template.

Supported providers (selected by the admin via the `ai_provider`
setting in app_settings):
  - "deepseek" (default): https://api.deepseek.com/chat/completions,
    model `deepseek-v4-flash`. Supports `thinking: {type: "disabled"}`.
  - "ollama": https://ollama.com/api/chat, model `glm-4.7-flash`.

The API key is NOT hardcoded — it is read from the `app_settings` table
(key "ai_api_key"), set by the admin through the admin UI. This keeps
secrets out of the repo.
"""

import json
import logging
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.app_setting import AppSetting
from app.models.scan_run import ScanRun
from app.models.score import Score

logger = logging.getLogger("myeview.ai_report")

# Defaults — the admin can override provider/endpoint/model via app_settings.
DEFAULT_PROVIDER = "deepseek"
DEFAULT_ENDPOINT = "https://api.deepseek.com/chat/completions"
DEFAULT_MODEL = "deepseek-v4-flash"

# Ollama Cloud (alternative provider)
OLLAMA_ENDPOINT = "https://ollama.com/api/chat"
OLLAMA_MODEL = "glm-4.7-flash"

PROVIDER_PRESETS = {
    "deepseek": {"endpoint": DEFAULT_ENDPOINT, "model": DEFAULT_MODEL},
    "ollama": {"endpoint": OLLAMA_ENDPOINT, "model": OLLAMA_MODEL},
}

# Cap the size of each raw_payload sent to the model so a single huge
# evidence blob (e.g. a 200-row subdomain list) doesn't blow the context
# window or the request budget. The model sees a trimmed but
# representative slice.
MAX_PAYLOAD_CHARS = 2000
MAX_EVIDENCE_ITEMS = 40


def _get_setting(db: Session, key: str) -> str | None:
    row = db.query(AppSetting).filter(AppSetting.key == key).first()
    return row.value if row else None


def get_ai_config(db: Session) -> dict[str, str | None]:
    """Read the AI report config from app_settings.

    The `ai_provider` setting ("deepseek" or "ollama") selects the
    provider preset (endpoint + model). The admin can still override the
    endpoint/model explicitly via `ai_endpoint`/`ai_model`.
    """
    provider = _get_setting(db, "ai_provider") or DEFAULT_PROVIDER
    preset = PROVIDER_PRESETS.get(provider, PROVIDER_PRESETS[DEFAULT_PROVIDER])
    return {
        "provider": provider,
        "api_key": _get_setting(db, "ai_api_key"),
        "endpoint": _get_setting(db, "ai_endpoint") or preset["endpoint"],
        "model": _get_setting(db, "ai_model") or preset["model"],
    }


def _trim(value: Any, limit: int = MAX_PAYLOAD_CHARS) -> Any:
    """Recursively trim long strings in a JSON-serializable structure."""
    if isinstance(value, str):
        return value if len(value) <= limit else value[:limit] + "…[truncated]"
    if isinstance(value, list):
        return [_trim(v, limit) for v in value[:MAX_EVIDENCE_ITEMS]]
    if isinstance(value, dict):
        return {k: _trim(v, limit) for k, v in value.items()}
    return value


def build_scan_summary(db: Session, scan_run_id: str) -> dict[str, Any]:
    """Assemble a compact JSON summary of a scan for the LLM.

    Pulls together: scan metadata, the rule-based score (for reference),
    every vector finding (key + state), every category score (points
    lost), and the raw evidence payloads from each collector (DNS, TLS,
    HTTP, WHOIS, threat intel, asset discovery). The raw payloads are
    the richest signal — they contain the actual headers, TLS versions,
    DNS records, and threat-feed hits the model needs to reason about
    the org's real posture.
    """
    run = db.query(ScanRun).filter(ScanRun.id == scan_run_id).first()
    if not run:
        raise ValueError(f"ScanRun {scan_run_id} not found")

    org = run.organization
    score = run.score

    # Vector findings: key + state + evidence_ref
    vectors = [
        {
            "key": vf.vector.key,
            "name": vf.vector.name,
            "state": vf.state,
            "evidence_ref": vf.evidence_ref,
        }
        for vf in run.vector_findings
    ]

    # Scan completeness: which collectors actually produced data
    collectors_with_data = set()
    collectors_empty = []
    for re_ in run.raw_evidence:
        payload = re_.raw_payload if isinstance(re_.raw_payload, dict) else {}
        if payload:
            collectors_with_data.add(re_.collector_name)
        else:
            collectors_empty.append(re_.collector_name)
    # Vectors that are NOT_OBSERVED (scan couldn't make a determination)
    not_observed_vectors = [v["key"] for v in vectors if v["state"] == "NOT_OBSERVED"]
    failed_vectors = [v["key"] for v in vectors if v["state"] == "FAIL"]
    warn_vectors = [v["key"] for v in vectors if v["state"] == "WARN"]

    # Category scores: where points were lost
    categories = [
        {
            "key": cs.category.key,
            "name": cs.category.name,
            "parent_group": cs.category.parent_group,
            "points_total": cs.category.points_total,
            "points_lost": cs.points_lost,
            "points_remaining": cs.points_remaining,
        }
        for cs in run.category_scores
        if cs.category.scored
    ]

    # Raw evidence per collector — the actual technical observations.
    evidence = {}
    for re_ in run.raw_evidence:
        payload = re_.raw_payload if isinstance(re_.raw_payload, dict) else {}
        evidence.setdefault(re_.collector_name, []).append(_trim(payload))

    return {
        "organization": {
            "name": org.name,
            "domain": org.primary_domain,
            "sector": org.sector,
        },
        "scan": {
            "id": str(run.id),
            "status": run.status,
            "is_full_report": run.is_full_report,
            "started_at": run.started_at.isoformat() if run.started_at else None,
            "finished_at": run.finished_at.isoformat() if run.finished_at else None,
            "completeness": {
                "collectors_with_data": sorted(collectors_with_data),
                "collectors_empty": sorted(set(collectors_empty)),
                "not_observed_vectors": not_observed_vectors,
                "failed_vectors": failed_vectors,
                "warn_vectors": warn_vectors,
                "total_vectors": len(vectors),
                "total_collectors_with_data": len(collectors_with_data),
            },
        },
        "rule_based_score": {
            "overall_score": score.overall_score if score else None,
            "shield_tier": score.shield_tier if score else None,
            "outlook": score.outlook if score else None,
        },
        "vector_findings": vectors,
        "category_scores": categories,
        "raw_evidence": evidence,
    }


SYSTEM_PROMPT = """You are MYEVIEW's senior cyber-trust analyst — a CISO-grade advisor assessing the external digital posture of Cameroonian organizations (banks, credit unions, telcos, government bodies, SMEs). You are given passive scan evidence and must produce a comprehensive, actionable security report.

You will receive a JSON summary of a scan containing:
- Organization metadata (name, domain, sector)
- Scan status and completeness
- The rule-based score (for reference — you may override it)
- Every vector finding (PASS/WARN/FAIL/NOT_OBSERVED state)
- Category point deductions
- Raw technical evidence from each collector (DNS records, TLS versions/ciphers, HTTP security headers, WHOIS/RDAP, threat-intel feeds, subdomain/asset discovery, email authentication records)

YOUR ANALYSIS METHODOLOGY:
1. Read the RAW EVIDENCE carefully — not just the pass/fail states. The raw_payload fields contain the actual technical observations (specific TLS versions, actual HTTP headers, real DNS records, threat feed timestamps). Quote specifics in your analysis.
2. Cross-reference findings across collectors. E.g., if TLS shows 1.0/1.1 enabled alongside 1.3, that's worse than the rule score reflects. If a cert expires in <30 days, flag it as urgent. If HSTS exists but lacks preload, note the gap. If threat intel shows a recent malware pulse, escalate severity.
3. Identify SCAN QUALITY issues — which collectors returned no data, which vectors are NOT_OBSERVED, whether the scan completed fully. This affects confidence in the assessment.
4. For CRITICAL and HIGH severity findings, provide a Proof of Concept (PoC) showing how the weakness could be demonstrated or exploited. Be specific and technical.
5. You are NOT bound by the rule-based tier. If the evidence warrants a different score, assign one. But justify it in the executive_summary and risk_factors.

You MUST respond with a single JSON object (no markdown fences, no prose before or after) matching exactly this schema:
{
  "overall_score": <integer 0-1000>,
  "shield_tier": <integer 1-5>,
  "outlook": "<short string: 'Positive', 'Watch', 'Elevated Risk', or 'MYETREND: available after 90 days' for a first scan>",
  "executive_summary": "<3-5 sentence paragraph referencing the org name, the most material findings, and the overall posture. Be specific — mention actual TLS versions, missing headers, threat hits, etc.>",
  "risk_factors": [
    {
      "key": "<category key from the input, must match exactly>",
      "name": "<category name>",
      "severity": "critical|high|medium|low",
      "tia": {
        "technical_observation": "<what was ACTUALLY observed in the evidence — cite specifics like 'TLS 1.0 and 1.1 are enabled on port 443 alongside TLS 1.3' or 'HSTS header absent from response; max-age not set' or 'SPF record is ~all (soft fail) allowing spoofing'>",
        "business_impact": "<what real risk this creates for the institution — e.g. 'Man-in-the-middle attacks can intercept banking traffic' or 'Email spoofing enables phishing of customers'>",
        "stakeholders_affected": ["<group1>", "<group2>"],
        "regulatory_relevance": "<relevant Cameroon/regional regulation if any: ANTIC Law 2010/012, Data Protection Law 2024/017, COBAC. Else 'Low'>",
        "recommended_action": "<concrete fix step — not 'improve security' but 'Disable TLS 1.0/1.1 in nginx server block; set ssl_protocols TLSv1.2 TLSv1.3;' or 'Add DMARC record at _dmarc.domain with p=reject to block spoofed email'>"
      }
    }
  ],
  "proofs_of_concept": [
    {
      "title": "<short name of the PoC>",
      "finding_ref": "<category key or vector key this PoC relates to>",
      "severity": "critical|high",
      "description": "<what the vulnerability or weakness is>",
      "steps": [
        "<step 1: concrete reproduction command or action, e.g. 'openssl s_client -connect domain:443 -tls1' to verify TLS 1.0 acceptance>",
        "<step 2: ...>",
        "<step 3: ...>"
      ],
      "impact": "<what an attacker could achieve if this is exploited>"
    }
  ],
  "scan_quality_notes": {
    "completeness": "<'complete' | 'partial' | 'incomplete' — based on how many collectors returned data>",
    "missing_or_failed": [
      "<collector or vector that returned no data or failed, e.g. 'WHOIS/RDAP returned no registrar data' or 'Subdomain discovery found 0 results (may indicate DNS is not enumerated)' or 'Threat intel feed returned no hits (not necessarily good — may be a new domain)'>"
    ],
    "coverage_gaps": [
      "<area where the scan could not make a determination, e.g. 'DKIM selector not known — DKIM signing status cannot be verified without knowing the selector' or 'Port scan not authorized — open port inventory is unavailable'>"
    ],
    "confidence": "<'high' | 'medium' | 'low' — how confident you are in the overall score given the scan completeness>"
  },
  "hygiene": [
    {"title": "<short>", "description": "<short, specific>", "status": "ok|warn|info"}
  ],
  "conclusion": "<3-4 sentence closing paragraph. Summarize the posture, acknowledge what was assessed vs what couldn't be assessed, and give a forward-looking recommendation. Speak in the institution's context — e.g. 'Bayelle Credit Union should prioritize...'"
}

RULES:
- shield_tier 1 = Critical (score <400), 2 = Elevated (400-549), 3 = Moderate (550-699), 4 = Strong (700-849), 5 = Exceptional (850-1000).
- Only include risk_factors for categories with material deductions or real observed problems. If everything is clean, return an empty array.
- proofs_of_concept: ONLY for critical and high severity findings. If none are critical/high, return an empty array. Be specific with commands (openssl, curl, dig, nmap, nslookup) that a technician can run to verify the issue.
- hygiene should cover: HTTPS enforcement, Security headers (HSTS, CSP, X-Frame-Options), TLS version, Exposed admin interfaces, Email authentication (SPF/DKIM/DMARC), DNSSEC, Certificate validity.
- For a first scan with no history, outlook must be "MYETREND: available after 90 days".
- Be SPECIFIC and TECHNICAL in technical_observation — quote the actual evidence (exact header values, TLS versions, DNS records). Be INSTITUTIONAL in business_impact and conclusion.
- In recommended_action, provide CONCRETE fixes with actual config directives or DNS record formats, not vague advice.
- scan_quality_notes: Be honest about what the scan couldn't determine. If a collector returned empty data, say so. This helps the reader understand the confidence level.
- regulatory_relevance: Reference Cameroon laws specifically when applicable (ANTIC 2010/012 for cybersecurity, Law 2024/017 for data protection, COBAC for financial institutions).
- Output ONLY the JSON. No markdown, no explanation, no text before or after."""


def _call_llm(
    endpoint: str,
    api_key: str,
    model: str,
    summary: dict[str, Any],
    provider: str = DEFAULT_PROVIDER,
) -> dict[str, Any]:
    """Call an OpenAI-compatible chat completions endpoint.

    Supports DeepSeek (default) and Ollama Cloud. Both use Bearer auth
    and a messages array; DeepSeek additionally accepts the `thinking`
    parameter to disable chain-of-thought (faster, cheaper, and avoids
    leaking reasoning tokens into the content field). Uses urllib so
    there's no new dependency. Non-streaming. Raises RuntimeError on
    auth failure or non-JSON model output.
    """
    user_msg = json.dumps(summary, ensure_ascii=False)
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        "temperature": 0.3,
        "stream": False,
    }
    if provider == "deepseek":
        # Disable DeepSeek's internal chain-of-thought so the response
        # content field is the raw JSON we asked for, not reasoning text.
        payload["thinking"] = {"type": "disabled"}

    body = json.dumps(payload).encode()

    req = urllib.request.Request(endpoint, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {api_key}")

    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode()[:500]
        logger.error("LLM API error %s: %s", e.code, detail)
        raise RuntimeError(f"AI provider returned HTTP {e.code}: {detail}") from None
    except urllib.error.URLError as e:
        logger.error("LLM API connection error: %s", e)
        raise RuntimeError(f"Could not reach AI provider: {e}") from None

    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise RuntimeError(f"Unexpected AI provider response shape: {str(data)[:300]}")

    # The model may wrap JSON in markdown fences despite instructions —
    # strip them defensively before parsing.
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[-1]
        if content.endswith("```"):
            content = content.rsplit("```", 1)[0]
        content = content.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        logger.error("LLM returned non-JSON: %s", content[:500])
        raise RuntimeError(f"AI returned invalid JSON: {e}") from None


def generate_ai_report(db: Session, scan_run_id: str) -> dict[str, Any]:
    """End-to-end: assemble evidence, call the LLM, persist and return the result.

    The AI result is stored on the Score row (ai_result JSONB +
    ai_generated_at) so it can be rendered later via the report endpoints
    without re-calling the LLM.

    Raises RuntimeError with a human-readable message on any failure
    (missing key, auth error, non-JSON output). The caller maps this to
    an HTTP error.
    """
    config = get_ai_config(db)
    if not config["api_key"]:
        raise RuntimeError("No AI API key configured. Set it in Admin Settings first.")

    # Verify the scan run exists and has a score
    run = db.query(ScanRun).filter(ScanRun.id == scan_run_id).first()
    if not run:
        raise ValueError(f"ScanRun {scan_run_id} not found")
    if not run.score:
        raise RuntimeError("Scan has no score yet — wait for the scan to complete first.")

    summary = build_scan_summary(db, scan_run_id)
    ai = _call_llm(
        config["endpoint"],
        config["api_key"],
        config["model"],
        summary,
        provider=config.get("provider") or DEFAULT_PROVIDER,
    )

    # Persist the AI result onto the Score row so report endpoints can
    # render it without re-calling the LLM.
    run.score.ai_result = ai
    run.score.ai_generated_at = datetime.now(timezone.utc)
    db.commit()

    return {
        "ai": ai,
        "provider": {
            "name": config.get("provider") or DEFAULT_PROVIDER,
            "endpoint": config["endpoint"],
            "model": config["model"],
        },
        "scan_run_id": scan_run_id,
        "summary_size_bytes": len(json.dumps(summary)),
        "ai_report_path": f"/api/reports/{scan_run_id}/ai",
    }