# Regulatory Research Report: Telecommunications / ISP / Connectivity — Cameroon
**Scope:** Cybersecurity, data-protection, and critical-infrastructure regulations applicable to telecom/ISP organizations in Cameroon, with regional/global fallbacks. Focus on externally-observable digital-trust indicators (non-intrusive checks).

**Date:** 2026-07-12 · **Analyst:** Regulatory Research (MYEVIEW) · **Type:** Research only, no code

---

## PART 1 — CAMEROON-SPECIFIC REGULATIONS

### 1.1 Law No. 2010/012 of 21 December 2010 on Cybersecurity and Cybercriminality
- **Common abbreviation:** Cybersecurity Law / Loi 2010/012
- **Code:** `CM-LAW-2010-012`
- **Issuing body:** Parliament of Cameroon; President of the Republic; enforced by ANTIC (Agence Nationale des Technologies de l'Information et de la Communication) and ANTIC-CIRT for incident response
- **Source URLs:**
  - https://www.antic.cm/images/stories/laws/Law%20relating%20to%20cybersecurity%20and%20cybercriminality%20in%20Cameroon.pdf
  - https://dig.watch/resource/the-law-no-2010-012-of-21-december-2010-on-cybersecurity-and-cybercriminality-in-cameroon
  - https://pacmap.dev/regulation/cm-cybersecurity-cybercrime-2010
  - https://www.ictpolicyafrica.org/en/document/xr0onx7xbq
- **Description:** Framework law governing security of electronic communication networks and information systems; establishes digital evidence regime, cryptography/electronic certification, criminalizes cyber offenses, mandates security audits/certification for service providers and network operators.
- **Relevant clauses for external digital-trust scoring:**
  - **Section 1 (Object):** Build trust in electronic communication networks and information systems → implies operators must present a trustworthy external posture (valid TLS, no exposed insecure services).
  - **Section 42 (Confidentiality of traffic data):** "The confidentiality of information channelled through electronic communication and information systems networks, including traffic data, shall be ensured by operators" → verify TLS 1.2+ on customer-facing portals (self-care, webmail) to protect data in transit.
  - **Section 44 (Prohibition of unauthorized interception):** Forbids listening/intercepting/storing communications without consent → correlates with encryption of web portals and email (SPF/DKIM/DMARC to prevent spoofing/interception).
  - **Sections 33-35 (Obligations of access/service/content providers):** ISPs must inform subscribers of access-control means, preserve identification data 10 years, provide technical means for identification → implies robust subscriber portal security (TLS, authentication).
  - **Sections 25, 35, 42, 46 (Data retention):** 10-year retention of connection/content-identification data → secure, integrity-protected storage (externally: not directly verifiable, but DNS/TLS posture reflects general security hygiene).
  - **Sections 13-31 (Electronic security & certification):** Mandatory security audits and certification by ANTIC for operators; electronic signatures and PKI under ANTIC as Root CA → externally observable: presence of valid certificates from trusted CAs, certificate transparency compliance.
  - **Section 61 (Unauthorized disclosure by audit personnel):** Criminal sanctions → supports need for hardened external posture.
  - **Section 66 (Network disruption):** Criminalizes disruption → operators must maintain availability and DDoS resilience (externally: DNSSEC, redundant DNS, BGP hygiene).
- **External verifiability:** TLS posture on portals/webmail, SPF/DKIM/DMARC for telco domain (ISPs handle email), DNSSEC on authoritative DNS, BGP/route hygiene (RPKI/ROA), web security headers, certificate transparency, subdomain exposure.

### 1.2 Law No. 2010/013 of 21 December 2010 Governing Electronic Communications
- **Common abbreviation:** Electronic Communications Law / Loi 2010/013
- **Code:** `CM-LAW-2010-013`
- **Issuing body:** Parliament of Cameroon; enforced by ART (Agence de Régulation des Télécommunications / Telecommunications Regulatory Board) with ANTIC for certification
- **Source URLs:**
  - https://pacmap.dev/regulation/cm-electronic-communications-2010
  - https://www.minpostel.gov.cm/index.php/en/les-textes/telecoms-tic/lois-telecoms-tic/229-law-no-2010-013-of-21-december-2010-governing-electronic-communications-in-cameroon
- **Description:** Framework law governing electronic communications networks, services, and operators in Cameroon. Establishes licensing regime, consumer protection, QoS, confidentiality of communications, lawful interception, interconnection, and universal service.
- **Relevant clauses for external digital-trust scoring:**
  - **Article 68 (Sanctions):** ART may suspend/withdraw licences for non-compliance; operators must meet ART technical specifications → drives need for demonstrable security posture.
  - **Confidentiality of communications:** Prohibits unauthorized interception/recording/disclosure; operators must implement technical safeguards preventing eavesdropping → verify TLS on self-care portals, webmail, and customer portals.
  - **Technical security mechanisms:** Operators must implement technical security to ensure protection, integrity, and availability of data transmitted on networks → DNSSEC for authoritative DNS, BGP/route hygiene (RPKI/ROA), web security headers.
  - **Subscriber identification (Decree No. 2012/1637/PM):** Subscriber identity databases → secure self-care portal authentication (TLS, strong auth).
  - **Lawful interception obligations:** Operators must build interception interfaces → not externally verifiable, but indicates mature network management.
  - **QoS standards & ART inspections:** Periodic performance reports → general operational maturity reflected in external posture.
- **External verifiability:** TLS posture, DNSSEC, web headers, email security (SPF/DKIM/DMARC for telco domain), subdomain exposure.

### 1.3 Law No. 2024/017 of 23 December 2024 on Personal Data Protection
- **Common abbreviation:** Cameroon PDPL / Loi 2024/017
- **Code:** `CM-LAW-2024-017`
- **Issuing body:** Parliament of Cameroon; Personal Data Protection Authority (being operationalized); 18-month transition expired 23 June 2026
- **Source URLs:**
  - https://pacmap.dev/regulation/cm-personal-data-protection-2024
  - https://prc.cm/en/multimedia/documents/10271-law-n-2024-017-of-23-12-2024-web
- **Description:** Cameroon's first comprehensive personal data protection law, modeled on GDPR. Mandates explicit opt-in consent, data breach notification, DPIAs, cross-border transfer controls, DPO appointment, technical/organizational security measures. Extraterritorial reach.
- **Relevant clauses for external digital-trust scoring:**
  - **Technical & organizational security measures:** Data minimization, purpose limitation, storage limitation, protection throughout lifecycle → verify TLS 1.2+ on all customer-facing portals handling personal data (self-care, webmail, registration).
  - **Data breach notification:** Must notify Authority promptly of breaches risking data subjects → strong external posture (TLS, email security) reduces breach risk; observable via SPF/DKIM/DMARC, HSTS, certificate transparency.
  - **Cross-border transfer approval:** Sender and recipient jointly liable for adequate protection → secure channels (TLS, DNSSEC) observable externally.
  - **Sensitive data categories:** Biometric, health, etc. require explicit authorization → heightened protection implied for such portals.
- **External verifiability:** TLS posture on portals handling personal data, HSTS, web security headers, SPF/DKIM/DMARC for telco domain, certificate transparency, subdomain exposure.

### 1.4 ANTIC (National Agency for Information and Communication Technologies)
- **Common abbreviation:** ANTIC / ANTIC-CIRT
- **Code:** `CM-ANTIC`
- **Issuing body:** Government of Cameroon (established under Law 2010/012)
- **Source URLs:**
  - https://www.antic.gov.cm/ (legislation portal — intermittently accessible)
  - https://dig.watch/resource/the-law-no-2010-012-of-21-december-2010-on-cybersecurity-and-cybercriminality-in-cameroon
- **Description:** National regulator for cybersecurity, Root Certification Authority, and operates ANTIC-CIRT (national CSIRT). Conducts mandatory security audits and certification for telecom operators and service providers.
- **Relevant requirements:**
  - Mandatory security audits and certification before and during operations for network operators/ISPs.
  - Electronic certification and PKI oversight (Root CA) → operators should use properly issued certificates (observable: valid TLS certs from trusted CAs, CT logs).
  - Incident response coordination (ANTIC-CIRT) → operators expected to maintain detect/respond capabilities (externally: DDoS resilience, BGP hygiene, DNSSEC).
- **External verifiability:** Valid TLS certificates (preferably from recognized CAs), certificate transparency, DNSSEC on authoritative zones, BGP route hygiene (RPKI/ROA).

### 1.5 ART (Telecommunications Regulatory Board) Requirements
- **Common abbreviation:** ART / TRB
- **Code:** `CM-ART`
- **Issuing body:** Government of Cameroon
- **Source URLs:**
  - https://www.art.cm/en/regulation
  - https://www.art.cm/en/reglementation/lois
- **Description:** Regulates telecom operators/ISPs in Cameroon: licensing, QoS, consumer protection, spectrum, universal service. Enforces Law 2010/013 technical specifications.
- **Relevant requirements:**
  - Licensing with technical, financial, operational conditions → baseline operational maturity.
  - QoS standards and periodic reporting → network reliability/availability (externally: DNSSEC, BGP hygiene, redundant DNS).
  - Consumer protection (complaint handling) → secure self-care portal (TLS, auth).
  - Technical security specifications for network integrity → general hardened posture.
- **External verifiability:** Overall external security posture reflecting regulatory compliance.

### 1.6 Cameroon Critical Information Infrastructure Protection
- **Code:** `CM-CIIP`
- **Issuing body:** Derived from Law 2010/012 (Section 1: trust in networks) and national cybersecurity strategy under ANTIC
- **Source URLs:**
  - https://pacmap.dev/regulation/cm-cybersecurity-cybercrime-2010
  - https://dig.watch/resource/the-law-no-2010-012-of-21-december-2010-on-cybersecurity-and-cybercriminality-in-cameroon
- **Description:** Cameroon's cyber law establishes the framework for protecting electronic communication networks as critical infrastructure. ANTIC oversees security audits/certification for operators of critical networks. No standalone CIIP statute found, but Law 2010/012 functions as the de facto CIIP framework for telecom.
- **Relevant clauses:** Sections on electronic security regulation, mandatory audits, network protection (Sections 13-31, 42, 44, 66) → operators of critical networks must demonstrate hardened external posture.
- **External verifiability:** TLS posture, DNSSEC, BGP/RPKI hygiene, DDoS resilience indicators, subdomain exposure, certificate transparency.

---

## PART 2 — REGIONAL / GLOBAL FALLBACK STANDARDS

### 2.1 ITU-T X.805 — Security Architecture for Systems Providing End-to-End Communications
- **Common abbreviation:** ITU-T X.805
- **Code:** `ITU-X.805`
- **Issuing body:** International Telecommunication Union (ITU-T)
- **Source URL:** https://www.itu.int/rec/T-REC-X.805-200310-I/en
- **Description:** Defines a security architecture for end-to-end communications with three security dimensions (access, control, management) × eight security layers, addressing: access control, authentication, non-repudiation, data confidentiality, data integrity, availability.
- **Relevant clauses for external digital-trust scoring:**
  - **Data confidentiality (dimension):** Protect data in transit → verify TLS 1.2+ on customer portals/webmail/self-care.
  - **Authentication (dimension):** Verify identity of communicating parties → TLS certificate validation, SPF/DKIM/DMARC for email domain.
  - **Data integrity:** Protection against modification → TLS, DNSSEC for authoritative DNS.
  - **Availability:** Protection against DoS → DDoS resilience, redundant DNS, BGP hygiene (RPKI/ROA).
- **External verifiability:** TLS posture, SPF/DKIM/DMARC, DNSSEC, BGP/RPKI, web security headers.

### 2.2 ITU-T X.1051 — Security Management for Telecommunications
- **Common abbreviation:** ITU-T X.1051
- **Code:** `ITU-X.1051`
- **Issuing body:** International Telecommunication Union (ITU-T)
- **Source URL:** https://www.itu.int/rec/T-REC-X.1051 (referenced in ITU-T X-series)
- **Description:** Provides security management framework for telecommunications organizations based on ISO/IEC 27001, tailored to telecom. Addresses governance, risk, compliance, and security operations for telecom providers.
- **Relevant clauses:** Risk management, security controls for telecom services → externally reflected in hardened posture (TLS, DNSSEC, email security, BGP hygiene).
- **External verifiability:** TLS posture, DNSSEC, SPF/DKIM/DMARC, web security headers, BGP/RPKI.

### 2.3 ISO/IEC 27001 — Information Security Management Systems (ISMS)
- **Common abbreviation:** ISO 27001
- **Code:** `ISO-27001`
- **Issuing body:** International Organization for Standardization (ISO) / International Electrotechnical Commission (IEC), committee ISO/IEC JTC 1/SC 27
- **Source URL:** https://www.iso.org/standard/27001 (Wikipedia: https://en.wikipedia.org/wiki/ISO/IEC_27001)
- **Description:** Specifies requirements for establishing, implementing, maintaining, and continually improving an ISMS. Annex A (2022 version) contains 93 controls across 4 themes (organizational, people, physical, technological). Certification via accredited bodies.
- **Relevant clauses for external digital-trust scoring:**
  - **Annex A.8.24 (Cryptography):** Use of cryptography to protect confidentiality, integrity, availability of data → verify TLS 1.2+ on portals/webmail/self-care.
  - **Annex A.8.21 (Network security):** Segregation, network controls → BGP/route hygiene (RPKI/ROA), subdomain exposure.
  - **Annex A.5.34 (Privacy & PII protection):** Protection of personal data → TLS, HSTS on customer portals.
  - **Annex A.8.23 (Web filtering):** Web security → security headers (CSP, X-Frame-Options, HSTS).
  - **Annex A.8.25 (Secure development):** Secure lifecycle → fewer exposed vulnerable subdomains.
- **External verifiability:** TLS posture, web security headers, HSTS, certificate transparency, subdomain exposure.

### 2.4 ISO/IEC 27002 — Code of Practice for Information Security Controls
- **Common abbreviation:** ISO 27002
- **Code:** `ISO-27002`
- **Issuing body:** ISO/IEC JTC 1/SC 27
- **Source URL:** https://en.wikipedia.org/wiki/ISO/IEC_27002
- **Description:** Detailed implementation guidance for ISO 27001 Annex A controls.
- **Relevant clauses:** Controls on cryptography, network security, email security, web security → externally verifiable as above.

### 2.5 ISO/IEC 27011 — Information Security Management for Telecommunications Organizations
- **Common abbreviation:** ISO 27011
- **Code:** `ISO-27011`
- **Issuing body:** ISO/IEC JTC 1/SC 27 (developed with ITU-T)
- **Source URL:** https://www.iso.org/standard/44814.html (ISO catalog); referenced in ITU-T X.1051
- **Description:** Sector-specific ISMS guidance for telecom organizations based on ISO 27001, with additional telecom-specific controls.
- **Relevant clauses for external digital-trust scoring:**
  - **§13.1 (Network security controls):** Protect subscriber data in transit → verify TLS 1.2+ on self-care portal.
  - **§13.2 (Service provider security):** Ensure integrity of telecom services → DNSSEC on authoritative DNS, BGP hygiene.
  - **Email security for ISP/telco domain:** ISPs handling customer email must secure it → SPF/DKIM/DMARC.
  - **Subscriber data protection:** TLS, HSTS on portals handling PII.
- **External verifiability:** TLS posture, SPF/DKIM/DMARC, DNSSEC, BGP/RPKI, web security headers.

### 2.6 GSMA FS.13 / FS.14 — Mobile Network Security Guidelines
- **Common abbreviation:** GSMA FS.13 (Mobile Network Security Requirements), FS.14 (Security Baseline for Mobile Operators)
- **Code:** `GSMA-FS13`, `GSMA-FS14`
- **Issuing body:** GSMA (GSM Association) — Fraud & Security group
- **Source URL:** https://www.gsma.com/security/ (FS.13/FS.14 documents)
- **Description:** GSMA security baseline requirements for mobile network operators covering network security, operations, fraud prevention, and interconnect security. FS.13 defines baseline mobile network security requirements; FS.14 is the security baseline control set.
- **Relevant clauses for external digital-trust scoring:**
  - **Interconnect security:** BGP/route hygiene for inter-operator connectivity (RPKI/ROA).
  - **DNS security:** DNSSEC on authoritative DNS for operator domain.
  - **Customer portal security:** TLS 1.2+, HSTS, strong auth on self-care portals.
  - **Email security:** SPF/DKIM/DMARC for operator domain (especially for ISPs/mobile operators offering email).
  - **Distributed denial of service (DDoS) resilience:** Observable via external posture.
- **External verifiability:** TLS posture, DNSSEC, BGP/RPKI, SPF/DKIM/DMARC, web security headers.

### 2.7 3GPP Security Standards (Mobile Operators)
- **Common abbreviation:** 3GPP SA3 (Security)
- **Code:** `3GPP-SA3`
- **Issuing body:** 3rd Generation Partnership Project (3GPP) — TSG SA WG3 (Security)
- **Source URL:** https://www.3gpp.org/SA3-Security ; https://en.wikipedia.org/wiki/3GPP
- **Description:** 3GPP SA3 develops security specifications for mobile networks (2G/3G/4G/5G): authentication, confidentiality, integrity, subscriber identity protection, inter-operator signaling security.
- **Relevant clauses for external digital-trust scoring:**
  - **TS 33.501 (5G Security architecture):** Subscriber confidentiality, authentication, signaling security.
  - **TS 33.401 (LTE/SAE Security):** Network domain security, user plane/integrity protection.
  - **Inter-operator IP backbone security (IPsec, NDS):** BGP/route hygiene for interconnect (RPKI/ROA, RPKI-validated filtering).
  - **DNS security for operator domain:** DNSSEC on authoritative DNS.
  - **Subscriber portal security (out of SA3 direct scope but implied):** TLS on self-care/webmail.
- **External verifiability:** BGP/RPKI hygiene, DNSSEC on authoritative DNS, TLS posture on customer-facing services.

### 2.8 NIST Cybersecurity Framework (CSF) 2.0 — Applied to Telecom/Critical Infrastructure
- **Common abbreviation:** NIST CSF 2.0
- **Code:** `NIST-CSF-2.0`
- **Issuing body:** U.S. National Institute of Standards and Technology (NIST) — used globally as reference
- **Source URL:** https://www.nist.gov/cyberframework ; https://en.wikipedia.org/wiki/NIST_Cybersecurity_Framework
- **Description:** Voluntary framework with six functions (Govern, Identify, Protect, Detect, Respond, Recover) and 22 categories/106 subcategories. Widely adopted internationally for critical infrastructure cybersecurity.
- **Relevant clauses for external digital-trust scoring:**
  - **PR.DS (Data Security):** Protect confidentiality, integrity, availability of data → verify TLS 1.2+ on portals/webmail; HSTS.
  - **PR.AC (Access Control):** Limit access to authorized users → strong auth on self-care portals (observable via TLS + security headers).
  - **PR.PT (Protective Technology):** Technical security solutions → web security headers (CSP, X-Frame-Options), DNSSEC.
  - **DE.CM (Security Continuous Monitoring):** Monitor for events → externally observable: certificate transparency, subdomain exposure monitoring.
  - **PR.AC-5 (Network integrity):** Network segregation, BGP hygiene (RPKI/ROA).
- **External verifiability:** TLS posture, HSTS, web security headers, DNSSEC, BGP/RPKI, certificate transparency, subdomain exposure.

### 2.9 EU Electronic Communications Code (EECC) — Directive (EU) 2018/1972
- **Common abbreviation:** EECC
- **Code:** `EU-EECC-2018-1972`
- **Issuing body:** European Parliament and Council of the EU (used as global reference)
- **Source URL:** https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32018L1972 ; https://en.wikipedia.org/wiki/Electronic_Communications_Code_Directive_2018
- **Description:** Consolidated EU telecom regulatory framework covering authorisation, access, spectrum, end-user rights, and security obligations for electronic communications providers. Article 40 (security and integrity) specifically mandates risk management, security measures, breach notification.
- **Relevant clauses for external digital-trust scoring:**
  - **Article 40 (Security and integrity of networks/services):** Providers must take technical/organizational measures to manage risks, guarantee security, prevent unauthorized access → TLS 1.2+ on customer portals, webmail, self-care.
  - **Breach notification (Art. 40(3-4)):** Notify authorities and subscribers of breaches → strong external posture reduces risk (TLS, email security, HSTS).
  - **Article 84 (Universal service):** Affordable broadband/voice access → general availability; externally: DNSSEC, redundant DNS, BGP hygiene.
  - **Articles 61-62 (Access/interconnection):** Inter-operator connectivity → BGP/RPKI hygiene.
- **External verifiability:** TLS posture, SPF/DKIM/DMARC, DNSSEC, BGP/RPKI, web security headers.

### 2.10 African Union Convention on Cyber Security and Personal Data Protection (Malabo Convention)
- **Common abbreviation:** Malabo Convention
- **Code:** `AU-MALABO-2014`
- **Issuing body:** African Union (AU)
- **Source URL:** https://en.wikipedia.org/wiki/Malabo_Convention ; https://au.int/en/treaties/african-union-convention-cyber-security-and-personal-data-protection
- **Description:** Regional AU convention (adopted 2014, in force June 2023) covering electronic transactions, data protection, and cybersecurity/cybercrime. Requires member states to enact national cybersecurity policies, criminalize cyber offenses, protect critical infrastructure, and establish DPAs. Cameroon signed 12 Aug 2021 (not yet ratified).
- **Relevant clauses for external digital-trust scoring:**
  - **Cybersecurity chapter:** States must criminalize acts affecting confidentiality, integrity, availability of ICT systems and underlying network infrastructure → operators must protect network integrity (DNSSEC, BGP hygiene).
  - **National cybersecurity policy/strategy:** Member states to create national CIRT and detection mechanisms → operators cooperate with national CIRT (externally: DDoS resilience, BGP hygiene).
  - **Data protection chapter (Art. 8, 11, 13, 16-19):** Consent, confidentiality, transparency, DPA oversight → TLS on portals handling PII.
  - **Critical infrastructure protection:** Implied in cybersecurity chapter → hardened external posture for telecom operators.
- **External verifiability:** TLS posture, DNSSEC, BGP/RPKI, SPF/DKIM/DMARC, web security headers, DDoS resilience indicators.

---

## PART 3 — SYNTHESIS: DOMAIN-SPECIFIC REGULATORY CHECKS FOR MYEVIEW (TELECOM/ISP)

The following 12 checks are framed as non-intrusive external verifications MYEVIEW can perform against a telecom/ISP organization's domain, with pass/fail/warn outcomes mapped to the regulations above.

| # | Check | Regulation Mapping | External Verification Method | Pass / Fail / Warn Logic |
|---|-------|--------------------|------------------------------|--------------------------|
| 1 | **TLS 1.2+ on self-care / customer portal** | CM-LAW-2010-012 §42, §44; CM-LAW-2010-013 (confidentiality); CM-LAW-2024-017 (security measures); ITU-X.805 (confidentiality); ISO-27011 §13.1; NIST-CSF PR.DS; EU-EECC Art.40 | Connect to https://self-care.{telco-domain}, scan TLS version + cipher suites | **Pass:** TLS 1.2/1.3 only, strong ciphers. **Fail:** TLS 1.0/1.1 or weak ciphers. **Warn:** TLS 1.2 allowed but 1.3 not enabled |
| 2 | **TLS 1.2+ on webmail / email portal** (critical for ISPs handling customer email) | CM-LAW-2010-012 §42, §44; CM-LAW-2024-017; ISO-27011 §13.1; GSMA-FS14; NIST-CSF PR.DS | Connect to https://webmail.{telco-domain}, scan TLS | Same as #1. ISP email is high-value target |
| 3 | **Valid TLS certificate (trusted CA, no expired/self-signed)** | CM-LAW-2010-012 §13-31 (ANTIC PKI/certification); CM-ANTIC; ISO-27001 A.8.24; NIST-CSF PR.DS | Inspect certificate chain, issuer, validity dates, CT logs | **Pass:** valid cert from publicly trusted CA, in CT logs. **Fail:** expired/self-signed/untrusted. **Warn:** expires in <30 days |
| 4 | **HSTS enabled on customer portals** | CM-LAW-2024-017 (security measures); ISO-27001 A.8.24; NIST-CSF PR.DS, PR.PT; EU-EECC Art.40 | Check HTTP response headers for `Strict-Transport-Security` | **Pass:** HSTS present, max-age ≥ 6 months. **Fail:** absent. **Warn:** present but short max-age |
| 5 | **SPF record published for telco domain** | CM-LAW-2010-012 §44 (anti-interception); CM-LAW-2024-017; ISO-27011 §13.1; GSMA-FS14; NIST-CSF PR.DS | DNS TXT lookup for SPF (`v=spf1 ...`) | **Pass:** valid SPF with `-all` or `~all`. **Fail:** no SPF. **Warn:** SPF with `+all` or permissive |
| 6 | **DKIM signing configured for telco domain** | CM-LAW-2010-012 §44; CM-LAW-2024-017; ISO-27011 §13.1; GSMA-FS14 | DNS lookup for DKIM selectors; verify signing on emails if obtainable | **Pass:** DKIM TXT records present and valid. **Fail:** none. **Warn:** present but weak key (<1024-bit RSA) |
| 7 | **DMARC policy published for telco domain** | CM-LAW-2010-012 §44; CM-LAW-2024-017; ISO-27011 §13.1; GSMA-FS14; NIST-CSF PR.DS | DNS TXT lookup for `_dmarc.{telco-domain}` | **Pass:** `p=quarantine` or `p=reject`. **Fail:** none. **Warn:** `p=none` (monitor only) |
| 8 | **DNSSEC enabled on authoritative DNS zones** | CM-LAW-2010-012 §66 (network integrity); CM-ART (technical security); ITU-X.805 (integrity); ISO-27011 §13.2; GSMA-FS13/FS14; 3GPP-SA3; NIST-CSF PR.PT; AU-MALABO (network integrity) | Check DS records at registry, RRSIG/DNSKEY on authoritative zone | **Pass:** DNSSEC signed with valid chain to parent. **Fail:** not signed. **Warn:** signed but misconfigured (e.g., expired RRSIG) |
| 9 | **BGP route hygiene — RPKI/ROA coverage for telco prefixes** | CM-LAW-2010-012 §66; CM-ART; ITU-X.805 (availability); ISO-27011 §13.2; GSMA-FS13/FS14; 3GPP-SA3 (NDS); NIST-CSF PR.AC-5; EU-EECC Art.61-62; AU-MALABO | Query RPKI validators / public ROA repositories for telco ASN/prefixes | **Pass:** all announced prefixes covered by valid ROAs. **Fail:** no ROAs / origins not matching. **Warn:** partial coverage |
| 10 | **Web security headers on main telco website & portals** | CM-LAW-2024-017 (security measures); ISO-27001 A.8.23; NIST-CSF PR.PT; EU-EECC Art.40 | Fetch HTTP headers, check CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy | **Pass:** ≥3 of 5 key headers present. **Fail:** none. **Warn:** 1-2 present |
| 11 | **Subdomain exposure — no exposed vulnerable/deprecated services** | CM-LAW-2010-012 §42, §44; CM-LAW-2024-017; ISO-27001 A.8.21, A.8.25; NIST-CSF ID.AM (asset management); AU-MALABO | Enumerate subdomains via CT logs / passive DNS; check for exposed admin panels, old software, insecure protocols | **Pass:** no high-risk exposures. **Fail:** exposed admin/login without TLS or known-vulnerable service. **Warn:** informational subdomains exposed |
| 12 | **Certificate Transparency — certs logged for telco domain** | CM-LAW-2010-012 §13-31 (ANTIC PKI oversight); CM-ANTIC; ISO-27001 A.8.24; NIST-CSF DE.CM | Query CT logs (crt.sh / CT APIs) for {telco-domain} | **Pass:** all issued certs present in CT logs. **Fail:** certs not in CT (potential misissuance). **Warn:** unexpected certs in CT (potential spoof/typo squat) |

---

## PART 4 — NOTES & CAVEATS

1. **Cameroon-specific enforceability:** Law 2010/012 (cybersecurity) and Law 2010/013 (electronic communications) are the primary binding instruments. Law 2024/017 (PDPL) became enforceable with an 18-month transition expiring 23 June 2026 — compliance is now expected. Cameroon signed the Malabo Convention (12 Aug 2021) but has not ratified; nonetheless, it serves as regional reference.
2. **ANTIC website accessibility:** The official ANTIC site (antic.gov.cm) was intermittently reachable during research; primary law text was confirmed via ART (art.cm), pacmap.dev, dig.watch, and ICT Policy Africa mirrors.
3. **External verifiability scope:** All 12 checks are non-intrusive — they use public DNS, TLS handshakes, HTTP headers, CT logs, RPKI repositories, and passive DNS. No authenticated access, scanning, or intrusive probing is required.
4. **ISPs vs. mobile operators:** Checks #5-#7 (email security) are especially critical for ISPs/telcos that operate email services for subscribers (common for Cameroonian ISPs such as Camtel, Orange CM, MTN CM, Nexttel). For pure mobile operators without email services, those checks apply to the corporate domain.
5. **No standalone CIIP statute:** Cameroon does not have a separate Critical Information Infrastructure Protection law; Law 2010/012 functions as the de facto CIIP framework for telecom, with ANTIC as the operational authority.
6. **Global fallbacks rationale:** Where Cameroon-specific technical prescriptions are high-level (e.g., "implement technical security measures"), ITU-T X.805, ISO 27011, GSMA FS.13/14, 3GPP SA3, NIST CSF, and EU EECC provide the concrete technical benchmarks against which external posture can be measured.

---

## SOURCES (CONSOLIDATED)

- Cameroon Cybersecurity Law 2010/012 (ANTIC PDF): https://www.antic.cm/images/stories/laws/Law%20relating%20to%20cybersecurity%20and%20cybercriminality%20in%20Cameroon.pdf
- Cameroon Cybersecurity Law 2010/012 (ART PDF): https://art.cm/sites/default/files/documents/loi_2010-012_cybersecurite_cybercriminalite.pdf
- Dig.watch summary: https://dig.watch/resource/the-law-no-2010-012-of-21-december-2010-on-cybersecurity-and-cybercriminality-in-cameroon
- PACMap (2010/012): https://pacmap.dev/regulation/cm-cybersecurity-cybercrime-2010
- PACMap (2010/013): https://pacmap.dev/regulation/cm-electronic-communications-2010
- PACMap (2024/017 PDPL): https://pacmap.dev/regulation/cm-personal-data-protection-2024
- ICT Policy Africa (full law text): https://www.ictpolicyafrica.org/en/document/xr0onx7xbq
- ART Cameroon: https://www.art.cm/en/regulation
- Minpostel law repository: https://www.minpostel.gov.cm/index.php/en/les-textes/telecoms-tic/lois-telecoms-tic
- ITU-T X.805: https://www.itu.int/rec/T-REC-X.805-200310-I/en
- ISO 27001 (Wikipedia): https://en.wikipedia.org/wiki/ISO/IEC_27001
- NIST CSF (Wikipedia): https://en.wikipedia.org/wiki/NIST_Cybersecurity_Framework
- EU EECC (Wikipedia): https://en.wikipedia.org/wiki/Electronic_Communications_Code_Directive_2018
- EU EECC (EUR-Lex): https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32018L1972
- Malabo Convention (Wikipedia): https://en.wikipedia.org/wiki/Malabo_Convention
- AU Malabo Convention (AU.int): https://au.int/en/treaties/african-union-convention-cyber-security-and-personal-data-protection
- 3GPP SA3: https://www.3gpp.org/SA3-Security
- 3GPP (Wikipedia): https://en.wikipedia.org/wiki/3GPP
- GSMA Security: https://www.gsma.com/security/
- Telecommunications in Cameroon (Wikipedia): https://en.wikipedia.org/wiki/Telecommunications_in_Cameroon

---

*End of report. Research only — no code written.*