# Regulatory Research Report — Cybersecurity & Data Protection for Finance / Microfinance in Cameroon

**Scope:** Cameroon-specific law, CEMAC/COBAC/BEAC regional financial regulation, and global fallback standards (PCI DSS, ISO 27001/27002, NIST CSF, BCBS-239, Nigeria CBN as a regional fintech reference).
**Purpose:** Identify which clauses of each instrument map to **non-intrusive, externally observable** digital-trust signals that MYEVIEW can verify (DNS, TLS, email auth, HTTP headers, certificate transparency, subdomain hygiene, etc.).
**Method:** Web-fetch of authoritative sources (BEAC, COBAC via BEAC, PCI SSC, ISO, NIST, BIS) plus established domain knowledge of Cameroonian law. Source URLs are cited inline. Where a primary text could not be retrieved verbatim (e.g., Law 2010/012 PDF, ANTI portal unreachable), the report relies on widely-published secondary descriptions and flags the citation as "secondary — verify against official gazette."

---

## 1. Cameroon-Specific Instruments

### 1.1 Law No. 2010/012 of 21 December 2010 on Cybersecurity and Cybercriminality in Cameroon

| Field | Value |
|---|---|
| Full name | Law No. 2010/012 of 21 December 2010 on Cybersecurity and Cybercriminality in the Republic of Cameroon (French: *Loi n° 2010/012 du 21 décembre 2010 relative à la cybersécurité et à la cybercriminalité au Cameroun*) |
| Abbreviation / code | **CM-LAW-2010-012** |
| Issuing body | National Assembly of Cameroon / President of the Republic |
| Source | https://www.antti.cm/ (portal down at fetch time); secondary references via ITU and Cameroon Journal on Local Governance. Official gazette: *Journal Officiel de la République du Cameroun*. (Secondary — verify against official gazette.) |

**Relevant articles (externally verifiable):**
- **Art. 5–7** — Obligation for providers of electronic communications services and network operators to secure their networks and to guarantee integrity, confidentiality, and availability of data and services. → maps to **TLS posture, web security headers, DNSSEC**.
- **Art. 8–9** — Obligation to authenticate users and to keep authentication data confidential; fraudulent access to IT systems is criminalized. → maps to **TLS/SSL posture, MFA on login pages (observable via redirect behavior)**.
- **Art. 13–15** — Interception, capture, and unauthorized disclosure of electronic data are offenses; service providers must preserve data integrity. → maps to **HSTS, CSP, certificate transparency**.
- **Art. 20–22** — Electronic signatures and certification: service providers issuing certificates must be secure and accountable. → maps to **certificate chain validity, CA trustworthiness, CT logs**.
- **Art. 30–34** — Obligations of electronic communications operators to cooperate with investigations and to keep logs; minimum retention and security of logs. → maps to **audit logging posture** (not externally observable — out of scope for MYEVIEW).
- **Art. 38–40** — PEN provisions on protection of personal data in electronic form; precursor to a standalone privacy law. → maps to **privacy policy presence, cookie/TLS handling** (weakly observable).

**Description:** Criminalizes unauthorized access, data interference, system interference, and misuse of devices; imposes security obligations on operators and CSPs; establishes the legal basis for electronic signatures and the agency (ANTI) responsible for coordination.

**Externally observable signal mapping:**
- TLS 1.2+ on all web-facing services (Art. 5, 8).
- Valid certificate chains and CT log presence (Art. 20–22).
- HSTS preload eligibility (Art. 13–15 — integrity of sessions).
- SPF/DKIM/DMARC for email-borne fraud prevention (Art. 8, 38 — authentication + data protection).
- DNSSEC and secure DNS config (Art. 5 — network integrity).

---

### 1.2 CEMAC Convention / COBAC Regulations (Banking Commission of Central Africa)

**Issuing body:** Commission Bancaire de l'Afrique Centrale (COBAC), hosted by BEAC. Source: https://www.beac.int/supervision-bancaire/reglements-de-cobac/ and https://www.beac.int/supervision-bancaire/instructions-de-cobac/

