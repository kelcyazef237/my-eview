# Regulatory Research Report — Cybersecurity & Data Protection for FINTECH / PAYMENTS / MOBILE MONEY in Cameroon

**Scope:** Cameroon-specific law and fintech/e-payments decrees, CEMAC/COBAC/BEAC regional financial regulation (e-money issuers, payment service providers, mobile money), and global fallback standards (PCI DSS incl. SAQ-A/A-EP, PSD2 SCA-RTS, ISO 27001/27002, NIST CSF, Nigeria CBN Risk-Based Cybersecurity Framework, FSB cybersecurity recommendations, SWIFT CSP).
**Purpose:** Identify which clauses of each instrument map to **non-intrusive, externally observable** digital-trust signals that MYEVIEW can verify (TLS posture on payment pages / API endpoints, email security (SPF/DKIM/DMARC), HSTS, certificate transparency, subdomain exposure of API gateways, DNSSEC, presence of security.txt, etc.).
**Method:** Web-fetch of authoritative and secondary sources (BEAC, COBAC via BEAC and Cameroon DGTCFM, PCI SSC, ISO, NIST, European Commission, CBN/Mondaq, PACMap, ICT Policy Africa, ResearchGuru, VOVE ID, Bejuka & Partners). Source URLs are cited inline. Where a primary text could not be retrieved verbatim, the report relies on widely-published secondary descriptions and flags the citation as "secondary — verify against official gazette."
**Companion document:** `docs/regulatory-research-finance-cameroon.md` covers the finance/microfinance angle (EMFs, credit institutions). This document focuses on **fintech, payment service providers (PSPs), e-money issuers (EMIs), and mobile money operators (MMOs)** — a related but distinct regulatory perimeter.

---

## 1. Cameroon-Specific Instruments

### 1.1 Law No. 2010/012 of 21 December 2010 on Cybersecurity and Cybercriminality

| Field | Value |
|---|---|
| Full name | Law No. 2010/012 of 21 December 2010 Relating to Cybersecurity and Cybercriminality in Cameroon (French: *Loi n° 2010/012 du 21 décembre 2010 relative à la cybersécurité et à la cybercriminalité au Cameroun*) |
| Abbreviation / code | **CM-LAW-2010-012** |
| Issuing body | National Assembly of Cameroon / President of the Republic |
| Source (primary) | https://www.antic.cm/images/stories/laws/Law%20relating%20to%20cybersecurity%20and%20cybercriminality%20in%20Cameroon.pdf |
| Source (secondary) | https://pacmap.dev/regulation/cm-cybersecurity-cybercrime-2010 ; https://www.ictpolicyafrica.org/en/document/xr0onx7xbq ; https://art.cm/sites/default/files/documents/loi_2010-012_cybersecurite_cybercriminalite.pdf ; https://www.afapdp.org/wp-content/uploads/2018/05/Cameroun-Loi-relative-a-la-cybersecurite-et-a-la-cybercriminalite-du-21-decembre-2010.pdf |

**Relevant articles (externally verifiable):**
- **Part II, Ch. I (Electronic Security & General Cybersecurity)** — service providers and network operators must implement technical security measures (intrusion detection, access controls, data integrity) and undergo **mandatory security audits and certification** by ANTIC before and during operations. → maps to **TLS posture, web security headers, DNSSEC, subdomain hygiene**.
- **Part II, Ch. IX (Protection of Networks, Information Systems & Privacy)** — obligations to protect confidentiality, integrity, availability of electronic communications and personal data; access/service/content providers bear specific duties. → maps to **HSTS, CSP, certificate transparency, secure cookies**.
- **Part II, Ch. VI (Electronic Signature) & Ch. VII (Electronic Certificates)** — legal regime for certification authorities; certificates must meet strict technical standards. → maps to **certificate chain validity, CA trustworthiness, CT logs**.
- **Section 73 (payment card fraud)** — specific offence; fine of 25,000,000–50,000,000 CFA. → reinforces that **payment page security is a legal, not just contractual, obligation**.
- **Sections 25, 35, 42, 46** — electronic communications records retention ≥ 10 years. (Internal — not externally observable.)
- **Section 61** — unauthorized disclosure by audit personnel: 3 months–3 years, 20,000–100,000 CFA.

**Description:** Cameroon's primary cybersecurity and cybercrime legislation. Governs security of electronic communication networks, criminalizes cyber offences (unauthorized access, data manipulation, payment card fraud, identity theft), establishes the legal regime for digital evidence, cryptography and electronic certification, and mandates security audits for service providers. Penalties range from 3 months to 10 years imprisonment and up to 100,000,000 CFA. No suspended sentences available.

**Enforcement:** ANTIC (National Agency for Information and Communication Technologies); ANTIC-CIRT for incident response.

**Externally observable signal mapping:**
- TLS 1.2+ on all web-facing services (Part II, Ch. I & IX).
- Valid certificate chains and CT log presence (Ch. VI–VII).
- HSTS preload eligibility (Ch. IX — session integrity).
- SPF/DKIM/DMARC for email-borne fraud prevention (Ch. IX + Section 73 on payment card fraud).
- DNSSEC and secure DNS config (Ch. I — network integrity).
- Presence of security.txt / vulnerability disclosure channel (Ch. I — security audit posture, weak proxy).

---

### 1.2 Law No. 2024/017 of 23 December 2024 on Personal Data Protection (NEW — replaces the "no data law" gap)

| Field | Value |
|---|---|
| Full name | Law No. 2024/017 Relating to Personal Data Protection in Cameroon (French: *Loi n° 2024/017 du 23 décembre 2024 relative à la protection des données personnelles au Cameroun*) |
| Abbreviation / code | **CM-PDPL-2024** |
| Issuing body | Parliament of Cameroon / President of the Republic |
| Status | **In-force**; 18-month transition period expiring **23 June 2026** |
| Source (primary) | https://prc.cm/en/multimedia/documents/10271-law-n-2024-017-of-23-12-2024-web |
| Source (secondary) | https://pacmap.dev/regulation/cm-personal-data-protection-2024 |

**Relevant requirements (externally verifiable):**
- **Valid informed consent** before processing personal data; transparency about purpose, duration, recipients. → maps to **presence of privacy policy, cookie consent mechanism** (weakly observable).
- **Registration with the Personal Data Protection Authority** + appoint a **Data Protection Officer** for large-scale/sensitive processing. (Internal — not observable.)
- **Sensitive data categories** (biometrics, health, genetic, political, religious, racial/ethnic) require explicit legal authorization. → maps to **TLS strength on biometric/KYC endpoints** (e.g., eKYC APIs).
- **Cross-border transfer** requires **prior approval** from the Authority; sender and recipient **jointly liable**. → maps to **geographic location of API endpoints / hosting** (observable via IP geolocation, CDN headers).
- **Technical & organizational security measures**: data minimization, purpose limitation, storage limitation. → maps to **TLS, HSTS, secure cookies, SPF/DKIM/DMARC** as proxies.
- **Data breach notification** to the Authority promptly; maintain **records of processing activities**. (Internal.)
- **Compliance deadline: 23 June 2026** (18-month transition). Executives face **personal liability**.

**Description:** Cameroon's first comprehensive personal data protection law, modeled on GDPR principles. Extraterritorial — applies to processing of personal data of Cameroonian nationals, residents, even individuals transiting through Cameroon. Penalties: administrative fines up to 100,000,000 XAF (~USD 160,000); criminal penalties up to 10 years imprisonment and fines up to 1,000,000,000 XAF (~USD 1.6M).

**Externally observable signal mapping:**
- Presence of published privacy policy on fintech website (CM-PDPL-2024 consent obligation).
- TLS on all pages collecting personal/KYC data.
- HSTS + secure cookies on session/authentication endpoints.
- SPF/DKIM/DMARC (data-in-transit protection for email channels).
- IP geolocation of API endpoints (cross-border transfer compliance proxy).

**Note:** This **supersedes** the statement in the companion finance report (§1.4) that "Cameroon has no comprehensive standalone data-protection law." As of 23 December 2024, Cameroon now has one. The companion report predates enactment.

---

### 1.3 MINFI Decree of 28 February 2024 on Electronic Payment Service Providers (NEW)

