from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime
import os


def create_root_ca():

    print("\n Creating Root Certificate Authority (CA)...")
    print("Algorithm: RSA-2048")

    os.makedirs("storage/ca", exist_ok=True)

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    public_key = private_key.public_key()

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"NP"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"CryptoSign CA"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"CryptoSign Root CA"),
    ])

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(public_key)
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=3650)
        )
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        )
        .sign(private_key, hashes.SHA256())
    )

    with open("storage/ca/ca_private.pem", "wb") as f:
        f.write(
            private_key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption()
            )
        )

    with open("storage/ca/ca_cert.pem", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print("CA Private Key created")
    print("CA Certificate created ")

def load_ca_private_key():
    with open("storage/ca/ca_private.pem", "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def load_ca_public_key():
    from cryptography import x509

    with open("storage/ca/ca_cert.pem", "rb") as f:
        cert = x509.load_pem_x509_certificate(f.read())

    return cert.public_key()