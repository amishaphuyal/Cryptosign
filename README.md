<div align="center">

<svg width="88" height="88" viewBox="0 0 88 88" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="88" height="88" rx="22" fill="#111827"/>
  <path d="M26 40V32C26 22.1 34.1 14 44 14C53.9 14 62 22.1 62 32V40" stroke="#6366F1" stroke-width="6" stroke-linecap="round"/>
  <rect x="20" y="38" width="48" height="36" rx="8" fill="#6366F1"/>
  <circle cx="44" cy="55" r="5" fill="white"/>
  <path d="M44 59V66" stroke="white" stroke-width="4" stroke-linecap="round"/>
</svg>

# CryptoSign

### Secure Digital Signature, Certificate Authority & Document Protection Platform

<br>

<img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/GUI-CustomTkinter-6366F1?style=for-the-badge" alt="CustomTkinter">
<img src="https://img.shields.io/badge/Cryptography-RSA--2048%20%7C%20AES--256--GCM-red?style=for-the-badge" alt="Cryptography">
<img src="https://img.shields.io/badge/Certificate-X.509-success?style=for-the-badge" alt="X.509">
<img src="https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">

<br><br>

<b>Enterprise-style Digital Signature, Certificate Management, Encryption, Verification and Audit Logging System</b>

<br><br>

</div>

---

## About CryptoSign

**CryptoSign** is a secure desktop-based digital document signing and certificate management platform developed in Python.  
The system allows users to generate cryptographic key pairs, issue X.509 certificates, digitally sign documents, verify signatures, encrypt/decrypt files, manage revoked users and maintain complete audit logs of cryptographic activities.

The project is designed to demonstrate practical implementation of **public key infrastructure (PKI)**, **digital signatures**, **certificate authority**, **hybrid encryption**, **audit logging**, and **secure document handling** through a clean graphical interface.

---

## Key Features

<div align="center">

<svg width="720" height="90" viewBox="0 0 720 90" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="720" height="90" rx="18" fill="#111827"/>
  <circle cx="70" cy="45" r="24" fill="#6366F1"/>
  <path d="M58 45l8 8 16-18" stroke="white" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="115" y="39" fill="#F8FAFC" font-size="18" font-family="Arial" font-weight="700">PKI-Based Digital Signature Platform</text>
  <text x="115" y="62" fill="#94A3B8" font-size="13" font-family="Arial">RSA-2048 signing, X.509 certificates, AES-256-GCM encryption and SQLite audit logging</text>
</svg>

</div>

<br>

<table>
<tr>
<td width="50%">

### <svg width="18" height="18" viewBox="0 0 24 24" fill="#6366F1" xmlns="http://www.w3.org/2000/svg"><path d="M7 14a5 5 0 1 1 4.58-3H22v3h-3v3h-3v-3h-4.42A5 5 0 0 1 7 14Zm0-3a2 2 0 1 0 0-4 2 2 0 0 0 0 4Z"/></svg> Key Management
- RSA-2048 key pair generation
- Public and private key storage
- Optional password-protected private keys
- Secure keystore folder structure

</td>
<td width="50%">

### <svg width="18" height="18" viewBox="0 0 24 24" fill="#10B981" xmlns="http://www.w3.org/2000/svg"><path d="M12 2 4 5v6c0 5.1 3.4 9.9 8 11 4.6-1.1 8-5.9 8-11V5l-8-3Zm-1 14-4-4 2.1-2.1 1.9 1.9 4.9-4.9L18 9l-7 7Z"/></svg> Certificate Authority
- Root CA generation
- X.509 certificate issuing
- Certificate validation
- CA-based public key trust verification

</td>
</tr>

<tr>
<td width="50%">

### <svg width="18" height="18" viewBox="0 0 24 24" fill="#F59E0B" xmlns="http://www.w3.org/2000/svg"><path d="M3 17.25V21h3.75L17.8 9.95l-3.75-3.75L3 17.25ZM20.7 7.05a1 1 0 0 0 0-1.4l-2.35-2.35a1 1 0 0 0-1.4 0l-1.85 1.85 3.75 3.75 1.85-1.85Z"/></svg> Digital Signing
- External `.sig` signature generation
- Embedded PDF signing
- PKCS#7 PDF signature support
- Batch document signing

</td>
<td width="50%">

### <svg width="18" height="18" viewBox="0 0 24 24" fill="#0EA5E9" xmlns="http://www.w3.org/2000/svg"><path d="M9 16.2 4.8 12l-2 2L9 20 22 7l-2-2L9 16.2Z"/></svg> Signature Verification
- RSA signature verification
- PDF embedded signature detection
- Certificate validity checking
- Revocation status checking

