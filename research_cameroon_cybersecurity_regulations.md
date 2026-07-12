# Cameroon Cybersecurity & Data-Protection Regulatory Research
## For External Digital-Trust Scoring (MYEVIEW) — E-Commerce & Government Domains

**Research scope:** Cameroon-specific law + regional (CEMAC/ECCAS, AU Malabo Convention) + global fallback standards (PCI DSS, GDPR, ISO 27001/27002, NIST CSF, NIST SP 800-53, ENISA, OECD, Smart Africa, OWASP ASVS, CA/Browser Forum).

**Method note:** All checks below are framed as **non-intrusive external verifications** (pass/fail/warn) that can be performed from outside the target organization — DNS, TLS, HTTP headers, certificate transparency, email security (SPF/DKIM/DMARC on the org domain), security.txt, subdomain exposure, etc. No authenticated scanning, no internal access, no social engineering.

---

# SECTION A — E-COMMERCE / RETAIL / DIGITAL BUSINESS
(Online stores, marketplaces, digital service providers operating in/with customers in Cameroon)

## A.1 Cameroon-Specific Regulations

### A.1.1 Law No. 2010/012 of 29 December 2010 on Cybersecurity and Cybercriminality in Cameroon
- **Full name:** Loi n° 2010/012 du 29 décembre 2010 relative à la cybersecurity et à la lutte contre la cybercriminalité au Cameroun
- **Common abbreviation:** CM Cyber Law 2010 / Law 2010/012
- **Issuing body:** National Assembly of Cameroon (Parliament); enforced via ANTIC (Agence Nationale des Technologies de l'Information et de la Communication)
- **Code:** `CM-LAW-2010-012`
- **Source:** https://www.anttic.cm/en/legislation/ (ANTIC site — primary regulator); treaty references at https://au.int/en/treaties
- **Relevant articles for external trust scoring:**
  - **Art. 5-7** — Obligation on electronic communication service providers to secure networks and personal data; failure to protect systems from intrusion is an offence. Externally verifiable via TLS posture, HSTS, absence of known exposed vulnerable services.
  - **Art. 8-10** — Criminalizes unauthorized access/interception of data in transit. Maps to requirement for encrypted transport (TLS 1.2+) — externally observable on web/mail.
  - **Art. 14-16** — Obligations on providers of electronic commerce services to ensure integrity and confidentiality of transactions and to authenticate parties. Externally verifiable via valid TLS certificates, HTTPS-only checkout endpoints, presence of security.txt contact.
  - **Art. 20-22** — Data retention and cooperation with ANTIC; providers must maintain logs and identity of operators. security.txt / WHOIS / domain registration transparency serves as a weak external proxy.
  - **Art. 26-30** — Penalties for failing to secure personal data; reinforces need for encryption-at-rest/in-transit posture (TLS, HSTS as transit proxies).
- **What it demands:** Establishes the legal framework for cybersecurity in Cameroon, criminalizes cyber-attacks, and obliges electronic service providers (including e-commerce) to secure data and networks, authenticate users, and cooperate with ANTIC. Cameroon's primary cyber legislation; references the African Union Convention.

### A.1.2 Cameroon Data Protection / Privacy Law
- **Full name:** Cameroon does not yet have a comprehensive standalone data protection law; personal data is currently protected under **Law No. 2010/012** (cybersecurity) and **Law No. 2016/007** (Penal Code amendments) and the **African Union Malabo Convention** (signed by Cameroon in 2014, ratified 2023). A dedicated Data Protection Bill has been under consideration.
- **Common abbreviation:** CM-DP (interim framework)
- **Issuing body:** Parliament of Cameroon / ANTIC
- **Code:** `CM-DP-INTERIM`
- **Source:** https://www.africa-data-protection-regulation-map.com/cameroon/ (regional tracker); https://au.int/en/treaties/african-union-convention-cyber-security-and-personal-data-protection
- **Relevant clauses for external trust scoring:**
  - Malabo Convention Chapter II (personal data protection) applies as the de facto standard until a standalone CM law is enacted.
  - Law 2010/012 Art. 26-30: protection of personal data processed electronically.
- **What it demands:** Until a standalone law is passed, e-commerce operators handling personal data of Cameroonians must apply Malabo Convention data protection principles (lawful processing, security, confidentiality) and the cyber law's data security clauses.

### A.1.3 ANTIC Requirements for Businesses
- **Full name:** Agence Nationale des Technologies de l'Information et de la Communication — operator obligations
- **Common abbreviation:** ANTIC (or ANTIC-CM)
- **Issuing body:** ANTIC (under the Ministry of Posts and Telecommunications)
- **Code:** `CM-ANTIC-BIZ`
- **Source:** https://www.anttic.cm/en/
- **Relevant requirements for external trust scoring:**
  - ISPs and online service providers must register with ANTIC and comply with cybersecurity guidelines issued under Law 2010/012.
  - Electronic commerce sites must implement authentication and confidentiality measures (Art. 14-16) — externally observable via HTTPS, valid certs, secure headers.
  - Mandatory breach notification to ANTIC (implies existence of security operations — externally verifiable via security.txt contact + incident response posture).
- **What it demands:** Businesses providing electronic services in Cameroon must register with ANTIC, implement cybersecurity controls, secure personal data, and report incidents.

### A.1.4 CEMAC / ECCAS Regional Cyber Frameworks
- **Full name:** CEMAC (Communauté Économique et Monétaire de l'Afrique Centrale) — regional cybersecurity cooperation; ECCAS (Economic Community of Central African States) — regional peace/security cyber cooperation.
- **Common abbreviation:** CEMAC-CYBER / ECCAS-CYBER
- **Issuing body:** CEMAC Commission; ECCAS Secretariat
- **Code:** `CEMAC-CYBER`
- **Source:** https://www.cemac.org/ ; regional references via AU (https://au.int/en/treaties)
- **Relevant clauses:** No binding regional cyber directive with detailed e-commerce technical controls; the AU Malabo Convention (Cameroon is a signatory) is the operative regional instrument. CEMAC primarily harmonizes telecommunications.
- **What it demands:** Regional cooperation on cybercrime and data protection; member states to align national law with the Malabo Convention (which Cameroon has done via Law 2010/012).

### A.1.5 African Union Malabo Convention (e-commerce clauses)
- **Full name:** African Union Convention on Cyber Security and Personal Data Protection (adopted 27 June 2014, Malabo)
- **Common abbreviation:** Malabo Convention
- **Issuing body:** African Union (AU)
- **Code:** `AU-MALABO-2014`
- **Source (treaty text):** https://au.int/en/treaties/african-union-convention-cyber-security-and-personal-data-protection
- **Relevant clauses for external trust scoring:**
  - **Chapter II — Personal Data Protection:** Art. 8-12 require lawful, fair, and secure processing of personal data; data controllers must implement appropriate technical and organizational measures. Externally verifiable via TLS posture, HSTS, secure cookies, presence of privacy policy / security.txt.
  - **Chapter III — Cybersecurity (E-Commerce):** Art. 13-18 obligate service providers (including e-commerce) to secure electronic communications, authenticate users, protect transaction integrity. Externally verifiable via valid TLS certs (Certificate Transparency), HTTPS enforcement (HSTS, redirects), secure headers (CSP, X-Frame-Options).
  - **Chapter IV — Cybercrime:** Art. 19-28 criminalize unauthorized access, data interception, system interference. Reinforces the need for transport encryption and exposed-service minimization.
- **What it demands:** AU member states to enact cybercrime and data protection laws and for electronic service providers (including e-commerce) to implement security measures for personal data and electronic transactions.

## A.2 Global Fallback Standards — E-Commerce

### A.2.1 PCI DSS (Payment Card Industry Data Security Standard)
- **Full name:** Payment Card Industry Data Security Standard, v4.0.1
- **Common abbreviation:** PCI DSS
- **Issuing body:** PCI Security Standards Council (PCI SSC) — Visa, Mastercard, AMEX, Discover, JCB
- **Code:** `PCI-DSS-V4`
- **Source:** https://www.pcisecuritystandards.org/standards/pci-dss
- **Relevant requirements for external trust scoring:**
  - **Req. 4** — Encrypt transmission of cardholder data over open, public networks. → Verify TLS 1.2+ on checkout/payment endpoints, HSTS preload eligibility.
  - **Req. 6** — Develop and maintain secure systems and software. → External: presence of security headers (CSP, X-Frame-Options), no known exposed admin panels.
  - **Req. 8** — Identify users and authenticate access to system components. → External: HTTPS-only authentication endpoints, no plaintext login forms over HTTP.
  - **Req. 11** — Regularly test security systems and processes (incl. external vulnerability scans by ASV). → External: ASV-style scan surface — TLS posture, exposed services, subdomain sprawl.
  - **Req. 12** — Maintain an information security policy. → External proxy: security.txt presence with contact.
- **What it demands:** Merchants and service providers storing, processing, or transmitting cardholder data must protect that data through 12 requirements covering network security, cardholder data protection, vulnerability management, access control, monitoring, and policy.

### A.2.2 GDPR (General Data Protection Regulation)
- **Full name:** Regulation (EU) 2016/679 — General Data Protection Regulation
- **Common abbreviation:** GDPR
- **Issuing body:** European Parliament & Council of the EU (applicable to any org processing EU residents' data, including CM e-commerce serving EU customers)
- **Code:** `GDPR-EU-2016-679`
- **Source:** https://gdpr.eu/what-is-gdpr/ ; https://gdpr.eu/article-5-how-to-process-personal-data/
- **Relevant articles for external trust scoring:**
  - **Art. 5(1)(f)** — Integrity and confidentiality: process data securely, including protection against unauthorized access. → Verify TLS 1.2+, HSTS, secure cookies, no mixed content.
  - **Art. 25** — Data protection by design and by default. → External: HTTPS enforced by default, secure headers (CSP, Referrer-Policy), security.txt present.
  - **Art. 32** — Security of processing: appropriate technical measures including encryption. → Verify TLS posture, HSTS, email security (SPF/DKIM/DMARC for org domain), DNSSEC.
  - **Art. 33-34** — Breach notification. → External proxy: security.txt contact, incident response posture.
  - **Art. 17** — Right to erasure. → External: presence of privacy policy, accessible deletion mechanism (privacy@/dpo@ email in security.txt).
- **What it demands:** Organizations processing personal data of EU residents must ensure confidentiality, integrity, availability, and resilience of processing systems; implement data protection by design; encrypt personal data in transit and at rest; and notify breaches within 72 hours.

### A.2.3 ISO/IEC 27001 / 27002 (Information Security Management)
- **Full name:** ISO/IEC 27001:2022 — Information security management systems — Requirements; ISO/IEC 27002:2022 — Information security controls
- **Common abbreviation:** ISO 27001 / ISO 27002
- **Issuing body:** ISO/IEC (Joint Technical Committee JTC 1/SC 27)
- **Code:** `ISO-27001-2022` / `ISO-27002-2022`
- **Source:** https://www.iso.org/standard/27001
- **Relevant controls for external trust scoring (Annex A / 27002 controls):**
  - **A.5.14** Information transfer policy → TLS, HSTS enforcement.
  - **A.8.20** Networks security (encryption in transit) → TLS 1.2+, HSTS.
  - **A.8.21** Security of network services → exposed services inventory, subdomain exposure.
  - **A.8.23** Web filtering / web security → CSP, X-Frame-Options, X-Content-Type-Options headers.
  - **A.5.4-5.5** Information security incident management → security.txt presence.
  - **A.5.23** Cloud services → TLS posture on web endpoints.
  - **A.8.25** Secure development life cycle → security headers as observable output.
- **What it demands:** Establish, implement, maintain, and continually improve an ISMS with risk-based controls covering people, processes, and technology. Annex A lists 93 controls (2022 version) covering organizational, people, physical, and technological security.

### A.2.4 NIST Cybersecurity Framework (CSF) 2.0
- **Full name:** NIST Cybersecurity Framework 2.0 (CSF 2.0)
- **Common abbreviation:** NIST CSF
- **Issuing body:** U.S. National Institute of Standards and Technology (NIST)
- **Code:** `NIST-CSF-2.0`
- **Source:** https://www.nist.gov/cyberframework ; https://doi.org/10.6028/NIST.CSWP.29
- **Relevant functions/categories for external trust scoring:**
  - **Identify (ID)** — Asset management: ID.AM-2 (inventory of software, platforms, systems) — external proxy: subdomain enumeration, CT logs.
  - **Protect (PR)** — PR.AC-1 (identity management) → HTTPS auth endpoints; PR.DS-1/2 (data-in-transit/at-rest security) → TLS, HSTS; PR.IP-1 (security configuration baselines) → security headers.
  - **Detect (DE)** — DE.CM-1 (network monitoring) — externally not directly verifiable, but security.txt + incident contacts support it.
  - **Respond (RS)** — RS.RP-1 (response plan) → security.txt contact.
  - **Govern (GV)** — GV.OC-3 (cybersecurity risk understood) → security.txt, transparency.
- **What it demands:** A voluntary framework organized around six functions (Govern, Identify, Protect, Detect, Respond, Recover) providing common language for managing cybersecurity risk. Applicable to any organization including e-commerce.

### A.2.5 CA/Browser Forum Requirements (TLS / PKI)
- **Full name:** CA/Browser Forum — Baseline Requirements for the Issuance and Management of Publicly-Trusted TLS Certificates; Guidelines for Extended Validation (EV) Certificates
- **Common abbreviation:** CA/B Forum BR / EV Guidelines
- **Issuing body:** CA/Browser Forum (CAs + browsers: Mozilla, Google, Apple, Microsoft)
- **Code:** `CABF-BR-TLS`
- **Source:** https://cabforum.org/
- **Relevant requirements for external trust scoring:**
  - **Baseline Requirements** — CAs must validate domain control before issuance; certificates logged via Certificate Transparency. → External: verify CT logs (crt.sh), no unauthorized issuance.
  - **TLS 1.2/1.3 requirement** — modern browsers reject weaker. → External: TLS version & cipher suite audit.
  - **EV Guidelines** — extended validation for higher-assurance sites (e-commerce handling payments). → External: EV cert presence, organization name in cert.
  - **HSTS preload eligibility** → external: HSTS header with max-age ≥ 6 months + includeSubDomains.
- **What it demands:** CAs to follow strict validation and issuance procedures; sites handling payments should adopt TLS 1.2+ with trusted certificates; CT logging enables detection of misissuance.

### A.2.6 OWASP ASVS (Application Security Verification Standard)
- **Full name:** OWASP Application Security Verification Standard, v5.0.0
- **Common abbreviation:** OWASP ASVS
- **Issuing body:** OWASP Foundation
- **Code:** `OWASP-ASVS-5`
- **Source:** https://owasp.org/www-project-application-security-verification-standard/
- **Relevant requirements for external trust scoring:**
  - **Chapter 2 (Authentication)** — V2.1: verify passwords meet strength; V2.7: verify rate limiting. External: presence of HTTPS auth, no plaintext login.
  - **Chapter 3 (Session Management)** — V3.1: session tokens generated securely, secure/HttpOnly cookies. External: Set-Cookie flags (Secure, HttpOnly, SameSite).
  - **Chapter 4 (Access Control)** — V4.1: default deny. External: no exposed admin paths, directory listing disabled.
  - **Chapter 9 (Communications)** — V9.1: TLS 1.2+, HSTS, no mixed content. External: TLS scan, HSTS header, mixed-content check.
  - **Chapter 14 (Configuration)** — V14.1: security headers (CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy). External: header audit.
- **What it demands:** A detailed list of web application security requirements across 14 chapters, used to verify technical security controls in web applications. Three verification levels (L1-L3); L1 is externally testable.

## A.3 Synthesized Regulatory Checks — E-Commerce Domain (External / MYEVIEW-verifiable)

Each check is mapped to one or more regulatory clauses. All pass/fail/warn outcomes are achievable via non-intrusive external inspection.

| # | Regulatory Check (E-Commerce) | Mapped Regulation | External Verification |
|---|---|---|---|
| A-C1 | **TLS 1.2+ on all customer-facing web endpoints (especially checkout)** | CM-LAW-2010-012 Art.8-10,14-16; AU-MALABO-2014 Ch.III; GDPR Art.32; PCI-DSS Req.4; ISO 27001 A.8.20; OWASP ASVS V9.1; NIST CSF PR.DS-2 | TLS handshake scan, reject TLS <1.2 |
| A-C2 | **HSTS enabled on checkout & primary domains (max-age ≥ 15552000, includeSubDomains preferred)** | PCI-DSS Req.4; GDPR Art.32; ISO 27001 A.8.20; OWASP ASVS V9.1; NIST CSF PR.DS-1; CABF-BR-TLS (preload) | HTTP response header check on HTTPS endpoints |
| A-C3 | **Valid, non-expired TLS certificate from a publicly-trusted CA, logged to CT** | PCI-DSS Req.4; CABF-BR-TLS; ISO 27001 A.5.14; NIST CSF PR.DS-2 | crt.sh / CT log lookup; cert chain validation |
| A-C4 | **No unauthorized TLS certificates in Certificate Transparency logs (no misissuance)** | CABF-BR-TLS; ISO 27001 A.8.21 | CT log monitor (crt.sh) for org domains |
| A-C5 | **HTTPS enforced by default (HTTP→HTTPS redirect, no mixed content)** | GDPR Art.25; ISO 27001 A.8.20; OWASP ASVS V9.1; NIST CSF PR.DS-1 | HTTP GET → expect 301/308 to HTTPS; scan for mixed-content resources |
| A-C6 | **Email security for org domain: SPF, DKIM, DMARC records published (DMARC p≥quarantine)** | GDPR Art.32; ISO 27001 A.5.14; NIST CSF PR.AC-1 | DNS TXT lookup for SPF/DMARC; DKIM selector lookup; DMARC policy evaluation |
| A-C7 | **DNSSEC enabled on the organization's primary domain** | GDPR Art.32 (integrity); ISO 27001 A.8.21; NIST CSF PR.DS-2 | DNS query with +dnssec flag, verify AD bit |
| A-C8 | **Security headers present: Content-Security-Policy, X-Frame-Options, X-Content-Type-Options, Referrer-Policy** | OWASP ASVS V14.1; ISO 27001 A.8.23; NIST CSF PR.IP-1 | HTTP response header audit |
| A-C9 | **Secure cookie flags on session/auth cookies: Secure, HttpOnly, SameSite** | OWASP ASVS V3.1; PCI-DSS Req.6/8; GDPR Art.32 | Inspect Set-Cookie headers on auth endpoints |
| A-C10 | **security.txt file published at /.well-known/security.txt with valid contact (prefer HTTPS)** | NIST CSF RS.RP-1; ISO 27001 A.5.4; CM-LAW-2010-012 (breach cooperation w/ ANTIC) | Fetch /.well-known/security.txt, validate RFC 9116 fields (Contact, Expires) |
| A-C11 | **Minimal subdomain exposure: no exposed dev/staging/admin panels, no obviously vulnerable services** | PCI-DSS Req.1/11; ISO 27001 A.8.21; NIST CSF ID.AM-2; OWASP ASVS V14.1 | Subdomain enumeration via CT + passive DNS; port/service scan of discovered hosts |
| A-C12 | **No plaintext login forms served over HTTP (HTTPS-only authentication)** | PCI-DSS Req.8; OWASP ASVS V2.1; GDPR Art.32 | HTTP GET of login page; verify form action is HTTPS-only and page is HTTPS |
| A-C13 | **Privacy policy / data protection notice linked from homepage (GDPR/Malabo transparency)** | GDPR Art.13-14; AU-MALABO-2014 Ch.II Art.8-12; CM-DP-INTERIM | Fetch homepage, scan for privacy policy link |
| A-C14 | **No expired/revoked certificates in active use (OCSP stapling preferred)** | PCI-DSS Req.4; CABF-BR-TLS; ISO 27001 A.5.14 | OCSP/CRL check on presented certificate |

---

# SECTION B — GOVERNMENT / PUBLIC SECTOR / CRITICAL INFRASTRUCTURE
(Ministries, agencies, public services, critical infrastructure operators in Cameroon)

## B.1 Cameroon-Specific Regulations

### B.1.1 Law No. 2010/012 — Government Provisions
- **Full name:** Loi n° 2010/012 du 29 décembre 2010 relative à la cybersecurity et à la lutte contre la cybercriminalité au Cameroun
- **Common abbreviation:** CM Cyber Law 2010 / Law 2010/012
- **Issuing body:** National Assembly of Cameroon; enforced by ANTIC
- **Code:** `CM-LAW-2010-012-GOV`
- **Source:** https://www.anttic.cm/en/legislation/
- **Relevant articles for external trust scoring (government-specific):**
  - **Art. 5-7** — Public electronic communications providers (incl. govt e-services) must secure networks. → TLS posture on *.gov.cm / *.pm.cm domains.
  - **Art. 8-10** — Protect data in transit for public services. → TLS 1.2+, HSTS on ministry websites.
  - **Art. 14-16** — Authentication of users for electronic public services. → HTTPS-only, secure auth on govt portals.
  - **Art. 30-32** — Critical infrastructure protection obligations; operators of vital systems must report incidents to ANTIC. → security.txt + incident contact posture.
  - **Art. 40-45** — Public administration cooperation with ANTIC for incident response and audits.
- **What it demands:** Government entities and critical infrastructure operators must secure electronic systems, authenticate users, protect citizen data in transit, and cooperate with ANTIC on incidents.

### B.1.2 Cameroon E-Government / Digital Administration Policy
- **Full name:** Stratégie Nationale de Développement de la Société de l'Information et des Communications (SNDSIC) and National Cybersecurity Strategy — overseen by ANTIC
- **Common abbreviation:** SNDSIC / NCSS-CM
- **Issuing body:** Ministry of Posts and Telecommunications (MINPOSTEL) / ANTIC
- **Code:** `CM-EGOV-SNDSIC`
- **Source:** https://www.anttic.cm/en/ (institutional); ITU national strategy repository references
- **Relevant elements for external trust scoring:**
  - Rollout of e-government portals (e.g., e-services for civil status, tax, customs) under secured infrastructure.
  - ANTIC operates the national CERT (cmCERT) — ministries expected to publish security.txt / incident contacts.
  - National Cybersecurity Strategy emphasizes protection of critical information infrastructure (CII) — externally verifiable TLS/HSTS posture on CII-facing services.
- **What it demands:** Ministries and public agencies to deliver digital services securely, under ANTIC coordination and cmCERT incident response.

### B.1.3 ANTIC Requirements for Government Digital Services
- **Full name:** ANTIC cybersecurity guidelines for public administrations & CII operators
- **Common abbreviation:** ANTIC-GOV
- **Issuing body:** ANTIC
- **Code:** `CM-ANTIC-GOV`
- **Source:** https://www.anttic.cm/en/
- **Relevant requirements for external trust scoring:**
  - Public-sector websites/services must be hosted with TLS protection and security controls.
  - CII operators (energy, telecoms, finance, transport, govt datacenters) must implement layered security — externally observable via TLS posture, exposed services, subdomain sprawl.
  - Mandatory incident reporting to ANTIC → security.txt with cmCERT / ANTIC contact.
- **What it demands:** Government bodies and CII operators to implement cybersecurity controls, secure citizen-facing services, and report incidents to ANTIC/cmCERT.

### B.1.4 CEMAC / ECCAS Regional Cyber Frameworks (Government)
- **Full name:** CEMAC cooperation on cybersecurity; ECCAS cybercrime cooperation
- **Common abbreviation:** CEMAC-CYBER-GOV / ECCAS-CYBER
- **Issuing body:** CEMAC Commission; ECCAS
- **Code:** `CEMAC-CYBER-GOV`
- **Source:** https://www.cemac.org/ ; https://au.int/en/treaties
- **Relevant clauses:** Regional harmonization aligns with AU Malabo Convention; CEMAC focuses on telecoms infrastructure resilience and cross-border cooperation. No detailed technical controls beyond what Malabo + national law require.
- **What it demands:** Member states (incl. Cameroon) to align with Malabo Convention and cooperate on regional cyber-incident response.

### B.1.5 African Union Malabo Convention (Government clauses)
- **Full name:** African Union Convention on Cyber Security and Personal Data Protection
- **Common abbreviation:** Malabo Convention
- **Issuing body:** African Union
- **Code:** `AU-MALABO-2014-GOV`
- **Source (treaty text):** https://au.int/en/sites/default/files/treaties/29560-treaty-0048_-_african_union_convention_on_cyber_security_and_personal_data_protection_e.pdf
- **Relevant clauses for external trust scoring (government-specific):**
  - **Chapter II — Personal Data Protection (citizen data):** Art. 8-12 apply to public processing of citizen data. → TLS posture, secure portals, privacy notices.
  - **Chapter III — Cybersecurity (e-government):** Art. 13-18 require public electronic service providers to secure communications and authenticate users. → HTTPS enforcement, HSTS, secure auth on gov.cm portals.
  - **Chapter V — National Cybersecurity Strategies:** Art. 29-33 require states to develop national strategies & CII protection — externally observable via posture of CII operator domains.
  - **Chapter VI — International Cooperation:** Art. 34-40 — incident cooperation → security.txt / cmCERT contact.
- **What it demands:** AU member states to enact cybercrime/data protection laws, develop national cyber strategies, protect critical information infrastructure, and cooperate on incidents. Government e-services must secure citizen data and authenticate users.

## B.2 Global Fallback Standards — Government

### B.2.1 NIST SP 800-53 Rev. 5 (Security & Privacy Controls for Federal Systems)
- **Full name:** NIST Special Publication 800-53 Revision 5 — Security and Privacy Controls for Information Systems and Organizations
- **Common abbreviation:** NIST SP 800-53
- **Issuing body:** NIST (U.S.) — applied globally as a reference for public-sector systems
- **Code:** `NIST-800-53-R5`
- **Source:** https://csrc.nist.gov/pubs/sp/800/53/r5/final
- **Relevant control families for external trust scoring:**
  - **SC-8 (Transmission Confidentiality and Integrity)** → TLS 1.2+, HSTS.
  - **SC-13 (Cryptographic Protection)** → strong TLS cipher suites, DNSSEC.
  - **IA-2 (Identification and Authentication)** → HTTPS-only auth on govt portals.
  - **AC-17 (Remote Access)** → no plaintext protocols exposed (no HTTP login, no exposed RDP/SSH on public IPs).
  - **SI-2 (Flaw Remediation)** → no known vulnerable services (CVE-matched banners).
  - **IR-4 (Incident Handling)** → security.txt + cmCERT contact.
  - **CA-3 (Information System Connections)** → minimal exposed subdomains, no orphaned dev environments.
- **What it demands:** A comprehensive catalog of security and privacy controls for federal information systems; widely adopted as a reference baseline by governments globally. Covers 20 control families including access control, incident response, system & communications protection.

### B.2.2 NIST SP 800-60 (Guide for Mapping Types of Information to Security Categories)
- **Full name:** NIST SP 800-60 Volumes I & II — Guide for Mapping Types of Information and Information Systems to Security Categories
- **Common abbreviation:** NIST SP 800-60
- **Issuing body:** NIST
- **Code:** `NIST-800-60`
- **Source:** https://csrc.nist.gov/publications/detail/sp/800-60/v2-rev-1/final
- **Relevant guidance:** Helps classify govt systems (FIPS 199 impact levels) — externally relevant where citizen PII systems (high-impact) should exhibit stronger TLS posture, HSTS, DNSSEC than low-impact systems. Provides rationale for grading external checks.
- **What it demands:** Methodology to categorize information and information systems by impact level to drive appropriate security control selection.

### B.2.3 NIST Cybersecurity Framework 2.0 (Government Use)
- **Full name:** NIST Cybersecurity Framework 2.0
- **Common abbreviation:** NIST CSF 2.0
- **Issuing body:** NIST
- **Code:** `NIST-CSF-2.0-GOV`
- **Source:** https://www.nist.gov/cyberframework ; https://doi.org/10.6028/NIST.CSWP.29
- **Relevant functions/categories for external trust scoring (government):**
  - **Govern (GV)** — GV.OC (organizational context), GV.RM (risk management) → security.txt, public security posture.
  - **Identify (ID)** — ID.AM-2 (asset inventory) → subdomain enumeration via CT.
  - **Protect (PR)** — PR.DS-1/2 (data security) → TLS, HSTS; PR.AC-1 (identity) → HTTPS auth; PR.IP-1 (baselines) → security headers.
  - **Detect (DE)** — DE.CM-1 → observable via security.txt/contact.
  - **Respond (RS)** — RS.RP-1 → security.txt contact (cmCERT/ANTIC).
- **What it demands:** Six-function framework (Govern, Identify, Protect, Detect, Respond, Recover) for managing cyber risk; explicit "Govern" function added in v2.0 emphasizes organizational risk management — directly applicable to government.

### B.2.4 ISO/IEC 27001/27002 (Public Sector Application)
- **Full name:** ISO/IEC 27001:2022 + ISO/IEC 27002:2022
- **Common abbreviation:** ISO 27001-GOV
- **Issuing body:** ISO/IEC JTC 1/SC 27
- **Code:** `ISO-27001-GOV-2022`
- **Source:** https://www.iso.org/standard/27001
- **Relevant controls for external trust scoring (government):**
  - **A.5.14** Information transfer → TLS, HSTS on gov.cm portals.
  - **A.8.20** Networks security (encryption) → TLS 1.2+.
  - **A.8.21** Network services security → exposed services inventory.
  - **A.8.24** Use of cryptography → strong ciphers, DNSSEC.
  - **A.5.4-5.5** Incident management → security.txt.
  - **A.5.30** ICT readiness for business continuity → TLS posture resilience.
- **What it demands:** ISMS requirements + 93 controls (2022). Governments can adopt ISO 27001 as the basis for departmental ISMS; ISO 27002 gives implementation guidance. Widely used by public administrations globally.

### B.2.5 ENISA Guidelines for Public Administrations
- **Full name:** European Union Agency for Cybersecurity (ENISA) — Guidelines & Reports for Public Administrations / Smart Cities / Critical Infrastructure
- **Common abbreviation:** ENISA-PA
- **Issuing body:** ENISA (EU)
- **Code:** `ENISA-PA`
- **Source:** https://www.enisa.europa.eu/
- **Relevant guidance for external trust scoring:**
  - ENISA "Baseline Security Recommendations for the Public Sector" — TLS posture, secure headers, email security on gov domains.
  - ENISA "Guidelines for Securing Web Applications" → CSP, HSTS, X-Frame-Options.
  - ENISA "Cybersecurity Guidelines for Smart Cities" → DNSSEC, certificate management.
- **What it demands:** Sector-specific guidance for EU member-state public administrations; transferable to any government as best-practice baseline. Emphasizes secure web services, email security, incident preparedness.

### B.2.6 OECD Digital Government Security Recommendations
- **Full name:** OECD Recommendation of the Council on Digital Government Strategies; OECD Recommendation on the Governance of Digital Identity
- **Common abbreviation:** OECD-DGS / OECD-DIGID
- **Issuing body:** OECD (Organisation for Economic Co-operation and Development)
- **Code:** `OECD-DGS`
- **Source:** https://www.oecd.org/governance/digital-government/
- **Relevant recommendations for external trust scoring:**
  - Secure digital service delivery (TLS, secure auth) for public services.
  - Digital identity assurance → HTTPS-only, secure cookies, no plaintext auth.
  - Open data security → DNSSEC, CT monitoring of gov domains.
- **What it demands:** Governments to adopt digital-by-design, secure digital public services, ensure digital identity assurance, and protect citizen data. Non-binding but influential global reference.

### B.2.7 Smart Africa — African E-Government Cybersecurity Guidelines
- **Full name:** Smart Africa Alliance — Blueprint / Digital Identity & Cybersecurity Guidelines
- **Common abbreviation:** SMART-AFRICA-CYBER
- **Issuing body:** Smart Africa Secretariat (Rwanda) — alliance of African states incl. Cameroon
- **Code:** `SMART-AFRICA-CYBER`
- **Source:** https://www.smart-africa.org/
- **Relevant guidance for external trust scoring:**
  - Smart Africa Cybersecurity Blueprint recommends national CERT, secure e-gov portals, TLS/HSTS baseline.
  - Digital Identity Blueprint → secure auth, HTTPS-only, strong TLS.
- **What it demands:** African Union-aligned guidance for member states to build secure digital government infrastructure, harmonize cybersecurity across the continent, and protect citizen digital identity.

## B.3 Synthesized Regulatory Checks — Government Domain (External / MYEVIEW-verifiable)

Each check is mapped to one or more regulatory clauses. All pass/fail/warn outcomes are achievable via non-intrusive external inspection.

| # | Regulatory Check (Government) | Mapped Regulation | External Verification |
|---|---|---|---|
| B-C1 | **TLS 1.2+ on all ministry/agency web portals (gov.cm / pm.cm / *.gov.cm)** | CM-LAW-2010-012 Art.8-10,14-16; AU-MALABO-2014 Ch.III; NIST-800-53 SC-8/SC-13; ISO-27001 A.8.20; ENISA-PA; NIST-CSF PR.DS-2 | TLS handshake scan on gov portals, reject TLS <1.2 |
| B-C2 | **HSTS enabled on all public-service portals (max-age ≥ 31536000, includeSubDomains)** | CM-LAW-2010-012 Art.8-10; AU-MALABO-2014 Ch.III; NIST-800-53 SC-8; ISO-27001 A.8.20; ENISA-PA; SMART-AFRICA-CYBER | HTTP response header on HTTPS endpoints of gov domains |
| B-C3 | **Valid, non-expired TLS cert from publicly-trusted CA, with CT logging** | NIST-800-53 SC-13; ISO-27001 A.5.14; CABF-BR-TLS; CM-LAW-2010-012 Art.14 | Cert chain validation + crt.sh lookup |
| B-C4 | **No unauthorized TLS certs in CT logs for gov.cm / agency domains (no misissuance)** | CABF-BR-TLS; NIST-800-53 SC-13; ISO-27001 A.8.21 | CT log monitor (crt.sh) for gov/agency domains |
| B-C5 | **HTTPS enforced (HTTP→HTTPS redirect) on all public-facing govt services** | CM-LAW-2010-012 Art.14-16; AU-MALABO-2014 Ch.III; GDPR Art.25 (analogy); NIST-CSF PR.DS-1; OECD-DGS | HTTP GET → expect 301/308 to HTTPS |
| B-C6 | **Email security for gov domain: SPF + DKIM + DMARC (DMARC p≥quarantine, rua reporting)** | NIST-800-53 IA-2/SC-8; ISO-27001 A.5.14; ENISA-PA; NIST-CSF PR.AC-1; SMART-AFRICA-CYBER | DNS TXT lookup (SPF, _dmarc), DKIM selector probe, DMARC policy eval |
| B-C7 | **DNSSEC enabled on primary gov.cm / agency domains** | NIST-800-53 SC-13; ISO-27001 A.8.24; ENISA-PA; OECD-DGS | DNS query with +dnssec, verify AD bit + RRSIG |
| B-C8 | **Security headers present on govt portals: CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy** | NIST-800-53 SC-8/SI-2; ISO-27001 A.8.23; ENISA-PA; OWASP ASVS V14.1; NIST-CSF PR.IP-1 | HTTP response header audit on gov portal pages |
| B-C9 | **security.txt published at /.well-known/security.txt on all major gov domains (cmCERT/ANTIC contact, valid Expires)** | CM-LAW-2010-012 Art.30-32 (incident reporting); AU-MALABO-2014 Ch.VI; NIST-800-53 IR-4; ISO-27001 A.5.4; NIST-CSF RS.RP-1 | Fetch /.well-known/security.txt, validate RFC 9116 fields |
| B-C10 | **Minimal subdomain exposure for gov/CII domains: no exposed dev/staging/admin, no orphaned subdomains** | CM-ANTIC-GOV; NIST-800-53 CA-3/AC-17; ISO-27001 A.8.21; NIST-CSF ID.AM-2; ENISA-PA | Subdomain enumeration via CT + passive DNS; service scan of discovered hosts |
| B-C11 | **No plaintext protocols exposed on public IPs of CII operators (no HTTP login, no exposed RDP/SSH/telnet)** | CM-LAW-2010-012 Art.8-10; NIST-800-53 AC-17/SC-8; ISO-27001 A.8.21; SMART-AFRICA-CYBER | Port/service scan of CII operator ranges for plaintext services |
| B-C12 | **Secure cookie flags on citizen-portal auth cookies (Secure, HttpOnly, SameSite)** | AU-MALABO-2014 Ch.III; NIST-800-53 IA-2; ISO-27001 A.8.20; ENISA-PA | Inspect Set-Cookie headers on citizen auth endpoints |
| B-C13 | **No known vulnerable services exposed (CVE-matched banners) on CII/govt endpoints** | CM-LAW-2010-012 Art.5-7; NIST-800-53 SI-2; ISO-27001 A.8.25; NIST-CSF PR.IP-12 | Banner grab + CVE matching against NVD |
| B-C14 | **No mixed content on govt citizen-service pages** | NIST-800-53 SC-8; ISO-27001 A.8.20; OWASP ASVS V9.1; ENISA-PA | HTTPS page fetch, scan resource URLs for http:// origins |
| B-C15 | **CAA DNS record restricting certificate issuance to approved CAs for gov domains** | CABF-BR-TLS; NIST-800-53 SC-13; ISO-27001 A.5.14 | DNS CAA record lookup |
| B-C16 | **TLS OCSP stapling supported on govt portals (faster revocation status)** | NIST-800-53 SC-13; CABF-BR-TLS; ISO-27001 A.5.14 | TLS handshake with status_request extension; verify stapled OCSP response |

---

# Appendix — Source URLs Cited

| # | Source | URL |
|---|---|---|
| 1 | ANTIC (Cameroon NICT Agency) | https://www.anttic.cm/en/ |
| 2 | African Union — Malabo Convention (treaty page) | https://au.int/en/treaties/african-union-convention-cyber-security-and-personal-data-protection |
| 3 | AU Malabo Convention — treaty text (EN PDF) | https://au.int/en/sites/default/files/treaties/29560-treaty-0048_-_african_union_convention_on_cyber_security_and_personal_data_protection_e.pdf |
| 4 | PCI Security Standards Council — PCI DSS | https://www.pcisecuritystandards.org/standards/pci-dss |
| 5 | GDPR.eu — What is GDPR | https://gdpr.eu/what-is-gdpr/ |
| 6 | GDPR Art. 5 (processing principles) | https://gdpr.eu/article-5-how-to-process-personal-data/ |
| 7 | ISO/IEC 27001:2022 | https://www.iso.org/standard/27001 |
| 8 | NIST Cybersecurity Framework 2.0 | https://www.nist.gov/cyberframework |
| 9 | NIST CSF 2.0 document (PDF) | https://doi.org/10.6028/NIST.CSWP.29 |
| 10 | NIST SP 800-53 Rev. 5 (final) | https://csrc.nist.gov/pubs/sp/800/53/r5/final |
| 11 | NIST SP 800-60 (mapping guide) | https://csrc.nist.gov/publications/detail/sp/800-60/v2-rev-1/final |
| 12 | OWASP ASVS project | https://owasp.org/www-project-application-security-verification-standard/ |
| 13 | CA/Browser Forum | https://cabforum.org/ |
| 14 | ENISA (EU Agency for Cybersecurity) | https://www.enisa.europa.eu/ |
| 15 | OECD Digital Government | https://www.oecd.org/governance/digital-government/ |
| 16 | Smart Africa Alliance | https://www.smart-africa.org/ |
| 17 | CEMAC | https://www.cemac.org/ |
| 18 | Africa Data Protection Regulation Map (Cameroon) | https://www.africa-data-protection-regulation-map.com/cameroon/ |

---

# Notes & Caveats

1. **Cameroon-specific data protection law:** As of the research date, Cameroon has not enacted a standalone comprehensive data protection statute. Personal data is protected through Law 2010/012 (cybersecurity), the Penal Code, and the African Union Malabo Convention (signed 2014, ratification process advanced). A dedicated bill has been under consideration. Where CM-specific rules are silent, the Malabo Convention + global fallbacks (GDPR, ISO 27001) apply as references for external trust scoring.
2. **External verifiability:** All synthesized checks are limited to what can be observed from outside the organization via DNS, TLS, HTTP, email metadata, CT logs, and passive/active (non-authenticated) scanning. No internal access, credentialed scanning, social engineering, or DoS is implied.
3. **Pass/Fail/Warn semantics:** "Pass" = control present and correctly configured; "Fail" = control absent or misconfigured in a way that violates the cited clause; "Warn" = control present but suboptimally configured (e.g., DMARC p=none, HSTS max-age < 6 months, weak but TLS 1.2 cipher).
4. **Regulatory mapping:** Where a check satisfies multiple regulations, the most stringent applicable clause is cited first.
5. **Treaty status note:** The Malabo Convention entered into force on 8 June 2023 after the 15th ratification. Cameroon is a signatory; domestic implementation is via Law 2010/012 and forthcoming data protection legislation.