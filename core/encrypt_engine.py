from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
import os


def encrypt_file(file_path, public_key_path, username):
    """
    FIXED: User-specific encrypted file storage
    Saves to: storage/encrypted/{username}/original_name.bin
    """
    user_enc_dir = f"storage/encrypted/{username}"
    os.makedirs(user_enc_dir, exist_ok=True)

    print("\n Hybrid Encryption Started...")
    print("   • AES-256-GCM (file encryption)")
    print("   • RSA-2048 (key protection)")

    with open(file_path, "rb") as f:
        data = f.read()

    aes_key = AESGCM.generate_key(bit_length=256)
    aes = AESGCM(aes_key)

    nonce = os.urandom(12)
    ciphertext = aes.encrypt(nonce, data, None)

    original_name = os.path.basename(file_path)
    safe_name = original_name.replace(" ", "_")

    enc_filename = f"{safe_name}.bin"
    enc_file_path = os.path.join(user_enc_dir, enc_filename)

    with open(enc_file_path, "wb") as f:
        f.write(ciphertext)

    nonce_path = os.path.join(user_enc_dir, f"{safe_name}.nonce")
    with open(nonce_path, "wb") as f:
        f.write(nonce)

    key_path = os.path.join(user_enc_dir, f"{safe_name}.key")

    print("USING PUBLIC KEY:", public_key_path)

    if not os.path.exists(public_key_path):
        raise FileNotFoundError(f"Public key not found: {public_key_path}")

    with open(public_key_path, "rb") as f:
        rsa_public_key = serialization.load_pem_public_key(f.read())

    encrypted_key = rsa_public_key.encrypt(
        aes_key,
        padding.PKCS1v15()
    )

    with open(key_path, "wb") as f:
        f.write(encrypted_key)

    print("\n Encryption Successful")
    print(f"   ✔ File encrypted: {enc_file_path}")
    print(f"   ✔ Key secured: {key_path}")
    print(f"   ✔ Nonce saved: {nonce_path}")

    return enc_file_path