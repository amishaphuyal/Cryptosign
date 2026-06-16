from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import padding
import datetime

def verify_certificate(cert_path, ca_public_key):
    try:
        with open(cert_path, "rb") as f:
            cert = x509.load_pem_x509_certificate(f.read())

        now = datetime.datetime.now(datetime.timezone.utc)

        if now < cert.not_valid_before_utc or now > cert.not_valid_after_utc:
            print("Certificate expired!")
            return False

        ca_public_key.verify(
            cert.signature,
            cert.tbs_certificate_bytes,
            padding.PKCS1v15(),
            cert.signature_hash_algorithm
        )

        print("Certificate verified by CA")
        print(f"Valid till: {cert.not_valid_after_utc}")

        return True

    except Exception as e:
        print(f"Certificate validation failed: {str(e)}")
        return False