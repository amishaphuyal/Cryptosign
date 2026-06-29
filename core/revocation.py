import os

REVOCATION_FILE = "storage/revoked.txt"


def _normalise(username):
    return (username or "").strip()


def _read_revoked_users():
    if not os.path.exists(REVOCATION_FILE):
        return []

    with open(REVOCATION_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.read().splitlines() if line.strip()]


def _write_revoked_users(users):
    os.makedirs(os.path.dirname(REVOCATION_FILE) if os.path.dirname(REVOCATION_FILE) else ".", exist_ok=True)
    unique = []
    seen = set()
    for user in users:
        user = _normalise(user)
        key = user.lower()
        if user and key not in seen:
            unique.append(user)
            seen.add(key)

    with open(REVOCATION_FILE, "w", encoding="utf-8") as f:
        if unique:
            f.write("\n".join(unique) + "\n")
        else:
            f.write("")


def revoke_user(username):
    """Add username to revocation list without duplicates."""
    username = _normalise(username)
    if not username:
        return False

    users = _read_revoked_users()
    if username.lower() not in [u.lower() for u in users]:
        users.append(username)
        _write_revoked_users(users)

    print(f"❌ {username} certificate revoked!")
    return True


def unrevoke_user(username):
    """Remove username from revocation list after admin reactivation."""
    username = _normalise(username)
    if not username:
        return False

    users = _read_revoked_users()
    new_users = [u for u in users if u.lower() != username.lower()]
    changed = len(new_users) != len(users)
    _write_revoked_users(new_users)

    if changed:
        print(f"✅ {username} removed from revocation list!")
    return changed


def is_revoked(username):
    username = _normalise(username)
    if not username:
        return False

    users = _read_revoked_users()
    return username.lower() in [u.lower() for u in users]
