<div align="center">

<img src="https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/lock.svg" width="75" height="75" alt="CryptoSign Logo">

# CryptoSign

### Secure Digital Signature, Certificate Authority and Document Protection Platform

<img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/GUI-CustomTkinter-6366F1?style=for-the-badge" alt="CustomTkinter">
<img src="https://img.shields.io/badge/Cryptography-RSA--2048%20%7C%20AES--256--GCM-red?style=for-the-badge" alt="Cryptography">
<img src="https://img.shields.io/badge/Certificate-X.509-10B981?style=for-the-badge" alt="X.509">
<img src="https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">

<br><br>

<b>CryptoSign is a desktop-based digital signature and certificate management system developed in Python.</b>

</div>

---

## Overview

CryptoSign is a secure document signing platform that allows users to generate RSA key pairs, issue X.509 certificates, sign documents, verify signatures, encrypt files, decrypt files, revoke users and maintain audit logs.

The project demonstrates the practical use of Public Key Infrastructure, digital signatures, certificate authority, hybrid encryption and audit logging in a graphical desktop application.

---

## Screenshots

Create a folder named `screenshots` in the project root and add your screenshots using the exact file names below.

```text
CryptoSign/
│
├── screenshots/
│   ├── login.png
│   ├── user_dashboard.png
│   ├── admin_dashboard.png
│   ├── sign_file.png
│   ├── verify_file.png
│   ├── encrypt_file.png
│   ├── audit_history.png
│   └── certificate_management.png
```

### Login Screen

<p align="center">
  <img src="screenshots/login.png" width="850" alt="Login Screen">
</p>

### User Dashboard

<p align="center">
  <img src="screenshots/user_dashboard.png" width="850" alt="User Dashboard">
</p>

### Admin Dashboard

<p align="center">
  <img src="screenshots/admin_dashboard.png" width="850" alt="Admin Dashboard">
</p>

### Sign File

<p align="center">
  <img src="screenshots/sign_file.png" width="850" alt="Sign File">
</p>

### Verify File

<p align="center">
  <img src="screenshots/verify_file.png" width="850" alt="Verify File">
</p>

### Encrypt File

<p align="center">
  <img src="screenshots/encrypt_file.png" width="850" alt="Encrypt File">
</p>

### Audit History

<p align="center">
  <img src="screenshots/audit_history.png" width="850" alt="Audit History">
</p>

### Certificate Management

<p align="center">
  <img src="screenshots/certificate_management.png" width="850" alt="Certificate Management">
</p>

---

## Key Features

<table>
<tr>
<td width="50%">

### Key Management

- RSA-2048 key pair generation
- Public and private key storage
- Password-protected private key support
- Secure local keystore

</td>
<td width="50%">

### Certificate Authority

- Root Certificate Authority generation
- X.509 certificate issuing
- Certificate validation
- CA-based trust verification

</td>
</tr>

<tr>
<td width="50%">

### Digital Signature

- External `.sig` signature generation
- Embedded PDF signing
- PKCS#7 PDF signing support
- Batch document signing

</td>
<td width="50%">

### Signature Verification

- RSA signature verification
- Certificate validity checking
- Revocation checking
- Embedded signature detection

</td>
</tr>

<tr>
<td width="50%">

### Encryption and Decryption

- AES-256-GCM file encryption
- RSA-based AES key protection
- Hybrid encryption method
- Secure encrypted output handling

</td>
<td width="50%">

### Audit Logging

- SQLite-based audit database
- User activity history
- Operation statistics
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
| Cryptography | cryptography |
| PDF Signing | PyHanko |
| PDF Processing | pypdf |
| Database | SQLite |
| Image Handling | Pillow |
| Document Conversion | docx2pdf |
| Storage | Local File System |

---

## System Architecture

```text
User / Admin
    |
    v
Graphical User Interface
    |
    v
Application Logic Layer
    |
    |-- Authentication System
    |-- Key Manager
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
    |-- Keys
    |-- Certificates
    |-- Signatures
    |-- Encrypted Files
    |-- Audit Database
```

---

## Digital Signature Workflow

