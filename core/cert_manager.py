from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
import datetime
import os


def issue_certificate(ca_private_key, public_key, username):
    os.makedirs("storage/certs", exist_ok=True)

    ca_cert_path = "storage/ca/ca_cert.pem"

    if not os.path.exists(ca_cert_path):
        raise FileNotFoundError("CA certificate not found")

    with open(ca_cert_path, "rb") as f:
        ca_cert = x509.load_pem_x509_certificate(f.read())

    subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, username),
    ])

    valid_from = datetime.datetime.utcnow()
    valid_to = valid_from + datetime.timedelta(days=365)

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(public_key)
        .serial_number(x509.random_serial_number())
        .not_valid_before(valid_from)
        .not_valid_after(valid_to)

        .add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True
        )

        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=True,   # nonRepudiation
                key_encipherment=True,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False
            ),
            critical=True
        )

        .add_extension(
            x509.ExtendedKeyUsage([
                ExtendedKeyUsageOID.CODE_SIGNING,
                ExtendedKeyUsageOID.EMAIL_PROTECTION
            ]),
            critical=False
        )

        .sign(private_key=ca_private_key, algorithm=hashes.SHA256())
    )

    cert_path = f"storage/certs/{username}_cert.pem"

    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print(f"X.509 Certificate issued for {username}")
    return cert_path