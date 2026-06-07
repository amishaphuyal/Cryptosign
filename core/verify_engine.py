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

    # ✅ STEP 1: REVOCATION
    if is_revoked(username):
        return "INVALID"

    # ✅ STEP 2: CERT CHECK
    cert_path = f"storage/certs/{username}_cert.pem"

    if not os.path.exists(cert_path):
        return "ERROR"

    ca_public_key = load_ca_public_key()

    if not verify_certificate(cert_path, ca_public_key):
        return "INVALID"

    # ✅ STEP 3: FILE CHECK
    if not os.path.exists(file_path):
        return "ERROR"

    # =====================================================
    # ✅ CHECK IF FILE IS DECRYPTED ORIGINAL (not signed)
    # =====================================================
    file_name = os.path.basename(file_path)
    
    # If file is decrypted original (not _signed.pdf), check if signed version exists
    if not file_name.endswith("_signed.pdf") and not file_name.endswith(".sig"):
        # Check if signed version exists in same location
        signed_version = file_path.replace(".pdf", "_signed.pdf")
        if os.path.exists(signed_version):
            print(f"📄 Original file found, checking signed version: {signed_version}")
            file_path = signed_version  # Verify the signed version instead
        else:
            print("⚠️ This is original unsigned file")
            return "NOT_SIGNED"

    # =====================================================
    # ✅ ✅ EMBEDDED (PKCS) VERIFY ✅
    # =====================================================
    try:
        with open(file_path, "rb") as f:
            reader = PdfFileReader(f)

            if reader.embedded_signatures:
                print("✅ PKCS Signature Found ✅")
                return "VALID"

    except Exception as e:
        print("⚠️ PKCS check failed:", e)

    # =====================================================
    # ✅ ✅ EXTERNAL VERIFY (RSA FIX 🔥)
    # =====================================================
    
    # For signed PDFs, check external .sig file
    if file_name.endswith("_signed.pdf"):
        # Get original file name
        original_name = file_name.replace("_signed.pdf", ".pdf")
        signature_path = f"storage/signatures/{username}_{original_name}.sig"
        
        # Also check in same directory
        dir_path = os.path.dirname(file_path)
        alt_sig_path = os.path.join(dir_path, original_name + ".sig")
    else:
        signature_path = f"storage/signatures/{username}_{file_name}.sig"
        alt_sig_path = file_path + ".sig"

    # Try multiple signature locations
    sig_paths = [
        signature_path,
        alt_sig_path,
        file_path + ".sig",  # Direct .sig file
    ]

    sig_found = False
    for sig_path in sig_paths:
        if os.path.exists(sig_path):
            sig_found = True
            print(f"✅ External signature found: {sig_path}")
            
            try:
                # ✅ load data
                with open(file_path.replace("_signed.pdf", ".pdf") if "_signed.pdf" in file_path else file_path, "rb") as f:
                    data = f.read()

                # ✅ load signature
                import json
                with open(sig_path, "r") as f:
                    sig_data = json.load(f)
                    signature = base64.b64decode(sig_data['signature'])

                # ✅ load public key
                with open(public_key_path, "rb") as f:
                    public_key = serialization.load_pem_public_key(f.read())

                # ✅ ✅ VERIFY RSA SIGNATURE
                public_key.verify(
                    signature,
                    data,
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )

                print("✅ VALID (External Signature)")
                return "VALID"

            except Exception as e:
                print(f"⚠️ External verify failed: {e}")
                continue

    if not sig_found:
        print("❌ No signature found")
        return "NOT_SIGNED"

    return "INVALID"