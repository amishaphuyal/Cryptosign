import sqlite3
import os
from datetime import datetime


class AuditLogger:
    """SQLite-based audit logging for all cryptographic operations."""

    def __init__(self, db_path="storage/audit.db"):
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Create tables if not exist - using CREATE TABLE IF NOT EXISTS"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create audit_log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                username TEXT NOT NULL,
                action TEXT NOT NULL,
                file_name TEXT,
                file_hash TEXT,
                result TEXT NOT NULL,
                details TEXT,
                ip_address TEXT DEFAULT 'localhost'
            )
        """)

        # Create user_activity table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                username TEXT NOT NULL,
                activity TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)

        # ✅ NEW: Create user_files table for My Documents
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                username TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                original_name TEXT,
                file_size INTEGER,
                status TEXT DEFAULT 'active'
            )
        """)

        conn.commit()
        conn.close()
        print("✅ Audit database initialized")

    def log(self, username, action, result, file_name=None, file_hash=None, details=None):
        """Log a cryptographic operation."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_log (timestamp, username, action, file_name, file_hash, result, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (datetime.now().isoformat(), username, action, file_name, file_hash, result, details))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Audit log warning: {e}")
            # Don't crash the app if logging fails

    def add_user_file(self, username, file_type, file_path, original_name=None, file_size=0):
        """✅ NEW: Track user file for My Documents"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_files (timestamp, username, file_type, file_path, original_name, file_size, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (datetime.now().isoformat(), username, file_type, file_path, 
                  original_name or os.path.basename(file_path), file_size, 'active'))
            conn.commit()
            conn.close()
            print(f"✅ File tracked: {original_name} ({file_type})")
        except Exception as e:
            print(f"⚠️ File tracking warning: {e}")

    def get_user_files(self, username, file_type=None):
        """✅ NEW: Get all files for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            if file_type:
                cursor = conn.execute("""
                    SELECT timestamp, file_type, file_path, original_name, file_size, status
                    FROM user_files 
                    WHERE username = ? AND file_type = ? AND status = 'active'
                    ORDER BY timestamp DESC
                """, (username, file_type))
            else:
                cursor = conn.execute("""
                    SELECT timestamp, file_type, file_path, original_name, file_size, status
                    FROM user_files 
                    WHERE username = ? AND status = 'active'
                    ORDER BY timestamp DESC
                """, (username,))
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            print(f"⚠️ Get user files error: {e}")
            return []

    def delete_user_file(self, username, file_path):
        """✅ NEW: Mark file as deleted"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                UPDATE user_files SET status = 'deleted' 
                WHERE username = ? AND file_path = ?
            """, (username, file_path))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"⚠️ Delete file error: {e}")
            return False

    def get_user_history(self, username, limit=50):
        """Get operation history for a user."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("""
                SELECT timestamp, action, file_name, result, details
                FROM audit_log
                WHERE username = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (username, limit))
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            print(f"⚠️ Audit history error: {e}")
            return []

    def get_statistics(self, username=None):
        """Get operation statistics."""
        try:
            conn = sqlite3.connect(self.db_path)
            if username:
                cursor = conn.execute("""
                    SELECT action, COUNT(*) as total,
                           SUM(CASE WHEN result IN ('SUCCESS','VALID') THEN 1 ELSE 0 END) as success
                    FROM audit_log WHERE username = ? GROUP BY action
                """, (username,))
            else:
                cursor = conn.execute("""
                    SELECT action, COUNT(*) as total,
                           SUM(CASE WHEN result IN ('SUCCESS','VALID') THEN 1 ELSE 0 END) as success
                    FROM audit_log GROUP BY action
                """)
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            print(f"⚠️ Audit stats error: {e}")
            return []

    def export_to_csv(self, filepath, username=None):
        """Export audit log to CSV file."""
        import csv
        try:
            conn = sqlite3.connect(self.db_path)
            if username:
                cursor = conn.execute("SELECT * FROM audit_log WHERE username = ? ORDER BY timestamp DESC", (username,))
            else:
                cursor = conn.execute("SELECT * FROM audit_log ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            conn.close()

            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Timestamp', 'Username', 'Action', 'File', 'Hash', 'Result', 'Details', 'IP'])
                writer.writerows(rows)
            return filepath
        except Exception as e:
            print(f"⚠️ Audit export error: {e}")
            return None