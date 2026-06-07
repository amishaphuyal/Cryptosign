# CryptoSign

CryptoSign is a tool for digital signing and certificate management. It provides PDF signing, encryption/decryption, key and certificate (CA) management, and both GUI and CLI helpers for common signing workflows.

Features
- PDF digital signing (PKCS) and smart card support
- Key and certificate management, CA issuance and revocation
- Encryption, decryption and hashing utilities
- GUI and lightweight CLI entry points

Quick start (Windows)
1. Create and activate a virtual environment:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirement.txt
```

3. Run the application (GUI):

```powershell
python main.py
```

Project layout (short)
- `core/` — core functionality: signing, verification, key manager, CA engine, etc.
- `gui/` — GUI modules
- `storage/` — persisted artifacts: certs, keystores, backups, signatures

Security notes
- Never commit private keys, keystores, or passwords to source control.
- Keep `storage/keystores`, `storage/certs` and backups offline when possible.

License
This project is available under the MIT License — see the `LICENSE` file.

Questions or changes?
If you want a more detailed English README (examples, CLI usage, or developer notes), tell me what to add and I will update it.