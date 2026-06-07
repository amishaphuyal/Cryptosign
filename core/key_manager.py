from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os


def generate_key_pair(username, password=None):
    """
    Generate RSA key pair. 
    If password provided, encrypt private key with AES-256.
    """
    os.makedirs("storage/keystores", exist_ok=True)

    print("\n🔐 Generating RSA KEY PAIRS...\n")
    print("   Algorithm: RSA-2048")
    print("   Usage: Signing + Encryption")

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    public_key = private_key.public_key()

    # ✅ Save private key (encrypted if password provided)
    priv_path = f"storage/keystores/{username}_private.pem"

    if password:
        encrypted_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(
                password.encode('utf-8')
            )
        )
        with open(priv_path, "wb") as f:
            f.write(encrypted_private)
        print("   ✅ Private key ENCRYPTED with password")
    else:
        unencrypted_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        with open(priv_path, "wb") as f:
            f.write(unencrypted_private)
        print("   ⚠️ Private key saved (unencrypted)")

    # ✅ Save public key (always unencrypted)
    pub_path = f"storage/keystores/{username}_public.pem"
    with open(pub_path, "wb") as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

    print(f"\n   ✅ Private key saved → {priv_path}")
    print(f"   ✅ Public key saved → {pub_path}")
    print("\n🔥 RSA KEY GENERATION COMPLETE 🔥")

    return private_key, public_key


def load_private_key(username, password=None):
    """Load private key. If encrypted, password required."""
    priv_path = f"storage/keystores/{username}_private.pem"

    if not os.path.exists(priv_path):
        raise FileNotFoundError(f"Private key not found for user: {username}")

    with open(priv_path, "rb") as f:
        key_data = f.read()

    # Try without password first (backward compatibility)
    try:
        return serialization.load_pem_private_key(key_data, password=None)
    except Exception:
        pass

    # Try with password
    if password:
        try:
            return serialization.load_pem_private_key(key_data, password=password.encode('utf-8'))
        except Exception as e:
            raise ValueError(f"Invalid password or corrupted key: {e}")
    else:
        raise ValueError("Private key is password-protected. Please provide password.")


def is_key_encrypted(username):
    """Check if user's private key is password protected."""
    priv_path = f"storage/keystores/{username}_private.pem"
    if not os.path.exists(priv_path):
        return False

    with open(priv_path, "rb") as f:
        content = f.read()

    return b"ENCRYPTED" in content or b"Proc-Type:" in content