</td>
</tr>

<tr>
<td width="50%">

### <svg width="18" height="18" viewBox="0 0 24 24" fill="#EF4444" xmlns="http://www.w3.org/2000/svg"><path d="M17 8h-1V6a4 4 0 0 0-8 0v2H7a2 2 0 0 0-2 2v10h14V10a2 2 0 0 0-2-2Zm-7 0V6a2 2 0 0 1 4 0v2h-4Z"/></svg> Encryption & Decryption
- AES-256-GCM file encryption
- RSA-based AES key protection
- Hybrid cryptography approach
- Secure encrypted output handling

</td>
<td width="50%">

### <svg width="18" height="18" viewBox="0 0 24 24" fill="#8B5CF6" xmlns="http://www.w3.org/2000/svg"><path d="M4 3h16v18H4V3Zm4 5h8V6H8v2Zm0 4h8v-2H8v2Zm0 4h5v-2H8v2Z"/></svg> Audit Logging
- SQLite-based audit database
- User activity history
- Operation statistics
- CSV export support

</td>
</tr>
</table>

---

## User Interfaces

CryptoSign includes separate interfaces for normal users and administrators.

### User Dashboard
- View signing overview
- Sign, verify, encrypt and decrypt files
- Batch sign multiple documents
- View personal activity logs
- Manage profile and settings
- Receive certificate and activity alerts

### Admin Dashboard
- Manage users
- Approve or block pending accounts
- View audit logs
- Manage certificates
- Track revoked certificates
- Monitor system activity
- Configure admin interface settings

---

## Technology Stack

| Category | Technology |
|---|---|
| Programming Language | Python |
| GUI Framework | CustomTkinter |
| Cryptography | `cryptography` library |
| PDF Signing | PyHanko |
| PDF Processing | PyPDF / pypdf |
| Database | SQLite |
| Document Conversion | docx2pdf |
| Image Handling | Pillow |
| File Storage | Local secure storage folders |

---

## Cryptographic Design

CryptoSign uses a practical PKI-inspired architecture.

### Digital Signature Flow

```text
Document
   ↓
SHA-256 Hashing
   ↓
RSA Private Key Signing
   ↓
Signature File / Embedded PDF Signature
   ↓
Verification using Public Key + Certificate
```

### Hybrid Encryption Flow

```text
Original File
   ↓
AES-256-GCM Encryption
   ↓
AES Key Encrypted with RSA Public Key
   ↓
Encrypted File + Encrypted Key + Nonce
   ↓
RSA Private Key Decrypts AES Key
   ↓
AES Restores Original File
```

---

## Project Structure

