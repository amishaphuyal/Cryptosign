import customtkinter as ctk
from tkinter import messagebox, simpledialog
import sys
import os
import shutil
import sqlite3
from datetime import datetime, timedelta

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
            ("", "Certificate Management", "certs"),
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
        
        # SCROLLABLE CONTENT FRAME
        self.content_scroll = ctk.CTkScrollableFrame(self.main_content, fg_color="transparent")
        self.content_scroll.pack(fill="both", expand=True, padx=30, pady=10)
        
        self.content_frame = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)
    
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
            
            cursor.execute("""
                SELECT COUNT(*) FROM audit_log 
                WHERE action = 'DECRYPT' AND result = 'SUCCESS'
            """)
            decrypted_docs = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM audit_log 
                WHERE action = 'HASH' AND result = 'SUCCESS'
            """)
            hash_docs = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM audit_log 
                WHERE action LIKE 'ADMIN_%' AND result = 'SUCCESS'
            """)
            admin_actions = cursor.fetchone()[0]
            
            conn2 = sqlite3.connect(self.auth.db_path)
            cursor2 = conn2.cursor()
            cursor2.execute("SELECT COUNT(*) FROM users WHERE status IN ('blocked', 'suspended')")
            restricted_users = cursor2.fetchone()[0]
            conn2.close()
            
            conn.close()
            
        except Exception as e:
            print(f"Stats error: {e}")
            total_users = 0
            active_users = 0
            signed_docs = 0
            verified_docs = 0
            encrypted_docs = 0
            decrypted_docs = 0
            hash_docs = 0
            admin_actions = 0
            restricted_users = 0
        
        # Row 1 - User & Document Stats
        row1 = ctk.CTkFrame(stats_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        
        self.create_stat_card(row1, "👥 Total Users", str(total_users), 
                             f"{active_users} active", "#6366f1", "#3b82f6")
        self.create_stat_card(row1, "📝 Signed Documents", str(signed_docs), 
                             "All time", "#10b981", "#059669")
        self.create_stat_card(row1, "✅ Verified Documents", str(verified_docs), 
                             "All time", "#f59e0b", "#d97706")
        self.create_stat_card(row1, "🚫 Restricted Users", str(restricted_users), 
                             "Blocked / suspended", "#ef4444", "#dc2626")
        
        # Row 2 - Operation Stats
        row2 = ctk.CTkFrame(stats_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        
        self.create_stat_card(row2, "🔐 Encrypted", str(encrypted_docs), 
                             "All time", "#8b5cf6", "#7c3aed")
        self.create_stat_card(row2, "🔓 Decrypted", str(decrypted_docs), 
                             "All time", "#ec4899", "#db2777")
        self.create_stat_card(row2, "🔍 Hash Files", str(hash_docs), 
                             "All time", "#06b6d4", "#0891b2")
        self.create_stat_card(row2, " Admin Actions", str(admin_actions), 
                             "All time", "#f97316", "#ea580c")
        
        # BOTTOM SECTION - Recent Activities & Users
        bottom_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        bottom_frame.pack(fill="x", expand=True, pady=(10, 20))
        
        # Recent Activities (left)
        activities_frame = ctk.CTkFrame(bottom_frame, fg_color="#1e293b", corner_radius=12)
        activities_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(activities_frame, text="📈 Recent Activities", 
                    font=("Inter", 16, "bold"), text_color="#f8fafc").pack(anchor="w", padx=20, pady=(15, 10))
        
        activities_scroll = ctk.CTkScrollableFrame(activities_frame, fg_color="transparent", height=300)
        activities_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        try:
            conn = sqlite3.connect("storage/audit.db")
            cursor = conn.execute("""
                SELECT timestamp, username, action, file_name, result 
                FROM audit_log ORDER BY timestamp DESC LIMIT 15
            """)
            activities = cursor.fetchall()
            conn.close()
            
            for activity in activities:
                timestamp, username, action, file_name, result = activity
                self.create_activity_item(activities_scroll, username, action, file_name, timestamp, result)
        except:
            self.create_activity_item(activities_scroll, "System", "INIT", "No activities yet", "Now", "SUCCESS")
        
        # Recent Users (right)
        users_frame = ctk.CTkFrame(bottom_frame, fg_color="#1e293b", corner_radius=12)
        users_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        ctk.CTkLabel(users_frame, text="👥 Recent Users", 
                    font=("Inter", 16, "bold"), text_color="#f8fafc").pack(anchor="w", padx=20, pady=(15, 10))
        
        users_scroll = ctk.CTkScrollableFrame(users_frame, fg_color="transparent", height=300)
        users_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        try:
            conn = sqlite3.connect(self.auth.db_path)
            cursor = conn.execute("SELECT username, role, status, created_at FROM users ORDER BY created_at DESC LIMIT 10")
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
            "DECRYPT": "🔓", "SETUP": "⚙️", "USER_SET": "",
            "REVOKE": "❌", "HASH": "🔍", "ADMIN": "👑",
            "BATCH_SIGN": "📦", "ADMIN_ADD_USER": "➕",
            "ADMIN_REVOKE": "", "ADMIN_ACTIVATE": "✅",
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

        users = self.auth.get_all_users()
        total_users = len(users)
        active_users = sum(1 for user in users if user[2] == "active")
        blocked_users = sum(1 for user in users if user[2] == "blocked")
        suspended_users = sum(1 for user in users if user[2] == "suspended")
        admin_users = sum(1 for user in users if user[1] == "admin")

        # ===== HERO SECTION =====
        hero = ctk.CTkFrame(self.content_frame, fg_color="#111827", corner_radius=18)
        hero.pack(fill="x", pady=(0, 22))
        hero.grid_columnconfigure(0, weight=1)
        hero.grid_columnconfigure(1, weight=0)

        title_area = ctk.CTkFrame(hero, fg_color="transparent")
        title_area.grid(row=0, column=0, sticky="ew", padx=28, pady=24)

        ctk.CTkLabel(title_area, text=" Team Directory", font=("Inter", 28, "bold"),
                    text_color="#f8fafc").pack(anchor="w")
        ctk.CTkLabel(title_area,
                    text="Manage user accounts, assign administrative privileges, and control access levels across the organization.",
                    font=("Inter", 13), text_color="#94a3b8").pack(anchor="w", pady=(8, 0))

        action_area = ctk.CTkFrame(hero, fg_color="transparent")
        action_area.grid(row=0, column=1, sticky="e", padx=28, pady=24)

        ctk.CTkButton(action_area, text="➕ Add User", width=145, height=42,
                     font=("Inter", 13, "bold"), fg_color="#10b981", hover_color="#059669",
                     corner_radius=11, command=self.add_user).pack(side="left", padx=(0, 10))
        ctk.CTkButton(action_area, text="🔄 Refresh", width=125, height=42,
                     font=("Inter", 13, "bold"), fg_color="#6366f1", hover_color="#4f46e5",
                     corner_radius=11, command=lambda: self.switch_view("users")).pack(side="left")

        # ===== STATS ROW =====
        stats_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 22))
        self.create_stat_card(stats_frame, " Total Users", str(total_users), f"{admin_users} admins", "#6366f1", "#4f46e5")
        self.create_stat_card(stats_frame, "✅ Active", str(active_users), "Can login", "#10b981", "#059669")
        self.create_stat_card(stats_frame, "🚫 Blocked", str(blocked_users), "Access denied", "#ef4444", "#dc2626")
        self.create_stat_card(stats_frame, " Suspended", str(suspended_users), "Temporarily paused", "#f59e0b", "#d97706")

        # ===== TABLE CONTAINER =====
        table_frame = ctk.CTkFrame(self.content_frame, fg_color="#1e293b", corner_radius=18)
        table_frame.pack(fill="both", expand=True, pady=(0, 22))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(2, weight=1)

        # Table title
        table_top = ctk.CTkFrame(table_frame, fg_color="transparent")
        table_top.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 14))
        ctk.CTkLabel(table_top, text="All Users", font=("Inter", 22, "bold"),
                    text_color="#f8fafc").pack(side="left")
        ctk.CTkLabel(table_top, text="Role and status can be changed directly from each row.",
                    font=("Inter", 12), text_color="#94a3b8").pack(side="right")

        # ✅ FIXED HEADER SECTION START
        header_frame = ctk.CTkFrame(table_frame, fg_color="#334155", corner_radius=12, height=50)
        header_frame.grid(row=1, column=0, sticky="ew", padx=28, pady=(0, 8))
        header_frame.pack_propagate(False)
        
        # Column weights define width ratio
        header_frame.grid_columnconfigure(0, weight=3, minsize=200)   # User
        header_frame.grid_columnconfigure(1, weight=1, minsize=100)   # Role
        header_frame.grid_columnconfigure(2, weight=1, minsize=100)   # Status
        header_frame.grid_columnconfigure(3, weight=1, minsize=100)   # Created
        header_frame.grid_columnconfigure(4, weight=1, minsize=100)   # Last Login
        header_frame.grid_columnconfigure(5, weight=2, minsize=180)   # Actions

        headers = [
            ("User", 0), ("Role", 1), ("Status", 2), 
            ("Created", 3), ("Last Login", 4), ("Actions", 5)
        ]

        for text, col in headers:
            # Transparent wrapper ensures padding matches data cells exactly
            cell = ctk.CTkFrame(header_frame, fg_color="transparent")
            # Col 0 gets extra left padding (14), others get standard (10)
            pad_x = (14, 8) if col == 0 else (10, 10)
            cell.grid(row=0, column=col, sticky="w", padx=pad_x, pady=14)
            
            ctk.CTkLabel(cell, text=text, font=("Inter", 13, "bold"),
                        text_color="#e2e8f0", anchor="w").pack(anchor="w")
        # ✅ FIXED HEADER SECTION END

        # Scrollable Data Area
        scroll = ctk.CTkScrollableFrame(table_frame, fg_color="transparent", height=420)
        scroll.grid(row=2, column=0, sticky="nsew", padx=28, pady=(0, 24))

        if not users:
            empty = ctk.CTkFrame(scroll, fg_color="#0f172a", corner_radius=14)
            empty.pack(fill="x", pady=10, ipady=26)
            ctk.CTkLabel(empty, text="No users found", font=("Inter", 16, "bold"),
                        text_color="#f8fafc").pack(pady=(18, 4))
            ctk.CTkLabel(empty, text="Click Add User to create the first account.",
                        font=("Inter", 13), text_color="#94a3b8").pack(pady=(0, 18))
            return

        for user in users:
            self.create_user_row(scroll, user)

    # ✅ FIXED CREATE_USER_ROW METHOD START
    def create_user_row(self, parent, user):
        username, role, status, created, last_login = user
        status = status if status in ["active", "blocked", "suspended"] else "active"

        row = ctk.CTkFrame(parent, fg_color="#0f172a", corner_radius=10, height=56)
        row.pack(fill="x", pady=4)
        row.pack_propagate(False)

        # Exact same weights as header
        row.grid_columnconfigure(0, weight=3, minsize=200)
        row.grid_columnconfigure(1, weight=1, minsize=100)
        row.grid_columnconfigure(2, weight=1, minsize=100)
        row.grid_columnconfigure(3, weight=1, minsize=100)
        row.grid_columnconfigure(4, weight=1, minsize=100)
        row.grid_columnconfigure(5, weight=2, minsize=180)

        # --- Column 0: User ---
        user_cell = ctk.CTkFrame(row, fg_color="transparent")
        user_cell.grid(row=0, column=0, sticky="w", padx=(14, 8), pady=8)
        ctk.CTkLabel(user_cell, text=f" {username}", font=("Inter", 13, "bold"),
                    text_color="#f8fafc", anchor="w").pack(anchor="w")
        sub_text = "Current admin" if username == self.admin['username'] else "Managed account"
        ctk.CTkLabel(user_cell, text=sub_text, font=("Inter", 10), 
                    text_color="#64748b", anchor="w").pack(anchor="w")

        # --- Column 1: Role (Wrapped in transparent frame) ---
        role_cell = ctk.CTkFrame(row, fg_color="transparent")
        role_cell.grid(row=0, column=1, sticky="w", padx=10, pady=8)
        
        role_box = ctk.CTkOptionMenu(role_cell, values=["admin", "user"], width=110, height=32,
                                    font=("Inter", 11, "bold"), dropdown_font=("Inter", 11),
                                    fg_color="#1e293b", button_color="#6366f1", button_hover_color="#4f46e5",
                                    dropdown_fg_color="#1e293b", dropdown_hover_color="#334155",
                                    text_color="#f8fafc", corner_radius=8,
                                    command=lambda new_role, u=username: self.change_role(u, new_role))
        role_box.set(role if role in ["admin", "user"] else "user")
        role_box.pack(anchor="w")  # ✅ Pack inside wrapper instead of grid
        if username == self.admin['username']:
            role_box.configure(state="disabled")

        # --- Column 2: Status (Wrapped in transparent frame) ---
        status_cell = ctk.CTkFrame(row, fg_color="transparent")
        status_cell.grid(row=0, column=2, sticky="w", padx=10, pady=8)
        
        status_box = ctk.CTkOptionMenu(status_cell, values=["active", "blocked", "suspended"], 
                                      width=110, height=32,
                                      font=("Inter", 11, "bold"), dropdown_font=("Inter", 11),
                                      fg_color="#1e293b", button_color=self._status_color(status),
                                      button_hover_color=self._status_hover_color(status),
                                      dropdown_fg_color="#1e293b", dropdown_hover_color="#334155",
                                      text_color="#f8fafc", corner_radius=8,
                                      command=lambda new_status, u=username: self.change_status(u, new_status))
        status_box.set(status)
        status_box.pack(anchor="w")  # ✅ Pack inside wrapper instead of grid
        if username == self.admin['username']:
            status_box.configure(state="disabled")

        # --- Column 3: Created ---
        created_cell = ctk.CTkFrame(row, fg_color="transparent")
        created_cell.grid(row=0, column=3, sticky="w", padx=10, pady=8)
        ctk.CTkLabel(created_cell, text=self._format_date(created), font=("Inter", 11),
                    text_color="#cbd5e1", anchor="w").pack(anchor="w")

        # --- Column 4: Last Login ---
        login_cell = ctk.CTkFrame(row, fg_color="transparent")
        login_cell.grid(row=0, column=4, sticky="w", padx=10, pady=8)
        ctk.CTkLabel(login_cell, text=self._format_date(last_login), font=("Inter", 11),
                    text_color="#94a3b8", anchor="w").pack(anchor="w")

        # --- Column 5: Actions ---
        actions = ctk.CTkFrame(row, fg_color="transparent")
        actions.grid(row=0, column=5, sticky="w", padx=(10, 14), pady=8)

        ctk.CTkButton(actions, text="✏️ Edit", width=70, height=30,
                     font=("Inter", 11, "bold"), fg_color="#0ea5e9", hover_color="#0284c7",
                     corner_radius=8, command=lambda u=username: self.edit_user(u)).pack(side="left", padx=(0, 6))

        if username != self.admin['username']:
            ctk.CTkButton(actions, text="🗑 Delete", width=80, height=30,
                         font=("Inter", 11, "bold"), fg_color="#ef4444", hover_color="#dc2626",
                         corner_radius=8, command=lambda u=username: self.delete_user(u)).pack(side="left")
        else:
            ctk.CTkLabel(actions, text="Protected", font=("Inter", 11, "bold"),
                        text_color="#94a3b8", width=80).pack(side="left")
    # ✅ FIXED CREATE_USER_ROW METHOD END

    def _status_color(self, status):
        return {"active": "#10b981", "blocked": "#ef4444", "suspended": "#f59e0b"}.get(status, "#64748b")

    def _status_hover_color(self, status):
        return {"active": "#059669", "blocked": "#dc2626", "suspended": "#d97706"}.get(status, "#475569")

    def _format_date(self, value):
        if not value:
            return "N/A"
        return str(value)[:10]

    def show_logs(self):
        self.header_title.configure(text="Audit Logs")
        
        toolbar = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 15))
        
        ctk.CTkButton(toolbar, text=" Export CSV", width=120, height=35,
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
        
        ctk.CTkButton(toolbar, text=" View CA Cert", width=140, height=35,
                     font=("Inter", 12), fg_color="#10b981", hover_color="#059669",
                     corner_radius=8, command=self.view_ca_cert).pack(side="left", padx=5)
        
        stats_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 15))
        
        cert_count = 0
        ca_exists = os.path.exists("storage/ca/ca_cert.pem")
        if os.path.exists("storage/certs"):
            cert_count = len([f for f in os.listdir("storage/certs") if f.endswith("_cert.pem")])
        
        self.create_stat_card(stats_frame, " CA Certificate", "Active" if ca_exists else "Missing", 
                             "Root authority", "#10b981", "#059669")
        self.create_stat_card(stats_frame, " User Certs", str(cert_count), 
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
        
        ctk.CTkButton(actions, text=" Download", width=80, height=28,
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
        
        self.create_stat_card(stats_frame, " Signed", str(signed_count), 
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
        icon = icons.get(file_type, "")
        
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
            
            ctk.CTkButton(actions, text=" Save", width=60, height=28,
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

                    # Clean up empty parent folder
                    parent_dir = os.path.dirname(file_path)
                    if os.path.exists(parent_dir) and not os.listdir(parent_dir):
                        os.rmdir(parent_dir)
                        print(f"✅ Removed empty folder: {parent_dir}")

                        # Also check grandparent (user folder)
                        grandparent = os.path.dirname(parent_dir)
                        if os.path.exists(grandparent) and not os.listdir(grandparent):
                            os.rmdir(grandparent)
                            print(f"✅ Removed empty user folder: {grandparent}")

                self.audit.delete_user_file("admin", file_path)
                self.switch_view("docs")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def show_settings(self):
        self.header_title.configure(text="System Settings")
        
        settings_frame = ctk.CTkFrame(self.content_frame, fg_color="#1e293b", corner_radius=12)
        settings_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(settings_frame, text="️ System Settings", 
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
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Add User")
        dialog.geometry("430x560")
        dialog.configure(fg_color="#0f172a")
        dialog.grab_set()
        dialog.resizable(False, False)

        ctk.CTkLabel(dialog, text="➕ Add New User", font=("Inter", 20, "bold"),
                    text_color="#f8fafc").pack(pady=(16, 4))
        ctk.CTkLabel(dialog, text="Create an account with role and access status.",
                    font=("Inter", 12), text_color="#94a3b8").pack(pady=(0, 10))

        form = ctk.CTkFrame(dialog, fg_color="#1e293b", corner_radius=14)
        form.pack(fill="x", padx=24, pady=(0, 12))

        ctk.CTkLabel(form, text="Username", font=("Inter", 12, "bold"),
                    text_color="#cbd5e1").pack(anchor="w", padx=18, pady=(18, 4))
        username_entry = ctk.CTkEntry(form, height=36, placeholder_text="Enter username")
        username_entry.pack(fill="x", padx=18)

        ctk.CTkLabel(form, text="Password", font=("Inter", 12, "bold"),
                    text_color="#cbd5e1").pack(anchor="w", padx=18, pady=(14, 4))
        password_entry = ctk.CTkEntry(form, height=36, placeholder_text="Minimum 8 characters", show="*")
        password_entry.pack(fill="x", padx=18)

        ctk.CTkLabel(form, text="Role", font=("Inter", 12, "bold"),
                    text_color="#cbd5e1").pack(anchor="w", padx=18, pady=(14, 4))
        role_menu = ctk.CTkOptionMenu(form, values=["user", "admin"], height=36,
                                     fg_color="#0f172a", button_color="#6366f1", button_hover_color="#4f46e5")
        role_menu.set("user")
        role_menu.pack(fill="x", padx=18)

        ctk.CTkLabel(form, text="Status", font=("Inter", 12, "bold"),
                    text_color="#cbd5e1").pack(anchor="w", padx=18, pady=(14, 4))
        status_menu = ctk.CTkOptionMenu(form, values=["active", "blocked", "suspended"], height=36,
                                       fg_color="#0f172a", button_color="#10b981", button_hover_color="#059669")
        status_menu.set("active")
        status_menu.pack(fill="x", padx=18)

        buttons = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons.pack(fill="x", padx=24, pady=(0, 18), side="bottom")

        def save_user():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            role = role_menu.get()
            status = status_menu.get()

            if not username:
                messagebox.showerror("Error", "Username is required!", parent=dialog)
                return
            if not password or len(password) < 8:
                messagebox.showerror("Error", "Password must be at least 8 characters!", parent=dialog)
                return

            success, msg = self.auth.register(username, password, role)
            if not success:
                messagebox.showerror("Error", msg, parent=dialog)
                return

            self.change_status(username, status, refresh=False, silent=True)
            self.audit.log(self.admin['username'], "ADMIN_ADD_USER", "SUCCESS",
                          details=f"Added: {username} ({role}, {status})")
            dialog.destroy()
            messagebox.showinfo("Success", f"User '{username}' added successfully!")
            self.switch_view("users")

        ctk.CTkButton(buttons, text="Cancel", height=40, fg_color="#475569", hover_color="#334155",
                     font=("Inter", 12, "bold"), command=dialog.destroy).pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(buttons, text="✅ Add User", height=40, fg_color="#10b981", hover_color="#059669",
                     font=("Inter", 12, "bold"), command=save_user).pack(side="left", fill="x", expand=True, padx=(6, 0))

    def edit_user(self, username):
        user = self.auth.get_user(username)
        if not user:
            messagebox.showerror("Error", "User not found!")
            return

        current_username, current_role, current_status, _ = user
        current_status = current_status if current_status in ["active", "blocked", "suspended"] else "active"

        dialog = ctk.CTkToplevel(self.root)
        dialog.title(f"Edit User - {username}")
        dialog.geometry("430x590")
        dialog.configure(fg_color="#0f172a")
        dialog.grab_set()
        dialog.resizable(False, False)

        ctk.CTkLabel(dialog, text="✏️ Edit User", font=("Inter", 20, "bold"),
                    text_color="#f8fafc").pack(pady=(16, 4))
        ctk.CTkLabel(dialog, text="Update username, role, status or reset password.",
                    font=("Inter", 12), text_color="#94a3b8").pack(pady=(0, 10))

        form = ctk.CTkFrame(dialog, fg_color="#1e293b", corner_radius=14)
        form.pack(fill="x", padx=24, pady=(0, 12))

        ctk.CTkLabel(form, text="Username", font=("Inter", 12, "bold"),
                    text_color="#cbd5e1").pack(anchor="w", padx=18, pady=(18, 4))
        username_entry = ctk.CTkEntry(form, height=36)
        username_entry.insert(0, current_username)
        username_entry.pack(fill="x", padx=18)
        if current_username == self.admin['username']:
            username_entry.configure(state="disabled")

        ctk.CTkLabel(form, text="New Password (optional)", font=("Inter", 12, "bold"),
                    text_color="#cbd5e1").pack(anchor="w", padx=18, pady=(14, 4))
        password_entry = ctk.CTkEntry(form, height=36, placeholder_text="Leave empty to keep current password (min 8 chars)", show="*")
        password_entry.pack(fill="x", padx=18)

        ctk.CTkLabel(form, text="Role", font=("Inter", 12, "bold"),
                    text_color="#cbd5e1").pack(anchor="w", padx=18, pady=(14, 4))
        role_menu = ctk.CTkOptionMenu(form, values=["user", "admin"], height=36,
                                     fg_color="#0f172a", button_color="#6366f1", button_hover_color="#4f46e5")
        role_menu.set(current_role if current_role in ["admin", "user"] else "user")
        role_menu.pack(fill="x", padx=18)
        if current_username == self.admin['username']:
            role_menu.configure(state="disabled")

        ctk.CTkLabel(form, text="Status", font=("Inter", 12, "bold"),
                    text_color="#cbd5e1").pack(anchor="w", padx=18, pady=(14, 4))
        status_menu = ctk.CTkOptionMenu(form, values=["active", "blocked", "suspended"], height=36,
                                       fg_color="#0f172a", button_color=self._status_color(current_status),
                                       button_hover_color=self._status_hover_color(current_status))
        status_menu.set(current_status)
        status_menu.pack(fill="x", padx=18)
        if current_username == self.admin['username']:
            status_menu.configure(state="disabled")

        buttons = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons.pack(fill="x", padx=24, pady=(0, 18), side="bottom")

        def save_changes():
            new_username = username_entry.get().strip() if current_username != self.admin['username'] else current_username
            new_password = password_entry.get().strip()
            new_role = role_menu.get()
            new_status = status_menu.get()

            if not new_username:
                messagebox.showerror("Error", "Username is required!", parent=dialog)
                return
            if new_password and len(new_password) < 8:
                messagebox.showerror("Error", "Password must be at least 8 characters!", parent=dialog)
                return

            try:
                conn = sqlite3.connect(self.auth.db_path)
                if new_username != current_username:
                    exists = conn.execute("SELECT 1 FROM users WHERE username = ?", (new_username,)).fetchone()
                    if exists:
                        conn.close()
                        messagebox.showerror("Error", "Username already exists!", parent=dialog)
                        return

                if new_password:
                    conn.execute("""
                        UPDATE users
                        SET username = ?, password_hash = ?, role = ?, status = ?
                        WHERE username = ?
                    """, (new_username, self.auth._hash(new_password), new_role, new_status, current_username))
                else:
                    conn.execute("""
                        UPDATE users
                        SET username = ?, role = ?, status = ?
                        WHERE username = ?
                    """, (new_username, new_role, new_status, current_username))
                conn.commit()
                conn.close()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=dialog)
                return

            self.audit.log(self.admin['username'], "ADMIN_EDIT_USER", "SUCCESS",
                          details=f"Edited: {current_username} → {new_username} ({new_role}, {new_status})")
            dialog.destroy()
            messagebox.showinfo("Success", f"User '{new_username}' updated successfully!")
            self.switch_view("users")

        ctk.CTkButton(buttons, text="Cancel", height=40, fg_color="#475569", hover_color="#334155",
                     font=("Inter", 12, "bold"), command=dialog.destroy).pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(buttons, text="✅ Save Changes", height=40, fg_color="#0ea5e9", hover_color="#0284c7",
                     font=("Inter", 12, "bold"), command=save_changes).pack(side="left", fill="x", expand=True, padx=(6, 0))

    def change_status(self, username, new_status, refresh=True, silent=False):
        if new_status not in ["active", "blocked", "suspended"]:
            messagebox.showerror("Error", "Invalid status selected!")
            return
        if username == self.admin['username'] and new_status != "active":
            messagebox.showerror("Protected", "You cannot block or suspend the currently logged-in admin.")
            return

        if not silent and not messagebox.askyesno("Confirm Status Change", f"Change '{username}' status to {new_status}?"):
            if refresh:
                self.switch_view("users")
            return

        conn = sqlite3.connect(self.auth.db_path)
        conn.execute("UPDATE users SET status = ? WHERE username = ?", (new_status, username))
        conn.commit()
        conn.close()
        self.audit.log(self.admin['username'], "ADMIN_STATUS_CHANGE", "SUCCESS", details=f"{username} → {new_status}")
        if refresh:
            self.switch_view("users")

    def activate_user(self, username):
        self.change_status(username, "active")

    def revoke_user(self, username):
        self.change_status(username, "blocked")

    def change_role(self, username, new_role):
        if new_role not in ["admin", "user"]:
            messagebox.showerror("Error", "Invalid role selected!")
            return
        if username == self.admin['username']:
            messagebox.showerror("Protected", "You cannot change your own admin role while logged in.")
            self.switch_view("users")
            return

        if messagebox.askyesno("Confirm Role Change", f"Change '{username}' role to {new_role}?"):
            conn = sqlite3.connect(self.auth.db_path)
            conn.execute("UPDATE users SET role = ? WHERE username = ?", (new_role, username))
            conn.commit()
            conn.close()
            self.audit.log(self.admin['username'], "ADMIN_ROLE_CHANGE", "SUCCESS", details=f"{username} → {new_role}")
        self.switch_view("users")

    def delete_user(self, username):
        if username == self.admin['username']:
            messagebox.showerror("Protected", "You cannot delete the currently logged-in admin account.")
            return

        if messagebox.askyesno("⚠️ Delete User", f"Permanently delete '{username}'?\n\nThis removes the user account and related files."):
            conn = sqlite3.connect(self.auth.db_path)
            conn.execute("DELETE FROM users WHERE username = ?", (username,))
            conn.commit()
            conn.close()

            for folder in [
                f"storage/encrypted/{username}",
                f"storage/signatures/{username}",
            ]:
                if os.path.exists(folder):
                    try:
                        shutil.rmtree(folder)
                        print(f"✅ Deleted folder: {folder}")
                    except Exception as e:
                        print(f"⚠️ Could not delete folder {folder}: {e}")

            for file_path in [
                f"storage/keystores/{username}_private.pem",
                f"storage/keystores/{username}_public.pem",
                f"storage/certs/{username}_cert.pem",
            ]:
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        print(f"✅ Deleted file: {file_path}")
                    except Exception as e:
                        print(f"⚠️ Could not delete file {file_path}: {e}")

            try:
                conn = sqlite3.connect("storage/audit.db")
                conn.execute("DELETE FROM audit_log WHERE username = ?", (username,))
                conn.execute("DELETE FROM user_files WHERE username = ?", (username,))
                conn.execute("DELETE FROM user_activity WHERE username = ?", (username,))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"⚠️ Could not clean audit data: {e}")

            self.audit.log(self.admin['username'], "ADMIN_DELETE", "SUCCESS", details=f"Deleted: {username}")
            messagebox.showinfo("Deleted", f"User '{username}' deleted successfully!")
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