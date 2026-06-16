import os
import hashlib
import json
import base64
from datetime import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed


def sign_document(file_path, private_key_path, username, password=None, audit_logger=None):
    """
    FIXED: Create external .sig file with digital signature + metadata
    Also tracks file in database for My Documents
    """
    with open(file_path, 'rb') as f:
        file_data = f.read()

    file_hash = hashlib.sha256(file_data).digest()

    with open(private_key_path, 'rb') as f:
        private_key = serialization.load_pem_private_key(f.read(), password=password)

    signature = private_key.sign(
        file_hash,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        Prehashed(hashes.SHA256())
    )

    cert_path = f"storage/certs/{username}_cert.pem"
    cert_data = ""
    if os.path.exists(cert_path):
        with open(cert_path, 'rb') as f:
            cert_data = base64.b64encode(f.read()).decode('utf-8')

    signature_b64 = base64.b64encode(signature).decode('utf-8')
    hash_b64 = base64.b64encode(file_hash).decode('utf-8')

    sig_data = {
        'signature': base64.b64encode(signature).decode('utf-8'),
        'file_hash': base64.b64encode(file_hash).decode('utf-8'),
        'algorithm': 'SHA256_RSA_PSS',
        'original_filename': os.path.basename(file_path),
        'original_size': len(file_data),
        'signer': username,
        'certificate': cert_data,
        'timestamp': datetime.now().isoformat(),
        'signing_tool': 'CryptoSign v1.0'
    }

    user_sig_dir = f"storage/signatures/{username}"
    os.makedirs(user_sig_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(file_path))[0]
    sig_filename = f"{base_name}.sig"
    sig_path = os.path.join(user_sig_dir, sig_filename)

    with open(sig_path, 'w') as f:
        json.dump(sig_data, f, indent=2)

    orig_sig_path = os.path.splitext(file_path)[0] + ".sig"
    with open(orig_sig_path, 'w') as f:
        json.dump(sig_data, f, indent=2)

    if audit_logger:
        audit_logger.add_user_file(
            username=username,
            file_type='signed',
            file_path=sig_path,
            original_name=os.path.basename(file_path),
            file_size=len(file_data)
        )

    print(f"External signature created: {sig_path}")
    return sig_path