```text
Document
   |
   v
Read File Content
   |
   v
Generate SHA-256 Hash
   |
   v
Sign with RSA Private Key
   |
   v
Create Signature File or Embedded PDF Signature
   |
   v
Verify with Public Key and Certificate
```

---

## Hybrid Encryption Workflow

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
Store Encrypted File, Encrypted Key and Nonce
   |
   v
Decrypt AES Key using RSA Private Key
   |
   v
Restore Original File
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
├── screenshots/
│   ├── login.png
│   ├── user_dashboard.png
│   ├── admin_dashboard.png
│   ├── sign_file.png
│   ├── verify_file.png
│   ├── encrypt_file.png
│   ├── audit_history.png
│   └── certificate_management.png
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

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

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

If `requirements.txt` is not available:

```bash
pip install customtkinter cryptography pyhanko pypdf pillow docx2pdf
```

---

## Run the Application

```bash
python main.py
```

---

## Usage

### User Workflow

1. Register or login as a user.
2. Generate RSA key pair.
3. Issue or load X.509 certificate.
4. Select signing mode.
5. Sign a file using external or embedded signing.
6. Verify signed documents.
7. Encrypt or decrypt files.
8. View activity history.

### Admin Workflow

1. Login as administrator.
2. View system statistics.
3. Approve, block or manage users.
4. View audit logs.
5. Manage certificates.
6. Revoke users or certificates.
7. Monitor system activity.

---

## Security Controls

| Security Area | Implementation |
|---|---|
| Authentication | Login and registration system |
| Authorization | Separate user and admin dashboards |
| Key Protection | Password-protected RSA private keys |
| Integrity | SHA-256 hashing |
| Non-repudiation | RSA digital signatures |
| Confidentiality | AES-256-GCM encryption |
| Trust Management | X.509 certificates and CA verification |
| Revocation | Revoked user list |
| Accountability | SQLite audit logging |
| Monitoring | Admin dashboard and activity tracking |

---

## Core Modules

| Module | Purpose |
|---|---|
| `auth_system.py` | Handles user authentication and account status |
| `key_manager.py` | Generates and loads RSA key pairs |
| `ca_engine.py` | Creates root certificate authority |
| `cert_manager.py` | Issues X.509 certificates |
| `cert_verifier.py` | Verifies certificate validity |
| `sign_engine.py` | Creates external RSA signatures |
| `verify_engine.py` | Verifies signed documents |
| `pkcs_sign.py` | Performs embedded PDF signing |
| `smart_sign.py` | Selects correct signing method |
| `encrypt_engine.py` | Encrypts files using hybrid encryption |
| `decrypt_engine.py` | Decrypts encrypted files |
| `audit_logger.py` | Stores operation logs in SQLite |
| `batch_sign.py` | Signs multiple documents |
| `revocation.py` | Handles revoked users |
| `hash_engine.py` | Generates SHA-256 file hashes |

---

## Supported Operations

| Operation | Description |
|---|---|
| Setup User | Generates keys and certificate |
| Sign File | Digitally signs selected file |
| Verify File | Checks signature and certificate |
| Batch Sign | Signs multiple files from folder |
| Encrypt File | Encrypts file using AES and RSA |
| Decrypt File | Restores encrypted file |
| File Hash | Generates SHA-256 hash |
| Revoke User | Blocks signing for revoked user |
| Audit History | Shows logged user activities |

---

## Audit Logging

CryptoSign records all major security activities.

| Field | Description |
|---|---|
| Timestamp | Date and time of activity |
| Username | User who performed the action |
| Action | SIGN, VERIFY, ENCRYPT, DECRYPT, HASH |
| File Name | Target document |
| File Hash | SHA-256 hash if available |
| Result | SUCCESS, FAILED, VALID, INVALID |
| Details | Additional operation details |

---

## Future Enhancements

- Multi-factor authentication
- Cloud certificate repository
- OCSP or CRL-based certificate validation
- Visual PDF signature placement
- Email notification for certificate approval
- Secure backup and restore system
- Windows installer package
- Role-based access control policies
- Improved Office document conversion
- Centralized certificate lifecycle management

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
