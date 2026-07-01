<div align="center">

<svg width="100" height="100" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="120" height="120" rx="28" fill="#0F172A"/>
  <rect x="30" y="49" width="60" height="44" rx="10" fill="#6366F1"/>
  <path d="M40 49V39C40 27.9543 48.9543 19 60 19C71.0457 19 80 27.9543 80 39V49" stroke="#A5B4FC" stroke-width="8" stroke-linecap="round"/>
  <circle cx="60" cy="69" r="6" fill="white"/>
  <path d="M60 75V84" stroke="white" stroke-width="5" stroke-linecap="round"/>
</svg>

<br>

# CryptoSign

<b>Secure Digital Signature, Certificate Authority & Document Protection Platform</b>

<br><br>

<img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/GUI-CustomTkinter-6366F1?style=for-the-badge" alt="CustomTkinter">
<img src="https://img.shields.io/badge/RSA-2048-EF4444?style=for-the-badge" alt="RSA">
<img src="https://img.shields.io/badge/AES-256--GCM-10B981?style=for-the-badge" alt="AES">
<img src="https://img.shields.io/badge/Certificate-X.509-F59E0B?style=for-the-badge" alt="X.509">

<br><br>

<a href="#installation">Installation</a> •
<a href="#features">Features</a> •
<a href="#how-it-works">How It Works</a> •
<a href="#usage">Usage</a> •
<a href="#author">Author</a>

</div>

<br>

---

<br>

<div align="center">
<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg>
<h2>Overview</h2>
</div>

CryptoSign is a Python desktop app for signing, verifying, encrypting and managing documents securely. It lets users generate RSA key pairs, issue X.509 certificates, sign and verify files, encrypt/decrypt data, and keep a full audit log — all through a simple, clean GUI.

<br>

---

<br>

<div align="center">
<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2"><path d="M12 2l1.5 4.5H18l-3.5 3 1.5 4.5-4-3-4 3 1.5-4.5L6 6.5h4.5z"/></svg>
<h2 id="features">Features</h2>
</div>

<table width="100%">
<tr>
<td width="33%" align="center" valign="top">
<br>
<svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2"><rect x="3" y="11" width="18" height="10" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
<br><br>

**Key & Certificate Management**

RSA-2048 keys, password protection, X.509 certificates via a built-in CA

<br>
</td>
<td width="33%" align="center" valign="top">
<br>
<svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2"><path d="M12 2l8 4v6c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V6l8-4z"/><path d="M9 12l2 2 4-4"/></svg>
<br><br>

**Signing & Verification**

Sign PDFs and files, verify signatures, and validate certificates before trust

<br>
</td>
<td width="33%" align="center" valign="top">
<br>
<svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2"><rect x="3" y="11" width="18" height="10" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0"/><circle cx="12" cy="16" r="1.5"/></svg>
<br><br>

**Encryption & Decryption**

AES-256-GCM file encryption with RSA-protected keys

<br>
</td>
</tr>
<tr>
<td width="33%" align="center" valign="top">
<br>
<svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2"><path d="M9 12l2 2 4-4"/><path d="M21 12c0 5-3.5 9-9 10-5.5-1-9-5-9-10V6l9-4 9 4z"/></svg>
<br><br>

**Audit Logging**

Full SQLite activity history with CSV export support

<br>
</td>
<td width="33%" align="center" valign="top">
<br>
<svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#8B5CF6" stroke-width="2"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18"/><circle cx="7" cy="6.5" r="0.5" fill="#8B5CF6"/><circle cx="10" cy="6.5" r="0.5" fill="#8B5CF6"/></svg>
<br><br>

**Admin Dashboard**

Manage users, monitor activity, revoke access and certificates

<br>
</td>
<td width="33%" align="center" valign="top">
<br>
<svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#06B6D4" stroke-width="2"><path d="M4 4h6v6H4z"/><path d="M14 4h6v6h-6z"/><path d="M4 14h6v6H4z"/><path d="M14 14h6v6h-6z"/></svg>
<br><br>

**Batch Signing**

Sign multiple documents from a folder in one operation

<br>
</td>
</tr>
</table>

<br>

---

<br>

