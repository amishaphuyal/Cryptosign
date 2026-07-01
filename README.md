<div align="center">

<!-- ================= HEADER ================= -->

<img src="https://img.shields.io/badge/CryptoSign-Secure%20Digital%20Signature%20Platform-6366F1?style=for-the-badge" alt="CryptoSign">

<br><br>

<svg width="120" height="120" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="120" height="120" rx="28" fill="#0F172A"/>
  <rect x="30" y="49" width="60" height="44" rx="10" fill="#6366F1"/>
  <path d="M40 49V39C40 27.9543 48.9543 19 60 19C71.0457 19 80 27.9543 80 39V49" stroke="#A5B4FC" stroke-width="8" stroke-linecap="round"/>
  <circle cx="60" cy="69" r="6" fill="white"/>
  <path d="M60 75V84" stroke="white" stroke-width="5" stroke-linecap="round"/>
</svg>

# CryptoSign

### Secure Digital Signature, Certificate Authority and Document Protection Platform

<br>

<img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/GUI-CustomTkinter-6366F1?style=flat-square" alt="CustomTkinter">
<img src="https://img.shields.io/badge/RSA-2048-EF4444?style=flat-square" alt="RSA">
<img src="https://img.shields.io/badge/AES-256--GCM-10B981?style=flat-square" alt="AES">
<img src="https://img.shields.io/badge/Certificate-X.509-F59E0B?style=flat-square" alt="X.509">
<img src="https://img.shields.io/badge/Database-SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white" alt="SQLite">

<br><br>

<b>A Python desktop application for secure document signing, certificate management, encryption, verification and audit logging.</b>

</div>

---

## Table of Contents

