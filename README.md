# CryptoSign

**CryptoSign** is a secure and user-friendly digital signature and certificate management application. It allows users to digitally sign PDF documents, manage cryptographic keys and certificates, and perform encryption/decryption operations with both graphical and command-line interfaces.

## Features

- **PDF Digital Signing** — Support for PKCS#7 and smart card signing
- **Certificate Authority (CA)** — Create, issue, verify, and revoke digital certificates
- **Key Management** — Generate, import, and manage private keys and certificates
- **Encryption & Decryption** — Secure file encryption and decryption
- **Hashing Utilities** — Multiple hashing algorithms support
- **User Interfaces** — Modern GUI and efficient CLI tools
- **Batch Signing** — Sign multiple documents at once

## Quick Start (Windows)

1. **Create and activate virtual environment:**

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1

Install required packages:PowerShellpip install -r requirement.txt
Run the application:PowerShellpython main.py

## Project Structure
CryptoSign/
│
├── 📂 core/                          # Core cryptographic engines
│   ├── init.py
│   ├── audit_logger.py              # SQLite audit logging
│   ├── auth_system.py               # User authentication (SHA-256)
│   ├── auto_convert.py              # Office to PDF conversion
│   ├── batch_sign.py                # Batch document signing
│   ├── ca_engine.py                 # Certificate Authority
│   ├── cert_manager.py              # X.509 certificate issuance
│   ├── cert_verifier.py             # Certificate validation
│   ├── decrypt_engine.py            # Hybrid decryption (RSA+AES)
│   ├── embed_pdf.py                 # PDF embedded signatures
│   ├── encrypt_engine.py            # Hybrid encryption (RSA+AES)
│   ├── hash_engine.py               # SHA-256 file hashing
│   ├── history_viewer.py            # Audit history dialog
│   ├── key_manager.py               # RSA key pair generation
│   ├── pkcs_sign.py                 # PKCS#7 PDF signing
│   ├── revocation.py                # Certificate revocation
│   ├── sign_engine.py               # External .sig signing
│   ├── smart_sign.py                # Auto mode signing
│   └── verify_engine.py             # Signature verification
│
├── 📂 gui/                           # User interface
│   ├── init.py
│   ├── admin_dashboard.py           # Admin panel (full featured)
│   ├── login_dialog.py              # Login/Register UI
│   ├── main_app.py                  # Main application window
│   └── user_dashboard.py            # User dashboard
│
├── 📂 storage/                       # Data storage (auto-created)
│   ├── audit.db                     # Audit logs database
│   ├── auth.db                      # User auth database
│   ├── backups/                     # Database backups
│   ├── ca/                          # CA certificates
│   │   ├── ca_cert.pem
│   │   └── ca_private.pem
│   ├── certs/                       # User certificates
│   │   └── {username}_cert.pem
│   ├── encrypted/                   # Encrypted files
│   │   └── {username}/
│   ├── keystores/                   # Private keys
│   │   ├── {username}_private.pem
│   │   └── {username}_public.pem
│   └── signatures/                  # Signed documents
│       └── {username}/
│
├── 📄 .gitignore                     # Git ignore rules
├── 📄 LICENSE                        # MIT License
├── 📄 main.py                        # Application entry point
├── 📄 main_app.py                    # CryptoSignApp class
├── 📄 README.md                      # This file
└── 📄 requirement.txt                # Python dependencies

Security Recommendations

Never commit private keys, keystores, or sensitive credentials to Git.
Keep storage/keystores/ and storage/certs/ directories secure and preferably offline.
Use strong passwords for all keystores and private keys.

License
This project is licensed under the MIT License. See the LICENSE file for more details.