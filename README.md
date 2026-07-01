<div align="center">

<svg width="90" height="90" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="120" height="120" rx="28" fill="#0F172A"/>
  <rect x="30" y="49" width="60" height="44" rx="10" fill="#6366F1"/>
  <path d="M40 49V39C40 27.9543 48.9543 19 60 19C71.0457 19 80 27.9543 80 39V49" stroke="#A5B4FC" stroke-width="8" stroke-linecap="round"/>
  <circle cx="60" cy="69" r="6" fill="white"/>
  <path d="M60 75V84" stroke="white" stroke-width="5" stroke-linecap="round"/>
</svg>

# CryptoSign

### Secure Digital Signature & Certificate Authority Platform

<img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/GUI-CustomTkinter-6366F1?style=flat-square" alt="CustomTkinter">
<img src="https://img.shields.io/badge/RSA-2048-EF4444?style=flat-square" alt="RSA">
<img src="https://img.shields.io/badge/AES-256--GCM-10B981?style=flat-square" alt="AES">

</div>

---

## Overview

CryptoSign is a Python desktop app for signing, verifying, encrypting and managing documents securely. It lets users generate RSA key pairs, issue X.509 certificates, sign and verify files, encrypt/decrypt data, and keep a full audit log — all through a simple GUI.

---

## Features

<table>
<tr>
<td width="33%" valign="top">

<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2"><rect x="3" y="11" width="18" height="10" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>

**Key & Certificate Management**
RSA-2048 keys, password protection, X.509 certificate issuing via a built-in CA.

</td>
<td width="33%" valign="top">

<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2"><path d="M12 2l8 4v6c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V6l8-4z"/><path d="M9 12l2 2 4-4"/></svg>

**Signing & Verification**
Sign PDFs and files, verify signatures, and check certificates before trusting them.

</td>
<td width="33%" valign="top">

<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2"><rect x="3" y="11" width="18" height="10" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0"/><circle cx="12" cy="16" r="1.5"/></svg>

**Encryption & Audit**
AES-256-GCM file encryption with RSA-protected keys, plus full SQLite audit logging.

</td>
</tr>
</table>

---

## Technology Stack

| Category | Technology |
|---|---|
| Language | Python |
| GUI | CustomTkinter |
| Cryptography | `cryptography`, PyHanko |
| PDF Handling | pypdf |
| Database | SQLite |
| Images | Pillow |

---

## How It Works

```text
Document → SHA-256 Hash → Signed with RSA Private Key → Verified with Public Key + Certificate
```

```text
File → AES-256 Encrypted → AES Key Locked with RSA Public Key → Decrypted with RSA Private Key
```

---

## Project Structure

```text
CryptoSign/
├── core/        → signing, verification, encryption, certificates, audit logic
├── gui/         → login, dashboards, main app
├── assets/      → screenshots
├── storage/     → keys, certs, encrypted files, audit database
├── main.py
└── requirements.txt
```

---

## Installation

```bash
git clone https://github.com/amishaphuyal/Cryptosign.git
cd Cryptosign
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux / macOS
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

---

## Usage

**As a User:** Register/login → generate keys → get a certificate → sign or verify documents → encrypt/decrypt files → view your history.

**As an Admin:** Login → manage users → view audit logs → issue or revoke certificates → monitor activity.

---

## Security Highlights

| Area | Method |
|---|---|
| Integrity | SHA-256 hashing |
| Non-repudiation | RSA digital signatures |
| Confidentiality | AES-256-GCM encryption |
| Trust | X.509 certificates + CA verification |
| Accountability | SQLite audit logs |

---

## Author

<div align="center">

**Amisha Phuyal**
BSc (Hons) Ethical Hacking and Cybersecurity
Softwarica College of IT and E-Commerce, Coventry University

</div>

---

<div align="center">

### CryptoSign — Secure. Trusted. Verifiable.

</div>