import os

REVOCATION_FILE = "storage/revoked.txt"

def revoke_user(username):
    os.makedirs("storage", exist_ok=True)

    with open(REVOCATION_FILE, "a") as f:
        f.write(username + "\n")

    print(f"❌ {username} certificate revoked!")


def is_revoked(username):
    if not os.path.exists(REVOCATION_FILE):
        return False

    with open(REVOCATION_FILE, "r") as f:
        revoked_list = f.read().splitlines()

    return username in revoked_list
