from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
import os


def decrypt_file(username, encrypted_file_path, password=None):
    """
    ✅ FIXED: Decrypt file using hybrid decryption with user-specific paths.
    Supports both old global format and new user-specific format.
    """
    print("\n🔓 Hybrid Decryption Started...")

    private_key_path = f"storage/keystores/{username}_private.pem"

    print("✅ USING PRIVATE KEY:", private_key_path)

    if not os.path.exists(private_key_path):
        raise FileNotFoundError("Private key not found")

    # ✅ LOAD PRIVATE KEY (with password if encrypted)
    with open(private_key_path, "rb") as f:
        key_data = f.read()

    # Try without password first (backward compatibility)
    try:
        private_key = serialization.load_pem_private_key(key_data, password=None)
    except Exception:
        # Try with password
        if password:
            private_key = serialization.load_pem_private_key(key_data, password=password.encode('utf-8'))
        else:
            raise ValueError("Private key is password-protected. Please provide password.")

    # ✅ DETERMINE FILE PATHS
    enc_dir = os.path.dirname(encrypted_file_path)
    enc_name = os.path.basename(encrypted_file_path)

    # If user-specific format (ends with .bin in user dir)
    if enc_name.endswith('.bin'):
        base_name = enc_name[:-4]  # Remove .bin
        nonce_path = os.path.join(enc_dir, f"{base_name}.nonce")
        key_path = os.path.join(enc_dir, f"{base_name}.key")
    else:
        # Old global format fallback
        nonce_path = os.path.join(enc_dir, "nonce.bin")
        key_path = os.path.join(enc_dir, "encrypted_key.bin")

    # ✅ LOAD ENCRYPTED AES KEY
    if not os.path.exists(key_path):
        # Try old global path as fallback
        key_path = "storage/encrypted/encrypted_key.bin"
        if not os.path.exists(key_path):
            raise FileNotFoundError(f"Encrypted key not found at {key_path}")

    with open(key_path, "rb") as f:
        encrypted_key = f.read()

    # ✅ RSA DECRYPT
    aes_key = private_key.decrypt(
        encrypted_key,
        padding.PKCS1v15()
    )

    print("✅ AES KEY LENGTH:", len(aes_key))

    if len(aes_key) not in [16, 24, 32]:
        raise ValueError("Invalid AES key size")

    # ✅ USE SELECTED FILE
    if not os.path.exists(encrypted_file_path):
        raise FileNotFoundError(f"Encrypted file not found: {encrypted_file_path}")

    with open(encrypted_file_path, "rb") as f:
        ciphertext = f.read()

    # ✅ LOAD NONCE
    if not os.path.exists(nonce_path):
        # Try old global path
        nonce_path = "storage/encrypted/nonce.bin"
        if not os.path.exists(nonce_path):
            raise FileNotFoundError(f"Nonce file not found at {nonce_path}")

    with open(nonce_path, "rb") as f:
        nonce = f.read()

    # ✅ AES DECRYPT
    aes = AESGCM(aes_key)
    decrypted_data = aes.decrypt(nonce, ciphertext, None)

    # ✅ SAVE WITH ORIGINAL NAME
    if enc_name.endswith('.bin'):
        original_name = enc_name[:-4]  # Remove .bin to get original
    else:
        original_name = enc_name.replace("encrypted_", "").replace(".bin", "")

    # Ensure proper extension
    if not any(original_name.endswith(ext) for ext in ['.pdf', '.docx', '.xlsx', '.txt', '.jpg', '.png']):
        original_name += ".pdf"

    output_dir = f"storage/encrypted/{username}/decrypted"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"decrypted_{original_name}")

    with open(output_path, "wb") as f:
        f.write(decrypted_data)

    print("\n✅ Decryption Successful ✅")
    print(f"📄 File restored: {output_path}")

    return output_path