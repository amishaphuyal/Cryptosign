import os
import base64
import json

from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign.validation import validate_pdf_signature
from pyhanko_certvalidator import ValidationContext
from pyhanko.keys import load_cert_from_pemder

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed

from core.revocation import is_revoked
from core.ca_engine import load_ca_public_key
from core.cert_verifier import verify_certificate


def verify_embedded_pdf_signature(pdf_path):
    try:
        print("Checking embedded PDF signature...")

        if not os.path.exists("storage/ca/ca_cert.pem"):
            print("CA certificate not found")
            return False

        ca_cert = load_cert_from_pemder("storage/ca/ca_cert.pem")

        validation_context = ValidationContext(
            trust_roots=[ca_cert],
            allow_fetching=False
        )

        with open(pdf_path, "rb") as f:
            reader = PdfFileReader(f)

            if not reader.embedded_signatures:
                print("No embedded signature found")
                return False

            embedded_sig = reader.embedded_signatures[0]

            status = validate_pdf_signature(
                embedded_sig,
                signer_validation_context=validation_context
            )

            print(status.pretty_print_details())

            if status.bottom_line:
                return True

            return False

    except Exception as e:
        print(f"Embedded PDF verification failed: {e}")
        return False


def find_external_signature(file_path, username=None):
    file_name = os.path.basename(file_path)
    sig_paths = []

    if file_name.endswith(".sig"):
        sig_paths.append(file_path)
        original_file_path = file_path.replace(".sig", "")

    elif file_name.endswith("_signed.pdf"):
        original_file_path = file_path.replace("_signed.pdf", ".pdf")

        sig_paths.append(file_path + ".sig")
        sig_paths.append(os.path.splitext(file_path)[0] + ".sig")
        sig_paths.append(original_file_path.replace(".pdf", ".sig"))

        if username:
            original_name = os.path.basename(original_file_path)
            sig_paths.append(
                os.path.join(
                    "storage",
                    "signatures",
                    username,
                    original_name.replace(".pdf", ".sig")
                )
            )

    else:
        original_file_path = file_path

        sig_paths.append(file_path + ".sig")
        sig_paths.append(os.path.splitext(file_path)[0] + ".sig")

        if username:
            sig_paths.append(
                os.path.join(
                    "storage",
                    "signatures",
                    username,
                    os.path.splitext(file_name)[0] + ".sig"
                )
            )

    return original_file_path, sig_paths


def verify_external_signature(file_path, username=None):
    original_file_path, sig_paths = find_external_signature(file_path, username)

    sig_found = False

    for sig_path in sig_paths:
        if os.path.exists(sig_path):
            sig_found = True
            print(f"External signature found: {sig_path}")

            try:
                with open(sig_path, "r") as f:
                    sig_data = json.load(f)

                signer = sig_data.get("signer")

                if not signer:
                    print("Signer not found inside .sig file")
                    return "INVALID"

                print(f"Detected signer: {signer}")

                if is_revoked(signer):
                    print("Signer certificate is revoked")
                    return "INVALID"

                cert_path = f"storage/certs/{signer}_cert.pem"

                if not os.path.exists(cert_path):
                    print("Signer certificate not found")
                    return "ERROR"

                ca_public_key = load_ca_public_key()

                if not verify_certificate(cert_path, ca_public_key):
                    print("Signer certificate validation failed")
                    return "INVALID"

                signer_public_key_path = f"storage/keystores/{signer}_public.pem"

                if not os.path.exists(signer_public_key_path):
                    print("Signer public key not found")
                    return "ERROR"

                if not os.path.exists(original_file_path):
                    original_name = sig_data.get("original_filename")
                    if original_name:
                        alt_path = os.path.join(
                            os.path.dirname(sig_path),
                            original_name
                        )
                        if os.path.exists(alt_path):
                            original_file_path = alt_path

                if not os.path.exists(original_file_path):
                    print("Original document not found")
                    return "ERROR"

                with open(original_file_path, "rb") as f:
                    data = f.read()

                signature = base64.b64decode(sig_data["signature"])

                digest = hashes.Hash(hashes.SHA256())
                digest.update(data)
                file_hash = digest.finalize()

                with open(signer_public_key_path, "rb") as f:
                    public_key = serialization.load_pem_public_key(f.read())

                public_key.verify(
                    signature,
                    file_hash,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    Prehashed(hashes.SHA256())
                )

                print("VALID (External Signature)")
                return "VALID"

            except Exception as e:
                print(f"External verify failed: {e}")
                continue

    if not sig_found:
        return "NOT_SIGNED"

    return "INVALID"


def verify_document(file_path, public_key_path=None, username=None):
    print("\n🔍 ===== Verification Process Started =====")

    if not os.path.exists(file_path):
        print("File not found")
        return "ERROR"

    file_name = os.path.basename(file_path)

    if not file_name.endswith("_signed.pdf") and not file_name.endswith(".sig"):
        signed_version = file_path.replace(".pdf", "_signed.pdf")

        if os.path.exists(signed_version):
            print(f"Original file selected, checking signed version: {signed_version}")
            file_path = signed_version
            file_name = os.path.basename(file_path)

    # Embedded PDF verification
    if file_name.endswith(".pdf"):
        embedded_result = verify_embedded_pdf_signature(file_path)

        if embedded_result:
            print("VALID (Embedded PDF Signature)")
            return "VALID"

        print("INVALID Embedded PDF Signature")
        return "INVALID"

    # External .sig verification
    external_result = verify_external_signature(file_path, username)

    if external_result == "VALID":
        return "VALID"

    if external_result == "INVALID":
        return "INVALID"

    print("No valid signature found")
    return "NOT_SIGNED"