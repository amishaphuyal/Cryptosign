import customtkinter as ctk
from tkinter import messagebox, simpledialog
import sys
import os
import shutil
import sqlite3
import json
from datetime import datetime, timedelta
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.auth_system import AuthSystem
from core.audit_logger import AuditLogger
from core.revocation import is_revoked
from core.ca_engine import create_root_ca, load_ca_private_key
from core.key_manager import generate_key_pair
from core.cert_manager import issue_certificate


class AdminDashboard:
    def __init__(self, root, admin_user):
        self.root = root
        self.admin = admin_user
        self.auth = AuthSystem()
        self.audit = AuditLogger()
        self.ui_settings = self._load_ui_settings()
        self.is_light_mode = self.ui_settings.get("theme", "dark") == "light"
        self.P = self._palette()
        ctk.set_appearance_mode("light" if self.is_light_mode else "dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.root.title("CryptoSign - Admin Dashboard")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)
        self.root.configure(fg_color=self.P["bg"])
        
        self.current_view = "dashboard"
        self.build_sidebar()
        self.build_main_content()
        self.show_dashboard()
        self._apply_theme_to_tree(self.root)
    

    # ---------------- ADMIN UI THEME HELPERS ----------------
    def _settings_file(self):
        return f"storage/settings/{self.admin.get('username', 'admin')}_admin_ui_settings.json"

    def _load_ui_settings(self):
        default = {"theme": "dark", "compact_rows": False, "admin_notifications": True}
        try:
            os.makedirs("storage/settings", exist_ok=True)
            path = self._settings_file()
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                default.update(data if isinstance(data, dict) else {})
        except Exception as e:
            print(f"Admin settings load warning: {e}")
        return default

    def _save_ui_settings(self):
        try:
            os.makedirs("storage/settings", exist_ok=True)
            with open(self._settings_file(), "w", encoding="utf-8") as f:
                json.dump(self.ui_settings, f, indent=2)
        except Exception as e:
            print(f"Admin settings save warning: {e}")

    def _palette(self):
        if getattr(self, "is_light_mode", False):
            return {
                "bg": "#f8fafc",
                "sidebar": "#e8eef6",
                "card": "#ffffff",
                "card_alt": "#f1f5f9",
                "row": "#ffffff",
                "row_alt": "#f8fafc",
                "border": "#cbd5e1",
                "text": "#0f172a",
                "text_2": "#334155",
                "muted": "#64748b",
                "accent": "#6366f1",
                "accent_hover": "#4f46e5",
                "success": "#10b981",
                "danger": "#ef4444",
                "warning": "#f59e0b",
                "info": "#0ea5e9",
                "header": "#e2e8f0",
                "danger_bg": "#fff1f2",
                "danger_border": "#fecdd3",
            }
        return {
            "bg": "#0a0e1a", "sidebar": "#111827", "card": "#111827",
            "card_alt": "#0b1220", "row": "#0a0e1a", "row_alt": "#0f172a",
            "border": "#243044", "text": "#f8fafc", "text_2": "#cbd5e1",
            "muted": "#94a3b8", "accent": "#6366f1", "accent_hover": "#4f46e5",
            "success": "#10b981", "danger": "#ef4444", "warning": "#f59e0b",
            "info": "#38bdf8", "header": "#1e293b", "danger_bg": "#160b14",
            "danger_border": "#7f1d1d"
        }

    def _shorten(self, value, limit=46):
        value = "-" if value is None or value == "" else str(value)
        return value if len(value) <= limit else value[: max(0, limit - 3)] + "..."

    def _set_admin_theme(self, mode):
        self.ui_settings["theme"] = mode
        self.is_light_mode = mode == "light"
        self.P = self._palette()
        self._save_ui_settings()
        ctk.set_appearance_mode("light" if self.is_light_mode else "dark")
        self._rebuild_admin_shell()

    def _rebuild_admin_shell(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.configure(fg_color=self.P["bg"])
        self.build_sidebar()
        self.build_main_content()
        self.switch_view(self.current_view)
        self._apply_theme_to_tree(self.root)

    def _apply_theme_to_tree(self, widget=None):
        """Force every admin page to use readable light-mode colors.
        The old admin dashboard had many hardcoded dark colors (#111827, #f8fafc, etc.).
        In light mode those values caused white text on white cards or black cards mixed
        with light cards. This remaps both backgrounds and text colors safely.
        """
        if widget is None:
            widget = self.root
        if not getattr(self, "is_light_mode", False):
            return

        P = self.P

        old_dark_bg = {
            "#020617": P["bg"],
            "#030712": P["bg"],
            "#0a0e1a": P["bg"],
            "#0b1120": P["bg"],
            "#0b1220": P["card_alt"],
            "#0b1222": P["card_alt"],
            "#0f172a": P["row_alt"],
            "#111827": P["card"],
            "#162033": P["card"],
            "#172033": P["card"],
            "#1e293b": P["header"],
            "#1f2937": P["header"],
            "#243044": P["border"],
            "#273449": P["border"],
        }

        old_dark_text = {
            "#f8fafc": P["text"],
            "#ffffff": P["text"],
            "white": P["text"],
            "#e2e8f0": P["text_2"],
            "#cbd5e1": P["text_2"],
            "#94a3b8": P["muted"],
            "#64748b": P["muted"],
        }

        brand_or_status = {
            "#6366f1", "#4f46e5", "#10b981", "#059669", "#ef4444", "#dc2626",
            "#f59e0b", "#d97706", "#0ea5e9", "#38bdf8", "#06b6d4", "#0891b2",
            "#8b5cf6", "#a78bfa", "#ec4899", "#db2777", "#f97316", "#ea580c",
        }

        def first_color(value):
            if isinstance(value, (list, tuple)) and value:
                return first_color(value[0])
            return value

        def lower(value):
            value = first_color(value)
            return value.lower() if isinstance(value, str) else value

        def rgb(hex_value):
            if not isinstance(hex_value, str) or not hex_value.startswith("#"):
                return None
            h = hex_value.lstrip("#")
            if len(h) == 3:
                h = "".join(ch * 2 for ch in h)
            if len(h) != 6:
                return None
            try:
                return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
            except Exception:
                return None

        def luminance(hex_value):
            c = rgb(hex_value)
            if not c:
                return None
            r, g, b = c
            return (0.2126 * r) + (0.7152 * g) + (0.0722 * b)

        def map_bg(value, fallback=None):
            c = lower(value)
            if c in (None, "transparent"):
                return value
            if c in old_dark_bg:
                return old_dark_bg[c]
            lum = luminance(c)
            if lum is not None and lum < 90:
                return fallback or P["card"]
            return value

        def map_border(value):
            c = lower(value)
            if c in (None, "transparent"):
                return value
            if c in old_dark_bg:
                return P["border"]
            lum = luminance(c)
            if lum is not None and lum < 130:
                return P["border"]
            return value

        def map_text(value, default=P["text"]):
            c = lower(value)
            if c in (None, "transparent"):
                return default
            if c in brand_or_status:
                return c
            if c in old_dark_text:
                return old_dark_text[c]
            lum = luminance(c)
            if lum is not None:
                # Light text from dark mode becomes invisible on light cards.
                if lum > 185:
                    return default
                return c
            # CTk named defaults like gray10/gray90 can be inconsistent after mode switching.
            if isinstance(c, str) and ("gray" in c or "grey" in c):
                return default
            return default

        try:
            if isinstance(widget, ctk.CTkScrollableFrame):
                current = getattr(widget, "_fg_color", None)
                # In light mode, CTkScrollableFrame with transparent fg can keep a dark internal canvas.
                # Force the scroll body to a readable light surface.
                target_bg = P["card"] if lower(current) in (None, "transparent") else map_bg(current, P["card"])
                widget.configure(fg_color=target_bg)
                if hasattr(widget, "_border_color"):
                    widget.configure(border_color=map_border(getattr(widget, "_border_color", None)))
                try:
                    widget._parent_canvas.configure(bg=target_bg, highlightthickness=0)
                except Exception:
                    pass
                try:
                    widget._scrollbar.configure(fg_color=target_bg, button_color="#94a3b8", button_hover_color="#64748b")
                except Exception:
                    pass
            elif isinstance(widget, ctk.CTkFrame):
                current = getattr(widget, "_fg_color", None)
                if current != "transparent":
                    widget.configure(fg_color=map_bg(current, P["card"]))
                if hasattr(widget, "_border_color"):
                    widget.configure(border_color=map_border(getattr(widget, "_border_color", None)))
            elif isinstance(widget, ctk.CTkLabel):
                current = getattr(widget, "_text_color", None)
                widget.configure(text_color=map_text(current))
            elif isinstance(widget, ctk.CTkButton):
                fg = lower(getattr(widget, "_fg_color", None))
                hover = getattr(widget, "_hover_color", None)
                txt = getattr(widget, "_text_color", None)
                if fg == "transparent":
                    widget.configure(text_color=P["text_2"], hover_color=P["card_alt"])
                elif fg in brand_or_status:
                    widget.configure(text_color="white")
                else:
                    widget.configure(
                        fg_color=map_bg(fg, P["card_alt"]),
                        hover_color=map_bg(hover, P["header"]),
                        text_color=map_text(txt, P["text"]),
                    )
            elif isinstance(widget, (ctk.CTkEntry, ctk.CTkTextbox)):
                widget.configure(fg_color=P["card"], text_color=P["text"], border_color=P["border"])
            elif isinstance(widget, ctk.CTkSwitch):
                widget.configure(
                    text_color=P["text"],
                    progress_color=P["accent"],
                    button_color="#64748b",
                    button_hover_color="#475569",
                )
            elif isinstance(widget, ctk.CTkOptionMenu):
                widget.configure(
                    fg_color=P["card_alt"],
                    text_color=P["text"],
                    button_color=P["accent"],
                    button_hover_color=P["accent_hover"],
                )
        except Exception:
            pass

        try:
            for child in widget.winfo_children():
                self._apply_theme_to_tree(child)
        except Exception:
            pass

    def build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self.root, fg_color=self.P["sidebar"], width=260, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=100)
        logo_frame.pack(fill="x", pady=(20, 10))
        
        ctk.CTkLabel(logo_frame, text="🔐", font=("Inter", 40)).pack()
        ctk.CTkLabel(logo_frame, text="CryptoSign", font=("Inter", 18, "bold"), 
                    text_color="#6366f1").pack()
        ctk.CTkLabel(logo_frame, text="Secure Digital Document Signing", 
                    font=("Inter", 11), text_color="#64748b").pack()
        
        ctk.CTkFrame(self.sidebar, fg_color="#1e293b", height=1).pack(fill="x", padx=20, pady=15)
        
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
                               fg_color="transparent", hover_color="#1e293b",
                               text_color="#94a3b8", anchor="w",
                               corner_radius=10, command=lambda v=view: self.switch_view(v))
            btn.pack(fill="x", padx=12, pady=3)
            self.menu_buttons[view] = btn
        
        ctk.CTkFrame(self.sidebar, fg_color="#1e293b", height=1).pack(fill="x", padx=20, pady=15)
        
        user_frame = ctk.CTkFrame(self.sidebar, fg_color="#0a0e1a", corner_radius=10)
        user_frame.pack(fill="x", padx=12, pady=10)

        ctk.CTkLabel(user_frame, text=f"👤 {self.admin['username']}", 
                    font=("Inter", 13, "bold"), text_color="#f8fafc").pack(pady=(10, 2))
        ctk.CTkLabel(user_frame, text="Super Administrator", 
                    font=("Inter", 11), text_color="#64748b").pack(pady=(0, 10))
        
        ctk.CTkButton(self.sidebar, text="🚪  Logout", 
                     font=("Inter", 13, "bold"), height=44,
                     fg_color="#ef4444", hover_color="#dc2626",
                     text_color="white", corner_radius=10,
                     command=self.logout).pack(fill="x", padx=12, pady=20)
    
    def build_main_content(self):
        self.main_content = ctk.CTkFrame(self.root, fg_color=self.P["bg"], corner_radius=0)
        self.main_content.pack(side="right", fill="both", expand=True)
        
        self.header = ctk.CTkFrame(self.main_content, fg_color="transparent", height=70)
        self.header.pack(fill="x", padx=30, pady=(20, 10))
        self.header.pack_propagate(False)
        
        self.header_title = ctk.CTkLabel(self.header, text="Dashboard", 
                                        font=("Inter", 26, "bold"), text_color=self.P["text"])
        self.header_title.pack(side="left")
        
        self.refresh_btn = ctk.CTkButton(self.header, text="🔄 Refresh", width=110, height=38,
                     font=("Inter", 12), fg_color="#6366f1", hover_color="#4f46e5",
                     text_color="white", corner_radius=10,
                     command=self.refresh_current_view)
        self.refresh_btn.pack(side="right", padx=5)
        
        self._create_notification_assets()
        self.notification_btn = ctk.CTkButton(
            self.header,
            text=self.get_notification_text(),
            image=self.notification_icon,
            compound="left",
            width=76,
            height=42,
            font=("Inter", 13, "bold"),
            fg_color="#111827",
            hover_color="#1e293b",
            text_color="#fca5a5" if self.get_pending_count() > 0 else "#94a3b8",
            corner_radius=12,
            command=self.show_pending_notifications
        )
        self.notification_btn.pack(side="right", padx=5)
        
        # Accent line
        accent_line = ctk.CTkFrame(self.main_content, fg_color="#6366f1", height=2)
        accent_line.pack(fill="x", padx=30, pady=(0, 15))
        
        # CONTENT FRAME - full height (no page-level scrollbar)
        self.content_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=30, pady=10)

    def _create_notification_assets(self):
        """Create a small red SVG-style bell icon using PIL/CTkImage."""
        try:
            os.makedirs("storage/ui", exist_ok=True)
            icon_path = "storage/ui/notification_red.png"
            if not os.path.exists(icon_path):
                img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                red = (239, 68, 68, 255)
                red_dark = (185, 28, 28, 255)
                # bell dome
                draw.arc((16, 14, 48, 48), 200, -20, fill=red, width=5)
                draw.line((16, 34, 16, 45), fill=red, width=5)
                draw.line((48, 34, 48, 45), fill=red, width=5)
                draw.line((14, 45, 50, 45), fill=red, width=5)
                draw.ellipse((27, 49, 37, 59), fill=red_dark)
                draw.line((32, 8, 32, 15), fill=red, width=5)
                img.save(icon_path)
            self.notification_icon = ctk.CTkImage(
                light_image=Image.open(icon_path),
                dark_image=Image.open(icon_path),
                size=(18, 18)
            )
        except Exception as e:
            print(f"Notification icon error: {e}")
            self.notification_icon = None

    def get_pending_count(self):
        try:
            conn = sqlite3.connect(self.auth.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE status = 'pending'")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            print(f"Pending count error: {e}")
            return 0

    def get_notification_text(self):
        if not self.ui_settings.get("admin_notifications", True):
            return ""
        count = self.get_pending_count()
        return str(count) if count > 0 else ""

    def refresh_notification(self):
        if hasattr(self, "notification_btn"):
            count = self.get_pending_count() if self.ui_settings.get("admin_notifications", True) else 0
            self.notification_btn.configure(
                text=str(count) if count > 0 else "",
                text_color=self.P["danger"] if count > 0 else self.P["muted"],
                fg_color=self.P["card_alt"] if count > 0 else self.P["card"]
            )

    def show_pending_notifications(self):
        try:
            conn = sqlite3.connect(self.auth.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT username, role, created_at
                FROM users
                WHERE status = 'pending'
                ORDER BY created_at DESC
            """)
            pending_users = cursor.fetchall()
            conn.close()
        except Exception as e:
            messagebox.showerror("Notification Error", str(e))
            return

        if not pending_users:
            messagebox.showinfo("Notifications", "No pending user approval requests.")
            return

        msg = "Pending user approval requests:\n\n"
        for username, role, created_at in pending_users:
            date_text = created_at[:10] if created_at else "N/A"
            msg += f"• {username} ({role}) - Registered: {date_text}\n"

        msg += "\nOpening User Management so you can approve or block them."
        messagebox.showinfo("Pending Requests", msg)
        self.switch_view("users")

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

        self._apply_theme_to_tree(self.root)
    
    def refresh_current_view(self):
        self.refresh_btn.configure(text="⏳ Refreshing...")
        self.root.update()

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if self.current_view == "dashboard":
            self.show_dashboard()
        elif self.current_view == "users":
            self.show_users()
        elif self.current_view == "logs":
            self.show_logs()
        elif self.current_view == "certs":
            self.show_certificates()
        elif self.current_view == "revoked":
            self.show_revoked()
        elif self.current_view == "docs":
            self.show_documents()
        elif self.current_view == "settings":
            self.show_settings()

        self.refresh_btn.configure(text="🔄 Refresh")
        self.refresh_notification()
        self._apply_theme_to_tree(self.root)
        self.root.update()

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
        
        # BOTTOM SECTION - Recent Activities & Users - fills remaining space
        bottom_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        bottom_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        # Recent Activities (left)
        activities_frame = ctk.CTkFrame(bottom_frame, fg_color="#111827", corner_radius=12)
        activities_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(activities_frame, text="📈 Recent Activities", 
                    font=("Inter", 16, "bold"), text_color="#f8fafc").pack(anchor="w", padx=20, pady=(15, 10))
        
        activities_scroll = ctk.CTkScrollableFrame(activities_frame, fg_color="transparent")
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
        users_frame = ctk.CTkFrame(bottom_frame, fg_color="#111827", corner_radius=12)
        users_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        ctk.CTkLabel(users_frame, text="👥 Recent Users", 
                    font=("Inter", 16, "bold"), text_color="#f8fafc").pack(anchor="w", padx=20, pady=(15, 10))
        
        users_scroll = ctk.CTkScrollableFrame(users_frame, fg_color="transparent")
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
        P = self.P
        card = ctk.CTkFrame(parent, fg_color=P["card_alt"], corner_radius=12, width=250, border_width=1, border_color=P["border"])
        card.pack(side="left", expand=True, fill="both", padx=5, pady=5)
        
        ctk.CTkLabel(card, text=title, font=("Inter", 12, "bold"), 
                    text_color=P["text_2"]).pack(anchor="w", padx=20, pady=(15, 5))
        
        ctk.CTkLabel(card, text=value, font=("Inter", 32, "bold"), 
                    text_color=color).pack(anchor="w", padx=20)
        
        ctk.CTkLabel(card, text=change, font=("Inter", 11), 
                    text_color=P["muted"]).pack(anchor="w", padx=20, pady=(5, 15))
    
    def create_activity_item(self, parent, user, action, detail, time, result):
        frame = ctk.CTkFrame(parent, fg_color="#0a0e1a", corner_radius=8)
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
        
        frame = ctk.CTkFrame(parent, fg_color="#0a0e1a", corner_radius=8)
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
        pending_users = sum(1 for user in users if user[2] == "pending")
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
        self.create_stat_card(stats_frame, "⏳ Pending", str(pending_users), "Waiting approval", "#f59e0b", "#d97706")

        # ===== TABLE CONTAINER - fills remaining space =====
        table_frame = ctk.CTkFrame(self.content_frame, fg_color="#111827", corner_radius=18)
        table_frame.pack(fill="both", expand=True, pady=(0, 0))
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
        header_frame = ctk.CTkFrame(table_frame, fg_color="#1e293b", corner_radius=12, height=50)
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
        scroll = ctk.CTkScrollableFrame(table_frame, fg_color="transparent")
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
        status = status if status in ["pending", "active", "blocked", "suspended"] else "pending"

        row = ctk.CTkFrame(parent, fg_color="#0a0e1a", corner_radius=10, height=56)
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
                                    fg_color="#0a0e1a", button_color="#6366f1", button_hover_color="#4f46e5",
                                    dropdown_fg_color="#0a0e1a", dropdown_hover_color="#1e293b",
                                    text_color="#f8fafc", corner_radius=8,
                                    command=lambda new_role, u=username: self.change_role(u, new_role))
        role_box.set(role if role in ["admin", "user"] else "user")
        role_box.pack(anchor="w")  # ✅ Pack inside wrapper instead of grid
        if username == self.admin['username']:
            role_box.configure(state="disabled")

        # --- Column 2: Status (Wrapped in transparent frame) ---
        status_cell = ctk.CTkFrame(row, fg_color="transparent")
        status_cell.grid(row=0, column=2, sticky="w", padx=10, pady=8)
        
        status_box = ctk.CTkOptionMenu(status_cell, values=["pending", "active", "blocked", "suspended"], 
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

        if status == "pending":
            ctk.CTkButton(actions, text="✅ Approve", width=90, height=30,
                         font=("Inter", 11, "bold"), fg_color="#10b981", hover_color="#059669",
                         corner_radius=8, command=lambda u=username: self.approve_user(u)).pack(side="left", padx=(0, 6))

        if username != self.admin['username']:
            ctk.CTkButton(actions, text="🗑 Delete", width=80, height=30,
                         font=("Inter", 11, "bold"), fg_color="#ef4444", hover_color="#dc2626",
                         corner_radius=8, command=lambda u=username: self.delete_user(u)).pack(side="left")
        else:
            ctk.CTkLabel(actions, text="Protected", font=("Inter", 11, "bold"),
                        text_color="#94a3b8", width=80).pack(side="left")
    # ✅ FIXED CREATE_USER_ROW METHOD END

    def _status_color(self, status):
        return {"pending": "#f59e0b", "active": "#10b981", "blocked": "#ef4444", "suspended": "#f59e0b"}.get(status, "#64748b")

    def _status_hover_color(self, status):
        return {"pending": "#d97706", "active": "#059669", "blocked": "#dc2626", "suspended": "#d97706"}.get(status, "#475569")

    def _format_date(self, value):
        if not value:
            return "N/A"
        return str(value)[:10]

    def show_logs(self):
        self.header_title.configure(text="Audit Logs")
        P = self.P

        toolbar = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            toolbar,
            text="All security, signing, verification and admin events are listed below.",
            font=("Inter", 12),
            text_color=P["muted"],
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            toolbar, text="Export CSV", width=130, height=38,
            font=("Inter", 12, "bold"), fg_color=P["success"], hover_color="#059669",
            text_color="white", corner_radius=9, command=self.export_logs
        ).pack(side="right")

        table_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=P["card"],
            corner_radius=14,
            border_width=1,
            border_color=P["border"],
        )
        table_frame.pack(fill="both", expand=True)

        header = ctk.CTkFrame(table_frame, fg_color=P["header"], corner_radius=10, height=48)
        header.pack(fill="x", padx=18, pady=(18, 8))
        header.pack_propagate(False)

        self.admin_log_cols = [
            ("Time", 180),
            ("User", 130),
            ("Action", 170),
            ("File", 300),
            ("Result", 120),
            ("Details", 360),
        ]

        for title, width in self.admin_log_cols:
            ctk.CTkLabel(
                header,
                text=title,
                font=("Inter", 11, "bold"),
                text_color=P["text_2"],
                width=width,
                anchor="w",
            ).pack(side="left", padx=8, pady=12)

        scroll = ctk.CTkScrollableFrame(table_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=18, pady=(0, 16))

        try:
            conn = sqlite3.connect("storage/audit.db")
            cursor = conn.execute("""
                SELECT id, timestamp, username, action, file_name, file_hash, result, details, ip_address
                FROM audit_log
                ORDER BY timestamp DESC
                LIMIT 200
            """)
            logs = cursor.fetchall()
            conn.close()

            if not logs:
                ctk.CTkLabel(
                    scroll,
                    text="No audit logs found yet.",
                    font=("Inter", 13),
                    text_color=P["muted"],
                ).pack(pady=35)
                return

            for idx, log in enumerate(logs):
                self.create_log_row(scroll, log, idx)
        except Exception as e:
            ctk.CTkLabel(
                scroll,
                text=f"Could not load audit logs: {e}",
                font=("Inter", 12),
                text_color=P["danger"],
            ).pack(pady=20)

    def create_log_row(self, parent, log, index=0):
        P = self.P
        _id, timestamp, username, action, file_name, file_hash, result, details, ip = log

        row = ctk.CTkFrame(
            parent,
            fg_color=P["row"] if index % 2 == 0 else P["row_alt"],
            corner_radius=9,
            border_width=1,
            border_color=P["border"],
            height=50,
        )
        row.pack(fill="x", pady=4)
        row.pack_propagate(False)

        result = result or "-"
        result_color = P["success"] if result in ["SUCCESS", "VALID", "ACTIVE", "OK"] else P["danger"]

        values = [
            ((timestamp or "")[:19] if timestamp else "N/A", P["muted"], "Courier"),
            (self._shorten(username, 18), P["text_2"], "Inter"),
            (self._shorten(action, 24), P["accent"], "Inter"),
            (self._shorten(file_name or "-", 42), P["text_2"], "Inter"),
            (self._shorten(result, 14), result_color, "Inter"),
            (self._shorten(details or "-", 58), P["muted"], "Inter"),
        ]

        for (text, color, family), (_, width) in zip(values, self.admin_log_cols):
            ctk.CTkLabel(
                row,
                text=text,
                font=(family, 10, "bold" if family == "Inter" and (text == action or text == result) else "normal"),
                text_color=color,
                width=width,
                anchor="w",
            ).pack(side="left", padx=8, pady=13)

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
        
        # Table fills remaining space
        table_frame = ctk.CTkFrame(self.content_frame, fg_color="#111827", corner_radius=12)
        table_frame.pack(fill="both", expand=True)
        
        headers = ctk.CTkFrame(table_frame, fg_color="#1e293b", corner_radius=8)
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
        row = ctk.CTkFrame(parent, fg_color="#0a0e1a", corner_radius=8)
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

        ctk.CTkButton(actions, text="⬇ Download", width=80, height=28,
                     fg_color="#10b981", hover_color="#059669",
                     corner_radius=6, command=lambda c=cert_path: self.download_cert(c)).pack(side="left", padx=2)

        ctk.CTkButton(actions, text="🔑 Pub Key", width=80, height=28,
                     fg_color="#06b6d4", hover_color="#0891b2",
                     corner_radius=6, command=lambda u=username: self.view_public_key(u)).pack(side="left", padx=2)

        ctk.CTkButton(actions, text="✅ Verify", width=70, height=28,
                     fg_color="#f59e0b", hover_color="#d97706",
                     corner_radius=6, command=lambda u=username, c=cert_path: self.verify_cert_full(u, c)).pack(side="left", padx=2)

        if not is_revoked(username):
            ctk.CTkButton(actions, text="❌ Revoke", width=60, height=28,
                         fg_color="#ef4444", hover_color="#dc2626",
                         corner_radius=6, command=lambda u=username: self.revoke_cert(u)).pack(side="left", padx=2)

    def view_cert(self, username):
        cert_path = f"storage/certs/{username}_cert.pem"
        if os.path.exists(cert_path):
            try:
                from cryptography import x509
                from cryptography.hazmat.primitives import serialization
                from datetime import datetime

                with open(cert_path, 'rb') as f:
                    cert_data = f.read()
                    cert = x509.load_pem_x509_certificate(cert_data)

                # Extract certificate details
                issuer = cert.issuer
                subject = cert.subject
                serial_number = cert.serial_number
                sig_algo = cert.signature_algorithm_oid._name if hasattr(cert.signature_algorithm_oid, '_name') else str(cert.signature_algorithm_oid)
                not_before = cert.not_valid_before
                not_after = cert.not_valid_after

                # Get issuer and subject common names
                issuer_cn = ""
                for attr in issuer:
                    if attr.oid == x509.oid.NameOID.COMMON_NAME:
                        issuer_cn = attr.value
                        break

                subject_cn = ""
                for attr in subject:
                    if attr.oid == x509.oid.NameOID.COMMON_NAME:
                        subject_cn = attr.value
                        break

                # Determine certificate status
                now = datetime.now()
                cert_status = "Valid"
                status_color = "#10b981"

                if is_revoked(username):
                    cert_status = "Revoked"
                    status_color = "#ef4444"
                elif now < not_before:
                    cert_status = "Not Yet Valid"
                    status_color = "#f59e0b"
                elif now > not_after:
                    cert_status = "Expired"
                    status_color = "#ef4444"
                else:
                    try:
                        from core.cert_verifier import verify_certificate
                        from core.ca_engine import load_ca_public_key
                        ca_key = load_ca_public_key()
                        if not verify_certificate(cert_path, ca_key):
                            cert_status = "Invalid Signature"
                            status_color = "#ef4444"
                    except:
                        cert_status = "Error"
                        status_color = "#f59e0b"

                # Create dialog
                dialog = ctk.CTkToplevel(self.root)
                dialog.title(f"Certificate Details - {username}")
                dialog.geometry("620x680")
                dialog.configure(fg_color="#0a0e1a")
                dialog.resizable(False, False)
                dialog.grab_set()

                # Center dialog
                dialog.update_idletasks()
                x = (dialog.winfo_screenwidth() - 620) // 2
                y = (dialog.winfo_screenheight() - 680) // 2
                dialog.geometry(f"+{x}+{y}")

                # Header
                header_frame = ctk.CTkFrame(dialog, fg_color="transparent")
                header_frame.pack(fill="x", padx=25, pady=(20, 5))

                ctk.CTkLabel(header_frame, text="🏛", font=("Inter", 32)).pack()
                ctk.CTkLabel(header_frame, text="Certificate Details", 
                            font=("Inter", 20, "bold"), text_color="#6366f1").pack()
                ctk.CTkLabel(header_frame, text=f"User: {username}", 
                            font=("Inter", 12), text_color="#94a3b8").pack(pady=(5, 0))

                # Separator
                ctk.CTkFrame(dialog, fg_color="#334155", height=1).pack(fill="x", padx=25, pady=10)

                # Details container
                details_frame = ctk.CTkFrame(dialog, fg_color="#111827", corner_radius=12)
                details_frame.pack(fill="x", padx=25, pady=10)

                def add_detail_row(parent, label, value, value_color="#f8fafc"):
                    row = ctk.CTkFrame(parent, fg_color="transparent")
                    row.pack(fill="x", padx=15, pady=4)
                    ctk.CTkLabel(row, text=f"{label}:", font=("Inter", 11, "bold"), 
                                text_color="#94a3b8", width=130, anchor="w").pack(side="left")
                    ctk.CTkLabel(row, text=str(value), font=("Inter", 11), 
                                text_color=value_color, anchor="w").pack(side="left", fill="x", expand=True)

                add_detail_row(details_frame, "Username", username)
                add_detail_row(details_frame, "Filename", f"{username}_cert.pem")
                add_detail_row(details_frame, "Issuer", issuer_cn or "CryptoSign Root CA")
                add_detail_row(details_frame, "Subject", subject_cn or username)
                add_detail_row(details_frame, "Serial Number", str(serial_number))
                add_detail_row(details_frame, "Signature Algorithm", sig_algo.upper().replace("SHA", "SHA-"))
                add_detail_row(details_frame, "Issue Date", not_before.strftime("%Y-%m-%d %H:%M:%S UTC"))
                add_detail_row(details_frame, "Expiry Date", not_after.strftime("%Y-%m-%d %H:%M:%S UTC"))
                add_detail_row(details_frame, "Status", cert_status, status_color)

                # Separator
                ctk.CTkFrame(dialog, fg_color="#334155", height=1).pack(fill="x", padx=25, pady=10)

                # PEM content section
                ctk.CTkLabel(dialog, text="📄 PEM Certificate Content", 
                            font=("Inter", 14, "bold"), text_color="#f8fafc").pack(anchor="w", padx=25, pady=(5, 5))

                text_box = ctk.CTkTextbox(dialog, width=570, height=220, font=("Courier", 9),
                                          fg_color="#111827", text_color="#f8fafc", corner_radius=8)
                text_box.pack(padx=25, pady=5)
                text_box.insert("1.0", cert_data.decode('utf-8'))
                text_box.configure(state="disabled")

                # Close button
                ctk.CTkButton(dialog, text="Close", width=120, height=35,
                             font=("Inter", 12, "bold"), fg_color="#475569", hover_color="#334155",
                             corner_radius=8, command=dialog.destroy).pack(pady=15)

            except Exception as e:
                # Fallback to simple viewer if parsing fails
                dialog = ctk.CTkToplevel(self.root)
                dialog.title(f"Certificate - {username}")
                dialog.geometry("600x400")
                dialog.configure(fg_color="#0a0e1a")

                ctk.CTkLabel(dialog, text=f"🏛 Certificate for {username}", 
                            font=("Inter", 16, "bold"), text_color="#6366f1").pack(pady=15)

                text_box = ctk.CTkTextbox(dialog, width=550, height=300, font=("Courier", 10),
                                          fg_color="#111827", text_color="#f8fafc")
                text_box.pack(pady=10)
                with open(cert_path, 'r') as f:
                    text_box.insert("1.0", f.read())
                text_box.configure(state="disabled")

    def view_public_key(self, username):
        """Display the user's public key in a dialog window."""
        pub_key_path = f"storage/keystores/{username}_public.pem"

        if not os.path.exists(pub_key_path):
            messagebox.showerror("Error", f"Public key not found for user: {username}")
            return

        try:
            with open(pub_key_path, 'r') as f:
                key_content = f.read()

            dialog = ctk.CTkToplevel(self.root)
            dialog.title(f"Public Key - {username}")
            dialog.geometry("600x480")
            dialog.configure(fg_color="#0a0e1a")
            dialog.resizable(False, False)
            dialog.grab_set()

            # Center dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() - 600) // 2
            y = (dialog.winfo_screenheight() - 480) // 2
            dialog.geometry(f"+{x}+{y}")

            ctk.CTkLabel(dialog, text="🔑", font=("Inter", 32)).pack(pady=(15, 5))
            ctk.CTkLabel(dialog, text="Public Key", 
                        font=("Inter", 18, "bold"), text_color="#06b6d4").pack()
            ctk.CTkLabel(dialog, text=f"User: {username}", 
                        font=("Inter", 12), text_color="#94a3b8").pack(pady=(5, 10))

            ctk.CTkFrame(dialog, fg_color="#334155", height=1).pack(fill="x", padx=25, pady=5)

            text_box = ctk.CTkTextbox(dialog, width=550, height=280, font=("Courier", 10),
                                      fg_color="#111827", text_color="#f8fafc", corner_radius=8)
            text_box.pack(padx=25, pady=10)
            text_box.insert("1.0", key_content)
            text_box.configure(state="disabled")

            ctk.CTkButton(dialog, text="Close", width=120, height=35,
                         font=("Inter", 12, "bold"), fg_color="#475569", hover_color="#334155",
                         corner_radius=8, command=dialog.destroy).pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"Could not read public key: {str(e)}")

    def verify_cert_full(self, username, cert_path):
        """Comprehensive certificate verification: signature, validity period, and revocation status."""
        try:
            from cryptography import x509
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import padding
            from datetime import datetime
            import hashlib

            # Load certificate
            with open(cert_path, 'rb') as f:
                cert = x509.load_pem_x509_certificate(f.read())

            # Load CA public key
            ca_key = None
            ca_cert_path = "storage/ca/ca_cert.pem"
            if os.path.exists(ca_cert_path):
                with open(ca_cert_path, 'rb') as f:
                    ca_cert = x509.load_pem_x509_certificate(f.read())
                ca_key = ca_cert.public_key()

            results = {
                'signature_valid': False,
                'not_expired': False,
                'not_yet_valid': False,
                'not_revoked': False,
                'overall': 'INVALID'
            }

            # 1. Verify certificate signature
            if ca_key:
                try:
                    ca_key.verify(
                        cert.signature,
                        cert.tbs_certificate_bytes,
                        padding.PKCS1v15(),
                        cert.signature_hash_algorithm
                    )
                    results['signature_valid'] = True
                except Exception:
                    results['signature_valid'] = False

            # 2. Check validity period
            now = datetime.now()
            not_before = cert.not_valid_before
            not_after = cert.not_valid_after

            if now < not_before:
                results['not_yet_valid'] = True
                results['not_expired'] = False
            elif now > not_after:
                results['not_expired'] = False
                results['not_yet_valid'] = False
            else:
                results['not_expired'] = True
                results['not_yet_valid'] = False

            # 3. Check revocation status
            if not is_revoked(username):
                results['not_revoked'] = True

            # Determine overall status
            if results['signature_valid'] and results['not_expired'] and results['not_revoked'] and not results['not_yet_valid']:
                results['overall'] = 'VALID'
            elif results['not_yet_valid']:
                results['overall'] = 'NOT_YET_VALID'
            elif not results['not_expired']:
                results['overall'] = 'EXPIRED'
            elif not results['not_revoked']:
                results['overall'] = 'REVOKED'
            elif not results['signature_valid']:
                results['overall'] = 'INVALID_SIGNATURE'
            else:
                results['overall'] = 'INVALID'

            # Show results dialog
            dialog = ctk.CTkToplevel(self.root)
            dialog.title(f"Certificate Verification - {username}")
            dialog.geometry("520x520")
            dialog.configure(fg_color="#0a0e1a")
            dialog.resizable(False, False)
            dialog.grab_set()

            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() - 520) // 2
            y = (dialog.winfo_screenheight() - 520) // 2
            dialog.geometry(f"+{x}+{y}")

            # Header
            ctk.CTkLabel(dialog, text="✅" if results['overall'] == 'VALID' else "⚠️", 
                        font=("Inter", 36)).pack(pady=(15, 5))

            status_text = {
                'VALID': 'Certificate is Valid',
                'NOT_YET_VALID': 'Not Yet Valid',
                'EXPIRED': 'Certificate Expired',
                'REVOKED': 'Certificate Revoked',
                'INVALID_SIGNATURE': 'Invalid Signature',
                'INVALID': 'Invalid Certificate'
            }
            status_color = "#10b981" if results['overall'] == 'VALID' else "#ef4444" if results['overall'] in ['EXPIRED', 'REVOKED', 'INVALID_SIGNATURE', 'INVALID'] else "#f59e0b"

            ctk.CTkLabel(dialog, text=status_text.get(results['overall'], 'Unknown'), 
                        font=("Inter", 18, "bold"), text_color=status_color).pack()
            ctk.CTkLabel(dialog, text=f"Certificate: {username}_cert.pem", 
                        font=("Inter", 11), text_color="#94a3b8").pack(pady=(5, 10))

            ctk.CTkFrame(dialog, fg_color="#334155", height=1).pack(fill="x", padx=25, pady=5)

            # Verification details
            details_frame = ctk.CTkFrame(dialog, fg_color="#111827", corner_radius=12)
            details_frame.pack(fill="x", padx=25, pady=10)

            def add_check_row(parent, label, passed, detail=""):
                row = ctk.CTkFrame(parent, fg_color="transparent")
                row.pack(fill="x", padx=15, pady=6)

                icon = "✅" if passed else "❌"
                color = "#10b981" if passed else "#ef4444"

                ctk.CTkLabel(row, text=icon, font=("Inter", 14), text_color=color, width=30).pack(side="left")
                ctk.CTkLabel(row, text=label, font=("Inter", 12, "bold"), 
                            text_color="#f8fafc", anchor="w").pack(side="left", padx=(5, 0))

                if detail:
                    ctk.CTkLabel(row, text=detail, font=("Inter", 10), 
                                text_color="#94a3b8", anchor="w").pack(side="left", padx=(10, 0))

            # Signature check
            sig_detail = "Signature verified by CA" if results['signature_valid'] else "Signature verification failed"
            add_check_row(details_frame, "Certificate Signature", results['signature_valid'], sig_detail)

            # Validity period check
            if results['not_yet_valid']:
                valid_detail = f"Valid from {not_before.strftime('%Y-%m-%d')}"
                add_check_row(details_frame, "Validity Period", False, valid_detail)
            elif results['not_expired']:
                valid_detail = f"Valid until {not_after.strftime('%Y-%m-%d')}"
                add_check_row(details_frame, "Validity Period", True, valid_detail)
            else:
                valid_detail = f"Expired on {not_after.strftime('%Y-%m-%d')}"
                add_check_row(details_frame, "Validity Period", False, valid_detail)

            # Revocation check
            rev_detail = "Not in revocation list" if results['not_revoked'] else "User has been revoked"
            add_check_row(details_frame, "Revocation Status", results['not_revoked'], rev_detail)

            # Additional info
            ctk.CTkFrame(dialog, fg_color="#334155", height=1).pack(fill="x", padx=25, pady=5)

            info_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            info_frame.pack(fill="x", padx=25, pady=5)

            ctk.CTkLabel(info_frame, text=f"Serial: {cert.serial_number}", 
                        font=("Inter", 10), text_color="#64748b").pack(side="left", padx=5)
            algo_text = cert.signature_algorithm_oid._name.upper().replace("SHA", "SHA-") if hasattr(cert.signature_algorithm_oid, '_name') else str(cert.signature_algorithm_oid)
            ctk.CTkLabel(info_frame, text=f"|  Algo: {algo_text}", 
                        font=("Inter", 10), text_color="#64748b").pack(side="left", padx=5)

            # Close button
            ctk.CTkButton(dialog, text="Close", width=120, height=35,
                         font=("Inter", 12, "bold"), fg_color="#475569", hover_color="#334155",
                         corner_radius=8, command=dialog.destroy).pack(pady=15)

            # Log the verification
            self.audit.log(self.admin['username'], "ADMIN_VERIFY_CERT", 
                          "SUCCESS" if results['overall'] == 'VALID' else "FAILED",
                          details=f"User: {username}, Status: {results['overall']}")

        except Exception as e:
            messagebox.showerror("Verification Error", f"Could not verify certificate: {str(e)}")
            self.audit.log(self.admin['username'], "ADMIN_VERIFY_CERT", "FAILED", 
                          details=f"User: {username}, Error: {str(e)}")

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
        if messagebox.askyesno("Confirm", f"Revoke certificate for '{username}'?\n\nThis will block the account and add the user to revocation list."):
            self.change_status(username, "blocked", refresh=False, silent=True)
            self.audit.log(self.admin['username'], "ADMIN_REVOKE_CERT", "SUCCESS", details=f"Revoked: {username}")
            self.switch_view("certs")
            messagebox.showinfo("Success", f"Certificate for '{username}' revoked and account blocked!")

    def view_ca_cert(self):
        ca_path = "storage/ca/ca_cert.pem"
        if os.path.exists(ca_path):
            with open(ca_path, 'r') as f:
                content = f.read()
            
            dialog = ctk.CTkToplevel(self.root)
            dialog.title("CA Certificate")
            dialog.geometry("600x400")
            dialog.configure(fg_color="#0a0e1a")
            
            ctk.CTkLabel(dialog, text="🏛 Root CA Certificate", 
                        font=("Inter", 16, "bold"), text_color="#6366f1").pack(pady=15)
            
            text_box = ctk.CTkTextbox(dialog, width=550, height=300, font=("Courier", 10),
                                      fg_color="#111827", text_color="#f8fafc")
            text_box.pack(pady=10)
            text_box.insert("1.0", content)
            text_box.configure(state="disabled")
        else:
            messagebox.showerror("Error", "CA certificate not found!")
    
    def show_revoked(self):
        self.header_title.configure(text="Revoked Certificates")
        P = self.P
        
        revoked_users = []
        
        try:
            conn = sqlite3.connect(self.auth.db_path)
            cursor = conn.execute("SELECT username, role, status, created_at FROM users WHERE status IN ('revoked', 'blocked')")
            db_revoked = cursor.fetchall()
            conn.close()
            revoked_users.extend(db_revoked)
        except Exception:
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
        except Exception:
            pass
        
        stats_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 18))
        
        self.create_stat_card(stats_frame, "❌ Revoked Users", str(len(revoked_users)), 
                             "Access denied", P["danger"], P["danger"])
        active_count = 0
        try:
            conn = sqlite3.connect(self.auth.db_path)
            active_count = conn.execute("SELECT COUNT(*) FROM users WHERE status='active'").fetchone()[0]
            conn.close()
        except Exception:
            pass
        self.create_stat_card(stats_frame, "✅ Active Users", str(active_count), 
                             "Currently active accounts", P["success"], P["success"])
        
        table_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=P["card"],
            corner_radius=14,
            border_width=1,
            border_color=P["border"],
        )
        table_frame.pack(fill="both", expand=True)
        
        headers = ctk.CTkFrame(table_frame, fg_color=P["header"], corner_radius=10, height=50)
        headers.pack(fill="x", padx=18, pady=(18, 10))
        headers.pack_propagate(False)
        
        for col, width in [("Username", 250), ("Role", 150), ("Status", 180), ("Created", 200), ("Actions", 250)]:
            ctk.CTkLabel(
                headers,
                text=col,
                font=("Inter", 12, "bold"),
                text_color=P["text_2"],
                width=width,
                anchor="w",
            ).pack(side="left", padx=10, pady=14)
        
        scroll = ctk.CTkScrollableFrame(table_frame, fg_color=P["card"], corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        
        if not revoked_users:
            empty = ctk.CTkFrame(scroll, fg_color=P["row_alt"], corner_radius=10, border_width=1, border_color=P["border"])
            empty.pack(fill="both", expand=True, pady=4)
            ctk.CTkLabel(
                empty,
                text="No revoked users found",
                font=("Inter", 14),
                text_color=P["muted"],
            ).pack(pady=60)
        else:
            for user in revoked_users:
                self.create_revoked_row(scroll, user)

    def create_revoked_row(self, parent, user):
        P = self.P
        username, role, status, created = user
        
        row = ctk.CTkFrame(parent, fg_color=P["row_alt"], corner_radius=10, border_width=1, border_color=P["border"])
        row.pack(fill="x", pady=4)
        
        ctk.CTkLabel(row, text=username, font=("Inter", 12, "bold"), 
                    text_color=P["danger"], width=250, anchor="w").pack(side="left", padx=10, pady=12)
        
        ctk.CTkLabel(row, text=role, font=("Inter", 12), 
                    text_color=P["text_2"], width=150, anchor="w").pack(side="left", padx=10)
        
        ctk.CTkLabel(row, text="REVOKED", font=("Inter", 12, "bold"), 
                    text_color=P["danger"], width=180, anchor="w").pack(side="left", padx=10)
        
        ctk.CTkLabel(row, text=created[:10] if created and created != "N/A" else "N/A", 
                    font=("Inter", 11), text_color=P["muted"], width=200, anchor="w").pack(side="left", padx=10)
        
        actions = ctk.CTkFrame(row, fg_color="transparent", width=250)
        actions.pack(side="left", padx=10)
        
        ctk.CTkButton(actions, text="Reactivate", width=90, height=30,
                     fg_color=P["success"], hover_color="#059669", text_color="white",
                     corner_radius=7, command=lambda u=username: self.activate_user(u)).pack(side="left", padx=2)
        
        ctk.CTkButton(actions, text="Delete", width=70, height=30,
                     fg_color=P["danger"], hover_color="#dc2626", text_color="white",
                     corner_radius=7, command=lambda u=username: self.delete_user(u)).pack(side="left", padx=2)
    
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
        
        # Table fills remaining space
        self.docs_table_frame = ctk.CTkFrame(self.content_frame, fg_color="#111827", corner_radius=12)
        self.docs_table_frame.pack(fill="both", expand=True)
        
        self.build_docs_table("all")
    
    def build_docs_table(self, filter_type):
        for widget in self.docs_table_frame.winfo_children():
            widget.destroy()
        
        headers = ctk.CTkFrame(self.docs_table_frame, fg_color="#1e293b", corner_radius=8)
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
        
        row = ctk.CTkFrame(parent, fg_color="#0a0e1a", corner_radius=8)
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
        P = self.P

        settings_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color=P["card"],
            corner_radius=18,
            border_width=1,
            border_color=P["border"],
        )
        settings_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(
            settings_frame,
            text="System Control Center",
            font=("Inter", 26, "bold"),
            text_color=P["text"],
        ).pack(anchor="w", padx=28, pady=(24, 6))
        ctk.CTkLabel(
            settings_frame,
            text="Manage admin appearance, database status, certificate authority health and user approvals.",
            font=("Inter", 13),
            text_color=P["muted"],
        ).pack(anchor="w", padx=28, pady=(0, 18))

        # ----- Appearance / Notification controls -----
        top = ctk.CTkFrame(settings_frame, fg_color="transparent")
        top.pack(fill="x", padx=28, pady=(0, 14))
        top.grid_columnconfigure(0, weight=1)
        top.grid_columnconfigure(1, weight=1)

        appearance = ctk.CTkFrame(top, fg_color=P["card_alt"], corner_radius=14, border_width=1, border_color=P["border"])
        appearance.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ctk.CTkLabel(appearance, text="Appearance", font=("Inter", 18, "bold"), text_color=P["text"]).pack(anchor="w", padx=22, pady=(20, 4))
        ctk.CTkLabel(appearance, text="Switch admin dashboard between dark and light mode.", font=("Inter", 12), text_color=P["muted"]).pack(anchor="w", padx=22, pady=(0, 14))

        dark_var = ctk.BooleanVar(value=not self.is_light_mode)
        compact_var = ctk.BooleanVar(value=bool(self.ui_settings.get("compact_rows", False)))

        def save_compact():
            self.ui_settings["compact_rows"] = bool(compact_var.get())
            self._save_ui_settings()
            messagebox.showinfo("Settings", "Compact row preference saved.")

        ctk.CTkSwitch(
            appearance,
            text="Dark mode",
            variable=dark_var,
            onvalue=True,
            offvalue=False,
            command=lambda: self._set_admin_theme("dark" if dark_var.get() else "light"),
            font=("Inter", 13, "bold"),
            text_color=P["text"],
            progress_color=P["accent"],
        ).pack(fill="x", padx=22, pady=(6, 12))

        ctk.CTkSwitch(
            appearance,
            text="Compact audit rows",
            variable=compact_var,
            command=save_compact,
            font=("Inter", 13, "bold"),
            text_color=P["text"],
            progress_color=P["accent"],
        ).pack(fill="x", padx=22, pady=(0, 12))

        ctk.CTkLabel(
            appearance,
            text=f"Current theme: {'Light' if self.is_light_mode else 'Dark'}",
            font=("Inter", 12, "bold"),
            text_color=P["accent"],
        ).pack(anchor="w", padx=22, pady=(0, 18))

        notifications = ctk.CTkFrame(top, fg_color=P["card_alt"], corner_radius=14, border_width=1, border_color=P["border"])
        notifications.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        ctk.CTkLabel(notifications, text="Notifications", font=("Inter", 18, "bold"), text_color=P["text"]).pack(anchor="w", padx=22, pady=(20, 4))
        ctk.CTkLabel(notifications, text="Control pending-user alert indicator in admin header.", font=("Inter", 12), text_color=P["muted"]).pack(anchor="w", padx=22, pady=(0, 14))

        notify_var = ctk.BooleanVar(value=bool(self.ui_settings.get("admin_notifications", True)))

        def toggle_notifications():
            self.ui_settings["admin_notifications"] = bool(notify_var.get())
            self._save_ui_settings()
            self.refresh_notification()
            self._apply_theme_to_tree(self.root)

        ctk.CTkSwitch(
            notifications,
            text="Pending approval alerts",
            variable=notify_var,
            command=toggle_notifications,
            font=("Inter", 13, "bold"),
            text_color=P["text"],
            progress_color=P["accent"],
        ).pack(fill="x", padx=22, pady=(6, 12))

        ctk.CTkLabel(
            notifications,
            text="Alerts are ON" if notify_var.get() else "Alerts are OFF",
            font=("Inter", 12, "bold"),
            text_color=P["success"] if notify_var.get() else P["danger"],
        ).pack(anchor="w", padx=22, pady=(0, 18))

        # ----- Live system stats -----
        try:
            conn = sqlite3.connect("storage/audit.db")
            total_logs = conn.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]
            total_files = conn.execute("SELECT COUNT(*) FROM user_files").fetchone()[0]
            conn.close()
        except Exception:
            total_logs = 0
            total_files = 0

        try:
            conn = sqlite3.connect(self.auth.db_path)
            total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            pending_users = conn.execute("SELECT COUNT(*) FROM users WHERE status='pending'").fetchone()[0]
            active_users = conn.execute("SELECT COUNT(*) FROM users WHERE status='active'").fetchone()[0]
            conn.close()
        except Exception:
            total_users = pending_users = active_users = 0

        ca_exists = os.path.exists("storage/ca/ca_cert.pem")
        cert_count = len([f for f in os.listdir("storage/certs") if f.endswith("_cert.pem")]) if os.path.exists("storage/certs") else 0
        key_count = len([f for f in os.listdir("storage/keystores") if f.endswith("_private.pem")]) if os.path.exists("storage/keystores") else 0

        stats = ctk.CTkFrame(settings_frame, fg_color="transparent")
        stats.pack(fill="x", padx=28, pady=(0, 14))
        for i in range(3):
            stats.grid_columnconfigure(i, weight=1)

        def setting_card(parent, title, value, subtitle, accent_color, col):
            card = ctk.CTkFrame(parent, fg_color=P["card_alt"], corner_radius=14, border_width=1, border_color=P["border"])
            card.grid(row=0, column=col, sticky="nsew", padx=8, pady=8)
            ctk.CTkLabel(card, text=title, font=("Inter", 14, "bold"), text_color=P["text"]).pack(anchor="w", padx=20, pady=(18, 6))
            ctk.CTkLabel(card, text=str(value), font=("Inter", 34, "bold"), text_color=accent_color).pack(anchor="w", padx=20)
            ctk.CTkLabel(card, text=subtitle, font=("Inter", 12), text_color=P["muted"]).pack(anchor="w", padx=20, pady=(4, 18))

        setting_card(stats, "Database Logs", total_logs, "Total audit events recorded", P["info"], 0)
        setting_card(stats, "Tracked Files", total_files, "Documents stored in audit tracking", "#a78bfa", 1)
        setting_card(stats, "Pending Requests", pending_users, "Users waiting for admin approval", P["danger"] if pending_users else P["success"], 2)

        bottom = ctk.CTkFrame(settings_frame, fg_color="transparent")
        bottom.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        bottom.grid_columnconfigure(0, weight=2)
        bottom.grid_columnconfigure(1, weight=1)

        detail_left = ctk.CTkFrame(bottom, fg_color=P["card_alt"], corner_radius=14, border_width=1, border_color=P["border"])
        detail_left.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=8)
        detail_left.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(detail_left, text="Security & PKI Status", font=("Inter", 20, "bold"), text_color=P["text"]).grid(row=0, column=0, columnspan=2, sticky="w", padx=22, pady=(20, 14))

        def info_row(parent, r, label, value, color=None):
            ctk.CTkLabel(parent, text=label, font=("Inter", 13, "bold"), text_color=P["muted"]).grid(row=r, column=0, sticky="w", padx=22, pady=8)
            ctk.CTkLabel(parent, text=value, font=("Inter", 13, "bold"), text_color=color or P["text"]).grid(row=r, column=1, sticky="w", padx=10, pady=8)

        info_row(detail_left, 1, "Root CA", "Active" if ca_exists else "Missing", P["success"] if ca_exists else P["danger"])
        info_row(detail_left, 2, "Issued Certificates", str(cert_count), "#8b5cf6")
        info_row(detail_left, 3, "Private Key Stores", str(key_count), P["warning"])
        info_row(detail_left, 4, "User Accounts", f"{active_users} active / {total_users} total", P["info"])
        info_row(detail_left, 5, "Approval Mode", "Enabled - new users require admin approval", P["success"])
        info_row(detail_left, 6, "UI Settings File", self._settings_file(), P["muted"])

        detail_right = ctk.CTkFrame(bottom, fg_color=P["card_alt"], corner_radius=14, border_width=1, border_color=P["border"])
        detail_right.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=8)

        ctk.CTkLabel(detail_right, text="Quick Admin Actions", font=("Inter", 20, "bold"), text_color=P["text"]).pack(anchor="w", padx=22, pady=(20, 14))

        ctk.CTkButton(detail_right, text="Open Pending Requests", height=42, fg_color=P["danger"] if pending_users else "#64748b", hover_color="#dc2626", text_color="white", corner_radius=10, font=("Inter", 13, "bold"), command=self.show_pending_notifications).pack(fill="x", padx=22, pady=6)
        ctk.CTkButton(detail_right, text="Open Certificate Management", height=42, fg_color=P["accent"], hover_color=P["accent_hover"], text_color="white", corner_radius=10, font=("Inter", 13, "bold"), command=lambda: self.switch_view("certs")).pack(fill="x", padx=22, pady=6)
        ctk.CTkButton(detail_right, text="Open Audit Logs", height=42, fg_color=P["info"], hover_color="#0284c7", text_color="white", corner_radius=10, font=("Inter", 13, "bold"), command=lambda: self.switch_view("logs")).pack(fill="x", padx=22, pady=6)
        ctk.CTkButton(detail_right, text="Refresh Settings", height=42, fg_color=P["success"], hover_color="#059669", text_color="white", corner_radius=10, font=("Inter", 13, "bold"), command=lambda: self.switch_view("settings")).pack(fill="x", padx=22, pady=6)

    def add_user(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Add User")
        dialog.geometry("430x560")
        dialog.configure(fg_color="#0a0e1a")
        dialog.grab_set()
        dialog.resizable(False, False)

        ctk.CTkLabel(dialog, text="➕ Add New User", font=("Inter", 20, "bold"),
                    text_color="#f8fafc").pack(pady=(16, 4))
        ctk.CTkLabel(dialog, text="Create an account with role and access status.",
                    font=("Inter", 12), text_color="#94a3b8").pack(pady=(0, 10))

        form = ctk.CTkFrame(dialog, fg_color="#111827", corner_radius=14)
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
        status_menu = ctk.CTkOptionMenu(form, values=["pending", "active", "blocked", "suspended"], height=36,
                                       fg_color="#0f172a", button_color="#10b981", button_hover_color="#059669")
        status_menu.set("pending")
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

            success, msg = self.auth.register(username, password, role, status)
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
        dialog.configure(fg_color="#0a0e1a")
        dialog.grab_set()
        dialog.resizable(False, False)

        ctk.CTkLabel(dialog, text="✏️ Edit User", font=("Inter", 20, "bold"),
                    text_color="#f8fafc").pack(pady=(16, 4))
        ctk.CTkLabel(dialog, text="Update username, role, status or reset password.",
                    font=("Inter", 12), text_color="#94a3b8").pack(pady=(0, 10))

        form = ctk.CTkFrame(dialog, fg_color="#111827", corner_radius=14)
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
        status_menu = ctk.CTkOptionMenu(form, values=["pending", "active", "blocked", "suspended"], height=36,
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
        if new_status not in ["pending", "active", "blocked", "suspended"]:
            messagebox.showerror("Error", "Invalid status selected!")
            return
        if username == self.admin['username'] and new_status != "active":
            messagebox.showerror("Protected", "You cannot block, suspend, or set pending the currently logged-in admin.")
            return

        if not silent and not messagebox.askyesno("Confirm Status Change", f"Change '{username}' status to {new_status}?"):
            if refresh:
                self.switch_view("users")
            return

        conn = sqlite3.connect(self.auth.db_path)
        conn.execute("UPDATE users SET status = ? WHERE username = ?", (new_status, username))
        conn.commit()
        conn.close()

        # Keep database status and storage/revoked.txt synchronized.
        # Before this, Reactivate changed only DB status to active, but the username
        # stayed in revoked.txt, so the user dashboard still blocked operations.
        try:
            from core.revocation import revoke_user as add_to_revocation_list, unrevoke_user
            if new_status == "active":
                unrevoke_user(username)
            elif new_status == "blocked":
                add_to_revocation_list(username)
        except Exception as e:
            print(f"Revocation sync warning for {username}: {e}")

        self.audit.log(self.admin['username'], "ADMIN_STATUS_CHANGE", "SUCCESS", details=f"{username} → {new_status}")

        # Real-world approval: certificate/key is issued only when admin activates user
        if new_status == "active" and username != self.admin['username']:
            self._issue_user_certificate(username)

        if refresh:
            self.switch_view("users")

    def _issue_user_certificate(self, username):
        """Generate RSA keys and CA-signed certificate for an approved user."""
        try:
            private_path = f"storage/keystores/{username}_private.pem"
            public_path = f"storage/keystores/{username}_public.pem"
            cert_path = f"storage/certs/{username}_cert.pem"

            if not os.path.exists("storage/ca/ca_private.pem") or not os.path.exists("storage/ca/ca_cert.pem"):
                create_root_ca()

            # Generate a fresh keypair only if missing
            if not os.path.exists(private_path) or not os.path.exists(public_path):
                private_key, public_key = generate_key_pair(username, None)
            else:
                from cryptography.hazmat.primitives import serialization
                with open(public_path, "rb") as f:
                    public_key = serialization.load_pem_public_key(f.read())

            ca_key = load_ca_private_key()
            if not os.path.exists(cert_path):
                issue_certificate(ca_key, public_key, username)

            self.audit.log(self.admin['username'], "ADMIN_CERT_ISSUE", "SUCCESS", details=f"Issued keys/certificate for {username}")
            return True

        except Exception as e:
            self.audit.log(self.admin['username'], "ADMIN_CERT_ISSUE", "FAILED", details=f"{username}: {e}")
            messagebox.showerror("Certificate Issue Failed", f"Could not issue certificate for {username}:\n{e}")
            return False

    def approve_user(self, username):
        if messagebox.askyesno("Approve User", f"Approve '{username}' and issue signing certificate?"):
            self.change_status(username, "active")

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
        from main import show_login
        show_login()