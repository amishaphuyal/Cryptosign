<div align="center">

<h1>🔐 CryptoSign</h1>

<h3>Secure Digital Signature & Certificate Management Platform</h3>

<br>

<img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white">

<img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge">

<img src="https://img.shields.io/badge/Cryptography-RSA--2048%20%7C%20AES--256--GCM-red?style=for-the-badge">

<img src="https://img.shields.io/badge/Platform-Windows%20|%20Linux%20|%20macOS-blue?style=for-the-badge">

<br><br>

<b>Enterprise Grade Digital Signature, Certificate Authority & Secure Document Protection System</b>

<br><br>

</div>

<hr>

<h2>📖 About CryptoSign</h2>

<p align="justify">
CryptoSign is a comprehensive Digital Signature and Certificate Management Platform developed using Python. It enables secure document signing, certificate issuance, verification, revocation, encryption, decryption, key management, and audit logging through a modern graphical interface.

The system implements industry-standard cryptographic technologies including RSA-2048, AES-256-GCM, SHA-256, PKCS#7 Digital Signatures, and X.509 Certificates to ensure confidentiality, integrity, authenticity, and non-repudiation.
</p>

<hr>

<h2>✨ Core Features</h2>

<table>
<tr>
<th>Feature</th>
<th>Description</th>
<th>Technology</th>
</tr>

<tr>
<td>📝 PDF Digital Signing</td>
<td>Embedded & PKCS#7 Signatures</td>
<td>PyHanko</td>
</tr>

<tr>
<td>🏛 Certificate Authority</td>
<td>Issue, Verify & Revoke Certificates</td>
<td>X.509</td>
</tr>

<tr>
<td>🔑 Key Management</td>
<td>RSA Public/Private Key Generation</td>
<td>RSA-2048</td>
</tr>

<tr>
<td>🔒 Encryption</td>
<td>Hybrid File Encryption</td>
<td>AES-256-GCM + RSA-OAEP</td>
</tr>

<tr>
<td>🔓 Decryption</td>
<td>Secure File Recovery</td>
<td>RSA + AES</td>
</tr>

<tr>
<td>🔍 Hashing</td>
<td>Document Integrity Verification</td>
<td>SHA-256</td>
</tr>

<tr>
<td>📦 Batch Signing</td>
<td>Multiple Document Processing</td>
<td>RSA-PSS</td>
</tr>

<tr>
<td>👤 User Management</td>
<td>Admin & User Roles</td>
<td>SQLite</td>
</tr>

<tr>
<td>📊 Audit Logging</td>
<td>Security Event Tracking</td>
<td>SQLite</td>
</tr>

</table>

<hr>

<h2>🛠 Technology Stack</h2>

<table>
<tr>
<th>Category</th>
<th>Technology</th>
</tr>

<tr>
<td>Programming Language</td>
<td>Python 3.9+</td>
</tr>

<tr>
<td>GUI Framework</td>
<td>CustomTkinter</td>
</tr>

<tr>
<td>Database</td>
<td>SQLite</td>
</tr>

<tr>
<td>Cryptography</td>
<td>Cryptography Library</td>
</tr>

<tr>
<td>Digital Signature</td>
<td>PyHanko</td>
</tr>

<tr>
<td>Certificate Management</td>
<td>X.509 PKI</td>
</tr>

<tr>
<td>Encryption</td>
<td>RSA-2048 + AES-256-GCM</td>
</tr>

<tr>
<td>Hashing</td>
<td>SHA-256</td>
</tr>

</table>

<hr>

<h2>🏗 System Architecture</h2>

<pre>
CryptoSign
│
├── Authentication Layer
│   ├── Login
│   ├── Registration
│   └── Access Control
│
├── Cryptographic Layer
│   ├── RSA Key Management
│   ├── Certificate Authority
│   ├── PKCS#7 Signing
│   ├── Encryption
│   ├── Decryption
│   └── Hash Verification
│
├── Application Layer
│   ├── User Dashboard
│   ├── Admin Dashboard
│   ├── Batch Signing
│   └── History Viewer
│
└── Storage Layer
    ├── Audit Logs
    ├── Certificates
    ├── Keystores
    ├── Signatures
    └── Encrypted Files
</pre>

<hr>

<h2>📂 Project Structure</h2>

<pre>
CryptoSign/
│
├── core/
├── gui/
├── storage/
│
├── main.py
├── requirements.txt
├── LICENSE
└── README.md
</pre>

<hr>

<h2>🚀 Installation</h2>

<h3>1️⃣ Clone Repository</h3>

<pre>
git clone https://github.com/yourusername/CryptoSign.git
cd CryptoSign
</pre>

<h3>2️⃣ Create Virtual Environment</h3>

<pre>
python -m venv venv
.\venv\Scripts\activate
</pre>

<h3>3️⃣ Install Dependencies</h3>

<pre>
pip install -r requirements.txt
</pre>

<h3>4️⃣ Run Application</h3>

<pre>
python main.py
</pre>

<hr>

<h2>🎯 Application Workflow</h2>

<pre>
User Login
    ↓
Generate RSA Keys
    ↓
Issue Certificate
    ↓
Sign Document
    ↓
Verify Signature
    ↓
Encrypt / Decrypt Files
    ↓
Audit Logging
</pre>

<hr>

<h2>🔒 Security Features</h2>

<ul>
<li>RSA-2048 Key Pair Generation</li>
<li>AES-256-GCM Encryption</li>
<li>PKCS#7 Digital Signatures</li>
<li>X.509 Certificate Authority</li>
<li>Certificate Revocation Management</li>
<li>Role-Based Access Control</li>
<li>SHA-256 Integrity Verification</li>
<li>Comprehensive Audit Logging</li>
</ul>

<hr>

<h2>📸 Screenshots</h2>

<div align="center">

<img src="docs/screenshots/login.png" width="700">

<br><br>

<b>Secure Login Interface</b>

<br><br>

<img src="docs/screenshots/user_dashboard.png" width="700">

<br><br>

<b>User Dashboard</b>

<br><br>

<img src="docs/screenshots/admin_dashboard.png" width="700">

<br><br>

<b>Admin Dashboard</b>

</div>

<hr>

<h2>⚠️ Security Notice</h2>

<pre>
storage/
*.pem
*.key
*.crt
*.db
*.pfx
*.p12
</pre>

<p>
Never upload private keys, certificates, keystores, databases, or encrypted files to public repositories.
</p>

<hr>

<h2>📜 License</h2>

<p>
This project is licensed under the MIT License.
</p>

<hr>

<div align="center">

<h2>👨‍💻 Developer</h2>

<h3>Amisha Phuyal</h3>

Cybersecurity Enthusiast • VAPT Researcher • Python Developer

<br>

⭐ If you found this project useful, consider giving it a star.

</div>