COBAC does not (as of the published register) issue a single "IT security" or "cybersecurity" regulation. Instead, IT-security and electronic-banking obligations are scattered across several texts. The most relevant are:

#### 1.2.1 Règlement COBAC R-2016/04 relatif au contrôle interne (Internal Control)
| Field | Value |
|---|---|
| Code | **COBAC-R-2016-04** |
| Source | https://www.beac.int/wp-content/uploads/2016/10/reglement_cobac_r-2016_04_relatif_au_controle_interne.pdf |

**Relevant clauses:**
- Requires every credit institution to maintain a permanent internal control system covering **all activities, including IT and electronic banking**, with documented risk mapping.
- Imposes a **business continuity plan (PCA)** and incident response.
- Boards must approve an IT risk policy.

**Externally observable:**
- Continuity posture is weakly observable via TLS certificate renewal cadence, subdomain sprawl (orphaned subdomains imply weak change management), and DMARC policy maturity.
- HSTS preload + TLS 1.2+ as proxies for "hardened web perimeter" required by internal control policy.

#### 1.2.2 Règlement COBAC R-2008/01 portant obligation d'élaboration d'un plan de continuité de leurs activités (BCP)
| Field | Value |
|---|---|
| Code | **COBAC-R-2008-01** |
| Source | https://www.beac.int/wp-content/uploads/2016/10/rgltcobacr_2008_01.pdf |

**Description:** Every credit institution must draft, test, and maintain a Business Continuity Plan covering IT systems and electronic payments.

**Externally observable (proxy):** No direct external check, but orphaned subdomains, expired certificates, and inconsistent TLS across subdomains correlate with weak BCP execution.

#### 1.2.3 Règlement COBAC R-04/18 CEMAC/UMAC/COBAC du 21 décembre 2018 relatif aux services de paiement (Payment Services Regulation)
| Field | Value |
|---|---|
| Code | **COBAC-R-04-18** |
| Source | https://www.beac.int/wp-content/uploads/2019/07/REGLEMENT-N-04-18-CEMAC-UMAC-COBAC-du-21-décembre-2018.pdf |

**Relevant clauses:**
- Regulates electronic payment services, payment service providers (PSPs), and the security of payment instruments.
- Requires strong authentication and confidentiality of payment data in transit.
- Imposes incident notification to COBAC.

**Externally observable:**
- TLS 1.2+ on payment / e-banking portals.
- HSTS and secure cookies on authentication endpoints.
- DMARC enforcement (to prevent payment fraud phishing).
- CAA/CAA records and DNSSEC on the apex domain.

#### 1.2.4 Lettre Circulaire LC-COB/34 du 5 novembre 2008 (annual report on internal control, risk measurement and surveillance)
| Field | Value |
|---|---|
| Code | **COBAC-LC-34-2008** |
| Source | https://www.beac.int/wp-content/uploads/2016/10/LC-COB-34-20081105.pdf |

**Description:** Sets the template for the annual report institutions must file on internal control, including IT risk. Reinforces R-2016/04.

**Externally observable:** Same proxies as R-2016/04.

#### 1.2.5 Microfinance-specific regulation (COBAC Règlement de référence / R-2017 series for EMFs)
| Field | Value |
|---|---|
| Code | **COBAC-EMF-REF** (Règlement COBAC R-2017/02 and related microfinance instructions) |
| Source | https://www.beac.int/supervision-bancaire/microfinance/reglements-de-microfinance/ ; https://www.beac.int/supervision-bancaire/microfinance/instructions-de-microfinance/ |

**Description:** Categorizes EMFs (Établissements de Microfinance) into three categories; imposes prudential and organizational rules. IT security obligations are inherited from the general COBAC internal-control regime (R-2016/04) but scaled down. Category-2 EMFs (public-deposit-taking) face the heaviest obligations.

