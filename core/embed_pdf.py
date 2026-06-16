from pypdf import PdfReader, PdfWriter
import os
import hashlib
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
import base64
from datetime import datetime


def embed_pdf_signature(pdf_path, username, password=None, audit_logger=None):
   
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    private_key_path = f"storage/keystores/{username}_private.pem"
    cert_path = f"storage/certs/{username}_cert.pem"

    if not os.path.exists(private_key_path):
        raise FileNotFoundError(f"Private key not found for user: {username}")
    if not os.path.exists(cert_path):
        raise FileNotFoundError(f"Certificate not found for user: {username}")

    try:
        from core.pkcs_sign import sign_pdf_pkcs
        output_path = sign_pdf_pkcs_wrapper(pdf_path, username, password)
        if output_path and os.path.exists(output_path):
            print(f"PKCS#7 signature created: {output_path}")
    
            if audit_logger:
                audit_logger.add_user_file(
                    username=username,
                    file_type='signed',
                    file_path=output_path,
                    original_name=os.path.basename(pdf_path),
                    file_size=os.path.getsize(output_path)
                )
            return output_path
    except Exception as e:
        print(f"PKCS#7 failed: {e}")
        print("Falling back to metadata-only signature...")

    return create_metadata_signature(pdf_path, username, password, audit_logger)


def sign_pdf_pkcs_wrapper(input_pdf, username, password=None):
  
    from core.pkcs_sign import sign_pdf_pkcs

    sign_pdf_pkcs(input_pdf, username, password)

    return input_pdf.replace(".pdf", "_signed.pdf")


def create_metadata_signature(pdf_path, username, password=None, audit_logger=None):
    
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()

    pdf_hash = hashlib.sha256(pdf_bytes).digest()

    # Sign with private key
    private_key_path = f"storage/keystores/{username}_private.pem"
    with open(private_key_path, 'rb') as f:
        private_key = serialization.load_pem_private_key(f.read(), password=password)

    signature = private_key.sign(
        pdf_hash,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        Prehashed(hashes.SHA256())
    )

    cert_path = f"storage/certs/{username}_cert.pem"
    with open(cert_path, 'rb') as f:
        cert_data = f.read()

    signature_b64 = base64.b64encode(signature).decode('utf-8')
    hash_b64 = base64.b64encode(pdf_hash).decode('utf-8')
    cert_b64 = base64.b64encode(cert_data).decode('utf-8')

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.add_metadata({
        "/CryptoSign-Signed-By": username,
        "/CryptoSign-Signature": signature_b64,
        "/CryptoSign-Hash": hash_b64,
        "/CryptoSign-Certificate": cert_b64,
        "/CryptoSign-Algorithm": "SHA256-RSA-PSS",
        "/CryptoSign-Timestamp": datetime.now().isoformat(),
        "/CryptoSign-Original-File": os.path.basename(pdf_path),
        "/CryptoSign-Status": "DIGITALLY SIGNED",
    })

    user_signed_dir = f"storage/signatures/{username}/embedded"
    os.makedirs(user_signed_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_path = os.path.join(user_signed_dir, f"{base_name}_signed.pdf")

    with open(output_path, "wb") as f:
        writer.write(f)

    if audit_logger:
        audit_logger.add_user_file(
            username=username,
            file_type='signed',
            file_path=output_path,
            original_name=os.path.basename(pdf_path),
            file_size=os.path.getsize(output_path)
        )

    print(f"Metadata signature created: {output_path}")
    print(f"No visual stamp (install pyhanko for full PKCS#7 signature)")
    return output_path