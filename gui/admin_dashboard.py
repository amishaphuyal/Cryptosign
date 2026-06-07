import customtkinter as ctk
from tkinter import messagebox, simpledialog
import sys
import os
import sqlite3
from datetime import datetime, timedelta  # ✅ timedelta pani add gara

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.auth_system import AuthSystem
from core.audit_logger import AuditLogger
from core.revocation import is_revoked


class AdminDashboard:
    def __init__(self, root, admin_user):
        self.root = root
        self.admin = admin_user
        self.auth = AuthSystem()
        self.audit = AuditLogger()
        
        self.root.title("CryptoSign - Admin Dashboard")
        self.root.geometry("1200x800")
        self.root.configure(fg_color="#0f172a")
        
        self.current_view = "dashboard"
        self.build_sidebar()
        self.build_main_content()
        self.show_dashboard()
    
    def build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self.root, fg_color="#1e293b", width=250, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=80)
        logo_frame.pack(fill="x", pady=(20, 10))
        
        ctk.CTkLabel(logo_frame, text="🔐", font=("Inter", 32)).pack()
        ctk.CTkLabel(logo_frame, text="CryptoSign", font=("Inter", 16, "bold"), 
                    text_color="#6366f1").pack()
        ctk.CTkLabel(logo_frame, text="Digital Document Signing", 
                    font=("Inter", 10), text_color="#64748b").pack()
        
        ctk.CTkFrame(self.sidebar, fg_color="#334155", height=1).pack(fill="x", padx=20, pady=10)
        
        self.menu_buttons = {}
        
        menu_items = [
            ("📊", "Dashboard", "dashboard"),
            ("👥", "User Management", "users"),
            ("📜", "Audit Logs", "logs"),
            ("🔐", "Certificate Management", "certs"),
            ("❌", "Revoked Certificates", "revoked"),
            ("📄", "Documents", "docs"),
            ("⚙️", "System Settings", "settings"),
        ]
        
        for icon, text, view in menu_items:
            btn = ctk.CTkButton(self.sidebar, text=f"{icon}  {text}", 
                               font=("Inter", 13), height=40,
                               fg_color="transparent", hover_color="#334155",
                               text_color="#94a3b8", anchor="w",
                               corner_radius=8, command=lambda v=view: self.switch_view(v))
            btn.pack(fill="x", padx=10, pady=2)
            self.menu_buttons[view] = btn
        
        ctk.CTkFrame(self.sidebar, fg_color="#334155", height=1).pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(self.sidebar, text=f"👤 {self.admin['username']}", 
                    font=("Inter", 12, "bold"), text_color="#f8fafc").pack(pady=5)
        ctk.CTkLabel(self.sidebar, text="Super Administrator", 
                    font=("Inter", 10), text_color="#64748b").pack()
        
        ctk.CTkButton(self.sidebar, text="🚪 Logout", 
                     font=("Inter", 12, "bold"), height=40,
                     fg_color="#ef4444", hover_color="#dc2626",
                     text_color="white", corner_radius=8,
                     command=self.logout).pack(fill="x", padx=10, pady=20)
    
    def build_main_content(self):
        self.main_content = ctk.CTkFrame(self.root, fg_color="#0f172a", corner_radius=0)
        self.main_content.pack(side="right", fill="both", expand=True)
        
        self.header = ctk.CTkFrame(self.main_content, fg_color="transparent", height=60)
        self.header.pack(fill="x", padx=30, pady=(20, 10))
        self.header.pack_propagate(False)
        
        self.header_title = ctk.CTkLabel(self.header, text="Dashboard", 
                                        font=("Inter", 24, "bold"), text_color="#f8fafc")
        self.header_title.pack(side="left")
        
        ctk.CTkButton(self.header, text="📅 May 12, 2024 - May 19, 2024", 
                     font=("Inter", 12), height=35, width=250,
                     fg_color="#1e293b", hover_color="#334155",
                     text_color="#94a3b8", corner_radius=8).pack(side="right")
        
        self.content_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=30, pady=10)
    
    def switch_view(self, view):
        for v, btn in self.menu_buttons.items():
            if v == view:
                btn.configure(fg_color="#6366f1", text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color="#94a3b8")
        
        self.current_view = view
        
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        if view == "dashboard":
            self.show_dashboard()
        elif view == "users":
            self.show_users()
        elif view == "logs":
            self.show_logs()
        elif view == "certs":
            self.show_certificates()
        elif view == "revoked":
            self.show_revoked()
        elif view == "docs":
            self.show_documents()
        elif view == "settings":
            self.show_settings()
    
    def show_dashboard(self):
        self.header_title.configure(text="Dashboard")
        
        stats_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))
        
        try:
            conn = sqlite3.connect("storage/audit.db")
            cursor = conn.cursor()
            
            conn2 = sqlite3.connect(self.auth.db_path)
            cursor2 = conn2.cursor()
            cursor2.execute("SELECT COUNT(*) FROM users WHERE role != 'admin'")
            total_users = cursor2.fetchone()[0]
            cursor2.execute("SELECT COUNT(*) FROM users WHERE status = 'active' AND role != 'admin'")
            active_users = cursor2.fetchone()[0]
            conn2.close()
            
            cursor.execute("""
                SELECT COUNT(*) FROM audit_log 
                WHERE action IN ('SIGN', 'BATCH_SIGN') AND result = 'SUCCESS'
            """)
            signed_docs = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM audit_log 
                WHERE action = 'VERIFY' AND result = 'VALID'
            """)
            verified_docs = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM audit_log 
                WHERE action = 'ENCRYPT' AND result = 'SUCCESS'
            """)
            encrypted_docs = cursor.fetchone()[0]
            
            conn2 = sqlite3.connect(self.auth.db_path)
            cursor2 = conn2.cursor()
            cursor2.execute("SELECT COUNT(*) FROM users WHERE status = 'revoked'")
            revoked_users = cursor2.fetchone()[0]
            conn2.close()
            
            conn.close()
            
        except Exception as e:
            print(f"Stats error: {e}")
            total_users = 0
            active_users = 0
            signed_docs = 0
            verified_docs = 0
            encrypted_docs = 0
            revoked_users = 0
        
        self.create_stat_card(stats_frame, "👥 Total Users", str(total_users), 
                             f"{active_users} active", "#6366f1", "#3b82f6")
        self.create_stat_card(stats_frame, "📝 Signed Documents", str(signed_docs), 
                             "All time", "#10b981", "#059669")
        self.create_stat_card(stats_frame, "✅ Verified Documents", str(verified_docs), 
                             "All time", "#f59e0b", "#d97706")
        self.create_stat_card(stats_frame, "❌ Revoked Users", str(revoked_users), 
                             "Access denied", "#ef4444", "#dc2626")
        
        bottom_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        bottom_frame.pack(fill="both", expand=True)
        
        activities_frame = ctk.CTkFrame(bottom_frame, fg_color="#1e293b", corner_radius=12)
        activities_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(activities_frame, text="📈 Recent Activities", 
                    font=("Inter", 16, "bold"), text_color="#f8fafc").pack(anchor="w", padx=20, pady=(15, 10))
        
        activities_scroll = ctk.CTkScrollableFrame(activities_frame, fg_color="transparent")
        activities_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        try:
            conn = sqlite3.connect("storage/audit.db")
            cursor = conn.execute("""
                SELECT timestamp, username, action, file_name, result 
                FROM audit_log ORDER BY timestamp DESC LIMIT 10
            """)
            activities = cursor.fetchall()
            conn.close()
            
            for activity in activities:
                timestamp, username, action, file_name, result = activity
                self.create_activity_item(activities_scroll, username, action, file_name, timestamp, result)
        except:
            self.create_activity_item(activities_scroll, "System", "INIT", "No activities yet", "Now", "SUCCESS")
        
        users_frame = ctk.CTkFrame(bottom_frame, fg_color="#1e293b", corner_radius=12)
        users_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        ctk.CTkLabel(users_frame, text="👥 Recent Users", 
                    font=("Inter", 16, "bold"), text_color="#f8fafc").pack(anchor="w", padx=20, pady=(15, 10))
        
        users_scroll = ctk.CTkScrollableFrame(users_frame, fg_color="transparent")
        users_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        try:
            conn = sqlite3.connect(self.auth.db_path)
            cursor = conn.execute("SELECT username, role, status, created_at FROM users ORDER BY created_at DESC LIMIT 8")
            users = cursor.fetchall()
            conn.close()
            
            for user in users:
                self.create_user_item(users_scroll, user)
        except:
            ctk.CTkLabel(users_scroll, text="No users found", font=("Inter", 12), text_color="#64748b").pack(pady=20)
    
    def create_stat_card(self, parent, title, value, change, color, hover_color):
        card = ctk.CTkFrame(parent, fg_color="#1e293b", corner_radius=12, width=250)
        card.pack(side="left", expand=True, fill="both", padx=5, pady=5)
        
        ctk.CTkLabel(card, text=title, font=("Inter", 12), 
                    text_color="#94a3b8").pack(anchor="w", padx=20, pady=(15, 5))
        
        ctk.CTkLabel(card, text=value, font=("Inter", 32, "bold"), 
                    text_color=color).pack(anchor="w", padx=20)
        
        ctk.CTkLabel(card, text=change, font=("Inter", 11), 
                    text_color="#64748b").pack(anchor="w", padx=20, pady=(5, 15))
    
    def create_activity_item(self, parent, user, action, detail, time, result):
        frame = ctk.CTkFrame(parent, fg_color="#0f172a", corner_radius=8)
        frame.pack(fill="x", pady=3)
        
        icons = {
            "SIGN": "📝", "VERIFY": "✅", "ENCRYPT": "🔐", 
            "DECRYPT": "🔓", "SETUP": "⚙️", "USER_SET": "👤",
            "REVOKE": "❌", "HASH": "🔍", "ADMIN": "👑",
            "BATCH_SIGN": "📦", "ADMIN_ADD_USER": "➕",
            "ADMIN_REVOKE": "🚫", "ADMIN_ACTIVATE": "✅",
            "ADMIN_DELETE": "🗑️", "ADMIN_ROLE_CHANGE": "👑"
        }
        icon = icons.get(action, "📋")
        
        result_color = "#10b981" if result in ["SUCCESS", "VALID"] else "#ef4444"
        
        ctk.CTkLabel(frame, text=f"{icon} {user} {action.lower()} {detail or ''}", 
                    font=("Inter", 12), text_color="#f8fafc").pack(side="left", padx=15, pady=10)
        
        ctk.CTkLabel(frame, text=result, 
                    font=("Inter", 10, "bold"), text_color=result_color).pack(side="right", padx=5)
        
        ctk.CTkLabel(frame, text=time[:10] if time != "Now" else time, 
                    font=("Inter", 10), text_color="#64748b").pack(side="right", padx=15)
    
    def create_user_item(self, parent, user):
        username, role, status, created = user
        
        frame = ctk.CTkFrame(parent, fg_color="#0f172a", corner_radius=8)
        frame.pack(fill="x", pady=3)
        
        ctk.CTkLabel(frame, text=f"👤 {username}", 
                    font=("Inter", 12, "bold"), text_color="#f8fafc").pack(side="left", padx=15, pady=10)
        
        role_color = "#6366f1" if role == "admin" else "#94a3b8"
        ctk.CTkLabel(frame, text=role, font=("Inter", 10), 
                    text_color=role_color).pack(side="left", padx=10)
        
        status_color = "#10b981" if status == "active" else "#ef4444"
        ctk.CTkLabel(frame, text=status, font=("Inter", 10), 
                    text_color=status_color).pack(side="right", padx=15)
        
        ctk.CTkLabel(frame, text=created[:10] if created else "N/A", 
                    font=("Inter", 10), text_color="#64748b").pack(side="right", padx=10)
    
    def show_users(self):
        self.header_title.configure(text="User Management")
        
        toolbar = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 15))
        
        ctk.CTkButton(toolbar, text="➕ Add User", width=120, height=35,
                     font=("Inter", 12), fg_color="#10b981", hover_color="#059669",
                     corner_radius=8, command=self.add_user).pack(side="left", padx=5)
        
        ctk.CTkButton(toolbar, text="🔄 Refresh", width=120, height=35,
                     font=("Inter", 12), fg_color="#6366f1", hover_color="#4f46e5",
                     corner_radius=8, command=lambda: self.switch_view("users")).pack(side="left", padx=5)
        
        table_frame = ctk.CTkFrame(self.content_frame, fg_color="#1e293b", corner_radius=12)
        table_frame.pack(fill="both", expand=True)
        
        headers = ctk.CTkFrame(table_frame, fg_color="#334155", corner_radius=8)
        headers.pack(fill="x", padx=20, pady=15)
        
        for col, width in [("Username", 200), ("Role", 150), ("Status", 150), ("Created", 200), ("Actions", 300)]:
            ctk.CTkLabel(headers, text=col, font=("Inter", 12, "bold"), 
                        text_color="#94a3b8", width=width).pack(side="left", padx=10, pady=10)
        
        scroll = ctk.CTkScrollableFrame(table_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        users = self.auth.get_all_users()
        for user in users:
            self.create_user_row(scroll, user)
    
    def create_user_row(self, parent, user):
        username, role, status, created, _ = user
        
        row = ctk.CTkFrame(parent, fg_color="#0f172a", corner_radius=8)
        row.pack(fill="x", pady=3)
        
        ctk.CTkLabel(row, text=username, font=("Inter", 12), 
                    text_color="#f8fafc", width=200).pack(side="left", padx=10, pady=10)
        
        role_color = "#6366f1" if role == "admin" else "#94a3b8"
        ctk.CTkLabel(row, text=role, font=("Inter", 12, "bold"), 
                    text_color=role_color, width=150).pack(side="left", padx=10)
        
        status_color = "#10b981" if status == "active" else "#ef4444"
        ctk.CTkLabel(row, text=status, font=("Inter", 12), 
                    text_color=status_color, width=150).pack(side="left", padx=10)
        
        ctk.CTkLabel(row, text=created[:10] if created else "N/A", 
                    font=("Inter", 11), text_color="#64748b", width=200).pack(side="left", padx=10)
        
        actions = ctk.CTkFrame(row, fg_color="transparent", width=300)
        actions.pack(side="left", padx=10)
        
        if username != self.admin['username']:
            if status == "active":
                ctk.CTkButton(actions, text="🚫", width=30, height=28,
                             fg_color="#ef4444", hover_color="#dc2626",
                             corner_radius=6, command=lambda u=username: self.revoke_user(u)).pack(side="left", padx=2)
            else:
                ctk.CTkButton(actions, text="✅", width=30, height=28,
                             fg_color="#10b981", hover_color="#059669",
                             corner_radius=6, command=lambda u=username: self.activate_user(u)).pack(side="left", padx=2)
            
            new_role = "user" if role == "admin" else "admin"
            ctk.CTkButton(actions, text="👑", width=30, height=28,
                         fg_color="#6366f1", hover_color="#4f46e5",
                         corner_radius=6, command=lambda u=username, r=new_role: self.change_role(u, r)).pack(side="left", padx=2)
            
            ctk.CTkButton(actions, text="🗑️", width=30, height=28,
                         fg_color="#64748b", hover_color="#475569",
                         corner_radius=6, command=lambda u=username: self.delete_user(u)).pack(side="left", padx=2)
    
    def show_logs(self):
        self.header_title.configure(text="Audit Logs")
        
        toolbar = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 15))
        
        ctk.CTkButton(toolbar, text="📥 Export CSV", width=120, height=35,
                     font=("Inter", 12), fg_color="#10b981", hover_color="#059669",
                     corner_radius=8, command=self.export_logs).pack(side="right")
        
        table_frame = ctk.CTkFrame(self.content_frame, fg_color="#1e293b", corner_radius=12)
        table_frame.pack(fill="both", expand=True)
        
        headers = ctk.CTkFrame(table_frame, fg_color="#334155", corner_radius=8)
        headers.pack(fill="x", padx=20, pady=15)
        
        for col, width in [("Time", 150), ("User", 120), ("Action", 120), ("File", 150), ("Result", 100), ("Details", 250)]:
            ctk.CTkLabel(headers, text=col, font=("Inter", 12, "bold"), 
                        text_color="#94a3b8", width=width).pack(side="left", padx=10, pady=10)
        
        scroll = ctk.CTkScrollableFrame(table_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        try:
            conn = sqlite3.connect("storage/audit.db")
            cursor = conn.execute("SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 100")
            logs = cursor.fetchall()
            conn.close()
            
            for log in logs:
                self.create_log_row(scroll, log)
        except:
            ctk.CTkLabel(scroll, text="No logs found", font=("Inter", 12), 
                        text_color="#64748b").pack(pady=20)
    
    def create_log_row(self, parent, log):
        id, timestamp, username, action, file_name, file_hash, result, details, ip = log
        
        row = ctk.CTkFrame(parent, fg_color="#0f172a", corner_radius=6)
        row.pack(fill="x", pady=2)
        
        ctk.CTkLabel(row, text=timestamp[:19], font=("Courier", 10), 
                    text_color="#64748b", width=150).pack(side="left", padx=5, pady=8)
        ctk.CTkLabel(row, text=username, font=("Inter", 10), 
                    text_color="#94a3b8", width=120).pack(side="left", padx=5)
        ctk.CTkLabel(row, text=action, font=("Inter", 10, "bold"), 
                    text_color="#6366f1", width=120).pack(side="left", padx=5)
        ctk.CTkLabel(row, text=file_name or "-", font=("Inter", 10), 
                    text_color="#94a3b8", width=150).pack(side="left", padx=5)
        
        result_color = "#10b981" if result in ["SUCCESS", "VALID"] else "#ef4444"
        ctk.CTkLabel(row, text=result, font=("Inter", 10), 
                    text_color=result_color, width=100).pack(side="left", padx=5)
        ctk.CTkLabel(row, text=details or "", font=("Inter", 9), 
                    text_color="#64748b", width=250).pack(side="left", padx=5)
    
    def show_certificates(self):
        self.header_title.configure(text="Certificate Management")
        
        toolbar = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 15))
        
        ctk.CTkButton(toolbar, text="🔄 Refresh", width=120, height=35,
                     font=("Inter", 12), fg_color="#6366f1", hover_color="#4f46e5",
                     corner_radius=8, command=lambda: self.switch_view("certs")).pack(side="left", padx=5)
        
        ctk.CTkButton(toolbar, text="🏛 View CA Cert", width=140, height=35,
                     font=("Inter", 12), fg_color="#10b981", hover_color="#059669",
                     corner_radius=8, command=self.view_ca_cert).pack(side="left", padx=5)
        
        stats_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 15))
        
        cert_count = 0
        ca_exists = os.path.exists("storage/ca/ca_cert.pem")
        if os.path.exists("storage/certs"):
            cert_count = len([f for f in os.listdir("storage/certs") if f.endswith("_cert.pem")])
        
        self.create_stat_card(stats_frame, "🏛 CA Certificate", "Active" if ca_exists else "Missing", 
                             "Root authority", "#10b981", "#059669")
        self.create_stat_card(stats_frame, "📜 User Certs", str(cert_count), 
                             "Issued certificates", "#6366f1", "#3b82f6")
        self.create_stat_card(stats_frame, "🔐 Key Stores", str(cert_count), 
                             "Private keys", "#f59e0b", "#d97706")
        
        table_frame = ctk.CTkFrame(self.content_frame, fg_color="#1e293b", corner_radius=12)
        table_frame.pack(fill="both", expand=True)
        
        headers = ctk.CTkFrame(table_frame, fg_color="#334155", corner_radius=8)
        headers.pack(fill="x", padx=20, pady=15)
        
        for col, width in [("User", 200), ("Certificate", 200), ("Status", 150), ("Actions", 300)]:
            ctk.CTkLabel(headers, text=col, font=("Inter", 12, "bold"), 
                        text_color="#94a3b8", width=width).pack(side="left", padx=10, pady=10)
        
        scroll = ctk.CTkScrollableFrame(table_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        if os.path.exists("storage/certs"):
            for cert_file in sorted(os.listdir("storage/certs")):
                if cert_file.endswith("_cert.pem"):
                    username = cert_file.replace("_cert.pem", "")
                    self.create_cert_row(scroll, username, cert_file)
        
        if cert_count == 0:
            ctk.CTkLabel(scroll, text="No certificates found. Users need to setup their keys first.", 
                        font=("Inter", 12), text_color="#64748b").pack(pady=20)
    
    def create_cert_row(self, parent, username, cert_file):
        row = ctk.CTkFrame(parent, fg_color="#0f172a", corner_radius=8)
        row.pack(fill="x", pady=3)
        
        cert_path = f"storage/certs/{cert_file}"
        
        status = "Valid"
        status_color = "#10b981"
        try:
            from core.cert_verifier import verify_certificate
            from core.ca_engine import load_ca_public_key
            ca_key = load_ca_public_key()
            if not verify_certificate(cert_path, ca_key):
                status = "Invalid"
                status_color = "#ef4444"
        except:
            status = "Error"
            status_color = "#f59e0b"
        
        if is_revoked(username):
            status = "Revoked"
            status_color = "#ef4444"
        
        ctk.CTkLabel(row, text=username, font=("Inter", 12), 
                    text_color="#f8fafc", width=200).pack(side="left", padx=10, pady=10)
        
        ctk.CTkLabel(row, text=cert_file, font=("Inter", 11), 
                    text_color="#94a3b8", width=200).pack(side="left", padx=10)
        
        ctk.CTkLabel(row, text=status, font=("Inter", 12, "bold"), 
                    text_color=status_color, width=150).pack(side="left", padx=10)
        
        actions = ctk.CTkFrame(row, fg_color="transparent", width=300)
        actions.pack(side="left", padx=10)
        
        ctk.CTkButton(actions, text="👁 View", width=60, height=28,
                     fg_color="#6366f1", hover_color="#4f46e5",
                     corner_radius=6, command=lambda u=username: self.view_cert(u)).pack(side="left", padx=2)
        
        ctk.CTkButton(actions, text="📥 Download", width=80, height=28,
                     fg_color="#10b981", hover_color="#059669",
                     corner_radius=6, command=lambda c=cert_path: self.download_cert(c)).pack(side="left", padx=2)
        
        if not is_revoked(username):
            ctk.CTkButton(actions, text="❌ Revoke", width=60, height=28,
                         fg_color="#ef4444", hover_color="#dc2626",
                         corner_radius=6, command=lambda u=username: self.revoke_cert(u)).pack(side="left", padx=2)
    
    def view_cert(self, username):
        cert_path = f"storage/certs/{username}_cert.pem"
        if os.path.exists(cert_path):
            with open(cert_path, 'r') as f:
                content = f.read()
            
            dialog = ctk.CTkToplevel(self.root)
            dialog.title(f"Certificate - {username}")
            dialog.geometry("600x400")
            dialog.configure(fg_color="#0f172a")
            
            ctk.CTkLabel(dialog, text=f"🏛 Certificate for {username}", 
                        font=("Inter", 16, "bold"), text_color="#6366f1").pack(pady=15)
            
            text_box = ctk.CTkTextbox(dialog, width=550, height=300, font=("Courier", 10),
                                      fg_color="#1e293b", text_color="#f8fafc")
            text_box.pack(pady=10)
            text_box.insert("1.0", content)
            text_box.configure(state="disabled")
    
    def download_cert(self, cert_path):
        from tkinter import filedialog
        if os.path.exists(cert_path):
            save_path = filedialog.asksaveasfilename(
                defaultextension=".pem",
                initialfile=os.path.basename(cert_path),
                filetypes=[("PEM files", "*.pem"), ("All files", "*.*")]
            )
            if save_path:
                import shutil
                shutil.copy2(cert_path, save_path)
                messagebox.showinfo("Success", f"Certificate saved to:\n{save_path}")
    
    def revoke_cert(self, username):
        if messagebox.askyesno("Confirm", f"Revoke certificate for '{username}'?\n\nThis will add them to revocation list."):
            from core.revocation import revoke_user
            revoke_user(username)
            self.audit.log(self.admin['username'], "ADMIN_REVOKE_CERT", "SUCCESS", details=f"Revoked: {username}")
            self.switch_view("certs")
            messagebox.showinfo("Success", f"Certificate for '{username}' revoked!")
    
    def view_ca_cert(self):
        ca_path = "storage/ca/ca_cert.pem"
        if os.path.exists(ca_path):
            with open(ca_path, 'r') as f:
                content = f.read()
            
            dialog = ctk.CTkToplevel(self.root)
            dialog.title("CA Certificate")
            dialog.geometry("600x400")
            dialog.configure(fg_color="#0f172a")
            
            ctk.CTkLabel(dialog, text="🏛 Root CA Certificate", 
                        font=("Inter", 16, "bold"), text_color="#6366f1").pack(pady=15)
            
            text_box = ctk.CTkTextbox(dialog, width=550, height=300, font=("Courier", 10),
                                      fg_color="#1e293b", text_color="#f8fafc")
            text_box.pack(pady=10)
            text_box.insert("1.0", content)
            text_box.configure(state="disabled")
        else:
            messagebox.showerror("Error", "CA certificate not found!")
    
    def show_revoked(self):
        self.header_title.configure(text="Revoked Certificates")
        
        revoked_users = []
        
        try:
            conn = sqlite3.connect(self.auth.db_path)
            cursor = conn.execute("SELECT username, role, status, created_at FROM users WHERE status = 'revoked'")
            db_revoked = cursor.fetchall()
            conn.close()
            revoked_users.extend(db_revoked)
        except:
            pass
        
        try:
            from core.revocation import REVOCATION_FILE
            if os.path.exists(REVOCATION_FILE):
                with open(REVOCATION_FILE, 'r') as f:
                    file_revoked = f.read().splitlines()
                existing = [u[0] for u in revoked_users]
                for username in file_revoked:
                    if username and username not in existing:
                        revoked_users.append((username, "user", "revoked", "N/A"))
        except:
            pass
        
        stats_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 15))
        
        self.create_stat_card(stats_frame, "❌ Revoked Users", str(len(revoked_users)), 
                             "Access denied", "#ef4444", "#dc2626")
        self.create_stat_card(stats_frame, "✅ Active Users", "See Dashboard", 
                             "Total minus revoked", "#10b981", "#059669")
        
        table_frame = ctk.CTkFrame(self.content_frame, fg_color="#1e293b", corner_radius=12)
        table_frame.pack(fill="both", expand=True)
        
        headers = ctk.CTkFrame(table_frame, fg_color="#334155", corner_radius=8)
        headers.pack(fill="x", padx=20, pady=15)
        
        for col, width in [("Username", 250), ("Role", 150), ("Status", 150), ("Created", 200), ("Actions", 250)]:
            ctk.CTkLabel(headers, text=col, font=("Inter", 12, "bold"), 
                        text_color="#94a3b8", width=width).pack(side="left", padx=10, pady=10)
        
        scroll = ctk.CTkScrollableFrame(table_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        if not revoked_users:
            ctk.CTkLabel(scroll, text="No revoked users found", 
                        font=("Inter", 14), text_color="#64748b").pack(pady=30)
        else:
            for user in revoked_users:
                self.create_revoked_row(scroll, user)
    
    def create_revoked_row(self, parent, user):
        username, role, status, created = user
        
        row = ctk.CTkFrame(parent, fg_color="#0f172a", corner_radius=8)
        row.pack(fill="x", pady=3)
        
        ctk.CTkLabel(row, text=username, font=("Inter", 12, "bold"), 
                    text_color="#ef4444", width=250).pack(side="left", padx=10, pady=10)
        
        ctk.CTkLabel(row, text=role, font=("Inter", 12), 
                    text_color="#94a3b8", width=150).pack(side="left", padx=10)
        
        ctk.CTkLabel(row, text="🔴 REVOKED", font=("Inter", 12, "bold"), 
                    text_color="#ef4444", width=150).pack(side="left", padx=10)
        
        ctk.CTkLabel(row, text=created[:10] if created and created != "N/A" else "N/A", 
                    font=("Inter", 11), text_color="#64748b", width=200).pack(side="left", padx=10)
        
        actions = ctk.CTkFrame(row, fg_color="transparent", width=250)
        actions.pack(side="left", padx=10)
        
        ctk.CTkButton(actions, text="✅ Reactivate", width=90, height=28,
                     fg_color="#10b981", hover_color="#059669",
                     corner_radius=6, command=lambda u=username: self.activate_user(u)).pack(side="left", padx=2)
        
        ctk.CTkButton(actions, text="🗑️ Delete", width=70, height=28,
                     fg_color="#64748b", hover_color="#475569",
                     corner_radius=6, command=lambda u=username: self.delete_user(u)).pack(side="left", padx=2)
    
    def show_documents(self):
        self.header_title.configure(text="Documents")
        
        toolbar = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 15))
        
        ctk.CTkButton(toolbar, text="📝 Signed", width=100, height=35,
                     font=("Inter", 12), fg_color="#6366f1", hover_color="#4f46e5",
                     corner_radius=8, command=lambda: self.filter_docs("signed")).pack(side="left", padx=5)
        
        ctk.CTkButton(toolbar, text="🔐 Encrypted", width=100, height=35,
                     font=("Inter", 12), fg_color="#f59e0b", hover_color="#d97706",
                     corner_radius=8, command=lambda: self.filter_docs("encrypted")).pack(side="left", padx=5)
        
        ctk.CTkButton(toolbar, text="📜 All", width=80, height=35,
                     font=("Inter", 12), fg_color="#10b981", hover_color="#059669",
                     corner_radius=8, command=lambda: self.filter_docs("all")).pack(side="left", padx=5)
        
        ctk.CTkButton(toolbar, text="🔄 Refresh", width=100, height=35,
                     font=("Inter", 12), fg_color="#64748b", hover_color="#475569",
                     corner_radius=8, command=lambda: self.switch_view("docs")).pack(side="right", padx=5)
        
        stats_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 15))
        
        try:
            conn = sqlite3.connect("storage/audit.db")
            signed_count = conn.execute("""
                SELECT COUNT(*) FROM user_files WHERE file_type = 'signed' AND status = 'active'
            """).fetchone()[0]
            encrypted_count = conn.execute("""
                SELECT COUNT(*) FROM user_files WHERE file_type = 'encrypted' AND status = 'active'
            """).fetchone()[0]
            total_count = conn.execute("""
                SELECT COUNT(*) FROM user_files WHERE status = 'active'
            """).fetchone()[0]
            conn.close()
        except:
            signed_count = 0
            encrypted_count = 0
            total_count = 0
        
        self.create_stat_card(stats_frame, "📝 Signed", str(signed_count), 
                             "Tracked files", "#6366f1", "#3b82f6")
        self.create_stat_card(stats_frame, "🔐 Encrypted", str(encrypted_count), 
                             "Tracked files", "#f59e0b", "#d97706")
        self.create_stat_card(stats_frame, "📜 Total", str(total_count), 
                             "All documents", "#10b981", "#059669")
        
        self.docs_table_frame = ctk.CTkFrame(self.content_frame, fg_color="#1e293b", corner_radius=12)
        self.docs_table_frame.pack(fill="both", expand=True)
        
        self.build_docs_table("all")
    
    def build_docs_table(self, filter_type):
        for widget in self.docs_table_frame.winfo_children():
            widget.destroy()
        
        headers = ctk.CTkFrame(self.docs_table_frame, fg_color="#334155", corner_radius=8)
        headers.pack(fill="x", padx=20, pady=15)
        
        for col, width in [("Type", 80), ("File", 250), ("User", 120), ("Size", 100), ("Date", 150), ("Actions", 250)]:
            ctk.CTkLabel(headers, text=col, font=("Inter", 12, "bold"), 
                        text_color="#94a3b8", width=width).pack(side="left", padx=10, pady=10)
        
        scroll = ctk.CTkScrollableFrame(self.docs_table_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        try:
            conn = sqlite3.connect("storage/audit.db")
            if filter_type == "all":
                cursor = conn.execute("""
                    SELECT file_type, original_name, username, file_size, timestamp, file_path, status
                    FROM user_files WHERE status = 'active' ORDER BY timestamp DESC
                """)
            else:
                cursor = conn.execute("""
                    SELECT file_type, original_name, username, file_size, timestamp, file_path, status
                    FROM user_files WHERE file_type = ? AND status = 'active' ORDER BY timestamp DESC
                """, (filter_type,))
            
            files = cursor.fetchall()
            conn.close()
        except:
            files = []
        
        files += self._scan_all_files(filter_type)
        
        if not files:
            ctk.CTkLabel(scroll, text="No documents found", 
                        font=("Inter", 14), text_color="#64748b").pack(pady=30)
        else:
            seen = set()
            unique_files = []
            for f in files:
                key = f[5] if len(f) > 5 else f[2]
                if key not in seen:
                    seen.add(key)
                    unique_files.append(f)
            
            for file_info in unique_files:
                self.create_doc_row(scroll, file_info)
    
    def _scan_all_files(self, filter_type):
        files = []
        
        sig_base = "storage/signatures"
        if os.path.exists(sig_base):
            for user_dir in os.listdir(sig_base):
                user_path = os.path.join(sig_base, user_dir)
                if os.path.isdir(user_path):
                    for f in os.listdir(user_path):
                        if f.endswith('.sig') or f.endswith('_signed.pdf'):
                            fpath = os.path.join(user_path, f)
                            if filter_type in ["all", "signed"]:
                                files.append(('signed', f, user_dir, os.path.getsize(fpath), 
                                            datetime.fromtimestamp(os.path.getmtime(fpath)).isoformat(),
                                            fpath, 'active'))
        
        enc_base = "storage/encrypted"
        if os.path.exists(enc_base):
            for user_dir in os.listdir(enc_base):
                user_path = os.path.join(enc_base, user_dir)
                if os.path.isdir(user_path):
                    for f in os.listdir(user_path):
                        if f.endswith('.bin'):
                            fpath = os.path.join(user_path, f)
                            if filter_type in ["all", "encrypted"]:
                                files.append(('encrypted', f, user_dir, os.path.getsize(fpath),
                                            datetime.fromtimestamp(os.path.getmtime(fpath)).isoformat(),
                                            fpath, 'active'))
        
        return files
    
    def create_doc_row(self, parent, file_info):
        file_type, original_name, username, file_size, timestamp, file_path, status = file_info
        
        row = ctk.CTkFrame(parent, fg_color="#0f172a", corner_radius=8)
        row.pack(fill="x", pady=3)
        
        icons = {"signed": "📝", "encrypted": "🔐", "cert": "🏛"}
        icon = icons.get(file_type, "📄")
        
        type_color = "#6366f1" if file_type == "signed" else "#f59e0b" if file_type == "encrypted" else "#10b981"
        
        ctk.CTkLabel(row, text=f"{icon} {file_type.upper()}", font=("Inter", 10, "bold"), 
                    text_color=type_color, width=80).pack(side="left", padx=10, pady=10)
        
        display_name = original_name[:35] + "..." if len(original_name) > 35 else original_name
        ctk.CTkLabel(row, text=display_name, font=("Inter", 11), 
                    text_color="#f8fafc", width=250).pack(side="left", padx=10)
        
        ctk.CTkLabel(row, text=username, font=("Inter", 11), 
                    text_color="#94a3b8", width=120).pack(side="left", padx=10)
        
        size_str = self._format_size(file_size) if isinstance(file_size, int) else str(file_size)
        ctk.CTkLabel(row, text=size_str, font=("Inter", 10), 
                    text_color="#64748b", width=100).pack(side="left", padx=10)
        
        date_str = timestamp[:10] if isinstance(timestamp, str) else str(timestamp)[:10]
        ctk.CTkLabel(row, text=date_str, font=("Inter", 10), 
                    text_color="#64748b", width=150).pack(side="left", padx=10)
        
        actions = ctk.CTkFrame(row, fg_color="transparent", width=250)
        actions.pack(side="left", padx=10)
        
        if os.path.exists(file_path):
            ctk.CTkButton(actions, text="👁 Open", width=60, height=28,
                         fg_color="#6366f1", hover_color="#4f46e5",
                         corner_radius=6, command=lambda p=file_path: self._open_file(p)).pack(side="left", padx=2)
            
            ctk.CTkButton(actions, text="⬇ Save", width=60, height=28,
                         fg_color="#10b981", hover_color="#059669",
                         corner_radius=6, command=lambda p=file_path, n=original_name: self._save_file(p, n)).pack(side="left", padx=2)
            
            ctk.CTkButton(actions, text="🗑", width=30, height=28,
                         fg_color="#ef4444", hover_color="#dc2626",
                         corner_radius=6, command=lambda p=file_path: self._delete_doc(p)).pack(side="left", padx=2)
    
    def filter_docs(self, filter_type):
        self.build_docs_table(filter_type)
    
    def _format_size(self, size):
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f} KB"
        else:
            return f"{size/(1024*1024):.1f} MB"
    
    def _open_file(self, file_path):
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "File not found!")
            return
        try:
            if os.name == 'nt':
                os.startfile(file_path)
            elif os.name == 'posix':
                import subprocess
                subprocess.run(['xdg-open', file_path], check=True)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open: {str(e)}")
    
    def _save_file(self, file_path, original_name):
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "File not found!")
            return
        from tkinter import filedialog
        save_path = filedialog.asksaveasfilename(
            defaultextension=os.path.splitext(original_name)[1],
            initialfile=original_name
        )
        if save_path:
            import shutil
            shutil.copy2(file_path, save_path)
            messagebox.showinfo("Success", f"Saved to:\n{save_path}")
    
    def _delete_doc(self, file_path):
        if messagebox.askyesno("Confirm", f"Delete this file?\n{os.path.basename(file_path)}"):
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                self.audit.delete_user_file("admin", file_path)
                self.switch_view("docs")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def show_settings(self):
        self.header_title.configure(text="System Settings")
        
        settings_frame = ctk.CTkFrame(self.content_frame, fg_color="#1e293b", corner_radius=12)
        settings_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(settings_frame, text="⚙️ System Settings", 
                    font=("Inter", 20, "bold"), text_color="#f8fafc").pack(pady=30)
        
        info_frame = ctk.CTkFrame(settings_frame, fg_color="#0f172a", corner_radius=10)
        info_frame.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(info_frame, text="📊 Database Info", 
                    font=("Inter", 16, "bold"), text_color="#6366f1").pack(anchor="w", padx=15, pady=(10, 5))
        
        try:
            conn = sqlite3.connect("storage/audit.db")
            total_logs = conn.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]
            total_files = conn.execute("SELECT COUNT(*) FROM user_files").fetchone()[0]
            conn.close()
            
            ctk.CTkLabel(info_frame, text=f"Total Audit Logs: {total_logs}", 
                        font=("Inter", 13), text_color="#f8fafc").pack(anchor="w", padx=15, pady=3)
            ctk.CTkLabel(info_frame, text=f"Total Tracked Files: {total_files}", 
                        font=("Inter", 13), text_color="#f8fafc").pack(anchor="w", padx=15, pady=3)
        except:
            ctk.CTkLabel(info_frame, text="Database info unavailable", 
                        font=("Inter", 13), text_color="#ef4444").pack(anchor="w", padx=15, pady=10)
        
        paths_frame = ctk.CTkFrame(settings_frame, fg_color="#0f172a", corner_radius=10)
        paths_frame.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(paths_frame, text="📁 Storage Paths", 
                    font=("Inter", 16, "bold"), text_color="#6366f1").pack(anchor="w", padx=15, pady=(10, 5))
        
        paths = [
            ("Signatures", "storage/signatures/"),
            ("Encrypted", "storage/encrypted/"),
            ("Certificates", "storage/certs/"),
            ("Keystores", "storage/keystores/"),
            ("Audit DB", "storage/audit.db"),
            ("Auth DB", "storage/auth.db"),
        ]
        
        for name, path in paths:
            exists = "✅" if os.path.exists(path) else "❌"
            ctk.CTkLabel(paths_frame, text=f"{exists} {name}: {path}", 
                        font=("Inter", 12), text_color="#94a3b8").pack(anchor="w", padx=15, pady=2)
        
        btn_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="🗑️ Clear All Logs", width=150, height=40,
                     font=("Inter", 12), fg_color="#ef4444", hover_color="#dc2626",
                     corner_radius=8, command=self.clear_all_logs).pack(side="left", padx=5)
        
        ctk.CTkButton(btn_frame, text="💾 Backup DB", width=150, height=40,
                     font=("Inter", 12), fg_color="#6366f1", hover_color="#4f46e5",
                     corner_radius=8, command=self.backup_db).pack(side="left", padx=5)
    
    def clear_all_logs(self):
        if messagebox.askyesno("⚠️ WARNING", "Clear ALL audit logs and file tracking?\n\nThis cannot be undone!"):
            try:
                conn = sqlite3.connect("storage/audit.db")
                conn.execute("DELETE FROM audit_log")
                conn.execute("DELETE FROM user_files")
                conn.commit()
                conn.close()
                self.audit.log(self.admin['username'], "ADMIN_CLEAR_ALL", "SUCCESS", details="All logs cleared")
                messagebox.showinfo("Cleared", "All logs and file tracking cleared!")
                self.switch_view("settings")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def backup_db(self):
        import shutil
        try:
            backup_dir = "storage/backups"
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            shutil.copy("storage/audit.db", f"{backup_dir}/audit_{timestamp}.db")
            shutil.copy("storage/auth.db", f"{backup_dir}/auth_{timestamp}.db")
            messagebox.showinfo("Backup Complete", f"Databases backed up to:\n{backup_dir}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def add_user(self):
        dialog = ctk.CTkInputDialog(title="Add New User", text="Enter username:")
        username = dialog.get_input()
        
        if username:
            password = simpledialog.askstring("Password", "Enter password:", show='*')
            if password:
                if len(password) < 6:
                    messagebox.showerror("Error", "Password must be at least 6 characters!")
                    return
                
                role_dialog = ctk.CTkInputDialog(title="Role", text="Enter role (admin/user):")
                role = role_dialog.get_input() or "user"
                
                success, msg = self.auth.register(username, password, role)
                if success:
                    self.audit.log(self.admin['username'], "ADMIN_ADD_USER", "SUCCESS", 
                                  details=f"Added: {username} ({role})")
                    messagebox.showinfo("Success", f"User '{username}' added!")
                    self.switch_view("users")
                else:
                    messagebox.showerror("Error", msg)
    
    def revoke_user(self, username):
        if messagebox.askyesno("Confirm", f"Revoke '{username}'?"):
            conn = sqlite3.connect(self.auth.db_path)
            conn.execute("UPDATE users SET status = 'revoked' WHERE username = ?", (username,))
            conn.commit()
            conn.close()
            from core.revocation import revoke_user
            revoke_user(username)
            self.audit.log(self.admin['username'], "ADMIN_REVOKE", "SUCCESS", details=f"Revoked: {username}")
            self.switch_view("users")
    
    def activate_user(self, username):
        conn = sqlite3.connect(self.auth.db_path)
        conn.execute("UPDATE users SET status = 'active' WHERE username = ?", (username,))
        conn.commit()
        conn.close()
        self.audit.log(self.admin['username'], "ADMIN_ACTIVATE", "SUCCESS", details=f"Activated: {username}")
        self.switch_view("users")
    
    def change_role(self, username, new_role):
        if messagebox.askyesno("Confirm", f"Change '{username}' to {new_role}?"):
            conn = sqlite3.connect(self.auth.db_path)
            conn.execute("UPDATE users SET role = ? WHERE username = ?", (new_role, username))
            conn.commit()
            conn.close()
            self.audit.log(self.admin['username'], "ADMIN_ROLE_CHANGE", "SUCCESS", details=f"{username} → {new_role}")
            self.switch_view("users")
    
    def delete_user(self, username):
        if messagebox.askyesno("⚠️ DANGER", f"PERMANENTLY delete '{username}'?"):
            conn = sqlite3.connect(self.auth.db_path)
            conn.execute("DELETE FROM users WHERE username = ?", (username,))
            conn.commit()
            conn.close()
            self.audit.log(self.admin['username'], "ADMIN_DELETE", "SUCCESS", details=f"Deleted: {username}")
            self.switch_view("users")
    
    def export_logs(self):
        import csv
        from datetime import datetime
        
        filepath = f"storage/audit_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            conn = sqlite3.connect("storage/audit.db")
            cursor = conn.execute("SELECT * FROM audit_log ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            conn.close()
            
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Timestamp', 'Username', 'Action', 'File', 'Hash', 'Result', 'Details', 'IP'])
                writer.writerows(rows)
            
            messagebox.showinfo("Export Complete", f"Logs saved to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
        # ✅ Go back to login screen
        from main import show_login
        show_login()