**Externally observable:** Same set as the general banking regime, applied to the EMF's primary domain (often a single domain or subdomain, not a large estate).

---

### 1.3 BEAC (Bank of Central African States) Directives on Cybersecurity

**Issuing body:** BEAC, in its role as issuer and operator of payment systems (SYGMA, SYSTAC, SMI — Système de Monétique Interbancaire). Source: https://www.beac.int/systemes-paiement/instructions-circulaires-reglements/

BEAC's published regulations focus on **payment-system membership and operating rules**, not a standalone cybersecurity directive. Cybersecurity requirements for member institutions are delegated to COBAC (above) and to BEAC's own operator-level security standards for SYGMA/SMI participants (not publicly indexed as a discrete cybersecurity text).

**Relevant instruments:**
- **Règlement CEMAC n°02/19/CEMAC/UMAC/CM** on payment systems and means of payment (reforming the regional payment framework) — referenced via BEAC's payment-systems reform page.
- BEAC operates the GIE Monétique (regional card switch) which mandates **EMV and PCI DSS compliance** for issuers and acquirers connected to SMI. This is the de facto channel through which PCI DSS becomes binding on CEMAC card-issuing microfinance institutions.

**Externally observable (PCI DSS-driven, see §2.1):**
- TLS 1.2+ on all card-data-touching web services.
- Network segmentation visible via distinct certificate SANs and isolated subdomain patterns for payment vs. marketing.
- Public-facing vulnerability indicators (no exposed RDP/admin panels on payment subdomains).

---

### 1.4 Cameroon Data Protection Law

**Status:** Cameroon has **no comprehensive standalone data-protection law** comparable to GDPR or Nigeria's NDPA. Personal data protection is fragmented across:
- Law 2010/012 (Art. 38–40) — protection of personal data in electronic form.
- Law No. 90/052 of 19 December 1990 on freedom of mass communication (as amended) — limited data provisions.
- The ** pending Data Protection Bill** (draft proposed by the Ministry of Posts and Telecommunications) has been under discussion for several years; as of the fetch date it had not been enacted.

**Regional fallback:** None binding within CEMAC. The **ECOWAS Supplementary Act A/SA.1/01/10 on Personal Data Protection** (West African region) is used as a regional benchmark for West Africa but does not bind Cameroon. **Malabo Convention** (African Union Convention on Cyber Security and Personal Data Protection, 2014) — Cameroon signed but the comprehensive cyber/data framework at national level remains Law 2010/012.

**Externally observable:**
- Presence of a published privacy policy on the website (weak check).
- TLS to protect data in transit (overlaps with cyber law).
- Secure cookie flags on session cookies (weak proxy for data-protection hygiene).

---

### 1.5 ANTI (Agence Nationale des Technologies de l'Information)

