import sqlite3
import os
import hashlib
from datetime import datetime


class AuthSystem:
    def __init__(self, db_path="storage/auth.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
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
                status TEXT DEFAULT 'active',
                created_at TEXT,
                last_login TEXT,
                first_login INTEGER DEFAULT 1
            )
        """)
        
        cursor.execute("""
            INSERT OR IGNORE INTO users (username, password_hash, role, created_at, first_login)
            VALUES (?, ?, ?, ?, ?)
        """, ("admin", self._hash("amisha@admin"), "admin", datetime.now().isoformat(), 1))
        
        conn.commit()
        conn.close()
    
    def _migrate_db(self):
        """Add missing columns to existing database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if "first_login" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN first_login INTEGER DEFAULT 0")
            cursor.execute("UPDATE users SET first_login = 1 WHERE username = 'admin'")
        
        cursor.execute("UPDATE users SET status = 'blocked' WHERE status = 'revoked'")
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
        conn.close()
        
        if user:
            if user[2] in ["blocked", "suspended", "revoked"]:
                status_messages = {
                    "blocked": "Account blocked! Please contact admin.",
                    "suspended": "Account suspended! Please contact admin.",
                    "revoked": "Account revoked!"
                }
                return None, status_messages.get(user[2], "Account disabled!")
            
            is_first_login = user[3] == 1 if user[3] is not None else False
            
            return {
                "username": user[0], 
                "role": user[1],
                "first_login": is_first_login
            }, "Success"
        
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
    
    def register(self, username, password, role="user"):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                INSERT INTO users (username, password_hash, role, created_at, first_login)
                VALUES (?, ?, ?, ?, ?)
            """, (username, self._hash(password), role, datetime.now().isoformat(), 0))
            conn.commit()
            return True, "Registered!"
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
        cursor.execute("SELECT username, role, status, created_at, last_login FROM users")
        users = cursor.fetchall()
        conn.close()
        return users