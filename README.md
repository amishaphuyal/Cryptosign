<div align="center">

<h1>CryptoSign</h1>

<h3>PKI-Based Digital Document Signing, Certificate Management and Hybrid File Encryption System</h3>

<br>

<img src="https://img.shields.io/badge/Python-3.13-blue?logo=python&style=for-the-badge">
<img src="https://img.shields.io/badge/RSA-2048-success?style=for-the-badge">
<img src="https://img.shields.io/badge/RSA--PSS-Digital%20Signature-orange?style=for-the-badge">
<img src="https://img.shields.io/badge/AES--256--GCM-Encryption-red?style=for-the-badge">
<img src="https://img.shields.io/badge/SHA--256-Hashing-yellow?style=for-the-badge">
<img src="https://img.shields.io/badge/X.509-Certificate-green?style=for-the-badge">
<img src="https://img.shields.io/badge/SQLite-Database-blue?logo=sqlite&style=for-the-badge">
<img src="https://img.shields.io/badge/CustomTkinter-GUI-purple?style=for-the-badge">

<br><br>

<b>Secure desktop application for digital signing, verification, encryption, decryption, certificate management and audit logging.</b>

</div>

---

## About CryptoSign

CryptoSign is a desktop-based cryptography application developed in Python. It provides secure digital document signing, signature verification, certificate management, hybrid file encryption, file decryption, certificate revocation and audit logging through a graphical user interface.

The system uses RSA-2048, RSA-PSS, SHA-256, AES-256-GCM, X.509 certificates and Public Key Infrastructure to provide authentication, integrity, confidentiality, non-repudiation and accountability.

---

## Core Features

| Feature | Description | Technology |
|---|---|---|
| Digital Document Signing | Signs documents using the user's private key | RSA-PSS |
| Signature Verification | Verifies signed documents using public key and certificate | RSA-PSS, X.509 |
| RSA Key Management | Generates public and private key pairs | RSA-2048 |
| Certificate Authority | Issues and validates user certificates | X.509 PKI |
| Certificate Revocation | Blocks revoked users from sensitive operations | Revocation List |
| File Encryption | Encrypts confidential files | AES-256-GCM + RSA |
| File Decryption | Restores encrypted files using private key | RSA + AES |
| File Hashing | Generates file hash for integrity checking | SHA-256 |
| Batch Signing | Signs multiple documents | RSA-PSS |
| Audit Logging | Records user actions and security events | SQLite |
| User Management | Supports admin approval and user access control | SQLite |

---

## Technology Stack

| Category | Technology |
|---|---|
| Programming Language | Python 3.13+ |
| GUI Framework | CustomTkinter, Tkinter |
| Database | SQLite |
| Cryptographic Library | cryptography |
| PDF Support | pyHanko, pypdf |
| Hashing | hashlib |
| Data Format | JSON |
| Key and Certificate Format | PEM |
| Testing Framework | unittest |
| Version Control | Git and GitHub |

---

## Cryptographic Algorithms and Standards

| Algorithm / Standard | Purpose |
|---|---|
| RSA-2048 | Public and private key generation |
| RSA-PSS | Digital signature generation and verification |
| SHA-256 | File hashing and integrity verification |
| AES-256-GCM | Secure file encryption and decryption |
| X.509 Certificate | User identity and public key binding |
| PKI | Trust management between users and certificates |
| Hybrid Encryption | AES encrypts files, RSA protects AES key |

---

## System Architecture

```text
CryptoSign
│
├── Authentication Layer
│   ├── User Registration
│   ├── User Login
│   ├── Admin Approval
│   └── Access Control
│
├── Cryptographic Layer
│   ├── RSA-2048 Key Generation
│   ├── Root Certificate Authority
│   ├── X.509 Certificate Issuance
│   ├── RSA-PSS Digital Signature
│   ├── SHA-256 Hashing
│   ├── AES-256-GCM Encryption
│   └── RSA-Based AES Key Protection
│
├── Application Layer
│   ├── User Dashboard
│   ├── Admin Dashboard
│   ├── Sign Document
│   ├── Verify Document
│   ├── Encrypt File
│   ├── Decrypt File
│   ├── Batch Sign
│   └── Activity History
│
└── Storage Layer
    ├── User Database
    ├── Audit Database
    ├── Certificates
    ├── Keystores
    ├── Signatures
    ├── Encrypted Files
    └── Revocation Records