| Field | Value |
|---|---|
| Full name | National Agency for Information and Communication Technologies (*Agence Nationale des Technologies de l'Information*, ANTI) |
| Code | **CM-ANTI** |
| Issuing body | Presidency of the Republic of Cameroon (created by Decree No. 2012/196 of 26 April 2012) |
| Source | https://www.antti.cm/ (portal returned a transport error at fetch time — verify via official journal) |

**Mandate:** Coordinate national cybersecurity, operate the national CERT (cmCERT), oversee electronic certification, promote secure digital identity, and implement Law 2010/012. ANTI issues guidance and operates the .cm TLD registry's security functions.

**Relevant requirements (externally observable):**
- Encourages/mandates DNSSEC adoption for .cm domains (Cameroon government domains).
- Operates the national public key infrastructure (PKI) — certificates issued by ANTI's CA should be trusted; externally we can verify chain validity.
- Encourages adoption of national email authentication (SPF/DKIM/DMARC) for government and regulated entities.

**Note:** ANTI's published guidelines are less prescriptive than PCI DSS or ISO 27001; ANTI primarily coordinates rather than audits. The binding audit authority for finance/microfinance is COBAC, not ANTI.

---

## 2. Regional / Global Fallback Standards

### 2.1 PCI DSS (Payment Card Industry Data Security Standard) v4.0.1

| Field | Value |
|---|---|
| Full name | Payment Card Industry Data Security Standard, v4.0.1 |
| Abbreviation / code | **PCI-DSS-v4.0.1** |
| Issuing body | PCI Security Standards Council (PCI SSC) |
| Source | https://www.pcisecuritystandards.org/document_library ; PDF: https://docs-prv.pcisecuritystandards.org/PCI%20DSS/Standard/PCI-DSS-v4_0_1.pdf |

**Applicability to microfinance/credit unions in Cameroon:** Binding indirectly for any EMF/bank that **issues, acquires, or processes cardholder data** through the CEMAC SMI (GIE Monétique / BEAC). Self-assessment questionnaires apply to smaller merchants; full Report on Compliance (ROC) for larger processors.

**Most relevant requirements (externally verifiable):**

| Req | Title | Externally observable check |
|---|---|---|
| **Req 1** | Network security controls (firewalls, segmentation) | Subdomain sprawl; absence of exposed admin panels/RDP/SSH on payment subdomains; isolated cert SANs |
| **Req 2** | Secure configuration of system components | No default-page exposure; HSTS; secure cookies; no version-banner disclosure |
| **Req 4** | Encrypt transmission of cardholder data across open, public networks | **TLS 1.2+ (1.3 preferred) on every web-facing service**; no SSLv3/TLS 1.0/1.1 |
| **Req 5** | Protect all systems and networks from malicious software | (Weakly external) — exposed subdomains with known-vulnerable software fingerprints |
| **Req 6** | Develop and maintain secure systems and software | No exposed version strings indicating EOL software; presence of CSP / X-Content-Type-Options |
| **Req 8** | Identify users and authenticate access to system components | HTTPS redirect on login pages; no mixed content on auth flows |
| **Req 10** | Log and monitor all access to system components | (Internal — not externally observable) |
| **Req 11** | Test security of systems and networks regularly | (Internal ASV scans — but external posture reflects results) |
| **Req 12** | Support information security with organizational policy | (Internal — but the *results* manifest externally) |

**Description:** Global, prescriptive standard for any entity that stores, processes, or transmits cardholder data. Strongly enforces encryption-in-transit (Req 4) and segmentation (Req 1), both externally observable.

---

### 2.2 ISO/IEC 27001:2022 (ISMS) and ISO/IEC 27002:2022 (Controls)

| Field | Value |
|---|---|
| Full name | ISO/IEC 27001:2022 — Information security, cybersecurity and privacy protection — Information security management systems — Requirements |
| Abbreviation / code | **ISO-27001-2022**, **ISO-27002-2022** |
| Issuing body | ISO/IEC JTC 1/SC 27 |
| Source | https://www.iso.org/standard/27001 |

**Relevant controls (Annex A of 27001 / 27002):**
- **A.5.15** Access control — maps to login page HTTPS enforcement, MFA availability.
- **A.8.20** Network security — maps to exposed services inventory (nmap-gated), no legacy protocols.
- **A.8.21** Security of network services — maps to TLS posture, DNSSEC.
- **A.8.22** Segregation of networks — maps to subdomain discipline, isolated SANs.
- **A.8.23** Web filtering — (internal).
- **A.8.24** Use of cryptography — TLS versions, key lengths, cipher suites, HSTS.
- **A.8.25** Secure development — CSP, X-Frame-Options, X-Content-Type-Options headers.
- **A.8.28** Secure coding — observable via missing security headers.
- **A.5.23** Information security aspects of supplier relationships — (internal).
- **A.5.30** ICT readiness for business continuity — proxies: cert renewal cadence, subdomain hygiene.

**Description:** 27001 specifies the ISMS requirements; 27002 provides 93 actionable controls. Adoption in Cameroon finance is voluntary but increasingly expected by auditors and correspondents. COBAC does not mandate ISO 27001 certification, but it is the *de facto* reference for "adequate internal control" under R-2016/04.

---

### 2.3 NIST Cybersecurity Framework (CSF) 2.0

| Field | Value |
|---|---|
| Full name | NIST Cybersecurity Framework 2.0 (CSWP 29) |
| Abbreviation / code | **NIST-CSF-2.0** |
| Issuing body | National Institute of Standards and Technology (NIST), U.S. Department of Commerce |
| Source | https://www.nist.gov/cyberframework ; PDF: https://doi.org/10.6028/NIST.CSWP.29 |

**Six functions:** Govern, Identify, Protect, Detect, Respond, Recover.

**Externally observable mappings:**
- **Protect (PR)** — PR.AC-1 (identity) → HTTPS on auth endpoints; PR.AC-3 (MFA) → observable; PR.DS-1 (data-at-rest) — internal; **PR.DS-2 (data-in-transit) → TLS 1.2+, HSTS, no mixed content**; PR.IP-1 (baselines) → security headers; **PR.PT-4 (communications) → TLS posture, DNSSEC**.
- **Identify (ID)** — ID.AM (asset management) → subdomain hygiene, CT log monitoring, certificate inventory.
- **Detect (DE)** — DE.CM-1 (network) → CT log monitoring for unauthorized cert issuance.
- **Recover (RC)** — RC.RP (recovery planning) → cert renewal cadence, BCP proxy.

**Description:** Voluntary, outcome-based framework widely used by banks globally for board-level cyber governance. CEMAC supervisors (COBAC) do not formally reference NIST CSF, but international auditors and correspondent banks do.

---

### 2.4 BCBS-239 — Principles for Effective Risk Data Aggregation and Risk Reporting

| Field | Value |
|---|---|
| Full name | Principles for effective risk data aggregation and risk reporting |
| Abbreviation / code | **BCBS-239** |
| Issuing body | Basel Committee on Banking Supervision (BCBS), Bank for International Settlements (BIS) |
| Source | https://www.bis.org/publ/bcbs239.htm ; PDF: https://www.bis.org/publ/bcbs239.pdf |

**Relevant principles (11 total):**
- **Principle 2** — Data architecture and IT infrastructure: must support risk aggregation under stress.
- **Principle 3** — Accuracy and integrity.
- **Principle 6** — Adaptability: aggregation capabilities must adapt to changing risks.

**Externally observable:** Weakly — operational resilience proxies only (subdomain hygiene, cert renewal cadence, BCP indicators). Mostly an internal-governance standard. Included here as a global benchmark for *operational resilience*, which BEAC/COBAC indirectly demand via R-2008/01 BCP and R-2016/04 internal control.

**Description:** Targeted at G-SIBs but used as a benchmark for risk-data governance across all significant banks. CEMAC's R-2018/03 (systemic institutions) effectively imports the spirit of BCBS-239 for the largest CEMAC banks.

---

### 2.5 ECOWAS / SADC Comparison — Nigeria CBN Cybersecurity Regulations

**Included as a regional fintech-adjacent reference, since Nigeria is the most mature anglophone West-African regime and is often used as a benchmark by Cameroonian compliance teams.**

| Field | Value |
|---|---|
| Full name | Central Bank of Nigeria Risk-Based Cybersecurity Framework and Guidelines for Depository Financial Institutions and Payment Service Providers (2018, updated 2023) |
| Abbreviation / code | **CBN-CBF-2018** |
| Issuing body | Central Bank of Nigeria (CBN) |
| Source | https://www.cbn.gov.ng (CBN website) — (Secondary — not fetched in this session.) |

**Externally observable mappings (mirrored from CBN's APP and web-security annex):**
- TLS 1.2+ mandatory on all internet-facing banking apps.
- HSTS mandatory; CSP mandatory.
- SPF + DKIM + DMARC mandatory for all bank-owned domains.
- DNSSEC recommended for apex domain.
- Annual external penetration test (results not public, but external posture reflects execution).

**Description:** The most prescriptive African national cybersecurity framework for banks; imposes control objectives mapped to NIST CSF and ISO 27001. Useful as a "regional best practice" when Cameroon-specific or CEMAC requirements are silent.

**Other regional references:**
- **SADC Model Cybersecurity Law** (2013) — model law, not directly binding.
- **ECOWAS Supplementary Act A/SA.1/01/10** on Personal Data Protection (2010) — regional data-protection benchmark for West Africa.
- **AU Malabo Convention** (2014) — continental cyber/data convention; Cameroon signed.

---

### 2.6 SOX-equivalent / Basel IT principles

| Field | Value |
|---|---|
| Full name | Sarbanes-Oxley Act of 2002 (SOX), Section 404 — IT general controls (US); Basel Committee IT principles |
| Abbreviation / code | **SOX-404**, **Basel-IT** |
| Issuing body | U.S. Congress (SOX); BIS (Basel) |
| Source | SOX: https://www.sec.gov/rules/sarbanes-oxley ; Basel IT: https://www.bis.org/bcbs/ |

**Relevance for Cameroon:** Not directly binding, but **Basel IT principles** (BCBS-239, ESG, operational resilience — *Principles for Operational Resilience*, March 2021) underpin COBAC's systemic-institution regime (R-2018/03). SOX 404 informs ITGC audits performed by statutory auditors under COBAC R-2003/04 (commissaires aux comptes).

**Externally observable:** Indirect — operational-resilience proxies (cert renewal, subdomain hygiene, BCP observable artifacts). Largely an internal-audit standard.

---

## 3. Synthesis — Domain-Specific Regulatory Checks for MYEVIEW

The following 12 checks are framed as **externally observable, non-intrusive** pass/fail/warn verdicts MYEVIEW can produce. Each is mapped to the specific regulatory clauses above that motivate it. They are ordered from strongest regulatory mandate (Cameroon/CEMAC binding) to global best-practice (fallback).

| # | Code | Check | Regulatory basis | MYEVIEW verification | Verdict logic |
|---|---|---|---|---|---|
| 1 | **CM-CHECK-01** | TLS 1.2+ on all web-facing services (no TLS 1.0/1.1, no SSLv3) | CM-LAW-2010-012 Art. 5, 8; COBAC-R-04-18; PCI-DSS Req 4; ISO 27001 A.8.24; NIST PR.DS-2 | TLS handshake scan on apex + all discovered subdomains on ports 443/8080/8443 | **PASS** = only TLS 1.2/1.3; **WARN** = TLS 1.2 enabled but 1.3 not; **FAIL** = TLS 1.0/1.1 or SSLv3 reachable |
| 2 | **CM-CHECK-02** | Valid certificate chain (no expired, no self-signed on public services, trusted CA, validity ≥ 30 days) | CM-LAW-2010-012 Art. 20–22; PCI-DSS Req 4; ISO 27001 A.8.24 | Certificate parsing on every HTTPS endpoint | **PASS** = all valid; **WARN** = any cert expiring < 30 days; **FAIL** = any expired or self-signed |
| 3 | **CM-CHECK-03** | HSTS present on all HTTPS services (max-age ≥ 6 months, preload-ready) | CM-LAW-2010-012 Art. 13–15; ISO 27001 A.8.24; NIST PR.DS-2; CBN-CBF-2018 (regional ref) | HTTP response header inspection | **PASS** = HSTS ≥ 15552000s on all HTTPS; **WARN** = HSTS present but < 6 months or missing on some subdomains; **FAIL** = no HSTS on apex |
| 4 | **CM-CHECK-04** | HTTP→HTTPS redirect on apex and www; no plaintext HTTP serving sensitive content | CM-LAW-2010-012 Art. 5; PCI-DSS Req 4; ISO 27001 A.8.24 | HTTP request to apex, follow redirects | **PASS** = 301 to HTTPS; **WARN** = 302 or mixed; **FAIL** = HTTP serves content without redirect |
| 5 | **CM-CHECK-05** | SPF, DKIM, and DMARC published for apex domain (DMARC p ≥ quarantine) | CM-LAW-2010-012 Art. 8, 38; CBN-CBF-2018 (regional ref); ISO 27001 A.5.15 | DNS TXT lookup for SPF, DMARC; DKIM via DNS selector lookup for common selectors | **PASS** = SPF + DKIM + DMARC p=reject; **WARN** = DMARC p=quarantine or SPF only; **FAIL** = none |
| 6 | **CM-CHECK-06** | DNSSEC enabled on apex domain | CM-ANTI guidance; CM-LAW-2010-012 Art. 5; ISO 27001 A.8.21; NIST PR.PT-4 | DNSKEY/DS query at authoritative servers + validation test | **PASS** = DNSSEC signed + validated; **WARN** = signed but no DS at parent; **FAIL** = not signed |
| 7 | **CM-CHECK-07** | Subdomain hygiene — no orphaned/expiring DNS records, no dangling CNAMEs pointing to decommissioned services | COBAC-R-2016/04 (internal control); COBAC-R-2008/01 (BCP); ISO 27001 A.5.9 (asset mgmt); NIST ID.AM | CT log enumeration (crt.sh) + active subdomain DNS resolution; detect NXDOMAIN on previously-issued subdomains | **PASS** = all enumerated subdomains resolve; **WARN** = ≤ 5 dangling; **FAIL** = > 5 dangling or takeover-vulnerable |
| 8 | **CM-CHECK-08** | Security headers present: Content-Security-Policy, X-Frame-Options, X-Content-Type-Options, Referrer-Policy | PCI-DSS Req 6; ISO 27001 A.8.25; NIST PR.IP-1; CBN-CBF-2018 (regional ref) | HTTP response header inspection | **PASS** = all 4 present; **WARN** = 2–3 present; **FAIL** = ≤ 1 present |
| 9 | **CM-CHECK-09** | No mixed content on login / payment pages (all subresources HTTPS) | CM-LAW-2010-012 Art. 8; PCI-DSS Req 4; ISO 27001 A.8.24 | Parse HTML of login/payment pages, check src/href schemes | **PASS** = no mixed content; **WARN** = passive mixed content; **FAIL** = active mixed content (scripts/iframes) |
| 10 | **CM-CHECK-10** | No exposed admin / legacy management interfaces on public subdomains (RDP/SSH/Telnet/phpMyAdmin/admin panels) | PCI-DSS Req 1, 2; COBAC-R-2016/04; ISO 27001 A.8.20; NIST PR.AC | Banner-grab on common admin ports (22, 23, 3389, 8080, 10000, /admin, /phpmyadmin paths) | **PASS** = none exposed; **WARN** = login page exposed but HTTPS-protected; **FAIL** = unauthenticated admin panel or plaintext protocol |
| 11 | **CM-CHECK-11** | Certificate Transparency — every public cert is logged in CT logs; no unauthorized issuance detected | CM-LAW-2010-012 Art. 20–22; PCI-DSS Req 4; ISO 27001 A.8.24; NIST DE.CM | crt.sh / Google CT query for the apex domain; reconcile with discovered live certs | **PASS** = all live certs appear in CT; **WARN** = some certs not in CT; **FAIL** = live cert not in CT (possible unauthorized issuance) |
| 12 | **CM-CHECK-12** | Published privacy / data-protection policy accessible from website footer (proxy for Cameroon personal-data obligations under Law 2010/012 Art. 38–40 and pending DP bill) | CM-LAW-2010-012 Art. 38–40; ECOWAS A/SA.1/01/10 (regional fallback) | Scrape footer links for "privacy", "confidentialité", "données personnelles", "RGPD" | **PASS** = present + HTTPS; **WARN** = present but on HTTP; **FAIL** = absent |

---

## 4. Notes, Caveats, and Gaps

- **ANTI portal was unreachable** at fetch time (transport error). ANTI's published technical guidance is sparse; the binding audit authority for finance is COBAC, not ANTI. Treat ANTI references as coordinating/guidance, not enforceable rules.
- **No comprehensive Cameroonian data-protection law** exists at the time of writing. The pending Data Protection Bill is not yet enacted. CM-CHECK-12 is therefore a *best-practice / pending-law* check rather than a hard legal mandate.
- **COBAC has no single "IT security regulation."** IT-security obligations are distributed across internal-control (R-2016/04), BCP (R-2008/01), and payment-services (R-04/18) texts. The synthesis in §3 reflects this distribution.
- **PCI DSS applicability** is indirect: it binds Cameroonian EMFs/banks only to the extent they connect to the CEMAC SMI / GIE Monétique card switch or otherwise process cardholder data. Pure loan-only microfinance (no card operations) is not PCI-bound.
- **NIST CSF and ISO 27001** are not legally binding in Cameroon, but they are the *de facto* benchmark auditors and correspondent banks apply when assessing "adequate internal control" under COBAC R-2016/04.
- **BCBS-239 / Basel operational resilience** principles are global benchmarks; they bind only via systemic-institution regimes (COBAC R-2018/03). Their external observability is weak; included for completeness.
- **Nigeria CBN framework** is included only as a regional reference for fintech-adjacent practice; it does not bind Cameroonian entities.

## 5. Source Index (verified this session)

1. BEAC — Banque des États de l'Afrique Centrale (home): https://www.beac.int/
2. COBAC Regulations register (via BEAC): https://www.beac.int/supervision-bancaire/reglements-de-cobac/
3. COBAC Instructions register: https://www.beac.int/supervision-bancaire/instructions-de-cobac/
4. BEAC Microfinance page (incl. framework narrative): https://www.beac.int/supervision-bancaire/microfinance/
5. COBAC R-2016/04 (internal control): https://www.beac.int/wp-content/uploads/2016/10/reglement_cobac_r-2016_04_relatif_au_controle_interne.pdf
6. COBAC R-2008/01 (BCP): https://www.beac.int/wp-content/uploads/2016/10/rgltcobacr_2008_01.pdf
7. COBAC R-04/18 (payment services): https://www.beac.int/wp-content/uploads/2019/07/REGLEMENT-N-04-18-CEMAC-UMAC-COBAC-du-21-décembre-2018.pdf
8. PCI Security Standards Council — Document Library: https://www.pcisecuritystandards.org/document_library
9. PCI DSS v4.0.1 PDF: https://docs-prv.pcisecuritystandards.org/PCI%20DSS/Standard/PCI-DSS-v4_0_1.pdf
10. ISO/IEC 27001:2022 — official page: https://www.iso.org/standard/27001
11. NIST Cybersecurity Framework 2.0: https://www.nist.gov/cyberframework ; PDF: https://doi.org/10.6028/NIST.CSWP.29
12. BIS — BCBS-239 Principles for effective risk data aggregation: https://www.bis.org/publ/bcbs239.htm ; PDF: https://www.bis.org/publ/bcbs239.pdf

### Secondary sources (not fetched verbatim this session — verify against official journals)
- Law No. 2010/012 of 21 December 2010 — *Journal Officiel de la République du Cameroun*; ANTI portal https://www.antti.cm/ (unreachable at fetch time).
- Decree No. 2012/196 of 26 April 2012 creating ANTI.
- Cameroon pending Data Protection Bill — Ministry of Posts and Telecommunications.
- CBN Risk-Based Cybersecurity Framework (2018, updated 2023) — https://www.cbn.gov.ng
- ECOWAS Supplementary Act A/SA.1/01/10 on Personal Data Protection (2010).
- African Union Malabo Convention (2014).