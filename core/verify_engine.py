import os
import base64

from pyhanko.pdf_utils.reader import PdfFileReader
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

from core.revocation import is_revoked
from core.ca_engine import load_ca_public_key
from core.cert_verifier import verify_certificate


def verify_document(file_path, public_key_path, username):
    """
    Verify document - handles both signed and decrypted files.
    """
    print("\n🔍 ===== Verification Process Started =====")

    if is_revoked(username):
        return "INVALID"

    cert_path = f"storage/certs/{username}_cert.pem"

    if not os.path.exists(cert_path):
        return "ERROR"

    ca_public_key = load_ca_public_key()

    if not verify_certificate(cert_path, ca_public_key):
        return "INVALID"

    if not os.path.exists(file_path):
        return "ERROR"

    file_name = os.path.basename(file_path)
    
    if not file_name.endswith("_signed.pdf") and not file_name.endswith(".sig"):
        signed_version = file_path.replace(".pdf", "_signed.pdf")
        if os.path.exists(signed_version):
            print(f"Original file found, checking signed version: {signed_version}")
            file_path = signed_version  
        else:
            print("This is original unsigned file")
            return "NOT_SIGNED"

    try:
        with open(file_path, "rb") as f:
            reader = PdfFileReader(f)

            if reader.embedded_signatures:
                print("PKCS Signature Found")
                return "VALID"

    except Exception as e:
        print("PKCS check failed:", e)

    if file_name.endswith("_signed.pdf"):
        original_name = file_name.replace("_signed.pdf", ".pdf")
        signature_path = f"storage/signatures/{username}_{original_name}.sig"
        
        dir_path = os.path.dirname(file_path)
        alt_sig_path = os.path.join(dir_path, original_name + ".sig")
    else:
        signature_path = f"storage/signatures/{username}_{file_name}.sig"
        alt_sig_path = file_path + ".sig"

    sig_paths = [
        signature_path,
        alt_sig_path,
        file_path + ".sig",  
    ]

    sig_found = False
    for sig_path in sig_paths:
        if os.path.exists(sig_path):
            sig_found = True
            print(f"External signature found: {sig_path}")
            
            try:
                with open(file_path.replace("_signed.pdf", ".pdf") if "_signed.pdf" in file_path else file_path, "rb") as f:
                    data = f.read()

                import json
                with open(sig_path, "r") as f:
                    sig_data = json.load(f)
                    signature = base64.b64decode(sig_data['signature'])

                with open(public_key_path, "rb") as f:
                    public_key = serialization.load_pem_public_key(f.read())

                public_key.verify(
                    signature,
                    data,
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )

                print("VALID (External Signature)")
                return "VALID"

            except Exception as e:
                print(f"External verify failed: {e}")
                continue

    if not sig_found:
        print("No signature found")
        return "NOT_SIGNED"

    return "INVALID"