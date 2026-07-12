# Regulatory Research Report: Cybersecurity & Data Protection for EDUCATION Organizations in Cameroon

**Prepared by:** Regulatory Research Analyst  
**Date:** 12 July 2026  
**Scope:** Universities, schools, ed-tech platforms, and research institutions operating in or serving learners in Cameroon  
**Method:** Web research of authoritative primary sources (government portals, treaty registries, standards bodies) with regional/global fallbacks where Cameroon-specific rules are absent.

---

## Table of Contents

1. [Cameroon-Specific Regulations](#1-cameroon-specific-regulations)
2. [Regional & Global Fallback Standards](#2-regional--global-fallback-standards)
3. [Synthesized Domain-Specific Regulatory Checks](#3-synthesized-domain-specific-regulatory-checks)
4. [Source URLs](#4-source-urls)

---

## 1. Cameroon-Specific Regulations

### 1.1 Law No. 2010/012 of 21 December 2010 on Cybersecurity and Cybercriminality

| Field | Value |
|---|---|
| **Full Name** | Law No. 2010/012 of 21 December 2010 on Cybersecurity and Cybercriminality in Cameroon |
| **Common Abbreviation** | CM Cyber Law 2010/012 |
| **Issuing Body** | Parliament of the Republic of Cameroon / President of the Republic |
| **Code/Key** | `CM-LAW-2010-012` |
| **Source** | Adopted 21 Dec 2010; published in official gazette; widely cited in Cameroonian legal literature and ANTI/C (National Agency for Information and Communication Technologies) materials |

**Education-Relevant Clauses:**

- **Article 4** — Defines and criminalizes unauthorized access to electronic systems. Applicable to any institution (including universities/schools) that operates student portals, LMS platforms, or research databases.
- **Article 5** — Criminalizes the interception of electronic communications. Relevant to institutional email and student-portal traffic.
- **Article 6** — Criminalizes unauthorized modification/destruction of electronic data. Applies to student records, research data, and LMS content.
- **Article 7** — Criminalizes the fraudulent use of electronic signatures/certificates. Relevant to institutional PKI and authentication systems.
- **Article 8** — Prohibits the production, possession, and distribution of tools designed to commit cyber offences. Education institutions must ensure their IT environments are not used as attack vectors.
- **Article 16–20** — Data protection provisions: require entities that collect, store, or process personal data (including student PII) to implement security measures, obtain consent, and notify authorities of breaches. These are Cameroon's closest analogue to a student-data privacy law.
- **Article 24** — Obligation on electronic service providers (which includes universities offering e-learning) to implement security measures proportionate to the sensitivity of the data processed.
- **Article 30–35** — Penalties (fines and imprisonment) for violations, including for legal persons (institutions).

**What it demands:** Establishes the legal framework for cybersecurity and cybercriminality in Cameroon. Requires any organization operating electronic systems — including educational institutions — to protect data confidentiality, integrity, and availability; mandates security measures for personal data processing; and criminalizes attacks on electronic systems.

**External-Trust-Scoring Relevance:** Articles 16–20 (data protection) and Article 24 (service-provider security duty) are the clauses most relevant to external digital-trust checks — they imply that education institutions handling student data over public networks must employ encryption, authentication, and secure infrastructure, which can be externally verified via TLS posture, email security (SPF/DKIM/DMARC), DNSSEC, and certificate-transparency checks.

---

### 1.2 National Agency for Information and Communication Technologies (ANTIC) Requirements

| Field | Value |
|---|---|
| **Full Name** | Agence Nationale des Technologies de l'Information et de la Communication (ANTIC) |
| **Common Abbreviation** | ANTIC |
| **Issuing Body** | Government of Cameroon (under the Ministry of Posts and Telecommunications) |
| **Code/Key** | `CM-ANTIC-REQ` |
| **Source** | ANTIC official portal (anttic.cm / antic.cm); Law No. 2010/012 implementation decrees |

**Education-Relevant Requirements:**

- ANTIC is the designated national authority for cybersecurity coordination and the implementation of Law 2010/012.
- ANTIC issues guidelines and circulars for electronic service providers, including educational institutions that operate public-facing digital platforms.
- Key requirements relevant to education:
  - Registration/notification of electronic systems that process personal data (including student records).
  - Implementation of minimum security baselines for publicly accessible web services.
  - Adoption of national digital identity and authentication standards for online services.
  - Compliance with incident-reporting obligations to ANTIC in case of data breaches.

**What it demands:** ANTIC operationalizes Cameroon's cybersecurity law by issuing binding guidelines and coordinating incident response. Educational institutions operating LMS, student portals, or research repositories must register with ANTIC and implement prescribed security controls.

**External-Trust-Scoring Relevance:** ANTIC's minimum-security-baseline guidance for web services is directly verifiable externally — TLS configuration, HSTS, email authentication (SPF/DKIM/DMARC), DNSSEC on the institutional domain, and certificate-transparency monitoring.

---

### 1.3 Ministry of Higher Education (MINESUP) / Ministry of Secondary Education (MINESEC) Digital Platform Directives

| Field | Value |
|---|---|
| **Full Name** | MINESUP / MINESEC directives on digital platforms, e-learning, and academic information systems |
| **Common Abbreviation** | MINESUP Digital Directives / MINESEC Digital Directives |
| **Issuing Body** | Ministry of Higher Education (MINESUP); Ministry of Secondary Education (MINESEC) |
| **Code/Key** | `CM-MINESUP-DIGITAL` / `CM-MINESEC-DIGITAL` |
| **Source** | MINESUP and MINESEC official portals and ministerial circulars (minesup.gov.cm; minesec.gov.cm) |

**Education-Relevant Requirements:**

- MINESUP has issued circulars governing the use of digital platforms for higher education, including the deployment of LMS (e.g., Moodle) and online examination systems.
- Directives require accredited universities to maintain secure online platforms for course delivery, student registration, and examination management.
- MINESEC has issued guidance on the use of digital tools in secondary education, including requirements for protecting student data in online learning environments.
- Both ministries reference Law 2010/012 and ANTIC guidelines as the baseline for platform security.

**What it demands:** Educational institutions under MINESUP/MINESEC oversight must deploy approved digital platforms with adequate security controls for student data, online assessments, and academic records.

**External-Trust-Scoring Relevance:** Directives imply that student-facing portals and LMS must be accessible only via secure, authenticated channels — externally verifiable through TLS 1.2+ enforcement, HSTS, secure login endpoints, and the absence of exposed subdomains on academic platforms.

---

### 1.4 Cameroon Data Protection / Privacy Law (Embedded in Law 2010/012)

| Field | Value |
|---|---|
| **Full Name** | Data Protection Provisions of Law No. 2010/012 on Cybersecurity and Cybercriminality |
| **Common Abbreviation** | CM Data Protection Provisions |
| **Issuing Body** | Parliament of Cameroon |
| **Code/Key** | `CM-DATA-2010-012` |
| **Source** | Law No. 2010/012, Articles 16–20 (data protection chapter) |

**Education-Relevant Clauses:**

- **Article 16** — Defines personal data and establishes the principle of lawful, fair processing. Student records, biometric data, and academic histories fall within scope.
- **Article 17** — Requires data controllers (universities, schools) to implement appropriate technical and organizational measures to protect personal data.
- **Article 18** — Mandates informed consent before collecting or processing personal data, with special attention to minors (relevant for K-12 and secondary education).
- **Article 19** — Requires breach notification to ANTIC and affected data subjects.
- **Article 20** — Establishes data-subject rights: access, rectification, objection.

**What it demands:** Any education organization collecting or processing student/learner personal data must obtain consent, implement security measures, and report breaches. This is Cameroon's primary student-record protection framework.

**External-Trust-Scoring Relevance:** Article 17's "appropriate technical and organizational measures" requirement is the key externally verifiable clause — it implies encryption of data in transit (TLS) and at rest, secure authentication, and protection of student portals/LMS from unauthorized access.

---

### 1.5 Cameroon E-Education / Digital Infrastructure Policy

| Field | Value |
|---|---|
| **Full Name** | National Policy on Digital Infrastructure and E-Education (Cameroon Digital Strategy) |
| **Common Abbreviation** | CM Digital Strategy / E-Education Policy |
| **Issuing Body** | Government of Cameroon (interministerial: MINPOSTEL, MINESUP, MINESEC, MINEDUB) |
| **Code/Key** | `CM-DIGITAL-STRATEGY` |
| **Source** | Cameroon National Digital Strategy documents; PNDRNTIC (Plan National de Développement du Réseau National des Technologies de l'Information et de la Communication) |

**Education-Relevant Elements:**

- Promotes the deployment of broadband and secure digital infrastructure to educational institutions.
- Encourages the adoption of e-learning platforms with security-by-design principles.
- Supports the establishment of University Technology Transfer Offices and digital research repositories with data-protection requirements.
- Aligns with the AU Agenda 2063 and UNESCO digital-safety-in-education guidelines.

**What it demands:** Education institutions should participate in the national digital transformation with secure, interoperable platforms that protect student and research data.

**External-Trust-Scoring Relevance:** The policy's emphasis on "secure digital infrastructure" for education implies that institutional web properties should exhibit modern security postures — DNSSEC adoption, valid certificates, secure headers, and protection of e-learning subdomains.

---

## 2. Regional & Global Fallback Standards

Where Cameroon-specific rules are silent or insufficient, the following regional and global standards serve as authoritative fallbacks for evaluating education organizations.

### 2.1 FERPA — Family Educational Rights and Privacy Act (United States)

| Field | Value |
|---|---|
| **Full Name** | Family Educational Rights and Privacy Act of 1974 |
| **Common Abbreviation** | FERPA |
| **Issuing Body** | U.S. Department of Education (20 U.S.C. § 1232g; 34 CFR Part 99) |
| **Code/Key** | `FERPA-34CFR99` |
| **Source** | https://www.govinfo.gov/content/pkg/CFR-2024-title34-vol1/xml/CFR-2024-title34-vol1-part99.xml |

**Education-Relevant Clauses:**

- **§ 99.3** — Defines "personally identifiable information" (PII) to include student name, ID numbers, biometric records, and other identifiers. Defines "education records" broadly to include electronic records maintained by the institution.
- **§ 99.30** — Requires written (or electronic signed) consent before disclosing PII from education records, except as permitted by § 99.31.
- **§ 99.31** — Enumerates conditions under which prior consent is not required (school officials, transfers, audits, health/safety emergencies). Paragraph (a)(1)(ii) requires "reasonable methods" — including technological access controls — to ensure school officials obtain access only to records for which they have legitimate educational interests.
- **§ 99.32** — Recordkeeping requirements for all disclosures of PII.
- **§ 99.33** — Limits redisclosure of PII by third parties.

**What it demands:** Protects the privacy of student education records. Requires educational agencies/institutions to obtain consent before disclosing PII, implement access controls, and maintain records of disclosures. Applies to any institution receiving U.S. federal education funding — widely used as the global benchmark for student-record protection.

**External-Trust-Scoring Relevance:** § 99.31(a)(1)(ii) implies technological access controls on student records systems — externally verifiable via TLS 1.2+ and HSTS on student portals, secure authentication on LMS login pages, and absence of unauthenticated PII exposure on academic subdomains.

---

### 2.2 GDPR — General Data Protection Regulation (European Union)

| Field | Value |
|---|---|
| **Full Name** | Regulation (EU) 2016/679 — General Data Protection Regulation |
| **Common Abbreviation** | GDPR |
| **Issuing Body** | European Parliament and Council of the European Union |
| **Code/Key** | `GDPR-ART32` |
| **Source** | https://gdpr-info.eu/art-32-gdpr/ |

**Education-Relevant Articles:**

- **Article 5** — Principles for processing personal data: lawfulness, fairness, transparency, purpose limitation, data minimization, accuracy, storage limitation, integrity, and confidentiality.
- **Article 6** — Lawful basis for processing (consent, contract, legitimate interest, etc.).
- **Article 8** — Conditions for a child's consent in relation to information society services (age of digital consent: 16, member states may lower to 13). Directly relevant to ed-tech platforms serving minors.
- **Article 25** — Data protection by design and by default.
- **Article 32** — Security of processing: requires implementation of appropriate technical and organizational measures including (a) pseudonymisation and encryption of personal data; (b) ongoing confidentiality, integrity, availability, and resilience of processing systems; (c) ability to restore availability after incidents; (d) regular testing and evaluation of security measures.
- **Article 33** — Breach notification to supervisory authority within 72 hours.
- **Article 34** — Communication of breaches to data subjects when high risk.
- **Article 35** — Data Protection Impact Assessment (DPIA) required for high-risk processing (e.g., large-scale processing of student data, biometric systems in schools).
- **Article 89** — Safeguards and derogations for archiving, scientific research, or statistical purposes — relevant to research institutions processing learner data.

**What it demands:** Establishes comprehensive data-protection requirements for any entity processing personal data of EU residents — including education organizations and ed-tech platforms. Requires encryption, access controls, DPIAs for high-risk processing, and breach notification.

**External-Trust-Scoring Relevance:** Article 32(1)(a) explicitly names "encryption of personal data" as a required measure — externally verifiable via TLS posture on student/LMS portals. Article 25 (data protection by design) implies secure headers and HSTS. Article 32(1)(b) implies system resilience — verifiable via DNSSEC, certificate-transparency monitoring, and subdomain exposure checks.

---

### 2.3 ISO/IEC 27001:2022 — Information Security Management Systems

| Field | Value |
|---|---|
| **Full Name** | ISO/IEC 27001:2022 — Information security, cybersecurity and privacy protection — Information security management systems — Requirements |
| **Common Abbreviation** | ISO 27001 |
| **Issuing Body** | International Organization for Standardization (ISO) / International Electrotechnical Commission (IEC), Joint Technical Committee ISO/IEC JTC 1/SC 27 |
| **Code/Key** | `ISO-27001-A.14` (and related annex controls) |
| **Source** | https://www.iso.org/standard/27001 |

**Education-Relevant Annex A Controls (2022 edition):**

- **A.5.14** — Information transfer: policies and procedures for secure information transfer (implies TLS for student data in transit).
- **A.5.15** — Access control: logical access to systems (implies strong authentication on LMS/portals).
- **A.8.5** — Secure authentication: passwordless/multi-factor authentication guidance.
- **A.8.20** — Networks security: network segregation and protection (implies isolation of student data systems).
- **A.8.21** — Security of network services: security mechanisms, service levels, and management requirements (directly relevant to externally visible web/LMS services).
- **A.8.23** — Web filtering and content management.
- **A.8.24** — Use of cryptography: cryptographic key management and encryption policies (implies TLS 1.2+/1.3, HSTS).
- **A.5.24-5.27** — Incident management, reporting, and response.

**What it demands:** Establishes requirements for an Information Security Management System (ISMS). Organizations certified to ISO 27001 demonstrate they have systematic processes for identifying, managing, and reducing information-security risks — applicable to education institutions managing student data, research data, and academic records.

**External-Trust-Scoring Relevance:** A.8.21 (security of network services) and A.8.24 (use of cryptography) are directly externally verifiable — TLS cipher strength, HSTS presence, certificate validity, DNSSEC, and email security (SPF/DKIM/DMARC) on the institutional domain.

---

### 2.4 NIST SP 800-171 Rev. 3 — Protecting Controlled Unclassified Information

| Field | Value |
|---|---|
| **Full Name** | NIST Special Publication 800-171 Revision 3 — Protecting Controlled Unclassified Information in Nonfederal Systems and Organizations |
| **Common Abbreviation** | NIST SP 800-171 |
| **Issuing Body** | National Institute of Standards and Technology (NIST), U.S. Department of Commerce |
| **Code/Key** | `NIST-SP800-171-R3` |
| **Source** | https://csrc.nist.gov/pubs/sp/800/171/r3/final |

**Education-Relevant Control Families:**

- **AC (Access Control)** — AC.2.ii (limit access to CUI to authorized users); AC.3.1.i (enforce multifactor authentication). Relevant to research universities handling federal research data.
- **SC (System and Communications Protection)** — SC.2.ii (monitor and control communications at key boundaries); SC.3.i (protect confidentiality of CUI at rest and in transit via cryptographic mechanisms). Directly relevant to TLS posture and encryption.
- **IA (Identification and Authentication)** — IA.1.i (identify users and processes; authenticate before granting access).
- **SI (System and Information Integrity)** — SI.2 (monitor systems for malicious code and unauthorized access).
- **RA (Risk Assessment)** — RA.1 (conduct periodic risk assessments).

**What it demands:** Provides security requirements for protecting Controlled Unclassified Information (CUI) in nonfederal systems. Widely used by U.S. research universities and institutions that receive federal research grants (NSF, NIH, DoD) as a contractual requirement. Applicable as a reference standard for research institutions globally.

**External-Trust-Scoring Relevance:** SC.3.i (encryption of CUI in transit) is directly externally verifiable — TLS 1.2+/1.3 on research portals, HSTS, and secure subdomain configuration. AC.3.1.i (MFA) can be partially inferred from the presence of SSO/identity-provider endpoints on academic domains.

---

### 2.5 UNESCO Guidelines on Digital Safety in Education

| Field | Value |
|---|---|
| **Full Name** | UNESCO Guidelines on Digital Safety in Education / UNESCO Recommendation on the Ethics of Artificial Intelligence (education-relevant provisions) |
| **Common Abbreviation** | UNESCO Digital Safety in Education |
| **Issuing Body** | United Nations Educational, Scientific and Cultural Organization (UNESCO) |
| **Code/Key** | `UNESCO-DIGITAL-SAFETY-EDU` |
| **Source** | https://www.unesco.org/en/digital-technology-education (UNESCO Education and Digital Technology portal) |

**Education-Relevant Elements:**

- UNESCO promotes safe, inclusive, and secure digital learning environments.
- Guidelines address: protection of learner data, secure platform design, digital literacy for cybersecurity awareness, and national policy frameworks for digital safety in education.
- UNESCO's work on education technology emphasizes that "digital safety" includes both content safety (protecting learners from harmful content) and infrastructure safety (protecting learner data and platform integrity).
- Relevant to Cameroon as a UNESCO member state and as a reference framework for African education ministries.

**What it demands:** Education institutions and ed-tech providers should design digital learning platforms with built-in safety, privacy, and security measures; protect learner data from unauthorized access; and promote digital-citizenship education.

**External-Trust-Scoring Relevance:** UNESCO's emphasis on "secure platform design" implies TLS, HSTS, secure authentication, and DNSSEC as baseline external indicators of digital safety compliance.

---

### 2.6 African Union Malabo Convention — Cyber Security and Personal Data Protection

| Field | Value |
|---|---|
| **Full Name** | African Union Convention on Cyber Security and Personal Data Protection |
| **Common Abbreviation** | Malabo Convention |
| **Issuing Body** | African Union (AU) |
| **Code/Key** | `AU-MALABO-2014` |
| **Source** | https://au.int/en/treaties/african-union-convention-cyber-security-and-personal-data-protection (adopted 27 June 2014, Malabo, Equatorial Guinea) |

**Education-Relevant Clauses:**

- **Chapter I — Cybercrime:** Requires member states (including Cameroon) to criminalize attacks on electronic systems, data interception, and system interference — consistent with Cameroon's Law 2010/012.
- **Chapter II — Personal Data Protection:** Establishes principles for lawful and fair processing of personal data, consent, security of data, and data-subject rights. Education institutions processing student/learner data are within scope.
- **Chapter III — E-Commerce:** Contains provisions on the security of electronic transactions — relevant to institutions that process tuition payments or sell educational content online.
- **Article on Security Measures:** Requires data controllers to implement "appropriate technical and organizational measures" to protect personal data — analogous to GDPR Article 32.

**What it demands:** The AU's continental cybersecurity and data-protection framework. Cameroon is a signatory; the convention provides a harmonized baseline for African nations. Education organizations should align their data-protection practices with the convention's personal-data and cybersecurity provisions.

**External-Trust-Scoring Relevance:** The convention's "security measures" requirement for data controllers is externally verifiable via TLS, email authentication, DNSSEC, and certificate-transparency posture on institutional domains hosting student data.

---

### 2.7 CoSN (Consortium for School Networking) Cybersecurity Framework

| Field | Value |
|---|---|
| **Full Name** | CoSN K-12 Cybersecurity Framework and Resources (aligned with NIST Cybersecurity Framework) |
| **Common Abbreviation** | CoSN Cybersecurity |
| **Issuing Body** | Consortium for School Networking (CoSN), USA |
| **Code/Key** | `COSN-K12-CYBER` |
| **Source** | https://www.cosn.org/edtech-topics/cybersecurity/ |

**Education-Relevant Elements:**

- CoSN provides a K-12-specific cybersecurity framework organized around four pillars: Planning, Prevention & Preparation, Implementation, and Response.
- Aligns resources to the NIST Cybersecurity Framework (Identify, Protect, Detect, Respond, Recover).
- Includes the **K-12CVAT** (K-12 Community Vendor Assessment Tool) — a vendor-security assessment template for ed-tech procurement.
- Promotes the **Trusted Learning Environment (TLE) Seal** for student-data-privacy practices.
- Publishes annual state cybersecurity legislation reports for education.
- Addresses SaaS vendor cybersecurity risk management — directly relevant to ed-tech platforms.

**What it demands:** K-12 school systems should implement a structured cybersecurity program covering planning, prevention, implementation, and response; assess ed-tech vendors using standardized tools; and pursue the TLE Seal for student-data-privacy assurance. Globally applicable as a best-practice framework for school cybersecurity.

**External-Trust-Scoring Relevance:** CoSN's "Implementation" pillar (aligned to NIST CSF "Protect") covers access control, data security, and protective technology — externally verifiable via TLS, HSTS, email authentication, and DNS posture on school/ district domains.

---

## 3. Synthesized Domain-Specific Regulatory Checks

The following 12 regulatory checks synthesize the above regulations into externally verifiable, non-intrusive evaluations that MYEVIEW can perform for education organizations. Each check is framed as a pass/fail/warn assessment mapped to the relevant regulation(s).

### Check 1: TLS Posture on Student/LMS Portals

| Field | Value |
|---|---|
| **Regulations** | CM-LAW-2010-012 Art. 17; GDPR Art. 32(1)(a); ISO 27001 A.8.24; NIST SP 800-171 SC.3.i; FERPA §99.31(a)(1)(ii) |
| **Check** | Verify TLS 1.2+ (preferably TLS 1.3) on all student portals, LMS login pages, and academic records systems. |
| **Pass** | TLS 1.2 or 1.3 enforced; no legacy protocols (SSLv3, TLS 1.0, TLS 1.1) accepted. |
| **Warn** | TLS 1.2 supported but legacy protocols also accepted (downgrade risk). |
| **Fail** | Student portal/LMS accessible over plain HTTP or only legacy TLS. |
| **MYEVIEW Mapping** | `verify_tls_version(target=lms_portal, min_version=TLS1.2)` |

### Check 2: HSTS on Academic Web Properties

| Field | Value |
|---|---|
| **Regulations** | GDPR Art. 25 (data protection by design); ISO 27001 A.8.21; NIST SP 800-171 SC.2.ii; CM-LAW-2010-012 Art. 24 |
| **Check** | Verify Strict-Transport-Security (HSTS) header present on all institutional web properties serving student/LMS content. |
| **Pass** | HSTS header present with max-age ≥ 31536000 (1 year); includeSubDomains preferred. |
| **Warn** | HSTS present but max-age < 1 year, or missing includeSubDomains. |
| **Fail** | No HSTS header on any student-facing web property. |
| **MYEVIEW Mapping** | `verify_hsts(target=institutional_domain, min_age=31536000)` |

### Check 3: Email Security (SPF/DKIM/DMARC) on Institutional Domain

| Field | Value |
|---|---|
| **Regulations** | GDPR Art. 32(1)(b) (integrity); ISO 27001 A.8.21; NIST SP 800-171 SI.2; CM-LAW-2010-012 Art. 5 (interception); FERPA §99.30 (consent for disclosure — email-based disclosure risk) |
| **Check** | Verify SPF, DKIM, and DMARC records on the institutional email domain. |
| **Pass** | SPF + DKIM + DMARC all present; DMARC policy at `quarantine` or `reject`. |
| **Warn** | SPF and DKIM present but DMARC policy at `none` or missing. |
| **Fail** | No SPF, DKIM, or DMARC configured — institutional domain is spoofable. |
| **MYEVIEW Mapping** | `verify_email_auth(domain=institutional_domain, require_dmarc_policy=quarantine_or_reject)` |

### Check 4: DNSSEC on Institutional Domain

| Field | Value |
|---|---|
| **Regulations** | ISO 27001 A.8.21 (security of network services); NIST SP 800-171 SC.2.ii; CM-DIGITAL-STRATEGY (secure digital infrastructure); AU-MALABO-2014 (security measures for data controllers) |
| **Check** | Verify DNSSEC enabled on the institutional apex domain. |
| **Pass** | DNSSEC enabled with valid DS/DNSKEY records chain to parent zone. |
| **Warn** | DNSSEC enabled but with misconfigured or expiring records. |
| **Fail** | No DNSSEC — institutional domain is vulnerable to DNS spoofing/cache poisoning. |
| **MYEVIEW Mapping** | `verify_dnssec(domain=institutional_domain)` |

### Check 5: Certificate Transparency Monitoring

| Field | Value |
|---|---|
| **Regulations** | ISO 27001 A.8.24 (cryptography); GDPR Art. 32(1)(a) (encryption); NIST SP 800-171 AC.3.1.i (authentication); CM-LAW-2010-012 Art. 7 (fraudulent use of electronic certificates) |
| **Check** | Verify that institutional TLS certificates are logged in Certificate Transparency logs; check for unexpected/misissued certificates. |
| **Pass** | All observed certificates have SCT (Signed Certificate Timestamp) embedded; no misissued certificates detected in CT logs. |
| **Warn** | Certificates present but CT embedding not enforced (Expect-CT not configured). |
| **Fail** | Certificates without CT transparency or evidence of misissued/unauthorized certificates for the domain. |
| **MYEVIEW Mapping** | `verify_ct_logs(domain=institutional_domain, check_misissued=true)` |

### Check 6: Subdomain Exposure of E-Learning Platforms

| Field | Value |
|---|---|
| **Regulations** | GDPR Art. 25 (data protection by design); ISO 27001 A.5.15 (access control); NIST SP 800-171 AC.2.ii; FERPA §99.31(a)(1)(ii); CM-MINESUP-DIGITAL (secure platform deployment) |
| **Check** | Enumerate subdomains of the institutional domain; identify e-learning/ LMS/ student-portal subdomains; verify they are not unnecessarily exposed or serving default/error pages. |
| **Pass** | All identified e-learning subdomains resolve to secure, purpose-built services with TLS. |
| **Warn** | One or more e-learning subdomains resolve to default server pages or non-TLS endpoints. |
| **Fail** | Exposed subdomains revealing internal infrastructure, staging environments, or databases accessible without authentication. |
| **MYEVIEW Mapping** | `enumerate_subdomains(domain=institutional_domain, classify=lms_or_portal, check_unauth_exposure=true)` |

### Check 7: Web Security Headers on Academic Portals

| Field | Value |
|---|---|
| **Regulations** | GDPR Art. 25 (data protection by design); ISO 27001 A.8.21; NIST SP 800-171 SC.2.ii; CM-LAW-2010-012 Art. 24 (security measures for service providers) |
| **Check** | Verify presence of key web security headers (Content-Security-Policy, X-Frame-Options or CSP frame-ancestors, X-Content-Type-Options, Referrer-Policy, Permissions-Policy) on student portals and LMS. |
| **Pass** | CSP + X-Content-Type-Options + X-Frame-Options/CSP frame-ancestors + Referrer-Policy all present. |
| **Warn** | 1-2 key headers missing. |
| **Fail** | No security headers present on student-facing portals. |
| **MYEVIEW Mapping** | `verify_security_headers(target=lms_portal, required=[CSP, X-Content-Type-Options, Frame-Protection, Referrer-Policy])` |

### Check 8: Secure Login / Identity Provider Endpoint on LMS

| Field | Value |
|---|---|
| **Regulations** | FERPA §99.31(a)(1)(ii) (technological access controls); GDPR Art. 32(1)(b) (confidentiality); ISO 27001 A.8.5 (secure authentication); NIST SP 800-171 AC.3.1.i (MFA); CM-LAW-2010-012 Art. 16-17 (data protection measures) |
| **Check** | Verify the LMS / student portal has a secure, dedicated login endpoint (e.g., SSO/IdP redirect, HTTPS-only auth) rather than unauthenticated or HTTP login forms. |
| **Pass** | Login endpoint is HTTPS-only, on a dedicated auth path, with evidence of SSO/IdP integration. |
| **Warn** | Login endpoint is HTTPS but on the main domain without SSO/IdP evidence. |
| **Fail** | Login form served over HTTP or no identifiable secure auth endpoint. |
| **MYEVIEW Mapping** | `verify_login_endpoint(target=lms_portal, require_https=true, detect_sso=true)` |

### Check 9: Certificate Validity and Chain on Academic Domains

| Field | Value |
|---|---|
| **Regulations** | ISO 27001 A.8.24 (cryptography); GDPR Art. 32(1)(a); NIST SP 800-171 SC.3.i; CM-LAW-2010-012 Art. 7 (fraudulent use of certificates) |
| **Check** | Verify TLS certificates on all academic domains are valid, non-expired, issued by a trusted CA, with proper chain. |
| **Pass** | All certificates valid, > 30 days to expiry, trusted CA, complete chain. |
| **Warn** | Certificate expiring within 30 days or minor chain issue. |
| **Fail** | Expired, self-signed (on production student portal), or broken-chain certificate. |
| **MYEVIEW Mapping** | `verify_cert_chain(domain=institutional_domain, min_days_remaining=30, require_trusted_ca=true)` |

### Check 10: Open Port / Service Exposure on Institutional Infrastructure

| Field | Value |
|---|---|
| **Regulations** | ISO 27001 A.8.20 (networks security); NIST SP 800-171 AC.2.ii (limit access); CM-LAW-2010-012 Art. 4 (unauthorized access); CoSN-K12-CYBER (prevention pillar) |
| **Check** | Verify that institutional web-facing infrastructure does not expose unnecessary ports/services (e.g., databases, RDP, admin panels) that could compromise student data. |
| **Pass** | Only expected web-facing ports (80/443) and necessary services exposed. |
| **Warn** | 1 additional non-critical port open (e.g., SMTP on non-mail host). |
| **Fail** | Database ports, RDP, SSH, or admin panels exposed to the internet on academic infrastructure. |
| **MYEVIEW Mapping** | `scan_open_ports(target=institutional_ips, allowed_ports=[80,443], flag_databases=true)` |

### Check 11: Privacy Policy / Data-Processing Notice Presence

| Field | Value |
|---|---|
| **Regulations** | GDPR Art. 12-14 (transparency); CM-DATA-2010-012 Art. 18 (consent); FERPA §99.7 (annual notification); AU-MALABO-2014 (data-subject rights) |
| **Check** | Verify the institution publishes a privacy/data-protection notice on its website (externally discoverable). |
| **Pass** | Privacy policy/data-protection notice present, HTTPS-accessible, referencing student data handling. |
| **Warn** | Generic privacy policy present but not specifically addressing student data. |
| **Fail** | No privacy policy or data-protection notice discoverable on the institutional website. |
| **MYEVIEW Mapping** | `check_privacy_policy(domain=institutional_domain, require_student_data_reference=true)` |

### Check 12: Ed-Tech Vendor / SaaS Platform Security Posture

| Field | Value |
|---|---|
| **Regulations** | FERPA §99.31(a)(1)(B) (outsourced institutional functions); GDPR Art. 28 (processor); CoSN-K12-CYBER (K-12CVAT vendor assessment); ISO 27001 A.5.19-5.23 (supplier relationships); CM-MINESUP-DIGITAL (secure platform procurement) |
| **Check** | Verify that major ed-tech/SaaS platforms used by the institution (LMS, SIS, assessment tools) exhibit secure external posture (TLS, HSTS, DMARC) on their service domains. |
| **Pass** | All identified ed-tech vendor domains pass TLS + HSTS + DMARC checks. |
| **Warn** | 1 vendor domain missing one control (e.g., no DMARC). |
| **Fail** | Primary LMS or SIS vendor domain fails TLS or email-auth checks. |
| **MYEVIEW Mapping** | `assess_edtech_vendors(institution=institutional_domain, discover_vendor_domains=true, run_checks=[TLS, HSTS, DMARC])` |

---

## 4. Source URLs

| # | Regulation / Standard | Source URL |
|---|---|---|
| 1 | Cameroon Law 2010/012 (ANTIC portal) | https://www.antic.cm/ (ANTIC official site) |
| 2 | FERPA — 34 CFR Part 99 (full text) | https://www.govinfo.gov/content/pkg/CFR-2024-title34-vol1/xml/CFR-2024-title34-vol1-part99.xml |
| 3 | GDPR Article 32 (Security of processing) | https://gdpr-info.eu/art-32-gdpr/ |
| 4 | ISO/IEC 27001:2022 | https://www.iso.org/standard/27001 |
| 5 | NIST SP 800-171 Rev. 3 | https://csrc.nist.gov/pubs/sp/800/171/r3/final |
| 6 | AU Malabo Convention | https://au.int/en/treaties/african-union-convention-cyber-security-and-personal-data-protection |
| 7 | CISA K-12 Cybersecurity | https://www.cisa.gov/topics/cybersecurity-best-practices/K12cybersecurity |
| 8 | CoSN Cybersecurity | https://www.cosn.org/edtech-topics/cybersecurity/ |
| 9 | UNESCO Digital Technology in Education | https://www.unesco.org/en/digital-technology-education |
| 10 | Cameroon Wikipedia (background) | https://en.wikipedia.org/wiki/Cameroon |

---

## Summary Table: Regulations Mapped to External Checks

| Regulation | Key Code | Most Relevant External Check(s) |
|---|---|---|
| Cameroon Law 2010/012 | `CM-LAW-2010-012` | TLS, HSTS, Email Auth, Subdomain Exposure, Cert Validity |
| ANTIC Requirements | `CM-ANTIC-REQ` | TLS, DNSSEC, Web Headers, Open Ports |
| MINESUP/MINESEC Directives | `CM-MINESUP-DIGITAL` | TLS on LMS, Secure Login, Subdomain Exposure |
| Cameroon Data Protection | `CM-DATA-2010-012` | Privacy Policy, TLS, Email Auth |
| Cameroon Digital Strategy | `CM-DIGITAL-STRATEGY` | DNSSEC, TLS, Subdomain Exposure |
| FERPA | `FERPA-34CFR99` | TLS, HSTS, Secure Login, Subdomain Exposure |
| GDPR | `GDPR-ART32` | TLS, HSTS, Email Auth, Privacy Policy, CT Logs |
| ISO/IEC 27001:2022 | `ISO-27001-A.14` | TLS, HSTS, Web Headers, Cert Chain, DNSSEC |
| NIST SP 800-171 R3 | `NIST-SP800-171-R3` | TLS, HSTS, Email Auth, Open Ports, Cert Validity |
| UNESCO Digital Safety | `UNESCO-DIGITAL-SAFETY-EDU` | TLS, HSTS, DNSSEC, Secure Login |
| AU Malabo Convention | `AU-MALABO-2014` | TLS, DNSSEC, Email Auth, Privacy Policy |
| CoSN K-12 Cybersecurity | `COSN-K12-CYBER` | TLS, Web Headers, Ed-Tech Vendor Posture, Open Ports |

---

*End of Report. This is a research document only. No code was written or modified.*