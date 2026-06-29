import sqlite3
import os
import hashlib
from datetime import datetime


class AuthSystem:
    """
    Authentication system with real-world approval workflow.

    Flow:
    - Public registration => status = pending
    - Pending users cannot login/sign
    - Admin approves user => status = active
    - Admin approval can generate user's keys and certificate
    """

    def __init__(self, db_path="storage/auth.db"):
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)
        self.db_path = db_path
        self._init_db()
        self._migrate_db()

    def _hash(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                status TEXT DEFAULT 'pending',
                created_at TEXT,
                last_login TEXT,
                first_login INTEGER DEFAULT 1
            )
        """)

        # Admin must always be active
        cursor.execute("""
            INSERT OR IGNORE INTO users (username, password_hash, role, status, created_at, first_login)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("admin", self._hash("amisha@admin"), "admin", "active", datetime.now().isoformat(), 1))

        cursor.execute("UPDATE users SET status = 'active', role = 'admin' WHERE username = 'admin'")

        conn.commit()
        conn.close()

    def _migrate_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]

        if "first_login" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN first_login INTEGER DEFAULT 0")
            cursor.execute("UPDATE users SET first_login = 1 WHERE username = 'admin'")

        if "status" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'pending'")

        cursor.execute("UPDATE users SET status = 'blocked' WHERE status = 'revoked'")
        cursor.execute("UPDATE users SET status = 'active' WHERE username = 'admin'")
        conn.commit()
        conn.close()

    def login(self, username, password):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT username, role, status, first_login FROM users
            WHERE username = ? AND password_hash = ?
        """, (username, self._hash(password)))
        user = cursor.fetchone()

        if user:
            status = user[2]

            if status == "pending":
                conn.close()
                return None, "Account pending approval. Please wait for admin approval."

            if status in ["blocked", "suspended", "revoked"]:
                conn.close()
                status_messages = {
                    "blocked": "Account blocked! Please contact admin.",
                    "suspended": "Account suspended! Please contact admin.",
                    "revoked": "Account revoked!"
                }
                return None, status_messages.get(status, "Account disabled!")

            # Also block login when username is still present in storage/revoked.txt.
            try:
                from core.revocation import is_revoked
                if is_revoked(username):
                    conn.close()
                    return None, "Account revoked! Please contact admin."
            except Exception:
                pass

            cursor.execute("UPDATE users SET last_login = ? WHERE username = ?", (datetime.now().isoformat(), username))
            conn.commit()
            conn.close()

            is_first_login = user[3] == 1 if user[3] is not None else False
            return {
                "username": user[0],
                "role": user[1],
                "status": status,
                "first_login": is_first_login
            }, "Success"

        conn.close()
        return None, "Invalid credentials!"

    def change_password(self, username, new_password):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                UPDATE users
                SET password_hash = ?, first_login = 0
                WHERE username = ?
            """, (self._hash(new_password), username))
            conn.commit()
            return True, "Password changed!"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def register(self, username, password, role="user", status="pending"):
        """
        Register new user.
        Default status is pending for real-world CA approval workflow.
        """
        if status not in ["pending", "active", "blocked", "suspended"]:
            status = "pending"

        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                INSERT INTO users (username, password_hash, role, status, created_at, first_login)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, self._hash(password), role, status, datetime.now().isoformat(), 0))
            conn.commit()

            if status == "pending":
                return True, "Registered successfully! Your account is pending admin approval."
            return True, "Registered successfully!"

        except sqlite3.IntegrityError:
            return False, "Username exists!"
        finally:
            conn.close()

    def get_user(self, username):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT username, role, status, first_login FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        return user

    def get_all_users(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT username, role, status, created_at, last_login FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
        conn.close()
        return users

    def set_status(self, username, status):
        if status not in ["pending", "active", "blocked", "suspended"]:
            return False, "Invalid status"
        conn = sqlite3.connect(self.db_path)
        conn.execute("UPDATE users SET status = ? WHERE username = ?", (status, username))
        conn.commit()
        conn.close()
        return True, "Status updated"
