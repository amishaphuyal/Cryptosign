import hashlib

def generate_hash(file_path):

    with open(file_path, "rb") as f:
        data = f.read()

    sha256 = hashlib.sha256(data).hexdigest()

    print("File Hash (SHA-256):", sha256)

    return sha256