- [Overview](#overview)
- [Application Preview](#application-preview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Cryptographic Workflows](#cryptographic-workflows)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [How to Run](#how-to-run)
- [Usage Guide](#usage-guide)
- [Security Controls](#security-controls)
- [Core Modules](#core-modules)
- [Supported Operations](#supported-operations)
- [Future Enhancements](#future-enhancements)
- [Author](#author)

---

## Overview

CryptoSign is a secure desktop-based document signing and certificate management system developed using Python. The application allows users to generate RSA key pairs, issue X.509 certificates, digitally sign documents, verify signatures, encrypt and decrypt files, revoke users and maintain full audit logs of cryptographic operations.

This project demonstrates practical implementation of Public Key Infrastructure, digital signatures, certificate authority, hybrid encryption, audit logging and secure document workflow management through a graphical user interface.

---

## Application Preview

The application interface includes login, user dashboard, admin dashboard, signing, verification, encryption and audit history screens.

<table>
<tr>
<td width="50%" align="center">

### Login Interface

<img src="assets/login.png" width="100%" alt="Login Interface">

</td>
<td width="50%" align="center">

### User Dashboard

<img src="assets/user_dashboard.png" width="100%" alt="User Dashboard">

</td>
</tr>

<tr>
<td width="50%" align="center">

### Admin Dashboard

<img src="assets/admin_dashboard.png" width="100%" alt="Admin Dashboard">

</td>
<td width="50%" align="center">

### Sign Document

<img src="assets/sign_document.png" width="100%" alt="Sign Document">

</td>
</tr>

<tr>
<td width="50%" align="center">

### Verify Document

<img src="assets/verify_document.png" width="100%" alt="Verify Document">

</td>
<td width="50%" align="center">

### Audit History

<img src="assets/audit_history.png" width="100%" alt="Audit History">

</td>
</tr>
</table>

> Screenshot images should be placed inside the `assets/` folder using the same names shown above.

---

## Key Features

<table>
<tr>
<td width="50%">

### Key Management

- RSA-2048 public/private key generation
- Password-protected private key support
- Secure local key storage
- Public key loading for verification and encryption

</td>
<td width="50%">

### Certificate Authority

- Root Certificate Authority generation
- X.509 certificate issuing
- CA-signed user certificates
- Certificate validity verification

</td>
</tr>

<tr>
<td width="50%">

### Digital Signing

- External signature generation using `.sig` files
- Embedded PDF signing
- PKCS#7 PDF signature support
- Smart signing mode selection
- Batch signing support

</td>
<td width="50%">

### Signature Verification

- RSA-based signature verification
- Embedded PDF signature detection
- Certificate verification before trust decision
- Revocation check before validation

</td>
</tr>

<tr>
<td width="50%">

### Encryption and Decryption

- AES-256-GCM file encryption
- RSA-based AES key protection
- Hybrid cryptography design
- Secure encrypted output storage

</td>
<td width="50%">

### Audit Logging

- SQLite audit database
- User activity history
- Operation result tracking
- Admin monitoring
- CSV export support

</td>
</tr>
</table>

---

## Technology Stack

| Category | Technology |
|---|---|
| Programming Language | Python |
| GUI Framework | CustomTkinter |
| Cryptography Library | cryptography |
| PDF Signing | PyHanko |
| PDF Processing | pypdf |
| Database | SQLite |
| Image Handling | Pillow |
| Document Conversion | docx2pdf |
| Storage | Local file system |

---

## System Architecture

```text
User / Administrator
        |
        v
Graphical User Interface
        |
        v
Application Logic Layer
        |
        |-- Authentication System
        |-- Key Manager
        |-- Certificate Authority Engine
        |-- Certificate Manager
        |-- Signing Engine
        |-- Verification Engine
        |-- Encryption Engine
        |-- Decryption Engine
        |-- Audit Logger
        |
        v
Local Secure Storage
        |
        |-- User Keys
        |-- CA Certificate
        |-- User Certificates
        |-- Signature Files
        |-- Encrypted Files
        |-- Audit Database
```

---

## Cryptographic Workflows

### Digital Signature Workflow

```text
Document
   |
   v
Read File Content
   |
   v
Generate SHA-256 Digest
   |
   v
Sign Digest using RSA Private Key
   |
   v
Create External Signature or Embedded PDF Signature
   |
   v
Verify using Public Key and X.509 Certificate
```

### Hybrid Encryption Workflow

```text
Original File
   |
   v
Generate AES-256 Key
   |
   v
Encrypt File using AES-256-GCM
   |
   v
Encrypt AES Key using RSA Public Key
   |
   v
Store Encrypted Data, Encrypted Key and Nonce
   |
   v
Decrypt AES Key using RSA Private Key
   |
   v
Restore Original File
```

### Certificate Trust Workflow

```text
Root CA Private Key
   |
   v
Issue User X.509 Certificate
   |
   v
User Signs Document
   |
   v
Verifier Checks Certificate Validity
   |
   v
Verifier Checks CA Signature
   |
   v
Verifier Checks Revocation Status
   |
   v
Signature Trust Decision
```

---

## Project Structure

```text
CryptoSign/
│
├── core/
│   ├── audit_logger.py
│   ├── auth_system.py
│   ├── auto_convert.py
│   ├── batch_sign.py
│   ├── ca_engine.py
│   ├── cert_manager.py
│   ├── cert_verifier.py
│   ├── decrypt_engine.py
│   ├── embed_pdf.py
│   ├── encrypt_engine.py
│   ├── hash_engine.py
│   ├── history_viewer.py
│   ├── key_manager.py
│   ├── pkcs_sign.py
│   ├── revocation.py
│   ├── sign_engine.py
│   ├── smart_sign.py
│   └── verify_engine.py
│
├── gui/
│   ├── __init__.py
│   ├── admin_dashboard.py
│   ├── login_dialog.py
│   ├── main_app.py
│   └── user_dashboard.py
│
├── assets/
│   ├── login.png
│   ├── user_dashboard.png
│   ├── admin_dashboard.png
│   ├── sign_document.png
│   ├── verify_document.png
│   └── audit_history.png
│
├── storage/
│   ├── audit.db
│   ├── ca/
│   ├── certs/
│   ├── encrypted/
│   ├── keystores/
│   ├── settings/
│   └── signatures/
│
├── tests/
├── main.py
├── requirements.txt
└── README.md
```

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/amishaphuyal/Cryptosign.git
cd Cryptosign
```

### Create a Virtual Environment

```bash
python -m venv venv
```

### Activate the Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

Linux / macOS:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not available, install the main dependencies manually:

```bash
pip install customtkinter cryptography pyhanko pypdf pillow docx2pdf
```

---

## How to Run

```bash
python main.py
```

---

## Usage Guide

### User Workflow

1. Register or login as a user.
2. Generate RSA key pair.
3. Issue or load X.509 certificate.
4. Select external or embedded signing mode.
5. Sign a selected document.
6. Verify a signed document.
7. Encrypt or decrypt files when required.
8. View activity history from the dashboard.

### Admin Workflow

1. Login as administrator.
2. View users and system statistics.
3. Approve or block user accounts.
4. View audit logs.
5. Manage certificates.
6. Revoke users or certificates.
7. Monitor document security activity.

---

## Security Controls

| Security Area | Implementation |
|---|---|
| Authentication | Login and registration system |
| Authorization | Separate user and admin dashboards |
| Key Protection | Password-protected RSA private key support |
| Integrity | SHA-256 hashing |
| Non-repudiation | RSA digital signatures |
| Confidentiality | AES-256-GCM encryption |
| Trust Management | X.509 certificates and CA verification |
| Revocation | Revoked user tracking |
| Accountability | SQLite audit logging |
| Monitoring | Admin dashboard and activity logs |

---

## Core Modules

| Module | Purpose |
|---|---|
| `auth_system.py` | Handles user authentication, registration and account status |
| `key_manager.py` | Generates and loads RSA key pairs |
| `ca_engine.py` | Creates the root certificate authority |
| `cert_manager.py` | Issues X.509 certificates for users |
| `cert_verifier.py` | Verifies certificate validity and CA trust |
| `sign_engine.py` | Creates RSA external signatures |
| `pkcs_sign.py` | Performs embedded PDF signing |
| `smart_sign.py` | Selects the correct signing method |
| `verify_engine.py` | Verifies external and embedded signatures |
| `encrypt_engine.py` | Encrypts files using hybrid encryption |
| `decrypt_engine.py` | Decrypts encrypted files |
| `audit_logger.py` | Stores audit records in SQLite |
| `batch_sign.py` | Signs multiple documents in a folder |
| `revocation.py` | Handles revoked users |
| `hash_engine.py` | Generates SHA-256 hashes |
| `history_viewer.py` | Displays user audit history |

---

## Supported Operations

| Operation | Description |
|---|---|
| Setup User | Generates keys and certificate |
| Sign File | Digitally signs selected file |
| Verify File | Validates signature and certificate |
| Batch Sign | Signs multiple documents |
| Encrypt File | Encrypts files using AES and RSA |
| Decrypt File | Restores encrypted files |
| File Hash | Generates SHA-256 file hash |
| Revoke User | Blocks revoked users from signing |
| Audit History | Displays user activity history |

---

## Audit Logging

CryptoSign records important security events and document operations in an SQLite database.

| Field | Description |
|---|---|
| Timestamp | Date and time of activity |
| Username | User who performed the action |
| Action | Operation such as SIGN, VERIFY, ENCRYPT or DECRYPT |
| File Name | Target file name |
| File Hash | SHA-256 hash when available |
| Result | SUCCESS, FAILED, VALID or INVALID |
| Details | Additional operation information |

---

## Example Audit Records

| Timestamp | Username | Action | File | Result |
|---|---|---|---|---|
| 2026-07-01 10:30:21 | amisha | SIGN | report.pdf | SUCCESS |
| 2026-07-01 10:35:10 | amisha | VERIFY | report_signed.pdf | VALID |
| 2026-07-01 10:40:44 | admin | ADMIN_APPROVE | user1 | SUCCESS |

---

## Future Enhancements

- Multi-factor authentication
- Cloud-based certificate repository
- OCSP or CRL-based certificate validation
- Visual PDF signature placement
- Email notification for certificate approval
- Secure backup and restore feature
- Windows installer package
- Role-based permission policies
- Improved Office document conversion support
- Centralized certificate lifecycle management

---

## Learning Outcomes

This project demonstrates practical understanding of:

- Public Key Infrastructure
- RSA digital signatures
- AES-GCM encryption
- X.509 certificate issuing and validation
- Certificate authority implementation
- Secure key management
- Document integrity verification
- Revocation handling
- Audit logging and accountability
- GUI-based security application development

---

## Author

<div align="center">

<b>Amisha Phuyal</b>

BSc (Hons) Ethical Hacking and Cybersecurity  
Softwarica College of IT and E-Commerce  
Coventry University

<br><br>

<img src="https://img.shields.io/badge/Cybersecurity-Student-6366F1?style=for-the-badge" alt="Cybersecurity Student">
<img src="https://img.shields.io/badge/Project-CryptoSign-10B981?style=for-the-badge" alt="CryptoSign">

</div>

---

## License

This project is developed for academic and learning purposes.

---

<div align="center">

### CryptoSign — Secure. Trusted. Verifiable.

<b>Digital Signature and Certificate Management Platform</b>

</div>