| Field | Value |
|---|---|
| Full name | Ministerial Decree of 28 February 2024 governing the licensing and regulation of electronic payment service providers in Cameroon (French: *Arrêté du Ministre des Finances relatif à l'agrément et à la régulation des prestataires de services de paiement électronique*) |
| Abbreviation / code | **CM-MINFI-EPAY-2024** |
| Issuing body | Ministry of Finance (MINFI), Republic of Cameroon |
| Source (secondary) | https://bejukapartners.com/2025/07/22/new-regulation-on-electronic-payments-in-cameroon/ (verify against official gazette) |

**Relevant requirements (externally verifiable):**
- **Mandatory MINFI accreditation**, after **COBAC assent**, for any entity offering electronic payment services. → maps to **public registry lookup** (fintech should appear on DGTCFM "Approved payment institutions" list).
- Application must include **financial and technical guarantees** + **robust security measures**. (Internal — but external posture reflects execution.)
- **Operations via the Treasury Single Account**. (Internal.)
- **Local hosting of databases** (hébergement local des bases de données). → maps to **IP geolocation of API endpoints / DNS** — observable via IP geolocation of A/AAAA records.
- **Strict adherence to security and confidentiality standards**. → maps to **TLS, HSTS, SPF/DKIM/DMARC, security.txt, DNSSEC**.
- **Customer funds remain property of customers** (segregation). (Internal.)
- **Telecom-operator subsidiaries must implement functional separation within 3 months** or face license withdrawal. → maps to **distinct domains / IP ranges for the MMO subsidiary vs. the telecom parent** (observable).

**Description:** Major reform aligning Cameroon's e-payments sector with CEMAC standards. Establishes MINFI as the national licensing authority (with COBAC assent), imposes local data hosting, security/confidentiality obligations, and forces structural separation of mobile-money arms from telecom parents.

**Externally observable signal mapping:**
- Fintech domain appears in DGTCFM public registry: https://dgtcfm.cm/en/payment-institution/approved-payment-institutions/ (PASS if listed, WARN if not found, FAIL if operating unlicensed).
- API endpoints / DNS records resolve to Cameroonian IP space (local hosting) — observable via IP geolocation.
- MMO subsidiary uses a distinct domain / certificate SAN from the telecom parent (functional separation).
- TLS 1.2+, HSTS, SPF/DKIM/DMARC, DNSSEC, security.txt on the fintech's apex domain.

---

### 1.4 CEMAC / COBAC Regulations on E-Money Issuers and Payment Service Providers

**Issuing bodies:** Commission Bancaire de l'Afrique Centrale (COBAC), hosted by BEAC; and UMAC (Union Monétaire de l'Afrique Centrale) of CEMAC. Source register: https://www.beac.int/supervision-bancaire/reglements-de-cobac/

#### 1.4.1 Regulation n° 01/11-CEMAC/UMAC/CM of 18 September 2011 — E-money issuer conditions

| Field | Value |
|---|---|
| Full name | Regulation n° 01/11-CEMAC/UMAC/CM of 18 September 2011 setting the conditions to exercise the activity of e-money issuer, and the roles of the regulatory authorities |
| Abbreviation / code | **CEMAC-R-01-11-EMI** |
| Issuing body | CEMAC / UMAC (Council of Ministers) |
| Source (secondary) | https://researchguru.pro/the-legal-and-institutional-framework-for-mobile-money-services-in-cameroon/ (cite §1.1.1.1) — verify against BEAC/CEMAC official journal |

