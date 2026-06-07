from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
import datetime
import os

from core.ca_engine import load_ca_private_key


def issue_certificate(ca_private_key, public_key, username):

    os.makedirs("storage/certs", exist_ok=True)

    # ✅ SUBJECT (USER)
    subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, username),
    ])

    # ✅ ✅ FIX: ISSUER MUST BE CA ✅
    issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "CryptoSign Root CA"),
    ])

    valid_from = datetime.datetime.utcnow()
    valid_to = valid_from + datetime.timedelta(days=365)

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)   # ✅ IMPORTANT FIX
        .public_key(public_key)
        .serial_number(x509.random_serial_number())
        .not_valid_before(valid_from)
        .not_valid_after(valid_to)
        .add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True
        )
        .sign(private_key=ca_private_key, algorithm=hashes.SHA256())
    )

    cert_path = f"storage/certs/{username}_cert.pem"

    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print(f"✅ X.509 Certificate issued for {username}")