<div align="center">
<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2"><path d="M4 17V5a2 2 0 0 1 2-2h9l5 5v9a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2z"/><path d="M8 21v-6h8v6"/></svg>
<h2>Technology Stack</h2>
</div>

<div align="center">

| Category | Technology |
|:---|:---|
| Language | Python |
| GUI | CustomTkinter |
| Cryptography | `cryptography`, PyHanko |
| PDF Handling | pypdf |
| Database | SQLite |
| Images | Pillow |

</div>

<br>

---

<br>

<div align="center">
<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2"><path d="M13 2L3 14h7l-1 8 10-12h-7l1-8z"/></svg>
<h2 id="how-it-works">How It Works</h2>
</div>

**Digital Signature Flow**
```text
Document → SHA-256 Hash → Signed with RSA Private Key → Verified with Public Key + Certificate
```

**Encryption Flow**
```text
File → AES-256 Encrypted → AES Key Locked with RSA Public Key → Decrypted with RSA Private Key
```

<br>

---

<br>

<div align="center">
<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#8B5CF6" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
<h2>Project Structure</h2>
</div>

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

<br>

---

<br>

<div align="center">
<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2"><path d="M21 15V6a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v13"/><path d="M2 8h10v13H4a2 2 0 0 1-2-2z"/></svg>
<h2 id="installation">Installation</h2>
</div>

<img src="https://img.shields.io/badge/Step%201-Clone%20the%20Repository-6366F1?style=flat-square" alt="Step 1"><br>
```bash
git clone https://github.com/amishaphuyal/Cryptosign.git
cd Cryptosign
```
<br>

<img src="https://img.shields.io/badge/Step%202-Create%20Virtual%20Environment-6366F1?style=flat-square" alt="Step 2"><br>
```bash
python -m venv venv
```
<br>

<img src="https://img.shields.io/badge/Step%203-Activate%20Virtual%20Environment-6366F1?style=flat-square" alt="Step 3"><br>
Windows:
```bash
venv\Scripts\activate
```
Linux / macOS:
```bash
source venv/bin/activate
```
<br>

<img src="https://img.shields.io/badge/Step%204-Install%20Dependencies-6366F1?style=flat-square" alt="Step 4"><br>
```bash
pip install -r requirements.txt
```
<br>

<img src="https://img.shields.io/badge/Step%205-Run%20the%20App-10B981?style=flat-square" alt="Step 5"><br>
```bash
python main.py
```

<br>

---

<br>

<div align="center">
<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8"/></svg>
<h2 id="usage">Usage</h2>
</div>

<table width="100%">
<tr>
<td width="50%" valign="top">

**As a User**
1. Register or login
2. Generate your RSA key pair
3. Get an X.509 certificate
4. Sign or verify documents
5. Encrypt / decrypt files
6. View your activity history

</td>
<td width="50%" valign="top">

**As an Admin**
1. Login as administrator
2. View users & statistics
3. Approve or block accounts
4. View audit logs
5. Issue or revoke certificates
6. Monitor security activity

</td>
</tr>
</table>

<br>

---

<br>

<div align="center">
<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2"><rect x="3" y="11" width="18" height="10" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/><circle cx="12" cy="16" r="1.5"/></svg>
<h2>Security Highlights</h2>
</div>

<div align="center">

| Area | Method |
|:---|:---|
| Integrity | SHA-256 hashing |
| Non-repudiation | RSA digital signatures |
| Confidentiality | AES-256-GCM encryption |
| Trust | X.509 certificates + CA verification |
| Accountability | SQLite audit logs |

</div>

<br>

---

<br>

<div align="center" id="author">

<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8"/></svg>

### Author

**Amisha Phuyal**
<br>
BSc (Hons) Ethical Hacking and Cybersecurity
<br>
Softwarica College of IT and E-Commerce, Coventry University

<br><br>

<img src="https://img.shields.io/badge/Cybersecurity-Student-6366F1?style=for-the-badge" alt="Cybersecurity Student">
<img src="https://img.shields.io/badge/Project-CryptoSign-10B981?style=for-the-badge" alt="CryptoSign">

</div>

<br>

---

<br>

<div align="center">

### CryptoSign — Secure. Trusted. Verifiable.

</div>