```text
CryptoSign/
│
├── core/
│   ├── audit_logger.py        # SQLite audit logging
│   ├── auth_system.py         # User authentication
│   ├── auto_convert.py        # Office to PDF conversion
│   ├── batch_sign.py          # Batch document signing
│   ├── ca_engine.py           # Root CA generation
│   ├── cert_manager.py        # X.509 certificate issuing
│   ├── cert_verifier.py       # Certificate validation
│   ├── decrypt_engine.py      # Hybrid decryption
│   ├── embed_pdf.py           # PDF metadata signature embedding
│   ├── encrypt_engine.py      # Hybrid encryption
│   ├── hash_engine.py         # SHA-256 hashing
│   ├── history_viewer.py      # Audit history viewer
│   ├── key_manager.py         # RSA key management
│   ├── pkcs_sign.py           # PKCS#7 PDF signing
│   ├── revocation.py          # Certificate/user revocation
│   ├── sign_engine.py         # RSA signing engine
│   ├── smart_sign.py          # Smart signing mode selection
│   └── verify_engine.py       # Signature verification
│
├── gui/
│   ├── __init__.py
│   ├── admin_dashboard.py     # Admin control panel
│   ├── login_dialog.py        # Login/register window
│   ├── main_app.py            # Main application window
│   └── user_dashboard.py      # User dashboard
│
├── storage/
│   ├── audit.db               # Audit database
│   ├── ca/                    # CA key and certificate
│   ├── certs/                 # User certificates
│   ├── encrypted/             # Encrypted output files
│   ├── keystores/             # User key pairs
│   ├── settings/              # UI settings
│   └── signatures/            # External signature files
│
├── tests/
│
├── main.py
├── requirements.txt
└── README.md
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/CryptoSign.git
cd CryptoSign
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / macOS

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not available, install the main packages manually:

```bash
pip install customtkinter cryptography pyhanko pypdf pillow docx2pdf
```

---

## How to Run

```bash
python main.py
```

After launching the application:

1. Register a new user.
2. Login using your account.
3. Generate keys and certificate from setup.
4. Select signing mode.
5. Sign, verify, encrypt or decrypt documents.
6. Check audit history from the dashboard.

---

## Main Functional Modules

### Key Generation

The system generates RSA-2048 key pairs and stores them inside `storage/keystores/`.

```text
username_private.pem
username_public.pem
```

Private keys can be stored with password protection.

---

### Certificate Issuing

CryptoSign creates a root certificate authority and issues user certificates signed by the CA.

```text
storage/ca/ca_private.pem
storage/ca/ca_cert.pem
storage/certs/username_cert.pem
```

---

### Document Signing

CryptoSign supports two signing modes:

| Mode | Description |
|---|---|
| External Signature | Creates separate `.sig` signature file |
| Embedded Signature | Signs PDF files using PKCS#7 embedded signature |

For Office documents such as `.docx`, `.xlsx`, and `.pptx`, the system attempts to convert the file into PDF before signing.

---

### Document Verification

The verification process checks:

1. User revocation status
2. Certificate existence
3. Certificate validity
4. CA signature validation
5. Embedded PDF signature or external `.sig` file
6. RSA signature correctness

---

### File Encryption

CryptoSign uses hybrid encryption:

- AES-256-GCM encrypts the file content.
- RSA-2048 encrypts the AES key.
- Nonce and encrypted key are stored for decryption.

---

### <svg width="18" height="18" viewBox="0 0 24 24" fill="#8B5CF6" xmlns="http://www.w3.org/2000/svg"><path d="M4 3h16v18H4V3Zm4 5h8V6H8v2Zm0 4h8v-2H8v2Zm0 4h5v-2H8v2Z"/></svg> Audit Logging

All major operations are logged into an SQLite database.

Logged data includes:

- Timestamp
- Username
- Action
- File name
- File hash
- Result
- Details
- IP address

Audit logs can also be exported as CSV.

---

## Security Controls Implemented

| Security Control | Implementation |
|---|---|
| Authentication | Login and registration system |
| Access Control | Admin and user dashboard separation |
| Key Protection | Password-protected private key support |
| Data Integrity | SHA-256 hashing |
| Non-repudiation | RSA digital signature |
| Confidentiality | AES-256-GCM encryption |
| Trust Management | X.509 certificates and CA verification |
| Revocation | Revoked user/certificate list |
| Accountability | SQLite audit logs |
| Admin Oversight | Admin dashboard and audit monitoring |

---

## Audit Log Example

| Timestamp | User | Action | File | Result |
|---|---|---|---|---|
| 2026-07-01 10:30:21 | amisha | SIGN | report.pdf | SUCCESS |
| 2026-07-01 10:35:10 | amisha | VERIFY | report_signed.pdf | VALID |
| 2026-07-01 10:40:44 | admin | ADMIN_APPROVE | user1 | SUCCESS |

---

## Suggested Screenshots for Report / GitHub

You can add screenshots inside a `screenshots/` folder and link them like this:

```html
<div align="center">
  <img src="screenshots/login.png" width="700" alt="Login Screen">
  <br>
  <b>Figure 1: CryptoSign Login Interface</b>
</div>
```

Recommended screenshots:

- Login and registration screen
- User dashboard
- Admin dashboard
- Sign document process
- Verify document result
- Audit history window
- Certificate management page

---

## Future Enhancements

- Cloud-based certificate repository
- Real-time CRL or OCSP validation
- Multi-factor authentication
- Role-based permission policies
- Visual signature placement on PDF
- Email-based certificate approval notification
- Secure backup and restore feature
- Improved document conversion support
- Installer package for Windows

---

## Learning Outcomes

This project demonstrates practical understanding of:

- Public Key Infrastructure
- RSA digital signatures
- AES-GCM encryption
- Certificate Authority implementation
- X.509 certificate issuing and validation
- Secure key management
- Audit logging
- GUI-based security application development
- Secure document workflow design

---

## Author

<div align="center">

<b>Amisha Phuyal</b>  
BSc (Hons) Ethical Hacking and Cybersecurity  
Softwarica College of IT & E-Commerce  
Coventry University

<br><br>

<img src="https://img.shields.io/badge/Cybersecurity-Student-6366F1?style=for-the-badge" alt="Cybersecurity Student">
<img src="https://img.shields.io/badge/Project-CryptoSign-10B981?style=for-the-badge" alt="CryptoSign">

</div>

---

## License

This project is developed for academic and learning purposes.  
You may modify and extend it according to your project requirements.

---

<div align="center">

### CryptoSign — Secure. Trusted. Verifiable.

<b>Digital Signature and Certificate Management Platform</b>

</div>
