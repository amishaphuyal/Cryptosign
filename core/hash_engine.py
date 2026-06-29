import hashlib


def generate_hash(file_path, username=None):
    """Generate SHA-256 hash.

    If username is provided, revoked users are blocked according to
    the CryptoSign project policy.
    """
    if username:
        try:
            from core.revocation import is_revoked
            if is_revoked(username):
                raise PermissionError("Operation blocked: user certificate is revoked. Hashing is not allowed.")
        except PermissionError:
            raise
        except Exception as e:
            print(f"Revocation check warning: {e}")

    with open(file_path, "rb") as f:
        data = f.read()

    sha256 = hashlib.sha256(data).hexdigest()

    print("File Hash (SHA-256):", sha256)

    return sha256