**Relevant requirements:**
- Only **credit institutions** (banks) may issue e-money in CEMAC; mobile network operators (MNOs) act as **technical partners** (bank-centered model, unlike Kenya's M-Pesa). → maps to **verification that the MMO's domain is owned by / partnered with a licensed bank**.
- License application must include: **network and security architecture**; **internal control plan** for activity-related risks; **technical platform presentation** (software, hardware, network, security). (Internal — but external posture reflects.)
- BEAC Governor issues authorization after Technical Committee opinion (BEAC experts + COBAC SG + e-money regulator); published in national gazette.

**Externally observable:**
- MMO domain WHOIS / footer disclosure of the licensed banking partner.
- TLS posture of the MMO's payment / wallet endpoints.
- Subdomain discipline (no orphaned test/staging endpoints leaking API keys).

#### 1.4.2 BEAC Order n° 01/GR of 31 October 2011 — Monitoring of e-money payment systems

| Field | Value |
|---|---|
| Full name | Order n° 01/GR of 31 October 2011 from the Governor of BEAC on the monitoring of e-money payment systems |
| Abbreviation / code | **BEAC-ORD-01-GR-2011** |
| Source (secondary) | https://researchguru.pro/... (cite §1.1.1.2) — verify against BEAC official journal |

**Description:** Defines BEAC's oversight function to promote **security and efficiency** of payment systems by monitoring them against technical, legal, and functional norms. Applies to both endogenous and exogenous (third-party) payment systems.

**Externally observable:** BEAC oversight is internal, but it is the channel through which PCI DSS and TLS expectations propagate to PSPs connected to regional switches.

#### 1.4.3 BEAC Order n° 02/GR/UMAC of 7 May 2014 — Multi-banking for e-money issuance

| Field | Value |
|---|---|
| Full name | Order n° 02/GR/UMAC of 7 May 2014 from the Governor of BEAC on the implementation of multi-banking as part of the issuance of e-money |
| Abbreviation / code | **BEAC-ORD-02-GR-2014** |
| Source (secondary) | https://researchguru.pro/... (cite §1.1.1.3) — verify against BEAC official journal |

**Relevant requirements:**
- Technical manager of a multi-banking network must obtain **BEAC certification** (valid only for e-money issuance activity).
- Application must include: **network and security architecture** of the technical platform; **internal control system** for risks; software/hardware operating licenses and technical certifications. (Internal — external posture reflects.)
- Settlement Account Agreement + framework agreement mandatory.

**Externally observable:** Same set as §1.4.1 — TLS, DNSSEC, email auth, subdomain hygiene on the technical manager's / PSP's domains.

#### 1.4.4 COBAC Regulation R-2019/01 — Authorization and changes of status of payment service providers

| Field | Value |
|---|---|
| Full name | COBAC Regulation R-2019/01 on the authorization and changes of status of payment service providers |
| Abbreviation / code | **COBAC-R-2019-01** |
| Issuing body | COBAC |
| Source (primary) | https://dgtcfm.cm/en/payment-institution/conditions-for-authorising-a-payment-institution/ (Cameroon DGTCFM page explicitly states it is "drawn up in accordance with COBAC Regulation R-2019/01") |

**Relevant requirements (from the DGTCFM application checklist):**
- **Procedure manuals** required for: **internal control system**, **information system management**, **business continuity plan**, **AML/CFT**, **monitoring of outsourced operations**, **corporate governance charter**.
- **Five-year business plan** including technical, financial, human resources.
- **Provisional balance sheets and income statements for 5 years**.
- **Technical assistance agreement** with a reference partner (if applicable).
- **Certificate of prior agreement / letter of no objection** from the banking supervisory authority of the country of origin (foreign applicants).

**Externally observable:**
- BCP posture proxies: cert renewal cadence, subdomain hygiene, no expired/orphaned DNS records.
- IS management posture proxies: TLS, security headers, no exposed admin panels, no version-banner disclosure.
- Outsourcing monitoring proxies: distinct certificate SANs / IP ranges for third-party-hosted components (e.g., if payment page is hosted by a PSP SaaS, its cert should be visible and consistent).

#### 1.4.5 COBAC R-04/18 CEMAC/UMAC/COBAC of 21 December 2018 — Payment services regulation

| Field | Value |
|---|---|
| Full name | Règlement n° 04/18 CEMAC/UMAC/COBAC du 21 décembre 2018 relatif aux services de paiement |
| Abbreviation / code | **COBAC-R-04-18** |
| Issuing body | CEMAC / UMAC / COBAC |
| Source | https://www.beac.int/wp-content/uploads/2019/07/REGLEMENT-N-04-18-CEMAC-UMAC-COBAC-du-21-décembre-2018.pdf |

**Relevant clauses:**
- Regulates electronic payment services, PSPs, and security of payment instruments.
- Requires **strong authentication** and **confidentiality of payment data in transit**.
- Imposes **incident notification to COBAC**.

**Externally observable:**
- TLS 1.2+ on payment / e-banking / wallet endpoints.
- HSTS and secure cookies on authentication endpoints.
- DMARC enforcement (to prevent payment fraud phishing).
- CAA records and DNSSEC on the apex domain.
- MFA availability on login flows (observable via redirect behavior, presence of OTP/2FA prompts in page HTML).

#### 1.4.6 COBAC R-2016/04 — Internal control (carries over from finance report)

| Field | Value |
|---|---|
| Abbreviation / code | **COBAC-R-2016-04** |
| Source | https://www.beac.int/wp-content/uploads/2016/10/reglement_cobac_r-2016_04_relatif_au_controle_interne.pdf |

**Relevant clauses:** Every credit institution (incl. e-money issuers) must maintain a permanent internal control system covering **all activities, including IT and electronic banking**, with documented risk mapping; **business continuity plan (PCA)**; board-approved IT risk policy.

**Externally observable (proxy):** Continuity posture via TLS certificate renewal cadence, subdomain sprawl, DMARC maturity. HSTS preload + TLS 1.2+ as proxies for "hardened web perimeter."

#### 1.4.7 COBAC R-2008/01 — Business Continuity Plan (carries over)

| Field | Value |
|---|---|
| Abbreviation / code | **COBAC-R-2008-01** |
| Source | https://www.beac.int/wp-content/uploads/2016/10/rgltcobacr_2008_01.pdf |

**Description:** Every credit institution must draft, test, and maintain a BCP covering IT systems and electronic payments.

**Externally observable (proxy):** Orphaned subdomains, expired certificates, inconsistent TLS across subdomains correlate with weak BCP execution.

---

### 1.5 Law No. 2003/004 of 21 April 2003 — Banking Secrecy

| Field | Value |
|---|---|
| Full name | Law n° 2003/004 of 21 April 2003 governing banking secrecy in Cameroon |
| Abbreviation / code | **CM-LAW-2003-004** |
| Source (secondary) | https://researchguru.pro/... (cite §1.2.3) — verify against official gazette |

**Relevant clauses:** Banking secrecy extends to **MNOs, retailers, and agents** in contact with confidential customer information. Distinguishes confidential (account balances, movements, writings) from non-confidential (general) information. Criminal penalties for violation.

**Externally observable:** Indirect — drives the expectation that MMO agent portals / APIs enforce TLS + auth + audit. Maps to TLS on agent-facing endpoints, MFA on agent login, no plaintext protocols.

---

### 1.6 ANIF — National Financial Investigation Agency (AML/CFT)

| Field | Value |
|---|---|
| Full name | Agence Nationale d'Investigation Financière (ANIF) — Cameroon's Financial Intelligence Unit |
| Abbreviation / code | **CM-ANIF** |
| Source | https://anif.cm/ ; https://blog.voveid.com/kyc-compliance-in-cameroon-2025-guide-to-digital-identity-and-aml-regulations/ |

**Relevant requirements (externally verifiable — weakly):**
- **Suspicious Transaction Reports (STRs)** filed with ANIF within **48 hours** of detection. (Internal.)
- **KYC data retention: 10 years** (per COBAC + Law 2010/012). (Internal.)
- **Beneficial Ownership disclosure** — UBOs declared. (Internal.)

**Externally observable:** Mostly internal. Presence of a KYC / AML policy page on the fintech website (weak proxy). FATF grey-list status drives stricter compliance — external posture maturity reflects.

---

### 1.7 ANTIC — National Agency for Information and Communication Technologies

| Field | Value |
|---|---|
| Full name | National Agency for Information and Communication Technologies (*Agence Nationale des Technologies de l'Information et de la Communication*, ANTIC) |
| Abbreviation / code | **CM-ANTIC** |
| Issuing body | Presidency of the Republic (created by Decree No. 2012/196 of 26 April 2012) |
| Source | https://www.antic.cm/index.php/en/the-agency/presentation.html |

**Mandate:** Coordinate national cybersecurity, operate **cmCERT** (national CERT), oversee electronic certification, promote secure digital identity, implement Law 2010/012. Operates .cm TLD registry security functions.

**Relevant requirements (externally observable):**
- Encourages/mandates **DNSSEC adoption** for .cm domains.
- Operates the national **PKI** — certificates issued by ANTIC's CA should be trusted; externally we verify chain validity.
- Encourages adoption of national **email authentication (SPF/DKIM/DMARC)** for government and regulated entities.
- Incident reporting to cmCERT.

**Note:** ANTIC's published guidelines are less prescriptive than PCI DSS or ISO 27001; ANTIC primarily coordinates rather than audits. The binding audit authority for fintech/PSPs is **COBAC + MINFI**, not ANTIC.

---

## 2. Regional / Global Fallback Standards

### 2.1 PCI DSS (Payment Card Industry Data Security Standard) v4.0.1

| Field | Value |
|---|---|
| Full name | Payment Card Industry Data Security Standard, v4.0.1 (June 2024) |
| Abbreviation / code | **PCI-DSS-v4.0.1** |
| Issuing body | PCI Security Standards Council (PCI SSC) — Visa, Mastercard, Amex, Discover, JCB |
| Source | https://www.pcisecuritystandards.org/document_library/ (current active version; v4.0 retired 31 Dec 2024, v4.0.1 compliance deadline 31 March 2025) |

**Applicability to Cameroon fintech/PSPs/MMOs:** Binding indirectly for any entity that **issues, acquires, or processes cardholder data** through the CEMAC SMI (GIE Monétique / BEAC regional card switch). EMV and PCI DSS compliance is the de facto channel through which PCI DSS becomes binding on CEMAC card-issuing PSPs and acquirers. Pure mobile-money / wallet operators not handling card data are not directly PCI-bound, but the standard is the global reference for payment security and is increasingly written into PSP contracts.

**The 12 requirements (v4.0.1):**

| Req | Title | Externally observable check |
|---|---|---|
| **Req 1** | Install and maintain network security controls (firewalls, segmentation) | Subdomain sprawl; absence of exposed admin panels/RDP/SSH on payment subdomains; isolated cert SANs for payment vs. marketing |
| **Req 2** | Apply secure configurations to all system components | No default-page exposure; HSTS; secure cookies; no version-banner disclosure; presence of CSP |
| **Req 3** | Protect stored account data | (Internal — tokenization not externally observable) |
| **Req 4** | Protect cardholder data with strong cryptography during transmission over open, public networks | **TLS 1.2+ (1.3 preferred) on every web-facing service**; no SSLv3/TLS 1.0/1.1; PFS cipher suites |
| **Req 5** | Protect all systems and networks from malicious software | (Weakly external) — exposed subdomains with known-vulnerable software fingerprints |
| **Req 6** | Develop and maintain secure systems and software | No exposed version strings indicating EOL software; presence of CSP, X-Content-Type-Options, X-Frame-Options |
| **Req 7** | Restrict access to system components and cardholder data by business need to know | (Internal) |
| **Req 8** | Identify users and authenticate access to system components | HTTPS redirect on login pages; no mixed content on auth flows; MFA on admin portals |
| **Req 9** | Restrict physical access to cardholder data | (Physical — not externally observable) |
| **Req 10** | Log and monitor all access to system components and cardholder data | (Internal) |
| **Req 11** | Test security of systems and networks regularly | (Internal ASV scans — but external posture reflects results; presence of security.txt / bug-bounty link is a weak proxy) |
| **Req 12** | Support information security with organizational policies and programs | (Internal — results manifest externally) |

**Description:** Global, prescriptive standard for any entity that stores, processes, or transmits cardholder data and/or sensitive authentication data. Enforces encryption-in-transit (Req 4) and segmentation (Req 1), both externally observable. Enforced by payment card brands via acquirer contracts and fines.

---

### 2.2 PCI DSS Self-Assessment Questionnaires (SAQs) — SAQ-A and SAQ-A-EP for e-commerce / hosted payment pages

| Field | Value |
|---|---|
| Full name | PCI DSS Self-Assessment Questionnaires — SAQ-A (card-present, fully outsourced; no electronic storage, processing, or transmission of CHD by the merchant) and SAQ-A-EP (e-commerce, website redirects to a PCI-DSS-compliant third-party payment processor) |
| Abbreviation / code | **PCI-SAQ-A**, **PCI-SAQ-A-EP** |
| Issuing body | PCI Security Standards Council |
| Source | https://www.pcisecuritystandards.org/ (Document Library → SAQ category) |

**SAQ-A:** Applicable to merchants who **only use fully-outsourced payment processing** (e.g., a hosted payment page on a third-party PSP domain). The merchant's own website never touches CHD. → MYEVIEW should verify that **the payment form's action URL points to a third-party PSP domain** (not the merchant's own domain) and that **the PSP domain has TLS 1.2+ and HSTS**.

**SAQ-A-EP:** Applicable to **e-commerce merchants** whose website **redirects** customers to a PCI-DSS-compliant third-party processor. The merchant's website does not store/process/transmit CHD itself, but it **initiates the redirect and may host the payment button**. Strictly requires: TLS 1.2+ on the merchant's own website, secure cookies, HSTS, vulnerability management, and **a web-application firewall (WAF) or consistent application-layer controls**. → MYEVIEW should verify **TLS on the merchant site + HSTS + security headers + presence of a WAF (cloud WAF like Cloudflare/Akamai/AWS WAF often observable via response headers)**.

**Externally observable (SAQ-A-EP specifically — the most common SAQ for fintech e-commerce):**
- TLS 1.2+ on **the merchant's own website** (not just the PSP's).
- HSTS on the merchant site.
- CSP, X-Frame-Options, X-Content-Type-Options headers.
- Redirect to a PSP domain on payment-button click.
- WAF presence (Server header, CDN headers, challenge pages).
- No payment form fields (PAN, CVV) present in the HTML of the merchant's own pages.

**Code mapping:** PCI-SAQ-A-EP covers Req 1, 2, 3, 4, 5, 6, 8, 10, 11, 12 in reduced scope. Req 4 (TLS) is **fully applicable** to the merchant's own site under SAQ-A-EP.

---

### 2.3 PSD2 (Revised Payment Services Directive) — Strong Customer Authentication & Secure Communication (global reference)

| Field | Value |
|---|---|
| Full name | Directive (EU) 2015/2366 (PSD2) + Commission Delegated Regulation (EU) 2018/389 (Regulatory Technical Standards on Strong Customer Authentication and Common and Secure Communication — SCA-RTS / CSC-RTS) |
| Abbreviation / code | **PSD2**, **PSD2-SCA-RTS**, **PSD2-CSC-RTS** |
| Issuing body | European Commission / European Banking Authority (EBA) |
| Source | https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex:32015L2366 (PSD2) ; https://eur-lex.europa.eu/eli/reg_del/2018/389/oj (SCA-RTS, 27 Nov 2017) ; https://en.wikipedia.org/wiki/Payment_Services_Directive |

**Relevance for Cameroon:** Not legally binding on Cameroonian entities, but the **global reference standard** for payment authentication security. Cited by international auditors, correspondent banks, and card schemes as the benchmark for SCA. Many card schemes (Visa, Mastercard) export SCA-like requirements globally via 3-D Secure 2.x.

**Most relevant articles (externally verifiable):**

- **SCA-RTS Art. 4** — Strong Customer Authentication: two or more independent factors (knowledge + possession + inherence). → maps to **MFA presence on login/payment flows** (observable via OTP/2FA prompts in page HTML, biometric SDK signatures in mobile apps).
- **SCA-RTS Art. 5** — Dynamic linking of the transaction to a specific amount and payee. (Internal to the payment flow — weakly observable.)
- **SCA-RTS Art. 30** — Account information service providers (AISPs) must communicate with ASPSPs (banks) over **common and secure open standards**. → maps to **API endpoint TLS posture**.
- **CSC-RTS Art. 4a (eIDAS qualified certificates for website authentication)** — ASPSPs exposing interfaces to PISPs/AISPs must use **eIDAS-qualified certificates for website authentication** and **electronic seals** for API responses. ETSI TS 119 495 defines the standard. → maps to **certificate chain validation, presence of Qualified eIDAS certificates (observable via cert extension: QCStatements / OID 0.4.0.1862.1.5)**.
- **PSD2 Art. 96** — Security of payment services: PSPs must mitigate fraud, manage operational/security risks, and report major incidents. (Internal.)

**Externally observable signal mapping:**
- MFA / 2FA prompts on login & payment authorization pages (SCA Art. 4).
- 3-D Secure 2.x redirect on card payment flows (Visa/Mastercard global export of SCA).
- TLS 1.2+ on all open-banking / API endpoints (CSC Art. 30).
- eIDAS qualified certificates on ASPSP API endpoints (CSC Art. 4a) — cert extension inspection.
- HSTS on all authentication surfaces.

**Description:** EU directive mandating strong customer authentication for electronic payments and common, secure open standards for bank-PSP communication. In force since 14 September 2019 (full SCA enforcement 31 Dec 2020 after EBA extension). Globally referenced by card schemes and auditors.

---

### 2.4 ISO/IEC 27001:2022 (ISMS) and ISO/IEC 27002:2022 (Controls)

| Field | Value |
|---|---|
| Full name | ISO/IEC 27001:2022 — Information security, cybersecurity and privacy protection — Information security management systems — Requirements; ISO/IEC 27002:2022 — Information security controls |
| Abbreviation / code | **ISO-27001-2022**, **ISO-27002-2022** |
| Issuing body | ISO/IEC JTC 1/SC 27 |
| Source | https://www.iso.org/standard/27001 ; https://www.iso.org/standard/75652.html (27002) ; https://en.wikipedia.org/wiki/ISO/IEC_27001 ; https://en.wikipedia.org/wiki/ISO/IEC_27002 |

**Relevant controls (Annex A of 27001:2022 / 27002:2022, 93 controls across 4 themes):**
- **A.5.15** Access control — login page HTTPS enforcement, MFA availability.
- **A.8.20** Network security — exposed services inventory, no legacy protocols on public subdomains.
- **A.8.21** Security of network services — TLS posture, DNSSEC.
- **A.8.22** Segregation of networks — subdomain discipline, isolated SANs for payment vs. marketing.
- **A.8.23** Web filtering — (internal).
- **A.8.24** Use of cryptography — TLS versions, key lengths, cipher suites, HSTS, PFS.
- **A.8.25** Secure development — CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy.
- **A.8.28** Secure coding — observable via missing security headers, exposed stack traces.
- **A.5.23** Information security in supplier relationships — (internal).
- **A.5.30** ICT readiness for business continuity — proxies: cert renewal cadence, subdomain hygiene.
- **A.5.7** Threat intelligence — (internal; presence of security.txt is a weak proxy).

**Description:** 27001 specifies the ISMS requirements (certifiable); 27002 provides 93 actionable controls across Organizational, People, Physical, and Technological themes. Adoption in Cameroon fintech is voluntary but increasingly expected by COBAC auditors, correspondent banks, and international partners. CBN's 2024 framework (§2.6) explicitly mandates ISO 27001 for third-party service providers — a regional precedent Cameroon is likely to follow.

---

### 2.5 NIST Cybersecurity Framework (CSF) 2.0

| Field | Value |
|---|---|
| Full name | NIST Cybersecurity Framework 2.0 (CSWP 29) |
| Abbreviation / code | **NIST-CSF-2.0** |
| Issuing body | National Institute of Standards and Technology (NIST), U.S. Department of Commerce |
| Source | https://www.nist.gov/cyberframework ; PDF: https://doi.org/10.6028/NIST.CSWP.29 |

**Six functions:** Govern (new in 2.0), Identify, Protect, Detect, Respond, Recover.

**Externally observable mappings:**
- **Govern (GV)** — GV.OC (organizational context) → presence of security.txt, published security policy (weak proxy); GV.RR (risk management) → (internal).
- **Identify (ID)** — ID.AM (asset management) → subdomain hygiene, CT log monitoring, certificate inventory; ID.RA (risk assessment) → (internal).
- **Protect (PR)** — PR.AC-1 (identity) → HTTPS on auth endpoints; PR.AC-3 (MFA) → observable; **PR.DS-2 (data-in-transit) → TLS 1.2+, HSTS, no mixed content**; PR.IP-1 (baselines) → security headers; **PR.PT-4 (communications) → TLS posture, DNSSEC**.
- **Detect (DE)** — DE.CM-1 (network monitoring) → CT log monitoring for unauthorized cert issuance.
- **Respond (RS)** — (internal).
- **Recover (RC)** — RC.RP (recovery planning) → cert renewal cadence, BCP proxy.

**Description:** Voluntary, outcome-based framework widely used by banks globally for board-level cyber governance. CEMAC supervisors (COBAC) do not formally reference NIST CSF, but international auditors and correspondent banks do. The CBN Nigeria framework (§2.6) is explicitly mapped to NIST CSF.

---

### 2.6 CBN (Central Bank of Nigeria) Risk-Based Cybersecurity Framework for DMBs and PSBs — 2024 edition (regional reference)

| Field | Value |
|---|---|
| Full name | CBN Risk-Based Cybersecurity Framework and Guidelines for Deposit Money Banks and Payment Service Banks (31 May 2024, effective 1 July 2024) |
| Abbreviation / code | **CBN-CBF-2024** |
| Issuing body | Central Bank of Nigeria (CBN) |
| Source | https://www.mondaq.com/nigeria/security/1518574/overview-of-the-cbn-risk-based-cybersecurity-framework-and-guidelines-for-deposit-money-banks-and-payment-service-banks (G Elias analysis) ; https://gelias.com/images/Newsletter/_Overview_of_the_CBN_Risk-Based_Cyber_Security_Framework.pdf |

**Relevance for Cameroon:** Not binding on Cameroonian entities, but the **most prescriptive African national cybersecurity framework for banks and PSPs**, and the regional benchmark Nigerian fintech compliance teams (and increasingly Cameroonian ones) reference. CEMAC supervisors cite it as a model.

**Key externally-relevant provisions (from the 2024 Framework):**

1. **Cybersecurity Governance & Oversight (Part 1)** — Board, via a Board Risk or IT Committee, holds oversight. **At least 2 non-executive directors** (one independent) must have **ICT/cybersecurity knowledge**. Quarterly board reports on: cyber risk assessment, security initiatives, incident counts/losses/recoveries, **vulnerability management / penetration test reports**. → (Internal governance; external posture reflects.)
2. **Cybersecurity Risk Management (Part 2)** — Risk identification (threats/vulns to CIA), annual risk assessment, risk measurement (financial impact), mitigation (reduce/accept/avoid/transfer), monitoring & reporting (independent risk function + risk register). **Third-party risk managers** mandatory; **SLAs must specify the SFI's right to audit third parties or receive audit reports**. **Third-party service providers must comply with PCI DSS, NDPR, ISO 27001, ISO 8385** (Para 2.9). → maps to **TLS, DNSSEC, SPF/DKIM/DMARC, security.txt on the fintech AND its third-party PSP/hosting providers** (observable on both domains).
3. **Enhancing Cybersecurity Resilience (Part 3)** — Know your environment, preventive controls, monitoring/detection, incident response (in-house or outsourced at short notice), industry cyber exercises.
4. **Emerging Technologies (Part 4)** — Contactless payments, QR codes, voice-initiated services, **USSD codes**, open banking, DLT, AI/ML, IoT. **CBN approval required before deployment**; products must not be offered by countries on the sanctions list. → maps to **USSD gateway endpoint TLS posture** (where exposed over IP), API security on open-banking endpoints.
5. **Metrics, Monitoring & Reporting (Part 5)** — KPIs/KRIs/KGIs reviewed annually; **cyber incidents reported to CBN within 24 hours**. → (Internal reporting; but the 24-hour clock rewards mature detection, which correlates with mature external posture.)
6. **Compliance with Statutory & Regulatory Requirements (Part 6)** — Board + senior management must comply with applicable statutes.
7. **Enforcement (Part 7)** — CBN monitors via annual cybersecurity supervisory review, risk-based examinations, annual industry compliance audits, periodic spot checks.

**Externally observable signal mapping (the strongest African benchmark):**
- TLS 1.2+ mandatory on all internet-facing banking/PSP apps.
- HSTS mandatory; CSP mandatory.
- SPF + DKIM + DMARC mandatory for all bank/PSP-owned domains.
- DNSSEC recommended for apex domain.
- Annual external penetration test (results not public, but external posture reflects execution).
- **Third-party providers must be PCI DSS / ISO 27001 compliant** — observable on the third party's domain.

**Description:** The 2024 Framework replaces the 2018 version. Adds explicit board ICT/cyber competency requirements, third-party risk management, emerging-technologies governance (USSD, open banking, DLT, AI), and 24-hour incident reporting. The most prescriptive African national cybersecurity framework for banks and PSPs.

---

### 2.7 FSB (Financial Stability Board) Cybersecurity Recommendations

| Field | Value |
|---|---|
| Full name | FSB Cyber Lexicon (2018) + FSB Cyber Incident Response and Recovery (2020) + FSB Effective Practices for Cyber Incident Response and Recovery (2022) |
| Abbreviation / code | **FSB-CIR-2022** |
| Issuing body | Financial Stability Board (FSB) |
| Source | https://www.fsb.org/work-of-the-fsb/financial-innovation-and-cybersecurity/cybersecurity/ |

**Relevance for Cameroon:** Not legally binding, but the **global benchmark for systemic financial market infrastructures (FMIs)** and G-SIBs. COBAC's systemic-institution regime (R-2018/03) effectively imports the spirit of FSB/BCBS operational resilience principles for the largest CEMAC banks. Cameroon fintechs connected to regional payment switches (SYGMA, SMI) are part of the FMI chain and inherit these expectations.

**Relevant recommendations (externally observable — weakly):**
- **Cyber Lexicon** — common taxonomy; not directly observable.
- **Effective Practices for CIR (2022)** — 7 practices: Governance, Identification, Response, Recovery, Information Sharing, Testing, Improvement. Mostly internal. **Information Sharing** → presence of security.txt / participation in a CERT/FS-ISAC (observable via published policy).
- **Operational Resilience** — recovery time objectives, BCP testing. → cert renewal cadence, subdomain hygiene as proxies.

**Description:** FSB's recommendations target systemic FMIs and G-SIBs but are used as a benchmark for operational resilience and cyber incident response across all significant financial institutions globally.

---

### 2.8 SWIFT Customer Security Programme (CSP) — for cross-border payments

| Field | Value |
|---|---|
| Full name | SWIFT Customer Security Programme — Customer Security Requirements (CSRs) |
| Abbreviation / code | **SWIFT-CSP-CSR** |
| Issuing body | SWIFT (Society for Worldwide Interbank Financial Telecommunication, S.W.I.F.T. SC) |
| Source | https://www.swift.com/myswift/customer-security-programme ; https://en.wikipedia.org/wiki/SWIFT (§Security — Bangladesh Bank heist 2016 context) |

**Relevance for Cameroon:** Binding on any Cameroonian bank or PSP that **connects to SWIFT for cross-border payments**. After the 2016 Bangladesh Bank heist ($81M theft via SWIFT Alliance Access malware), SWIFT made the CSP mandatory: all SWIFT users must **self-attest annually** against the CSRs, and the attestations are visible to correspondents.

**The Customer Security Requirements (3 objectives, 8 principles, ~16-31 controls depending on architecture):**

| Objective | Principle | Externally observable |
|---|---|---|
| **Secure your Environment** | 1. Restrict internet access & segregate critical systems from general IT | Subdomain isolation for SWIFT infrastructure; no exposed SWIFT-facing admin panels |
| | 2. Reduce attack surface and vulnerability | No exposed legacy protocols on SWIFT-facing IPs; patch cadence (weak proxy) |
| | 3. Physically secure the environment | (Physical — not observable) |
| | 4. Prevent compromise of credentials | MFA on SWIFT-facing admin; (internal mostly) |
| **Know your Environment** | 5. Detect anomalous activity | (Internal — SIEM) |
| | 6. Plan for incident response & information sharing | security.txt / published IR contact (weak proxy) |
| **Manage Cyber Risk** | 7. Manage third-party risk | Third-party hosting providers' TLS posture (observable) |
| | 8. Ensure security awareness | (Internal) |

**Externally observable signal mapping:**
- Distinct, isolated certificate SANs / IP ranges for SWIFT-facing infrastructure vs. general corporate web (Principle 1).
- No exposed admin panels / legacy protocols on SWIFT-facing IPs (Principle 2).
- TLS 1.2+ on any SWIFT-facing web interfaces (e.g., Alliance Access web console if internet-exposed — rare but observable).
- MFA availability on SWIFT-facing admin interfaces (Principle 4).
- Third-party hosting providers' TLS/DNSSEC posture (Principle 7).

**Description:** SWIFT CSP was launched in response to the 2016 Bangladesh Bank robbery and subsequent attacks on Vietnamese, Ecuadorian, and Ukrainian banks via SWIFT Alliance Access. Mandatory annual self-attestation against the CSRs is a condition of SWIFT connectivity. Most relevant to Cameroonian banks (not mobile-money-only fintechs), but PSPs handling cross-border correspondent flows inherit the requirements via their bank partners.

---

### 2.9 ECOWAS / African Union — Regional Data & Cyber Benchmarks

| Instrument | Code | Issuing body | Source |
|---|---|---|---|
| **ECOWAS Supplementary Act A/SA.1/01/10 on Personal Data Protection (2010)** | ECOWAS-DPA-2010 | ECOWAS | (regional benchmark for West Africa; does not bind Cameroon/CEMAC) |
| **African Union Convention on Cyber Security and Personal Data Protection (Malabo, 2014)** | AU-MALABO-2014 | African Union | https://au.int/en/treaties/african-union-convention-cyber-security-and-personal-data-protection (Cameroon signed; the 2024 PDPL now domesticates much of it) |
| **ECOWAS / WAES cyber directives** | ECOWAS-CYBER | ECOWAS | (West-African regional references — not binding on CEMAC) |

**Description:** The Malabo Convention is the continental framework; Cameroon's signature + the new 2024 PDPL (§1.2) now domesticates its data-protection pillar. ECOWAS instruments are useful as West-African benchmarks but do not bind Cameroon.

---

## 3. Synthesis — Domain-Specific Regulatory Checks for MYEVIEW (Fintech / Payments / Mobile Money)

The following 12 checks are framed as **externally observable, non-intrusive** pass/fail/warn verdicts MYEVIEW can produce for a fintech/payments/mobile-money operator in Cameroon. Each is mapped to the specific regulatory clauses above. They are ordered from strongest regulatory mandate (Cameroon/CEMAC binding) to global best-practice (fallback).

| # | Code | Check | Regulatory basis | MYEVIEW verification | Verdict logic |
|---|---|---|---|---|---|
| 1 | **FT-CHECK-01** | TLS 1.2+ on all web-facing services incl. payment pages & API endpoints (no TLS 1.0/1.1, no SSLv3, PFS cipher suites) | CM-LAW-2010-012 Part II Ch. I & IX; CM-MINFI-EPAY-2024 (security standards); COBAC-R-04-18 (strong auth + confidentiality in transit); COBAC-R-2019-01 (IS management); CEMAC-R-01-11-EMI (security architecture); **PCI-DSS Req 4**; ISO-27001 A.8.24; NIST PR.DS-2; CBN-CBF-2024 §2.9; PSD2-CSC-RTS Art. 30 | TLS handshake scan on apex + all discovered subdomains (incl. api.*, pay.*, wallet.*, checkout.*) on ports 443/8080/8443; inspect cipher suites for PFS | **PASS** = only TLS 1.2/1.3 with PFS; **WARN** = TLS 1.2 enabled but 1.3 not negotiated, or non-PFS ciphers present; **FAIL** = TLS 1.0/1.1 or SSLv3 reachable |
| 2 | **FT-CHECK-02** | Valid certificate chain on all HTTPS endpoints (no expired, no self-signed on public services, trusted CA, validity ≥ 30 days) | CM-LAW-2010-012 Ch. VI–VII (electronic certification); CM-PDPL-2024 (security measures); PCI-DSS Req 4; ISO-27001 A.8.24; PSD2-CSC-RTS Art. 4a (eIDAS qualified certs for ASPSPs) | Certificate parsing on every HTTPS endpoint; inspect chain, issuer, validity, SANs, QCStatements extension (for eIDAS) | **PASS** = all valid, trusted CA, ≥ 30 days remaining; **WARN** = any cert expiring < 30 days; **FAIL** = any expired, self-signed, or untrusted CA |
| 3 | **FT-CHECK-03** | HSTS present on all HTTPS services (max-age ≥ 6 months, includeSubDomains, preload-ready) | CM-LAW-2010-012 Ch. IX (session integrity); COBAC-R-04-18; PCI-DSS Req 2 & 4; ISO-27001 A.8.24; NIST PR.DS-2; CBN-CBF-2024 (HSTS mandatory); PSD2 SCA-RTS (secure surfaces) | HTTP response header inspection on apex + all subdomains | **PASS** = HSTS ≥ 15552000s with includeSubDomains on all; **WARN** = HSTS present but < 6 months or missing includeSubDomains or missing on some subdomains; **FAIL** = no HSTS on apex or payment page |
| 4 | **FT-CHECK-04** | HTTP→HTTPS redirect on apex, www, and all payment/wallet subdomains; no plaintext HTTP serving sensitive content | CM-LAW-2010-012 Ch. I (network security); CM-MINFI-EPAY-2024 (security standards); PCI-DSS Req 4; ISO-27001 A.8.24 | HTTP request to apex + each payment subdomain, follow redirects | **PASS** = 301 to HTTPS on all; **WARN** = 302 redirect or mixed on some; **FAIL** = HTTP serves content without redirect on payment/login page |
| 5 | **FT-CHECK-05** | SPF, DKIM, and DMARC published for apex domain (DMARC p ≥ quarantine, SPF not -all soft) | CM-LAW-2010-012 Art. 8, Ch. IX + Section 73 (payment card fraud prevention); CM-PDPL-2024 (data-in-transit protection); CBN-CBF-2024 (SPF+DKIM+DMARC mandatory); ISO-27001 A.5.15 | DNS TXT lookup for SPF, DMARC; DKIM via DNS selector lookup for common selectors (google, default, selector1, selector2, s1, s2, k1) | **PASS** = SPF + DKIM + DMARC p=reject with rua reporting; **WARN** = DMARC p=quarantine or SPF hardfail only; **FAIL** = none present |
| 6 | **FT-CHECK-06** | DNSSEC enabled on apex domain | CM-ANTIC guidance; CM-LAW-2010-012 Ch. I (network integrity); COBAC-R-04-18; ISO-27001 A.8.21; NIST PR.PT-4; CBN-CBF-2024 (DNSSEC recommended) | DNSKEY/DS query at authoritative servers + validation test against multiple resolvers | **PASS** = DNSSEC signed + DS at parent + validates; **WARN** = signed but no DS at parent or validation fails on some resolvers; **FAIL** = not signed |
| 7 | **FT-CHECK-07** | Subdomain hygiene — no orphaned/expiring DNS records, no dangling CNAMEs pointing to decommissioned services (esp. on api.*, pay.*, wallet.*, staging.*, test*) | COBAC-R-2016-04 (internal control); COBAC-R-2008-01 (BCP); COBAC-R-2019-01 (IS management); CM-MINFI-EPAY-2024 (telecom subsidiary separation — distinct domains); ISO-27001 A.5.9 (asset mgmt); NIST ID.AM; SWIFT-CSP-CSR Pr.1 (segregation) | CT log enumeration (crt.sh) + active subdomain DNS resolution; detect NXDOMAIN on previously-issued subdomains; detect dangling CNAMEs pointing to deletable cloud services (GitHub Pages, Heroku, S3, Azure) | **PASS** = all enumerated subdomains resolve; **WARN** = ≤ 5 dangling or non-resolving; **FAIL** = > 5 dangling, any takeover-vulnerable, or api.* subdomain compromised |
| 8 | **FT-CHECK-08** | Security headers present: Content-Security-Policy, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy | PCI-DSS Req 2 & 6; ISO-27001 A.8.25; NIST PR.IP-1; CBN-CBF-2024 (CSP mandatory); PSD2 SCA-RTS (secure surfaces) | HTTP response header inspection on apex + payment + API endpoints | **PASS** = all 5 present on all endpoints; **WARN** = 2–4 present or missing on some; **FAIL** = ≤ 1 present on payment/login page |
| 9 | **FT-CHECK-09** | No mixed content on login / payment / wallet / KYC pages (all subresources HTTPS) | CM-LAW-2010-012 Ch. IX + Section 73; PCI-DSS Req 4; ISO-27001 A.8.24; PSD2 SCA-RTS Art. 4 (auth surface integrity) | Parse HTML of login/payment/wallet/KYC pages, check src/href schemes on all subresources | **PASS** = no mixed content; **WARN** = passive mixed content (images); **FAIL** = active mixed content (scripts/iframes/stylesheets) on payment or login page |
| 10 | **FT-CHECK-10** | No exposed admin / legacy management interfaces on public subdomains (RDP/SSH/Telnet/phpMyAdmin/admin panels, .git directories, .env files) | PCI-DSS Req 1 & 2; COBAC-R-2016-04; ISO-27001 A.8.20; NIST PR.AC; CBN-CBF-2024 (reduce attack surface); SWIFT-CSP-CSR Pr.2 | Banner-grab on common admin ports (22, 23, 3389, 5900, 8080, 10000) + HTTP GET on /admin, /phpmyadmin, /.git/HEAD, /.env, /wp-admin | **PASS** = none exposed; **WARN** = login page exposed but HTTPS-protected + MFA; **FAIL** = unauthenticated admin panel, plaintext protocol, or exposed .git/.env |
| 11 | **FT-CHECK-11** | Certificate Transparency — every public cert is logged in CT logs; no unauthorized issuance detected | CM-LAW-2010-012 Ch. VI–VII; PCI-DSS Req 4; ISO-27001 A.8.24; NIST DE.CM-1 | crt.sh / Google CT query for the apex domain + all discovered subdomains; reconcile with discovered live certs | **PASS** = all live certs appear in CT; **WARN** = some certs not in CT or CT monitoring not configured; **FAIL** = live cert not in CT (possible unauthorized issuance) |
| 12 | **FT-CHECK-12** | Presence of security.txt file at /.well-known/security.txt with a valid contact (vulnerability disclosure channel) | ISO-27001 A.5.7 (threat intelligence); NIST GV.OC & RS.MI; FSB-CIR-2022 (information sharing); PCI-DSS Req 12 (security policy) | HTTP GET on /.well-known/security.txt on apex + payment subdomains; validate format (RFC 9116: Contact, Expires, Preferred:email) | **PASS** = present, valid, HTTPS, not expired, Contact field; **WARN** = present but malformed or expired; **FAIL** = absent |

### Bonus / emerging checks (consider for v2)

| # | Code | Check | Regulatory basis | MYEVIEW verification |
|---|---|---|---|---|
| B1 | **FT-CHECK-13** | Local hosting of databases — API endpoints resolve to Cameroonian IP space (DGTCFM/MINFI local-hosting requirement) | CM-MINFI-EPAY-2024 (hébergement local des bases de données) | IP geolocation of A/AAAA records for api.* and payment.* subdomains; ASN lookup | **PASS** = all in CM; **WARN** = some in CM, some in EU/US (CDN); **FAIL** = all outside CM |
| B2 | **FT-CHECK-14** | MFA / 2FA present on login & payment authorization flows (SCA proxy) | PSD2-SCA-RTS Art. 4; CM-LAW-2010-012 Art. 8; PCI-DSS Req 8; CBN-CBF-2024 | HTML parse of login/OTP pages for 2FA prompts; mobile APK inspection for biometric SDK signatures | **PASS** = MFA enforced; **WARN** = MFA optional; **FAIL** = no MFA on login or payment authorization |
| B3 | **FT-CHECK-15** | Published privacy / data-protection policy accessible from website footer (CM-PDPL-2024 consent obligation) | CM-PDPL-2024 (consent, transparency); AU-MALABO-2014; ECOWAS-DPA-2010 (regional fallback) | Scrape footer links for "privacy", "confidentialité", "données personnelles", "RGPD"; verify link is HTTPS and policy loads | **PASS** = present + HTTPS + comprehensive; **WARN** = present but on HTTP or thin; **FAIL** = absent (CM-PDPL-2024 violation after 23 June 2026) |
| B4 | **FT-CHECK-16** | eIDAS qualified certificate on open-banking / ASPSP API endpoints (if the fintech exposes account-access interfaces) | PSD2-CSC-RTS Art. 4a; ETSI TS 119 495 | Certificate extension inspection for QCStatements OID (0.4.0.1862.1.5) and QcCPS | **PASS** = eIDAS QC present; **WARN** = standard EV cert only; **FAIL** = no cert or self-signed on API endpoint |
| B5 | **FT-CHECK-17** | Functional separation of MMO subsidiary from telecom parent — distinct domain, distinct cert SANs, distinct IP ranges | CM-MINFI-EPAY-2024 (3-month functional separation); COBAC-R-2019-01 | WHOIS + cert SAN + IP geolocation comparison of MMO subsidiary domain vs. telecom parent domain | **PASS** = distinct domain, cert, IP range; **WARN** = distinct domain but shared infra; **FAIL** = same domain/cert/IP as telecom parent |

---

## 4. Notes, Caveats, and Gaps

- **Law 2024/017 (Cameroon PDPL) is now in force** (enacted 23 Dec 2024) with an 18-month transition ending **23 June 2026**. This **supersedes** the companion finance report's §1.4 statement that "Cameroon has no comprehensive standalone data-protection law." The Personal Data Protection Authority is not yet fully operationalized; expect enforcement to ramp after June 2026. FT-CHECK-15 (privacy policy) becomes a hard legal requirement at that deadline.
- **MINFI Decree of 28 Feb 2024** introduces **local database hosting** and **telecom-subsidiary functional separation within 3 months** — both novel, externally observable requirements (FT-CHECK-13, FT-CHECK-17). The local-hosting requirement may conflict with CDN/cloud-native fintech architectures; enforcement posture is still emerging.
- **COBAC has no single "IT security regulation."** IT-security obligations are distributed across internal-control (R-2016/04), BCP (R-2008/01), payment-services (R-04/18), and PSP-authorization (R-2019/01) texts. The synthesis in §3 reflects this distribution.
- **CEMAC e-money is bank-centered**: only credit institutions (banks) may issue e-money; MNOs are technical partners. This is structurally different from Kenya's M-Pesa model. A Cameroonian mobile-money operator's domain should disclose its licensed banking partner (CM-MINFI-EPAY-2024 + CEMAC-R-01-11-EMI).
- **PCI DSS applicability** is indirect: it binds Cameroonian fintechs only to the extent they connect to the CEMAC SMI / GIE Monétique card switch or otherwise process cardholder data. Pure mobile-money / wallet operators not handling card data are not directly PCI-bound, but PCI DSS is the global reference and increasingly written into PSP/acquirer contracts.
- **PSD2 SCA is not legally binding** in Cameroon but is the global reference for payment authentication. Visa/Mastercard export SCA-like requirements globally via 3-D Secure 2.x, so the practical effect reaches Cameroonian card-accepting fintechs.
- **SWIFT CSP** binds only Cameroonian banks/PSPs connected to SWIFT for cross-border payments. Mobile-money-only fintechs are out of scope unless they route cross-border via a SWIFT-connected bank.
- **CBN Nigeria framework (2024)** does not bind Cameroonian entities but is the **most prescriptive African regional benchmark** and explicitly mandates PCI DSS, ISO 27001, NDPR compliance for third-party PSPs — a precedent CEMAC is likely to follow.
- **ANTIC's published guidance** is less prescriptive than PCI DSS or ISO 27001; ANTIC coordinates rather than audits fintechs. The binding audit authority is **COBAC + MINFI**.
- **NIST CSF and ISO 27001** are not legally binding in Cameroon, but they are the *de facto* benchmark auditors and correspondent banks apply when assessing "adequate internal control" under COBAC R-2016/04 and "IS management" under COBAC R-2019/01.
- **FSB cybersecurity recommendations** bind only via systemic-institution regimes (COBAC R-2018/03). External observability is weak; included for completeness as the global benchmark for FMIs.
- **eIDAS qualified certificates** (PSD2-CSC-RTS Art. 4a) are an EU-specific requirement but increasingly observed on global open-banking endpoints. Cameroonian fintechs exposing open-banking APIs may adopt them for international interoperability.

---

## 5. Source Index (verified this session)

### Primary sources fetched
1. PACMap — Cameroon Cybersecurity Law 2010/012 summary: https://pacmap.dev/regulation/cm-cybersecurity-cybercrime-2010
2. ICT Policy Africa — Law 2010/012 full text: https://www.ictpolicyafrica.org/en/document/xr0onx7xbq
3. ART Cameroon — Law 2010/012 PDF: https://art.cm/sites/default/files/documents/loi_2010-012_cybersecurite_cybercriminalite.pdf
4. AFAPDP — Law 2010/012 PDF (mirror): https://www.afapdp.org/wp-content/uploads/2018/05/Cameroun-Loi-relative-a-la-cybersecurite-et-a-la-cybercriminalite-du-21-decembre-2010.pdf
5. PACMap — Cameroon PDPL 2024/017 summary: https://pacmap.dev/regulation/cm-personal-data-protection-2024
6. Cameroon Presidency — Law 2024/017 PDF: https://prc.cm/en/multimedia/documents/10271-law-n-2024-017-of-23-12-2024-web
7. Bejuka & Partners — MINFI e-payments decree analysis (28 Feb 2024): https://bejukapartners.com/2025/07/22/new-regulation-on-electronic-payments-in-cameroon/
8. Cameroon DGTCFM — Payment institution authorization (COBAC R-2019/01): https://dgtcfm.cm/en/payment-institution/conditions-for-authorising-a-payment-institution/
9. ResearchGuru — Mobile money legal/institutional framework in Cameroon (CEMAC regs + national laws): https://researchguru.pro/the-legal-and-institutional-framework-for-mobile-money-services-in-cameroon/
10. VOVE ID — KYC/AML compliance in Cameroon 2025 (ANIF, COBAC, BEAC, MINFI): https://blog.voveid.com/kyc-compliance-in-cameroon-2025-guide-to-digital-identity-and-aml-regulations/
11. ANTIC — Agency presentation: https://www.antic.cm/index.php/en/the-agency/presentation.html
12. ANIF — National Financial Investigation Agency (FIU): https://anif.cm/
13. PCI Security Standards Council — Document Library: https://www.pcisecuritystandards.org/document_library/
14. Wikipedia — PCI DSS (12 requirements, SAQ types, merchant/service-provider levels): https://en.wikipedia.org/wiki/Payment_Card_Industry_Data_Security_Standard
15. Wikipedia — Payment Services Directive (PSD2, SCA-RTS, CSC-RTS, eIDAS): https://en.wikipedia.org/wiki/Payment_Services_Directive
16. Wikipedia — ISO/IEC 27001:2022 (ISMS requirements, Annex A): https://en.wikipedia.org/wiki/ISO/IEC_27001
17. Wikipedia — ISO/IEC 27002:2022 (93 controls, 4 themes): https://en.wikipedia.org/wiki/ISO/IEC_27002
18. NIST — Cybersecurity Framework 2.0: https://www.nist.gov/cyberframework
19. Mondaq / G Elias — CBN Risk-Based Cybersecurity Framework 2024 analysis: https://www.mondaq.com/nigeria/security/1518574/overview-of-the-cbn-risk-based-cybersecurity-framework-and-guidelines-for-deposit-money-banks-and-payment-service-banks
20. G Elias — CBN Framework overview PDF: https://gelias.com/images/Newsletter/_Overview_of_the_CBN_Risk-Based_Cyber_Security_Framework.pdf
21. Wikipedia — SWIFT (history, security, Bangladesh Bank heist, CSP context): https://en.wikipedia.org/wiki/SWIFT
22. BEAC — COBAC regulations register: https://www.beac.int/supervision-bancaire/reglements-de-cobac/
23. BEAC — COBAC R-2016/04 (internal control) PDF: https://www.beac.int/wp-content/uploads/2016/10/reglement_cobac_r-2016_04_relatif_au_controle_interne.pdf
24. BEAC — COBAC R-2008/01 (BCP) PDF: https://www.beac.int/wp-content/uploads/2016/10/rgltcobacr_2008_01.pdf
25. BEAC — COBAC R-04/18 (payment services) PDF: https://www.beac.int/wp-content/uploads/2019/07/REGLEMENT-N-04-18-CEMAC-UMAC-COBAC-du-21-décembre-2018.pdf

### Secondary sources (not fetched verbatim — verify against official journals)
- CEMAC Regulation n° 01/11-CEMAC/UMAC/CM of 18 Sept 2011 (e-money issuers) — referenced via ResearchGuru; verify against BEAC/CEMAC official journal.
- BEAC Order n° 01/GR of 31 Oct 2011 (e-money payment system monitoring) — referenced via ResearchGuru.
- BEAC Order n° 02/GR/UMAC of 7 May 2014 (multi-banking for e-money) — referenced via ResearchGuru.
- Law n° 2003/004 of 21 April 2003 (banking secrecy) — referenced via ResearchGuru.
- SWIFT Customer Security Requirements (CSRs) — https://www.swift.com/myswift/customer-security-programme (portal requires SWIFT login; verify via published CSR framework document).
- FSB Cyber Lexicon & Effective Practices for CIR — https://www.fsb.org/work-of-the-fsb/financial-innovation-and-cybersecurity/cybersecurity/
- ECOWAS Supplementary Act A/SA.1/01/10 on Personal Data Protection (2010).
- African Union Malabo Convention (2014): https://au.int/en/treaties/african-union-convention-cyber-security-and-personal-data-protection
- PSD2 SCA-RTS full text: https://eur-lex.europa.eu/eli/reg_del/2018/389/oj
- ETSI TS 119 495 (eIDAS qualified certs for PSD2): https://www.etsi.org/deliver/etsi_ts/119400_119499/119495/
- PCI DSS SAQ-A and SAQ-A-EP documents: https://www.pcisecuritystandards.org/ (Document Library → SAQ category)

---

## 6. Comparison with Companion Finance/Microfinance Report

| Aspect | This report (Fintech/PSP/MMO) | Companion report (Finance/Microfinance) |
|---|---|---|
| **Target entities** | Fintechs, PSPs, e-money issuers, mobile money operators | Banks, EMFs (microfinance), credit unions |
| **Primary licensing** | MINFI (national) + COBAC assent (CM-MINFI-EPAY-2024) | COBAC (regional) + BEAC |
| **E-money framework** | CEMAC-R-01-11-EMI, BEAC-ORD-01-GR-2011, BEAC-ORD-02-GR-2014 | Inherits from banking license |
| **Data protection** | **CM-PDPL-2024** (NEW — in force 23 Dec 2024, deadline 23 June 2026) | States "no comprehensive data protection law" (now outdated) |
| **Local hosting** | **CM-MINFI-EPAY-2024** mandates local database hosting | Not specified |
| **Functional separation** | **CM-MINFI-EPAY-2024** — telecom MMO subsidiaries must separate within 3 months | N/A |
| **PCI DSS** | SAQ-A / SAQ-A-EP added for e-commerce/hosted payment pages | General PCI DSS Req coverage |
| **PSD2 SCA** | Added as global reference + eIDAS QC check | Not covered |
| **SWIFT CSP** | Added for cross-border payments | Not covered |
| **FSB** | Added as FMI benchmark | BCBS-239 covered (overlap) |
| **CBN framework** | 2024 edition (updated, more prescriptive) | 2018 edition |
| **Number of MYEVIEW checks** | 12 primary + 5 bonus (emerging) | 12 primary |

**Recommendation:** Update the companion finance/microfinance report's §1.4 to reflect the enactment of Law 2024/017 (CM-PDPL-2024). The two reports are complementary and should be cross-referenced when assessing a Cameroonian financial institution that spans both perimeters (e.g., a bank with a mobile-money subsidiary).