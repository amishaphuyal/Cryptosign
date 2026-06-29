import customtkinter as ctk
from tkinter import messagebox, filedialog, simpledialog
import sys
import os
import sqlite3
import shutil
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.auth_system import AuthSystem
from core.audit_logger import AuditLogger
from core.batch_sign import batch_sign_folder


class UserDashboard:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.username = user.get("username", "")
        self.auth = AuthSystem()
        self.audit = AuditLogger()

        # User interface settings
        self.user_settings = self._load_user_settings()
        self._configure_theme_palette()

        # Sign dialog variables
        self.sign_mode = ctk.StringVar(value="external")
        self.sign_file_path = ctk.StringVar(value="")

        self.root.title(f"CryptoSign - User Dashboard ({self.username})")
        self.root.geometry("1200x800")
        self.root.configure(fg_color=self.BG)
        self.root.minsize(1000, 700)

        ctk.set_appearance_mode("dark" if self.user_settings.get("dark_mode", True) else "light")
        ctk.set_default_color_theme("dark-blue")

        self.current_view = "dashboard"
        self.build_sidebar()
        self.build_main_content()
        self.show_dashboard()


    # ---------------- UI HELPERS ----------------
    BG = "#0b1120"
    SIDEBAR = "#111827"
    CARD = "#162033"
    CARD_DARK = "#0f172a"
    BORDER = "#273449"
    TEXT = "#f8fafc"
    TEXT_2 = "#cbd5e1"
    MUTED = "#94a3b8"
    PRIMARY = "#6366f1"
    SUCCESS = "#10b981"
    WARNING = "#f59e0b"
    DANGER = "#ef4444"
    INFO = "#38bdf8"

    def _card(self, parent, **kwargs):
        opts = {
            "fg_color": self.CARD,
            "corner_radius": 14,
            "border_width": 1,
            "border_color": self.BORDER,
        }
        opts.update(kwargs)
        return ctk.CTkFrame(parent, **opts)

    def _section_title(self, parent, title, subtitle=None):
        ctk.CTkLabel(parent, text=title, font=("Inter", 18, "bold"), text_color=self.TEXT).pack(anchor="w", padx=22, pady=(20, 4))
        if subtitle:
            ctk.CTkLabel(parent, text=subtitle, font=("Inter", 12), text_color=self.MUTED).pack(anchor="w", padx=22, pady=(0, 14))

    def _status_color(self, result):
        return self.SUCCESS if result in ["SUCCESS", "VALID", "ACTIVE", "OK"] else self.DANGER

    def _small_icon(self, parent, color=None):
        icon = ctk.CTkFrame(parent, fg_color=color or self.PRIMARY, width=9, height=9, corner_radius=4)
        icon.pack_propagate(False)
        return icon

    def _settings_file_path(self):
        os.makedirs("storage/settings", exist_ok=True)
        return f"storage/settings/{self.username}_ui_settings.json"

    def _load_user_settings(self):
        defaults = {
            "dark_mode": True,
            "compact_rows": False,
            "application_alerts": True,
            "certificate_alerts": True,
        }
        try:
            import json
            path = self._settings_file_path()
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                defaults.update({k: saved.get(k, v) for k, v in defaults.items()})
        except Exception:
            pass
        return defaults

    def _save_user_settings(self):
        try:
            import json
            path = self._settings_file_path()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.user_settings, f, indent=2)
        except Exception as e:
            messagebox.showerror("Settings Error", f"Could not save settings:\n{e}")

    def _configure_theme_palette(self):
        if self.user_settings.get("dark_mode", True):
            self.BG = "#0b1120"
            self.SIDEBAR = "#111827"
            self.CARD = "#162033"
            self.CARD_DARK = "#0f172a"
            self.BORDER = "#273449"
            self.TEXT = "#f8fafc"
            self.TEXT_2 = "#cbd5e1"
            self.MUTED = "#94a3b8"
            self.ROW_BG = "#0b1222"
            self.ROW_ALT = "#111827"
            self.HEADER_BG = "#1f2a44"
            self.ROW_HOVER = "#1f2a44"
            self.INPUT_BG = "#111827"
            self.TEXTBOX_BG = "#111827"
        else:
            self.BG = "#f8fafc"
            self.SIDEBAR = "#e2e8f0"
            self.CARD = "#ffffff"
            self.CARD_DARK = "#f1f5f9"
            self.BORDER = "#cbd5e1"
            self.TEXT = "#0f172a"
            self.TEXT_2 = "#1e293b"
            self.MUTED = "#64748b"
            self.ROW_BG = "#ffffff"
            self.ROW_ALT = "#f8fafc"
            self.HEADER_BG = "#e8eef7"
            self.ROW_HOVER = "#e2e8f0"
            self.INPUT_BG = "#ffffff"
            self.TEXTBOX_BG = "#ffffff"

        self.PRIMARY = "#6366f1"
        self.SUCCESS = "#10b981"
        self.WARNING = "#f59e0b"
        self.DANGER = "#ef4444"
        self.INFO = "#38bdf8"
        self.compact_row_height = 34 if self.user_settings.get("compact_rows", False) else 44

    def _rebuild_after_settings_change(self, keep_view="settings"):
        self._configure_theme_palette()
        ctk.set_appearance_mode("dark" if self.user_settings.get("dark_mode", True) else "light")
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.configure(fg_color=self.BG)
        self.current_view = keep_view
        self.build_sidebar()
        self.build_main_content()
        self.switch_view(keep_view)

    def _show_local_notification(self, title, message, level="info"):
        if not self.user_settings.get("application_alerts", True):
            return

        color = {
            "success": self.SUCCESS,
            "warning": self.WARNING,
            "error": self.DANGER,
            "info": self.PRIMARY,
        }.get(level, self.PRIMARY)

        try:
            toast = ctk.CTkToplevel(self.root)
            toast.title(title)
            toast.geometry("340x105")
            toast.configure(fg_color=self.CARD)
            toast.resizable(False, False)
            toast.attributes("-topmost", True)

            self.root.update_idletasks()
            x = self.root.winfo_rootx() + self.root.winfo_width() - 370
            y = self.root.winfo_rooty() + 95
            toast.geometry(f"+{max(x, 0)}+{max(y, 0)}")

            ctk.CTkFrame(toast, fg_color=color, width=6, corner_radius=0).pack(side="left", fill="y")
            body = ctk.CTkFrame(toast, fg_color="transparent")
            body.pack(side="left", fill="both", expand=True, padx=14, pady=12)
            ctk.CTkLabel(body, text=title, font=("Inter", 13, "bold"), text_color=self.TEXT).pack(anchor="w")
            ctk.CTkLabel(body, text=message, font=("Inter", 11), text_color=self.TEXT_2, wraplength=285, justify="left").pack(anchor="w", pady=(5, 0))
            toast.after(2600, toast.destroy)
        except Exception:
            pass

    def build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self.root, fg_color=self.SIDEBAR, width=260, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=120)
        logo_frame.pack(fill="x", pady=(28, 8))

        logo_box = ctk.CTkFrame(logo_frame, fg_color=self.PRIMARY, width=54, height=54, corner_radius=16)
        logo_box.pack(pady=(0, 8))
        logo_box.pack_propagate(False)
        ctk.CTkLabel(logo_box, text="CS", font=("Inter", 18, "bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(logo_frame, text="CryptoSign", font=("Inter", 20, "bold"), text_color=self.PRIMARY).pack()
        ctk.CTkLabel(logo_frame, text="Secure Digital Document Signing", font=("Inter", 11), text_color=self.MUTED).pack(pady=(3, 0))

        ctk.CTkFrame(self.sidebar, fg_color=self.BORDER, height=1).pack(fill="x", padx=22, pady=16)

        self.menu_buttons = {}
        menu_items = [
            ("Dashboard", "dashboard"),
            ("My Documents", "documents"),
            ("Batch Sign", "batch_sign"),
            ("Activity Log", "activity"),
            ("My Profile", "profile"),
            ("Settings", "settings"),
        ]

        for text, view in menu_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                font=("Inter", 13, "bold"),
                height=44,
                fg_color="transparent",
                hover_color=self.ROW_HOVER,
                text_color=self.TEXT_2,
                anchor="w",
                corner_radius=10,
                command=lambda v=view: self.switch_view(v),
            )
            btn.pack(fill="x", padx=12, pady=3)
            self.menu_buttons[view] = btn

        ctk.CTkFrame(self.sidebar, fg_color=self.BORDER, height=1).pack(fill="x", padx=22, pady=18)

        user_frame = ctk.CTkFrame(self.sidebar, fg_color=self.CARD_DARK, corner_radius=12, border_width=1, border_color=self.BORDER)
        user_frame.pack(fill="x", padx=12, pady=8)

        avatar = ctk.CTkFrame(user_frame, fg_color=self.PRIMARY, width=34, height=34, corner_radius=17)
        avatar.pack(pady=(14, 5))
        avatar.pack_propagate(False)
        ctk.CTkLabel(avatar, text=self.username[:1].upper(), font=("Inter", 14, "bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(user_frame, text=self.username, font=("Inter", 13, "bold"), text_color=self.TEXT).pack(pady=(0, 2))
        ctk.CTkLabel(user_frame, text="Standard User", font=("Inter", 11), text_color=self.MUTED).pack(pady=(0, 14))

        ctk.CTkButton(
            self.sidebar,
            text="Logout",
            font=("Inter", 13, "bold"),
            height=44,
            fg_color=self.DANGER,
            hover_color="#dc2626",
            text_color="white",
            corner_radius=10,
            command=self.logout,
        ).pack(fill="x", padx=12, pady=18)

    def build_main_content(self):
        self.main_content = ctk.CTkFrame(self.root, fg_color=self.BG, corner_radius=0)
        self.main_content.pack(side="right", fill="both", expand=True)

        self.header = ctk.CTkFrame(self.main_content, fg_color="transparent", height=72)
        self.header.pack(fill="x", padx=30, pady=(20, 8))
        self.header.pack_propagate(False)

        self.header_title = ctk.CTkLabel(self.header, text="Dashboard", font=("Inter", 28, "bold"), text_color=self.TEXT)
        self.header_title.pack(side="left")

        self.refresh_btn = ctk.CTkButton(
            self.header,
            text="Refresh",
            width=120,
            height=42,
            font=("Inter", 13, "bold"),
            fg_color=self.PRIMARY,
            hover_color="#4f46e5",
            text_color="white",
            corner_radius=10,
            command=self.refresh_current_view,
        )
        self.refresh_btn.pack(side="right", padx=5)

        self.notify_btn = ctk.CTkButton(
            self.header,
            text=self.get_alert_text(),
            width=110,
            height=42,
            font=("Inter", 13, "bold"),
            fg_color=self.CARD_DARK,
            hover_color=self.ROW_HOVER,
            text_color=self.DANGER if self.get_alert_count() > 0 else self.WARNING,
            corner_radius=10,
            command=self.show_alerts,
        )
        self.notify_btn.pack(side="right", padx=5)

        ctk.CTkFrame(self.main_content, fg_color=self.PRIMARY, height=2).pack(fill="x", padx=30, pady=(0, 14))

        self.content_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=30, pady=(0, 24))

    def get_alerts(self):
        alerts = []

        private_path = f"storage/keystores/{self.username}_private.pem"
        public_path = f"storage/keystores/{self.username}_public.pem"
        cert_path = f"storage/certs/{self.username}_cert.pem"

        if self.user_settings.get("certificate_alerts", True):
            if not os.path.exists(private_path):
                alerts.append("Private key is missing. You cannot sign new documents until admin re-issues your certificate.")
            if not os.path.exists(public_path):
                alerts.append("Public key file is missing from local keystore.")
            if not os.path.exists(cert_path):
                alerts.append("X.509 certificate is missing. Contact admin for certificate approval/re-issue.")

            try:
                from core.revocation import is_revoked
                if is_revoked(self.username):
                    alerts.append("Your signing certificate is revoked. Signing and trust validation may fail.")
            except Exception:
                pass

        if self.user_settings.get("application_alerts", True):
            try:
                conn = sqlite3.connect("storage/audit.db")
                failed_count = conn.execute("""
                    SELECT COUNT(*) FROM audit_log
                    WHERE username = ? AND result IN ('FAILED', 'INVALID', 'ERROR', 'NOT_SIGNED', 'BLOCKED')
                """, (self.username,)).fetchone()[0]
                conn.close()
                if failed_count > 0:
                    alerts.append(f"You have {failed_count} failed or blocked security activities in your audit log.")
            except Exception:
                pass

        return alerts

    def get_alert_count(self):
        return len(self.get_alerts())

    def get_alert_text(self):
        count = self.get_alert_count()
        return f"Alerts {count}" if count > 0 else "Alerts"

    def refresh_alerts(self):
        if hasattr(self, "notify_btn"):
            count = self.get_alert_count()
            self.notify_btn.configure(
                text=self.get_alert_text(),
                text_color=self.DANGER if count > 0 else self.WARNING,
            )

    def show_alerts(self):
        if not self.user_settings.get("application_alerts", True):
            messagebox.showinfo("Alerts", "Application alerts are disabled in Settings.")
            return

        alerts = self.get_alerts()
        if not alerts:
            messagebox.showinfo("Alerts", "No active alerts. Your account and certificate status look normal.")
            return

        message = "Active alerts:\n\n" + "\n".join([f"• {item}" for item in alerts])
        messagebox.showwarning("Alerts", message)

    def refresh_current_view(self):
        self.refresh_btn.configure(text="Refreshing...")
        self.root.update()

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if self.current_view == "dashboard":
            self.show_dashboard()
        elif self.current_view == "documents":
            self.show_documents()
        elif self.current_view == "batch_sign":
            self.show_batch_sign()
        elif self.current_view == "activity":
            self.show_activity()
        elif self.current_view == "profile":
            self.show_profile()
        elif self.current_view == "settings":
            self.show_settings()

        self.refresh_btn.configure(text="Refresh")
        self.refresh_alerts()
        self.root.update()

    def switch_view(self, view):
        for v, btn in self.menu_buttons.items():
            if v == view:
                btn.configure(fg_color=self.PRIMARY, text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=self.TEXT_2)

        self.current_view = view

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if view == "dashboard":
            self.show_dashboard()
        elif view == "documents":
            self.show_documents()
        elif view == "batch_sign":
            self.show_batch_sign()
        elif view == "activity":
            self.show_activity()
        elif view == "profile":
            self.show_profile()
        elif view == "settings":
            self.show_settings()

    def show_dashboard(self):
        self.header_title.configure(text="Dashboard")
        self.refresh_alerts()
        self.current_view = "dashboard"

        # IMPORTANT FIX:
        # quick_sign(), quick_verify(), quick_encrypt(), etc. call show_dashboard()
        # directly after an operation. If we do not clear the old widgets first,
        # the dashboard gets appended again at the bottom (duplicate Welcome card).
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Keep sidebar highlight correct even when dashboard is opened directly.
        if hasattr(self, "menu_buttons"):
            for v, btn in self.menu_buttons.items():
                if v == "dashboard":
                    btn.configure(fg_color=self.PRIMARY, text_color="white")
                else:
                    btn.configure(fg_color="transparent", text_color=self.TEXT_2)

        has_keys = os.path.exists(f"storage/keystores/{self.username}_private.pem")

        if not has_keys:
            self.show_setup_wizard()
            return

        # Dashboard uses compact spacing so Recent Activity rows stay visible
        # on 1200x800 / laptop screens without needing to scroll the dashboard.

        # Welcome card - compact
        welcome = ctk.CTkFrame(self.content_frame, fg_color=self.CARD, corner_radius=12)
        welcome.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            welcome,
            text=f"Welcome back, {self.username}!",
            font=("Inter", 21, "bold"),
            text_color=self.TEXT,
        ).pack(anchor="w", padx=20, pady=(14, 3))
        ctk.CTkLabel(
            welcome,
            text="Here's your document signing overview",
            font=("Inter", 12),
            text_color=self.TEXT_2,
        ).pack(anchor="w", padx=20, pady=(0, 14))

        # Stats cards - compact height
        stats_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 10))

        try:
            conn = sqlite3.connect("storage/audit.db")
            cursor = conn.execute("""
                SELECT action, COUNT(*)
                FROM audit_log
                WHERE username = ? COLLATE NOCASE
                GROUP BY action
            """, (self.username,))
            stats = dict(cursor.fetchall())
            conn.close()
        except Exception:
            stats = {}

        signed_count = stats.get("SIGN", 0) + stats.get("BATCH_SIGN", 0)
        self.create_stat_card(stats_frame, "Signed", str(signed_count), self.PRIMARY)
        self.create_stat_card(stats_frame, "Verified", str(stats.get("VERIFY", 0)), self.SUCCESS)
        self.create_stat_card(stats_frame, "Encrypted", str(stats.get("ENCRYPT", 0)), self.WARNING)
        self.create_stat_card(stats_frame, "Decrypted", str(stats.get("DECRYPT", 0)), self.DANGER)

        # Quick Actions - compact buttons
        actions_frame = ctk.CTkFrame(self.content_frame, fg_color=self.CARD, corner_radius=12)
        actions_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            actions_frame,
            text="Quick Actions",
            font=("Inter", 16, "bold"),
            text_color=self.TEXT,
        ).pack(anchor="w", padx=20, pady=(14, 8))

        grid = ctk.CTkFrame(actions_frame, fg_color="transparent")
        grid.pack(fill="x", padx=20, pady=(0, 14))

        row1 = ctk.CTkFrame(grid, fg_color="transparent")
        row1.pack(fill="x", pady=3)
        self.create_action_btn(row1, "Sign Document", self.quick_sign, self.PRIMARY)
        self.create_action_btn(row1, "Verify Document", self.quick_verify, self.SUCCESS)

        row2 = ctk.CTkFrame(grid, fg_color="transparent")
        row2.pack(fill="x", pady=3)
        self.create_action_btn(row2, "Encrypt File", self.quick_encrypt, self.WARNING)
        self.create_action_btn(row2, "Decrypt File", self.quick_decrypt, self.DANGER)

        row3 = ctk.CTkFrame(grid, fg_color="transparent")
        row3.pack(fill="x", pady=3)
        self.create_action_btn(row3, "Batch Sign", self.show_batch_sign, self.PRIMARY)
        self.create_action_btn(row3, "File Hash", self.quick_hash, self.WARNING)

        # Recent Activity - visible rows, no inner vertical scroll on dashboard
        self.show_dashboard_recent_activity()

    def show_dashboard_recent_activity(self):
        """Recent Activity panel for dashboard.

        This version lets the card cover the remaining dashboard space and
        keeps only the activity rows scrollable.
        """
        activity_frame = self._card(self.content_frame)
        activity_frame.pack(fill="both", expand=True, pady=(0, 0))

        header_row = ctk.CTkFrame(activity_frame, fg_color="transparent")
        header_row.pack(fill="x", padx=22, pady=(14, 6))

        ctk.CTkLabel(
            header_row,
            text="Recent Activity",
            font=("Inter", 17, "bold"),
            text_color=self.TEXT,
        ).pack(side="left")

        ctk.CTkLabel(
            header_row,
            text="Scrollable activity history",
            font=("Inter", 11),
            text_color=self.MUTED,
        ).pack(side="right")

        # Fixed table header: this part will not scroll.
        table_header = ctk.CTkFrame(activity_frame, fg_color="transparent")
        table_header.pack(fill="x", padx=22, pady=(0, 4))

        for col, weight in enumerate([1, 5, 1, 1]):
            table_header.grid_columnconfigure(col, weight=weight, uniform="dashboard_activity")

        headers = ["Action", "File", "Result", "Date"]
        for col, title in enumerate(headers):
            ctk.CTkLabel(
                table_header,
                text=title,
                font=("Inter", 11, "bold"),
                text_color=self.TEXT_2,
                anchor="w",
            ).grid(row=0, column=col, sticky="ew", padx=(10, 10), pady=(0, 6))

        ctk.CTkFrame(activity_frame, fg_color=self.BORDER, height=1).pack(fill="x", padx=22, pady=(0, 6))

        # Only this rows area scrolls. The whole dashboard stays stable.
        rows_scroll = ctk.CTkScrollableFrame(
            activity_frame,
            fg_color="transparent",
            scrollbar_button_color=self.BORDER,
            scrollbar_button_hover_color=self.PRIMARY,
        )
        rows_scroll.pack(fill="both", expand=True, padx=22, pady=(0, 14))

        for col, weight in enumerate([1, 5, 1, 1]):
            rows_scroll.grid_columnconfigure(col, weight=weight, uniform="dashboard_activity")

        try:
            conn = sqlite3.connect("storage/audit.db")
            cursor = conn.execute("""
                SELECT timestamp, action, file_name, result
                FROM audit_log
                WHERE username = ? COLLATE NOCASE
                ORDER BY timestamp DESC
                LIMIT 50
            """, (self.username,))
            activities = cursor.fetchall()
            conn.close()
        except Exception as e:
            activities = []
            self._dashboard_activity_empty(rows_scroll, f"Could not load activity: {e}", row_index=0)

        if activities:
            for index, (timestamp, action, file_name, result) in enumerate(activities):
                self.create_dashboard_activity_row(rows_scroll, timestamp, action, file_name, result, index)
        elif not rows_scroll.winfo_children():
            self._dashboard_activity_empty(
                rows_scroll,
                "No recent activity yet. Sign, Verify, Encrypt, Decrypt, Batch Sign, or File Hash will appear here.",
                row_index=0,
            )

    def _dashboard_activity_empty(self, parent, message, row_index=0):
        ctk.CTkLabel(
            parent,
            text=message,
            font=("Inter", 11),
            text_color=self.TEXT_2,
            anchor="w",
        ).grid(row=row_index, column=0, columnspan=4, sticky="ew", padx=10, pady=10)

    def create_dashboard_activity_row(self, parent, timestamp, action, file_name, result, row_index):
        action_color = {
            "SIGN": self.PRIMARY,
            "VERIFY": self.SUCCESS,
            "ENCRYPT": self.WARNING,
            "DECRYPT": self.DANGER,
            "HASH": self.INFO,
            "BATCH_SIGN": "#8b5cf6",
            "SETUP": self.WARNING,
        }.get(action or "", self.TEXT_2)

        result_color = self._status_color(result)
        date_text = (timestamp or "")[:10] if timestamp else "N/A"
        display_file = file_name or "-"
        if len(display_file) > 82:
            display_file = display_file[:79] + "..."

        row_bg = self.ROW_ALT if row_index % 2 == 0 else self.ROW_BG

        values = [
            (action or "-", action_color, "bold"),
            (display_file, self.TEXT_2, "normal"),
            (result or "-", result_color, "bold"),
            (date_text, self.MUTED, "normal"),
        ]

        for col, (text, color, weight) in enumerate(values):
            cell = ctk.CTkFrame(parent, fg_color=row_bg, corner_radius=7)
            cell.grid(row=row_index, column=col, sticky="ew", padx=(4 if col == 0 else 0, 4), pady=3)
            font_value = ("Inter", 10, "bold") if weight == "bold" else ("Inter", 10)
            ctk.CTkLabel(
                cell,
                text=text,
                font=font_value,
                text_color=color,
                anchor="w",
            ).pack(fill="x", padx=8, pady=7)

    def show_batch_sign(self):
        self.header_title.configure(text=" Batch Sign Documents")

        if not os.path.exists(f"storage/keystores/{self.username}_private.pem"):
            self.show_setup_wizard()
            return

        container = ctk.CTkFrame(self.content_frame, fg_color=self.CARD, corner_radius=12)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(container, text=" Batch Document Signing", 
                    font=("Inter", 24, "bold"), text_color=self.TEXT).pack(pady=(30, 10))

        ctk.CTkLabel(container, text="Sign multiple documents at once from a folder", 
                    font=("Inter", 14), text_color=self.TEXT_2).pack(pady=(0, 25))

        # Settings Frame
        settings_frame = ctk.CTkFrame(container, fg_color=self.ROW_BG, corner_radius=10)
        settings_frame.pack(fill="x", padx=40, pady=10)

        mode_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        mode_frame.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkLabel(mode_frame, text="Signature Mode:", 
                    font=("Inter", 13, "bold"), text_color=self.TEXT).pack(side="left", padx=(0, 15))

        self.batch_mode = ctk.StringVar(value="external")

        ctk.CTkRadioButton(mode_frame, text="External (.sig file)", 
                          variable=self.batch_mode, value="external",
                          font=("Inter", 12), text_color=self.TEXT,
                          fg_color=self.PRIMARY).pack(side="left", padx=10)

        ctk.CTkRadioButton(mode_frame, text="Embedded (PDF only)", 
                          variable=self.batch_mode, value="embedded",
                          font=("Inter", 12), text_color=self.TEXT,
                          fg_color=self.PRIMARY).pack(side="left", padx=10)

        types_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        types_frame.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(types_frame, text="File Types:", 
                    font=("Inter", 13, "bold"), text_color=self.TEXT).pack(side="left", padx=(0, 15))

        self.pdf_var = ctk.BooleanVar(value=True)
        self.docx_var = ctk.BooleanVar(value=True)
        self.xlsx_var = ctk.BooleanVar(value=False)
        self.txt_var = ctk.BooleanVar(value=True)

        ctk.CTkCheckBox(types_frame, text="PDF", variable=self.pdf_var,
                       font=("Inter", 11), text_color=self.TEXT_2,
                       fg_color=self.PRIMARY).pack(side="left", padx=8)
        ctk.CTkCheckBox(types_frame, text="DOCX", variable=self.docx_var,
                       font=("Inter", 11), text_color=self.TEXT_2,
                       fg_color=self.PRIMARY).pack(side="left", padx=8)
        ctk.CTkCheckBox(types_frame, text="XLSX", variable=self.xlsx_var,
                       font=("Inter", 11), text_color=self.TEXT_2,
                       fg_color=self.PRIMARY).pack(side="left", padx=8)
        ctk.CTkCheckBox(types_frame, text="TXT", variable=self.txt_var,
                       font=("Inter", 11), text_color=self.TEXT_2,
                       fg_color=self.PRIMARY).pack(side="left", padx=8)

        folder_frame = ctk.CTkFrame(container, fg_color="transparent")
        folder_frame.pack(fill="x", padx=40, pady=15)

        self.folder_path_var = ctk.StringVar(value="")

        ctk.CTkEntry(folder_frame, textvariable=self.folder_path_var,
                    width=500, height=44, font=("Inter", 12),
                    fg_color=self.ROW_BG, border_color=self.BORDER,
                    text_color=self.TEXT, placeholder_text="Select folder...").pack(side="left", padx=(0, 10))

        ctk.CTkButton(folder_frame, text=" Browse", width=110, height=44,
                     font=("Inter", 12), fg_color=self.PRIMARY, 
                     hover_color="#4f46e5", corner_radius=10,
                     command=self.browse_batch_folder).pack(side="left")

        self.progress_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.progress_frame.pack(fill="x", padx=40, pady=10)

        self.progress_label = ctk.CTkLabel(self.progress_frame, text="Ready to start", 
                                          font=("Inter", 12), text_color=self.TEXT_2)
        self.progress_label.pack(pady=5)

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, width=600, height=20,
                                            fg_color=self.ROW_BG, progress_color=self.PRIMARY)
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0)

        self.batch_result_label = ctk.CTkLabel(container, text="", 
                                                font=("Inter", 14), text_color=self.TEXT)
        self.batch_result_label.pack(pady=10)

        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(pady=25)

        ctk.CTkButton(btn_frame, text=" Start Batch Sign", width=200, height=50,
                     font=("Inter", 16, "bold"), fg_color=self.SUCCESS, 
                     hover_color="#059669", corner_radius=12,
                     command=self.execute_batch_sign).pack(side="left", padx=10)

        ctk.CTkButton(btn_frame, text=" Reset", width=120, height=50,
                     font=("Inter", 14), fg_color=self.MUTED, 
                     hover_color="#475569", corner_radius=12,
                     command=self.reset_batch_sign).pack(side="left", padx=10)

    def browse_batch_folder(self):
        file = filedialog.askopenfilename(
            title=" Select Any File in Target Folder",
            filetypes=[("All Files", "*.*")],
            parent=self.root
        )
        if file:
            folder = os.path.dirname(file)
            self.folder_path_var.set(folder)
            try:
                files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
                messagebox.showinfo("Folder Selected", 
                    f" Folder: {os.path.basename(folder)}\n"
                    f" Total Files: {len(files)}\n\n"
                    f"Supported files will be signed based on your selection.")
            except:
                pass

    def reset_batch_sign(self):
        self.folder_path_var.set("")
        self.progress_bar.set(0)
        self.progress_label.configure(text="Ready to start")
        self.batch_result_label.configure(text="")

    def execute_batch_sign(self):
        if self._is_signing_blocked():
            return

        folder_path = self.folder_path_var.get()

        if not folder_path:
            messagebox.showerror("Error", "Please select a folder first!")
            return

        if not os.path.exists(folder_path):
            messagebox.showerror("Error", "Selected folder does not exist!")
            return

        extensions = []
        if self.pdf_var.get(): extensions.append('.pdf')
        if self.docx_var.get(): extensions.append('.docx')
        if self.xlsx_var.get(): extensions.append('.xlsx')
        if self.txt_var.get(): extensions.append('.txt')

        if not extensions:
            messagebox.showerror("Error", "Please select at least one file type!")
            return

        mode = self.batch_mode.get()

        self.progress_label.configure(text="Scanning folder...")
        self.progress_bar.set(0.1)
        self.root.update()

        def on_progress(current, total, filename):
            progress = current / total if total > 0 else 0
            self.progress_bar.set(progress)
            self.progress_label.configure(
                text=f"Signing: {filename} ({current}/{total})"
            )
            self.root.update()

        try:
            results = batch_sign_folder(
                username=self.username,
                mode=mode,
                password=None,
                folder_path=folder_path,
                file_types=extensions,
                progress_callback=on_progress
            )

            if results is None:
                self.progress_label.configure(text="Cancelled")
                return

            if results.get('blocked'):
                block_msg = results['errors'][0][1] if results.get('errors') else "Signing blocked because certificate is revoked."
                self.progress_label.configure(text="Signing blocked")
                self.batch_result_label.configure(text=block_msg, text_color=self.DANGER)
                messagebox.showerror("Batch Signing Blocked", block_msg)
                self.audit.log(self.username, "BATCH_SIGN", "BLOCKED", details=block_msg)
                return

            signed = results['signed']
            failed = results['failed']
            total = signed + failed

            if failed == 0:
                self.batch_result_label.configure(
                    text=f" Success! Signed {signed}/{total} documents",
                    text_color=self.SUCCESS
                )
                self.audit.log(self.username, "BATCH_SIGN", "SUCCESS", 
                              details=f"Signed {signed} files in {folder_path}")
            else:
                self.batch_result_label.configure(
                    text=f" Signed {signed}/{total} documents ({failed} failed)",
                    text_color=self.WARNING
                )
                self.audit.log(self.username, "BATCH_SIGN", "PARTIAL", 
                              details=f"Signed {signed}/{total}, Failed {failed}")

            if results['errors']:
                error_text = "\n".join([f"{os.path.basename(f)}: {e}" for f, e in results['errors'][:5]])
                if len(results['errors']) > 5:
                    error_text += f"\n... and {len(results['errors']) - 5} more errors"
                messagebox.showwarning("Batch Sign Complete", 
                    f"Completed with some errors:\n\n{error_text}")

            messagebox.showinfo("Batch Sign Complete", 
                f"Batch signing finished!\n\n"
                f" Signed: {signed}\n"
                f" Failed: {failed}\n"
                f" Folder: {folder_path}")

            self.show_dashboard()

        except Exception as e:
            self.progress_label.configure(text=f"Error: {str(e)}")
            self.batch_result_label.configure(text=f" Error: {str(e)}", text_color=self.DANGER)
            messagebox.showerror("Batch Sign Error", str(e))
            self.audit.log(self.username, "BATCH_SIGN", "FAILED", details=str(e))

    def show_setup_wizard(self):
        wizard = ctk.CTkFrame(self.content_frame, fg_color=self.CARD, corner_radius=12)
        wizard.pack(fill="both", expand=True, padx=50, pady=50)

        ctk.CTkLabel(wizard, text="⏳ Certificate Not Issued Yet",
                    font=("Inter", 24, "bold"), text_color=self.TEXT).pack(pady=(30, 10))

        ctk.CTkLabel(wizard,
                    text="Your account is active, but your signing keys/certificate are missing.",
                    font=("Inter", 14), text_color=self.TEXT_2).pack(pady=(0, 10))

        ctk.CTkLabel(wizard,
                    text="In the real-world approval workflow, only the administrator/CA can issue signing certificates.",
                    font=("Inter", 13), text_color=self.TEXT_2, wraplength=650).pack(pady=(0, 20))

        ctk.CTkLabel(wizard,
                    text="Please contact the administrator to approve/re-issue your certificate.",
                    font=("Inter", 14, "bold"), text_color=self.WARNING, wraplength=650).pack(pady=15)

        ctk.CTkButton(wizard, text=" Refresh", width=180, height=45,
                     font=("Inter", 14, "bold"), fg_color=self.PRIMARY, hover_color="#4f46e5",
                     corner_radius=12, command=self.show_dashboard).pack(pady=25)

    def setup_keys(self):
        messagebox.showwarning(
            "Admin Approval Required",
            "Users cannot issue their own signing certificate. Please ask the administrator to approve/re-issue your account certificate."
        )
        self.audit.log(self.username, "SETUP", "BLOCKED", details="Self certificate issue blocked by admin-approval workflow")

    def create_stat_card(self, parent, title, value, color):
        card = self._card(parent)
        card.configure(height=82)
        card.pack(side="left", expand=True, fill="x", padx=6, pady=4)
        card.pack_propagate(False)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(12, 2))
        self._small_icon(top, color).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(top, text=title, font=("Inter", 12, "bold"), text_color=self.TEXT_2).pack(side="left")
        ctk.CTkLabel(card, text=value, font=("Inter", 27, "bold"), text_color=color).pack(anchor="w", padx=18, pady=(0, 8))

    def create_action_btn(self, parent, text, command, color):
        hover = "#4f46e5" if color == self.PRIMARY else "#059669" if color == self.SUCCESS else "#d97706" if color == self.WARNING else "#dc2626"
        btn = ctk.CTkButton(parent, text=text, width=300, height=42,
                           font=("Inter", 13, "bold"), fg_color=color, hover_color=hover,
                           text_color="#ffffff", corner_radius=10, command=command)
        btn.pack(side="left", padx=8, expand=True, fill="x")
        return btn

    def create_activity_item(self, parent, action, file_name, result, time):
        row = ctk.CTkFrame(parent, fg_color=self.ROW_BG, corner_radius=9, border_width=1, border_color=self.BORDER, height=48)
        row.pack(fill="x", pady=4)
        row.pack_propagate(False)

        for idx, weight in enumerate([2, 2, 5, 2, 2]):
            row.grid_columnconfigure(idx, weight=weight)

        safe_time = time or ""
        display_time = safe_time[11:19] if len(safe_time) >= 19 else "N/A"
        display_date = safe_time[:10] if len(safe_time) >= 10 else "N/A"
        display_file = file_name or "-"
        if len(display_file) > 58:
            display_file = display_file[:55] + "..."

        dot_wrap = ctk.CTkFrame(row, fg_color="transparent")
        dot_wrap.grid(row=0, column=0, sticky="ew", padx=14, pady=12)
        self._small_icon(dot_wrap, self.PRIMARY).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(dot_wrap, text=display_time, font=("Inter", 11), text_color=self.TEXT_2, anchor="w").pack(side="left")

        ctk.CTkLabel(row, text=action, font=("Inter", 11, "bold"),
                    text_color=self.PRIMARY, anchor="w").grid(row=0, column=1, sticky="ew", padx=14, pady=12)
        ctk.CTkLabel(row, text=display_file, font=("Inter", 11),
                    text_color=self.TEXT_2, anchor="w").grid(row=0, column=2, sticky="ew", padx=14, pady=12)
        ctk.CTkLabel(row, text=result, font=("Inter", 11, "bold"),
                    text_color=self._status_color(result), anchor="w").grid(row=0, column=3, sticky="ew", padx=14, pady=12)
        ctk.CTkLabel(row, text=display_date, font=("Inter", 11),
                    text_color=self.MUTED, anchor="w").grid(row=0, column=4, sticky="ew", padx=14, pady=12)

    def show_documents(self):
        self.header_title.configure(text="My Documents")

        # Whole My Documents page scrolls, so every section remains reachable
        # even when the window height is small.
        page = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        page.pack(fill="both", expand=True)

        def unique_files(file_list):
            seen = set()
            cleaned = []
            for item in file_list:
                try:
                    file_path = item[2]
                except Exception:
                    continue
                if file_path in seen:
                    continue
                seen.add(file_path)
                cleaned.append(item)
            return cleaned

        signed_files = unique_files(
            self.audit.get_user_files(self.username, 'signed') + self._scan_signed_files()
        )
        hash_files = unique_files(self._scan_hash_files())
        encrypted_files = unique_files(
            self.audit.get_user_files(self.username, 'encrypted') + self._scan_encrypted_files()
        )
        decrypted_files = unique_files(self._scan_decrypted_files())
        # Certificates and keys are intentionally kept only in Settings > Security
        # to avoid duplicate certificate/key sections in My Documents.
        # Hash Documents is placed near the top so it is easy to see after using File Hash.
        doc_types = [
            ("Signed Documents", signed_files, "#6366f1", "signed"),
            ("Hash Documents", hash_files, "#38bdf8", "hash"),
            ("Encrypted Files", encrypted_files, "#f59e0b", "encrypted"),
            ("Decrypted Files", decrypted_files, "#8b5cf6", "decrypted"),
        ]

        # Summary count cards
        summary = ctk.CTkFrame(page, fg_color="transparent")
        summary.pack(fill="x", pady=(0, 12))

        for title, files, color, ftype in doc_types[:4]:
            card = ctk.CTkFrame(
                summary,
                fg_color=self.CARD,
                corner_radius=12,
                border_width=1,
                border_color=self.BORDER,
            )
            card.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            ctk.CTkLabel(
                card,
                text=title,
                font=("Inter", 12, "bold"),
                text_color=self.TEXT_2,
            ).pack(anchor="w", padx=16, pady=(12, 2))
            ctk.CTkLabel(
                card,
                text=str(len(files)),
                font=("Inter", 26, "bold"),
                text_color=color,
            ).pack(anchor="w", padx=16, pady=(0, 12))

        for title, files, color, ftype in doc_types:
            frame = ctk.CTkFrame(
                page,
                fg_color=self.CARD,
                corner_radius=12,
                border_width=1,
                border_color=self.BORDER,
            )
            frame.pack(fill="x", pady=10)

            header = ctk.CTkFrame(frame, fg_color="transparent")
            header.pack(fill="x", padx=20, pady=(14, 8))

            ctk.CTkLabel(
                header,
                text=title,
                font=("Inter", 16, "bold"),
                text_color=color,
            ).pack(side="left")

            ctk.CTkLabel(
                header,
                text=f"{len(files)} files",
                font=("Inter", 11),
                text_color=self.MUTED,
            ).pack(side="right")

            # Hash section gets the same document controls as other sections:
            # Open, Save As, and Delete. Rows are scrollable inside each section.
            scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent", height=150)
            scroll.pack(fill="x", padx=20, pady=(0, 14))

            if not files:
                empty_text = "No hash documents found" if ftype == "hash" else "No files found"
                ctk.CTkLabel(
                    scroll,
                    text=empty_text,
                    font=("Inter", 11),
                    text_color=self.MUTED,
                ).pack(pady=22)
            else:
                for file_info in files:
                    self.create_file_item(scroll, file_info, ftype)

    def _scan_signed_files(self):
        files = []
        sig_dir = f"storage/signatures/{self.username}"
        if os.path.exists(sig_dir):
            for f in os.listdir(sig_dir):
                if f.endswith('.sig') or f.endswith('_signed.pdf'):
                    fpath = os.path.join(sig_dir, f)
                    files.append((
                        datetime.fromtimestamp(os.path.getmtime(fpath)).isoformat(),
                        'signed', fpath, f, os.path.getsize(fpath), 'active'
                    ))

        emb_dir = f"storage/signatures/{self.username}/embedded"
        if os.path.exists(emb_dir):
            for f in os.listdir(emb_dir):
                if f.endswith('_signed.pdf'):
                    fpath = os.path.join(emb_dir, f)
                    files.append((
                        datetime.fromtimestamp(os.path.getmtime(fpath)).isoformat(),
                        'signed', fpath, f, os.path.getsize(fpath), 'active'
                    ))

        return files

    def _scan_encrypted_files(self):
        files = []
        enc_dir = f"storage/encrypted/{self.username}"
        if os.path.exists(enc_dir):
            for f in os.listdir(enc_dir):
                if f.endswith('.bin'):
                    fpath = os.path.join(enc_dir, f)
                    files.append((
                        datetime.fromtimestamp(os.path.getmtime(fpath)).isoformat(),
                        'encrypted', fpath, f, os.path.getsize(fpath), 'active'
                    ))

        return files

    def _scan_decrypted_files(self):
        files = []
        dec_dir = f"storage/encrypted/{self.username}/decrypted"
        if os.path.exists(dec_dir):
            for f in os.listdir(dec_dir):
                if not f.startswith('.'):
                    fpath = os.path.join(dec_dir, f)
                    if os.path.isfile(fpath):
                        files.append((
                            datetime.fromtimestamp(os.path.getmtime(fpath)).isoformat(),
                            'decrypted', fpath, f, os.path.getsize(fpath), 'active'
                        ))

        return files

    def _scan_hash_files(self):
        files = []
        seen_paths = set()

        db_files = self.audit.get_user_files(self.username, 'hash')
        for file_info in db_files:
            timestamp, file_type, file_path, original_name, file_size, status = file_info
            if file_path not in seen_paths and os.path.exists(file_path):
                seen_paths.add(file_path)
                files.append(file_info)

        user_hash_dir = f"storage/hash/{self.username}"
        if os.path.exists(user_hash_dir):
            try:
                for f in os.listdir(user_hash_dir):
                    if f.endswith('_sha256.txt') or f.endswith('_hash.txt'):
                        fpath = os.path.join(user_hash_dir, f)
                        if os.path.isfile(fpath) and fpath not in seen_paths:
                            seen_paths.add(fpath)
                            files.append((
                                datetime.fromtimestamp(os.path.getmtime(fpath)).isoformat(),
                                'hash', fpath, f, os.path.getsize(fpath), 'active'
                            ))
            except:
                pass

        hash_dirs = [
            "storage",
            f"storage/{self.username}",
            f"storage/encrypted/{self.username}",
            f"storage/signatures/{self.username}",
            f"storage/encrypted/{self.username}/decrypted",
        ]

        for hash_dir in hash_dirs:
            if os.path.exists(hash_dir):
                try:
                    for f in os.listdir(hash_dir):
                        if f.endswith('_sha256.txt') or f.endswith('_hash.txt'):
                            fpath = os.path.join(hash_dir, f)
                            if os.path.isfile(fpath) and fpath not in seen_paths:
                                seen_paths.add(fpath)
                                files.append((
                                    datetime.fromtimestamp(os.path.getmtime(fpath)).isoformat(),
                                    'hash', fpath, f, os.path.getsize(fpath), 'active'
                                ))
                except:
                    pass

        return files

    def _get_cert_files(self):
        files = []
        key_and_cert_paths = [
            (f"storage/certs/{self.username}_cert.pem", f"{self.username}_cert.pem", "Certificate"),
            (f"storage/keystores/{self.username}_public.pem", f"{self.username}_public.pem", "Public Key"),
            (f"storage/keystores/{self.username}_private.pem", f"{self.username}_private.pem", "Private Key"),
        ]

        for path, display_name, label in key_and_cert_paths:
            if os.path.exists(path) and os.path.isfile(path):
                files.append((
                    datetime.fromtimestamp(os.path.getmtime(path)).isoformat(),
                    'cert', path, display_name,
                    os.path.getsize(path), 'active'
                ))

        return files

    def create_file_item(self, parent, file_info, ftype):
        timestamp, file_type, file_path, original_name, file_size, status = file_info

        frame = ctk.CTkFrame(parent, fg_color=self.ROW_BG, corner_radius=8)
        frame.pack(fill="x", pady=2)

        icons = {
            "signed": "", 
            "encrypted": "", 
            "decrypted": "",
            "hash": "",
            "cert": ""
        }
        icon = icons.get(ftype, "")

        display_name = original_name[:40] + "..." if len(original_name) > 40 else original_name

        ctk.CTkLabel(frame, text=f"{icon} {display_name}", 
                    font=("Inter", 11), text_color=self.TEXT).pack(side="left", padx=15, pady=8)

        size_str = self._format_size(file_size)
        ctk.CTkLabel(frame, text=size_str, 
                    font=("Inter", 10), text_color=self.MUTED).pack(side="left", padx=5)

        actions = ctk.CTkFrame(frame, fg_color="transparent")
        actions.pack(side="right", padx=10)

        btn_text = "View" if ftype == "cert" else "Open"
        ctk.CTkButton(actions, text=btn_text, width=60, height=25,
                     font=("Inter", 10), fg_color=self.PRIMARY, hover_color="#4f46e5",
                     corner_radius=6, command=lambda p=file_path: self._open_file(p)).pack(side="left", padx=2)

        ctk.CTkButton(actions, text=" Save As", width=70, height=25,
                     font=("Inter", 10), fg_color=self.SUCCESS, hover_color="#059669",
                     corner_radius=6, command=lambda p=file_path, n=original_name: self._save_file_as(p, n)).pack(side="left", padx=2)

        ctk.CTkButton(actions, text="", width=30, height=25,
                     font=("Inter", 10), fg_color=self.DANGER, hover_color="#dc2626",
                     corner_radius=6, command=lambda p=file_path, f=frame: self._delete_file(p, f)).pack(side="left", padx=2)

    def _format_size(self, size):
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f} KB"
        else:
            return f"{size/(1024*1024):.1f} MB"

    def _open_file(self, file_path):
        if not os.path.exists(file_path):
            messagebox.showerror("Error", f"File not found!\n{file_path}")
            return

        if file_path.endswith('.pem') or file_path.endswith('.crt') or file_path.endswith('.cert'):
            self._view_cert_file(file_path)
            return

        try:
            if os.name == 'nt':
                os.startfile(file_path)
            elif os.name == 'posix':
                import subprocess
                subprocess.run(['xdg-open', file_path], check=True)
            messagebox.showinfo("Open", f"Opening: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {str(e)}")

    def _view_cert_file(self, cert_path):
        if not os.path.exists(cert_path):
            messagebox.showerror("Error", f"Certificate not found!\n{cert_path}")
            return

        try:
            with open(cert_path, 'r') as f:
                content = f.read()

            dialog = ctk.CTkToplevel(self.root)
            dialog.title(f"Certificate - {os.path.basename(cert_path)}")
            dialog.geometry("650x450")
            dialog.configure(fg_color=self.BG)
            dialog.resizable(False, False)
            dialog.transient(self.root)
            dialog.grab_set()

            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() - 650) // 2
            y = (dialog.winfo_screenheight() - 450) // 2
            dialog.geometry(f"+{x}+{y}")

            ctk.CTkLabel(dialog, text=" Certificate Viewer", 
                        font=("Inter", 18, "bold"), text_color=self.PRIMARY).pack(pady=(20, 10))

            ctk.CTkLabel(dialog, text=f" {os.path.basename(cert_path)}", 
                        font=("Inter", 12), text_color=self.TEXT_2).pack(pady=(0, 10))

            text_box = ctk.CTkTextbox(dialog, width=600, height=320, font=("Courier", 10),
                                      fg_color=self.TEXTBOX_BG, text_color=self.TEXT, border_width=1, border_color=self.BORDER)
            text_box.pack(pady=10)
            text_box.insert("1.0", content)
            text_box.configure(state="disabled")

            ctk.CTkButton(dialog, text="Close", width=100, height=35,
                         font=("Inter", 12), fg_color=self.MUTED, hover_color="#475569",
                         corner_radius=8, command=dialog.destroy).pack(pady=15)

        except Exception as e:
            messagebox.showerror("Error", f"Could not read certificate: {str(e)}")

    def _save_file_as(self, file_path, original_name):
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "File not found!")
            return

        from tkinter import filedialog
        save_path = filedialog.asksaveasfilename(
            defaultextension=os.path.splitext(original_name)[1],
            initialfile=original_name,
            title="Save File As"
        )

        if save_path:
            try:
                shutil.copy2(file_path, save_path)
                messagebox.showinfo("Success", f"File saved to:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")

    def _delete_file(self, file_path, frame_widget):
        if messagebox.askyesno("Confirm Delete", f"Delete {os.path.basename(file_path)}?"):
            try:
                self.audit.delete_user_file(self.username, file_path)

                if os.path.exists(file_path):
                    os.remove(file_path)

                    parent_dir = os.path.dirname(file_path)
                    if os.path.exists(parent_dir) and not os.listdir(parent_dir):
                        os.rmdir(parent_dir)
                        print(f" Removed empty folder: {parent_dir}")

                        grandparent = os.path.dirname(parent_dir)
                        if os.path.exists(grandparent) and not os.listdir(grandparent):
                            os.rmdir(grandparent)
                            print(f" Removed empty user folder: {grandparent}")

                frame_widget.destroy()
                messagebox.showinfo("Deleted", "File deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete: {str(e)}")

    def show_activity(self):
        self.header_title.configure(text="Activity Log")

        toolbar = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            toolbar,
            text="Your account activity and document operations",
            font=("Inter", 13),
            text_color=self.MUTED,
        ).pack(side="left")

        ctk.CTkButton(
            toolbar,
            text="Export My Logs",
            width=150,
            height=40,
            font=("Inter", 12, "bold"),
            fg_color=self.PRIMARY,
            hover_color="#4f46e5",
            corner_radius=10,
            command=self.export_my_logs,
        ).pack(side="right")

        # One clean table card. Header and rows use EXACT same fixed column widths,
        # so Time / Action / File / Result / Details always stay aligned.
        table_frame = self._card(self.content_frame)
        table_frame.pack(fill="both", expand=True)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(1, weight=1)

        self.activity_col_widths = [180, 120, 330, 120, 440]

        header = ctk.CTkFrame(table_frame, fg_color=self.HEADER_BG, corner_radius=10, height=56)
        header.grid(row=0, column=0, sticky="ew", padx=22, pady=(20, 8))
        header.pack_propagate(False)

        for col_name, col_width in zip(["Time", "Action", "File", "Result", "Details"], self.activity_col_widths):
            ctk.CTkLabel(
                header,
                text=col_name,
                width=col_width,
                font=("Inter", 12, "bold"),
                text_color=self.TEXT_2,
                anchor="w",
            ).pack(side="left", padx=6, pady=16)

        scroll = ctk.CTkScrollableFrame(table_frame, fg_color="transparent")
        scroll.grid(row=1, column=0, sticky="nsew", padx=22, pady=(0, 20))

        try:
            conn = sqlite3.connect("storage/audit.db")
            cursor = conn.execute(
                """
                SELECT id, timestamp, username, action, file_name, file_hash, result, details, ip_address
                FROM audit_log
                WHERE username = ? COLLATE NOCASE
                ORDER BY timestamp DESC
                """,
                (self.username,),
            )
            logs = cursor.fetchall()
            conn.close()

            if not logs:
                ctk.CTkLabel(
                    scroll,
                    text="No activity found",
                    font=("Inter", 13),
                    text_color=self.MUTED,
                ).pack(pady=30)
                return

            for log in logs:
                self.create_log_row(scroll, log)

        except Exception as e:
            ctk.CTkLabel(
                scroll,
                text=f"No activity found: {e}",
                font=("Inter", 12),
                text_color=self.MUTED,
            ).pack(pady=20)

    def create_log_row(self, parent, log):
        id, timestamp, username, action, file_name, file_hash, result, details, ip = log

        row = ctk.CTkFrame(
            parent,
            fg_color=self.CARD_DARK,
            corner_radius=8,
            height=54,
            border_width=1,
            border_color=self.BORDER,
        )
        row.pack(fill="x", pady=4)
        row.pack_propagate(False)

        def shorten(value, max_len):
            value = str(value or "-")
            return value if len(value) <= max_len else value[:max_len - 3] + "..."

        time_text = (timestamp or "N/A")[:19]
        action_text = action or "-"
        file_text = shorten(file_name or "-", 44)
        result_text = result or "-"
        details_text = shorten(details or "-", 64)

        values = [time_text, action_text, file_text, result_text, details_text]
        colors = [self.MUTED, self.PRIMARY, self.TEXT_2, self._status_color(result), self.MUTED]
        fonts = [
            ("Consolas", 10),
            ("Inter", 11, "bold"),
            ("Inter", 11),
            ("Inter", 11, "bold"),
            ("Inter", 10),
        ]

        for value, width, color, font in zip(values, self.activity_col_widths, colors, fonts):
            ctk.CTkLabel(
                row,
                text=value,
                width=width,
                font=font,
                text_color=color,
                anchor="w",
            ).pack(side="left", padx=6, pady=14)

    def show_profile(self):
        self.header_title.configure(text="My Profile")

        # Main container
        main_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        main_container.pack(fill="both", expand=True)

        # ═══════════════════════════════════════════════════════
        # TOP SECTION: Profile Card + Stats
        # ═══════════════════════════════════════════════════════
        top_section = ctk.CTkFrame(main_container, fg_color="transparent")
        top_section.pack(fill="x", pady=(0, 15))

        # Profile Card
        profile_card = ctk.CTkFrame(top_section, fg_color=self.CARD, corner_radius=16)
        profile_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Avatar & Basic Info
        avatar_frame = ctk.CTkFrame(profile_card, fg_color="transparent")
        avatar_frame.pack(fill="x", padx=25, pady=(25, 15))

        # Avatar circle
        avatar = ctk.CTkFrame(avatar_frame, fg_color=self.PRIMARY, width=80, height=80, corner_radius=40)
        avatar.pack(side="left")
        avatar.pack_propagate(False)
        ctk.CTkLabel(avatar, text=self.username[0].upper(), font=("Inter", 32, "bold"), 
                    text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        info_frame = ctk.CTkFrame(avatar_frame, fg_color="transparent")
        info_frame.pack(side="left", padx=(20, 0), fill="y")

        ctk.CTkLabel(info_frame, text=self.username, 
                    font=("Inter", 22, "bold"), text_color=self.TEXT).pack(anchor="w")

        role_badge = ctk.CTkFrame(info_frame, fg_color=self.PRIMARY, corner_radius=6)
        role_badge.pack(anchor="w", pady=(5, 0))
        ctk.CTkLabel(role_badge, text="  Standard User  ", 
                    font=("Inter", 11, "bold"), text_color="white").pack(padx=8, pady=3)

        # Profile Details Grid
        details_grid = ctk.CTkFrame(profile_card, fg_color="transparent")
        details_grid.pack(fill="x", padx=25, pady=(0, 20))

        # Get user details from DB
        try:
            conn = sqlite3.connect(self.auth.db_path)
            cursor = conn.execute("SELECT created_at, last_login, status, first_login FROM users WHERE username = ?", 
                                (self.username,))
            user_data = cursor.fetchone()
            conn.close()
            created_at = user_data[0][:10] if user_data and user_data[0] else "N/A"
            last_login = user_data[1][:10] if user_data and user_data[1] else "N/A"
            status = user_data[2] if user_data else "active"
            first_login = user_data[3] if user_data else 0
        except:
            created_at = "N/A"
            last_login = "N/A"
            status = "active"
            first_login = 0

        details = [
            (" Joined", created_at),
            (" Last Login", last_login),
            (" Status", status.upper()),
            (" First Login", "Yes" if first_login else "No"),
        ]

        for i, (label, value) in enumerate(details):
            detail_frame = ctk.CTkFrame(details_grid, fg_color=self.ROW_BG, corner_radius=8)
            detail_frame.pack(side="left", fill="both", expand=True, padx=(0 if i==0 else 8, 8 if i<3 else 0), pady=5)
            ctk.CTkLabel(detail_frame, text=label, font=("Inter", 10), 
                        text_color=self.MUTED).pack(anchor="w", padx=12, pady=(8, 0))
            ctk.CTkLabel(detail_frame, text=value, font=("Inter", 12, "bold"), 
                        text_color=self.TEXT).pack(anchor="w", padx=12, pady=(0, 8))

        # Quick Stats Card
        stats_card = ctk.CTkFrame(top_section, fg_color=self.CARD, corner_radius=16, width=320)
        stats_card.pack(side="right", fill="y", padx=(10, 0))
        stats_card.pack_propagate(False)

        ctk.CTkLabel(stats_card, text=" Activity Overview", 
                    font=("Inter", 16, "bold"), text_color=self.TEXT).pack(anchor="w", padx=20, pady=(20, 15))

        try:
            conn = sqlite3.connect("storage/audit.db")
            cursor = conn.execute("""
                SELECT action, COUNT(*) FROM audit_log 
                WHERE username = ? GROUP BY action
            """, (self.username,))
            stats = dict(cursor.fetchall())

            total_files = conn.execute("""
                SELECT COUNT(*) FROM user_files WHERE username = ? AND status = 'active'
            """, (self.username,)).fetchone()[0]
            conn.close()
        except:
            stats = {}
            total_files = 0

        signed = stats.get("SIGN", 0) + stats.get("BATCH_SIGN", 0)
        verified = stats.get("VERIFY", 0)
        encrypted = stats.get("ENCRYPT", 0)
        decrypted = stats.get("DECRYPT", 0)
        hashed = stats.get("HASH", 0)
        total_activities = sum(stats.values())

        stat_items = [
            (" Signed", signed, "#6366f1"),
            (" Verified", verified, "#10b981"),
            (" Encrypted", encrypted, "#f59e0b"),
            (" Decrypted", decrypted, "#ef4444"),
            (" Hashed", hashed, "#ec4899"),
            (" Total Files", total_files, "#8b5cf6"),
        ]

        for label, value, color in stat_items:
            row = ctk.CTkFrame(stats_card, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=3)
            ctk.CTkLabel(row, text=label, font=("Inter", 12), 
                        text_color=self.TEXT_2).pack(side="left")
            ctk.CTkLabel(row, text=str(value), font=("Inter", 14, "bold"), 
                        text_color=color).pack(side="right")

        ctk.CTkFrame(stats_card, fg_color=self.BORDER, height=1).pack(fill="x", padx=20, pady=(10, 10))

        total_row = ctk.CTkFrame(stats_card, fg_color="transparent")
        total_row.pack(fill="x", padx=20, pady=(0, 15))
        ctk.CTkLabel(total_row, text=" Total Activities", font=("Inter", 13, "bold"), 
                    text_color=self.TEXT).pack(side="left")
        ctk.CTkLabel(total_row, text=str(total_activities), font=("Inter", 18, "bold"), 
                    text_color=self.PRIMARY).pack(side="right")

        # ═══════════════════════════════════════════════════════
        # MIDDLE SECTION: Security & Key Management
        # ═══════════════════════════════════════════════════════
        middle_section = ctk.CTkFrame(main_container, fg_color="transparent")
        middle_section.pack(fill="x", pady=(0, 15))

        # Security Card
        security_card = ctk.CTkFrame(middle_section, fg_color=self.CARD, corner_radius=16)
        security_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ctk.CTkLabel(security_card, text=" Security Settings", 
                    font=("Inter", 16, "bold"), text_color=self.TEXT).pack(anchor="w", padx=20, pady=(20, 15))

        # Password section
        pass_frame = ctk.CTkFrame(security_card, fg_color=self.ROW_BG, corner_radius=10)
        pass_frame.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(pass_frame, text=" Password", 
                    font=("Inter", 13, "bold"), text_color=self.TEXT).pack(anchor="w", padx=15, pady=(12, 5))
        ctk.CTkLabel(pass_frame, text="Change your account password. Minimum 6 characters required.", 
                    font=("Inter", 11), text_color=self.MUTED).pack(anchor="w", padx=15, pady=(0, 10))

        ctk.CTkButton(pass_frame, text=" Change Password", width=180, height=38,
                     font=("Inter", 12, "bold"), fg_color=self.PRIMARY, hover_color="#4f46e5",
                     corner_radius=10, command=self.change_password).pack(anchor="w", padx=15, pady=(0, 12))

        # Key Status section
        key_frame = ctk.CTkFrame(security_card, fg_color=self.ROW_BG, corner_radius=10)
        key_frame.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(key_frame, text=" Cryptographic Keys", 
                    font=("Inter", 13, "bold"), text_color=self.TEXT).pack(anchor="w", padx=15, pady=(12, 5))

        has_private = os.path.exists(f"storage/keystores/{self.username}_private.pem")
        has_public = os.path.exists(f"storage/keystores/{self.username}_public.pem")
        has_cert = os.path.exists(f"storage/certs/{self.username}_cert.pem")

        key_statuses = [
            ("Private Key", has_private, "#10b981", "#ef4444"),
            ("Public Key", has_public, "#10b981", "#ef4444"),
            ("Certificate", has_cert, "#10b981", "#ef4444"),
        ]

        for name, exists, ok_color, bad_color in key_statuses:
            row = ctk.CTkFrame(key_frame, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=2)
            ctk.CTkLabel(row, text=f"  {name}", font=("Inter", 11), 
                        text_color=self.TEXT_2).pack(side="left")
            status_text = " Active" if exists else " Missing"
            status_color = ok_color if exists else bad_color
            ctk.CTkLabel(row, text=status_text, font=("Inter", 11, "bold"), 
                        text_color=status_color).pack(side="right")

        if not has_private:
            ctk.CTkButton(key_frame, text=" Setup Keys", width=150, height=35,
                         font=("Inter", 12, "bold"), fg_color=self.SUCCESS, hover_color="#059669",
                         corner_radius=10, command=self.setup_keys).pack(anchor="w", padx=15, pady=(8, 12))
        else:
            ctk.CTkButton(key_frame, text=" View Certificate", width=150, height=35,
                         font=("Inter", 12), fg_color=self.PRIMARY, hover_color="#4f46e5",
                         corner_radius=10, command=lambda: self._view_cert_file(f"storage/certs/{self.username}_cert.pem")).pack(anchor="w", padx=15, pady=(8, 12))

        # Storage Usage Card
        storage_card = ctk.CTkFrame(middle_section, fg_color=self.CARD, corner_radius=16, width=320)
        storage_card.pack(side="right", fill="y", padx=(10, 0))
        storage_card.pack_propagate(False)

        ctk.CTkLabel(storage_card, text=" Storage Usage", 
                    font=("Inter", 16, "bold"), text_color=self.TEXT).pack(anchor="w", padx=20, pady=(20, 15))

        # Calculate storage
        storage_data = []
        total_size = 0

        for folder, label, color in [
            (f"storage/signatures/{self.username}", "Signatures", "#6366f1"),
            (f"storage/encrypted/{self.username}", "Encrypted", "#f59e0b"),
            (f"storage/hash/{self.username}", "Hash Files", "#ec4899"),
        ]:
            size = 0
            count = 0
            if os.path.exists(folder):
                for root, dirs, files in os.walk(folder):
                    for file in files:
                        fp = os.path.join(root, file)
                        size += os.path.getsize(fp)
                        count += 1
            storage_data.append((label, count, size, color))
            total_size += size

        # Progress bar for total
        ctk.CTkLabel(storage_card, text=f"Total: {self._format_size(total_size)}", 
                    font=("Inter", 14, "bold"), text_color=self.TEXT).pack(anchor="w", padx=20)

        progress = ctk.CTkProgressBar(storage_card, width=280, height=8, 
                                     fg_color=self.ROW_BG, progress_color=self.PRIMARY)
        progress.pack(padx=20, pady=(5, 15))
        progress.set(0.3 if total_size > 0 else 0)

        for label, count, size, color in storage_data:
            row = ctk.CTkFrame(storage_card, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=3)
            ctk.CTkLabel(row, text=f"{label}", font=("Inter", 11), 
                        text_color=self.TEXT_2).pack(side="left")
            ctk.CTkLabel(row, text=f"{count} files · {self._format_size(size)}", 
                        font=("Inter", 11), text_color=color).pack(side="right")

        # ═══════════════════════════════════════════════════════
        # BOTTOM SECTION: Danger Zone
        # ═══════════════════════════════════════════════════════
        danger_card = ctk.CTkFrame(main_container, fg_color=self.CARD, corner_radius=16)
        danger_card.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(danger_card, text=" Danger Zone", 
                    font=("Inter", 16, "bold"), text_color=self.DANGER).pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(danger_card, text="These actions are irreversible. Please proceed with caution.", 
                    font=("Inter", 11), text_color=self.MUTED).pack(anchor="w", padx=20, pady=(0, 15))

        danger_actions = ctk.CTkFrame(danger_card, fg_color="transparent")
        danger_actions.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkButton(danger_actions, text=" Export All My Data", width=180, height=40,
                     font=("Inter", 12, "bold"), fg_color=self.WARNING, hover_color="#d97706",
                     corner_radius=10, command=self.export_all_data).pack(side="left", padx=5)

        ctk.CTkButton(danger_actions, text=" Delete My Account", width=180, height=40,
                     font=("Inter", 12, "bold"), fg_color=self.DANGER, hover_color="#dc2626",
                     corner_radius=10, command=self.delete_my_account).pack(side="left", padx=5)

    def export_all_data(self):
        """Export all user data to a zip file"""
        import zipfile
        from datetime import datetime

        export_dir = f"storage/exports/{self.username}"
        os.makedirs(export_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_path = f"{export_dir}/export_{timestamp}.zip"

        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add audit logs
                try:
                    conn = sqlite3.connect("storage/audit.db")
                    cursor = conn.execute("""
                        SELECT * FROM audit_log WHERE username = ? ORDER BY timestamp DESC
                    """, (self.username,))
                    logs = cursor.fetchall()
                    conn.close()

                    import csv
                    log_csv = f"{export_dir}/audit_logs.csv"
                    with open(log_csv, 'w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(['ID', 'Timestamp', 'Username', 'Action', 'File', 'Hash', 'Result', 'Details', 'IP'])
                        writer.writerows(logs)
                    zipf.write(log_csv, "audit_logs.csv")
                    os.remove(log_csv)
                except:
                    pass

                # Add files
                for folder in [
                    f"storage/signatures/{self.username}",
                    f"storage/encrypted/{self.username}",
                    f"storage/hash/{self.username}",
                ]:
                    if os.path.exists(folder):
                        for root, dirs, files in os.walk(folder):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, "storage")
                                zipf.write(file_path, arcname)

                # Add certificate
                cert_path = f"storage/certs/{self.username}_cert.pem"
                if os.path.exists(cert_path):
                    zipf.write(cert_path, f"certificate/{self.username}_cert.pem")

            messagebox.showinfo("Export Complete", 
                f"All your data exported to:\n{zip_path}\n\nIncludes: audit logs, files, and certificate.")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")


    def show_settings(self):
        self.header_title.configure(text="Settings")

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        container = self._card(self.content_frame)
        container.pack(fill="both", expand=True)

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=28, pady=(20, 10))

        ctk.CTkLabel(
            header,
            text="Application Settings",
            font=("Inter", 24, "bold"),
            text_color=self.TEXT,
        ).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text="Manage appearance, notifications, security and account data.",
            font=("Inter", 13),
            text_color=self.MUTED,
        ).pack(anchor="w", pady=(5, 0))

        body = ctk.CTkScrollableFrame(container, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=28, pady=(8, 22))
        body.grid_columnconfigure(0, weight=1, uniform="settings_cols")
        body.grid_columnconfigure(1, weight=1, uniform="settings_cols")

        # Appearance card
        appearance = self._card(body, fg_color=self.CARD_DARK)
        appearance.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 12))
        self._section_title(appearance, "Appearance", "Change theme and table spacing.")

        self.dark_mode = ctk.BooleanVar(value=self.user_settings.get("dark_mode", True))
        self._settings_row(
            appearance,
            "Dark mode",
            "Turn off to switch the dashboard to light mode.",
            self.dark_mode,
            self.toggle_theme,
        )

        self.compact_mode = ctk.BooleanVar(value=self.user_settings.get("compact_rows", False))
        self._settings_row(
            appearance,
            "Compact rows",
            "Use smaller rows in tables such as Activity Log and My Documents.",
            self.compact_mode,
            self.toggle_compact_rows,
        )

        theme_text = "Current theme: Dark" if self.user_settings.get("dark_mode", True) else "Current theme: Light"
        ctk.CTkLabel(
            appearance,
            text=theme_text,
            font=("Inter", 11, "bold"),
            text_color=self.PRIMARY,
        ).pack(anchor="w", padx=22, pady=(2, 18))

        # Notifications card
        notification = self._card(body, fg_color=self.CARD_DARK)
        notification.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 12))
        self._section_title(notification, "Notifications", "Control alerts shown inside the app.")

        self.notifications = ctk.BooleanVar(value=self.user_settings.get("application_alerts", True))
        self._settings_row(
            notification,
            "Application alerts",
            "Show popups after important actions and alerts.",
            self.notifications,
            self.toggle_notifications,
        )

        self.cert_alerts = ctk.BooleanVar(value=self.user_settings.get("certificate_alerts", True))
        self._settings_row(
            notification,
            "Certificate alerts",
            "Warn when certificate, public key or private key files are missing.",
            self.cert_alerts,
            self.toggle_cert_alerts,
        )

        alert_state = "Alerts are ON" if self.user_settings.get("application_alerts", True) else "Alerts are OFF"
        ctk.CTkLabel(
            notification,
            text=alert_state,
            font=("Inter", 11, "bold"),
            text_color=self.SUCCESS if self.user_settings.get("application_alerts", True) else self.DANGER,
        ).pack(anchor="w", padx=22, pady=(2, 18))

        # Security card - compact 2-column button layout
        security = self._card(body, fg_color=self.CARD_DARK)
        security.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(0, 12))
        self._section_title(security, "Security", "View keys/certificate and manage password.")

        status_box = ctk.CTkFrame(security, fg_color=self.ROW_BG, corner_radius=10, border_width=1, border_color=self.BORDER)
        status_box.pack(fill="x", padx=22, pady=(0, 12))

        cert_path = f"storage/certs/{self.username}_cert.pem"
        pub_path = f"storage/keystores/{self.username}_public.pem"
        priv_path = f"storage/keystores/{self.username}_private.pem"

        self._security_status_line(status_box, "Certificate", cert_path)
        self._security_status_line(status_box, "Public key", pub_path)
        self._security_status_line(status_box, "Private key", priv_path)

        btn_grid = ctk.CTkFrame(security, fg_color="transparent")
        btn_grid.pack(fill="x", padx=22, pady=(0, 18))
        btn_grid.grid_columnconfigure(0, weight=1)
        btn_grid.grid_columnconfigure(1, weight=1)

        self._settings_button(btn_grid, "Change Password", self.PRIMARY, self.change_password, 0, 0)
        self._settings_button(btn_grid, "View Certificate", self.INFO, lambda: self._view_cert_file(cert_path), 0, 1)
        self._settings_button(btn_grid, "View Public Key", self.SUCCESS, lambda: self._view_cert_file(pub_path), 1, 0)
        self._settings_button(btn_grid, "View Private Key", self.DANGER, lambda: self._view_cert_file(priv_path), 1, 1)

        # Danger card
        danger = self._card(body, fg_color="#160f18" if self.user_settings.get("dark_mode", True) else "#fff1f2", border_color="#3b1d2b" if self.user_settings.get("dark_mode", True) else "#fecdd3")
        danger.grid(row=1, column=1, sticky="nsew", padx=(10, 0), pady=(0, 12))
        self._section_title(danger, "Danger Zone", "Sensitive actions. Use carefully.")

        danger_grid = ctk.CTkFrame(danger, fg_color="transparent")
        danger_grid.pack(fill="x", padx=22, pady=(4, 18))
        danger_grid.grid_columnconfigure(0, weight=1)
        danger_grid.grid_columnconfigure(1, weight=1)

        self._settings_button(danger_grid, "Export All My Data", self.WARNING, self.export_all_data, 0, 0)
        self._settings_button(danger_grid, "Delete My Account", self.DANGER, self.delete_my_account, 0, 1)

        help_card = self._card(body, fg_color=self.CARD_DARK)
        help_card.grid(row=2, column=0, columnspan=2, sticky="ew", padx=0, pady=(0, 8))
        ctk.CTkLabel(
            help_card,
            text="Settings are saved automatically for this user and applied after app restart or immediately after toggling.",
            font=("Inter", 12),
            text_color=self.TEXT_2,
            wraplength=900,
        ).pack(anchor="w", padx=22, pady=16)

    def _settings_button(self, parent, text, color, command, row, column):
        ctk.CTkButton(
            parent,
            text=text,
            height=38,
            font=("Inter", 12, "bold"),
            fg_color=color,
            hover_color=color,
            text_color="white",
            corner_radius=10,
            command=command,
        ).grid(row=row, column=column, sticky="ew", padx=5, pady=5)

    def _security_status_line(self, parent, label, path):
        exists = os.path.exists(path)
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=4)
        ctk.CTkLabel(row, text=label, font=("Inter", 11, "bold"), text_color=self.TEXT_2, width=95, anchor="w").pack(side="left")
        ctk.CTkLabel(row, text="Available" if exists else "Missing", font=("Inter", 11, "bold"), text_color=self.SUCCESS if exists else self.DANGER, width=80, anchor="w").pack(side="left")
        ctk.CTkLabel(row, text=path, font=("Inter", 10), text_color=self.MUTED, anchor="w").pack(side="left", fill="x", expand=True)

    def _settings_row(self, parent, title, description, variable, command=None):
        row = ctk.CTkFrame(parent, fg_color=self.ROW_BG, corner_radius=10, border_width=1, border_color=self.BORDER)
        row.pack(fill="x", padx=22, pady=6)

        text = ctk.CTkFrame(row, fg_color="transparent")
        text.pack(side="left", fill="x", expand=True, padx=16, pady=10)
        ctk.CTkLabel(text, text=title, font=("Inter", 13, "bold"), text_color=self.TEXT).pack(anchor="w")
        ctk.CTkLabel(text, text=description, font=("Inter", 11), text_color=self.MUTED, wraplength=360, justify="left").pack(anchor="w", pady=(3, 0))

        ctk.CTkSwitch(
            row,
            text="",
            variable=variable,
            command=command,
            progress_color=self.PRIMARY,
            fg_color=self.BORDER,
        ).pack(side="right", padx=16)

    def toggle_theme(self):
        self.user_settings["dark_mode"] = bool(self.dark_mode.get())
        self._save_user_settings()
        self._show_local_notification("Theme Updated", "Dashboard theme changed.", "success")
        self._rebuild_after_settings_change("settings")

    def toggle_compact_rows(self):
        self.user_settings["compact_rows"] = bool(self.compact_mode.get())
        self._save_user_settings()
        self._show_local_notification("Layout Updated", "Compact row setting saved.", "success")
        self.show_settings()

    def toggle_notifications(self):
        self.user_settings["application_alerts"] = bool(self.notifications.get())
        self._save_user_settings()
        self.refresh_alerts()
        if self.user_settings["application_alerts"]:
            self._show_local_notification("Notifications Enabled", "Application alerts will now be shown.", "success")
        else:
            messagebox.showinfo("Notifications Disabled", "Application alerts are now turned off.")
        self.show_settings()

    def toggle_cert_alerts(self):
        self.user_settings["certificate_alerts"] = bool(self.cert_alerts.get())
        self._save_user_settings()
        self.refresh_alerts()
        state = "enabled" if self.user_settings["certificate_alerts"] else "disabled"
        self._show_local_notification("Certificate Alerts", f"Certificate/key alerts {state}.", "info")
        self.show_settings()

    def quick_hash(self):
        # Project policy: revoked users cannot perform any cryptographic operation, including hashing.
        if self._is_revoked_operation_blocked("calculate file hashes", "HASH"):
            self.show_dashboard()
            return

        file = filedialog.askopenfilename(
            title="Select file to calculate hash",
            filetypes=[("All Files", "*.*"), ("PDF Files", "*.pdf"), 
                       ("Word Files", "*.docx"), ("Text Files", "*.txt"),
                       ("Images", "*.png *.jpg *.jpeg")]
        )

        if not file:
            return

        try:
            from core.hash_engine import generate_hash

            file_hash = generate_hash(file, username=self.username)
            file_name = os.path.basename(file)

            user_hash_dir = f"storage/hash/{self.username}"
            os.makedirs(user_hash_dir, exist_ok=True)

            safe_name = file_name.replace(" ", "_")
            auto_hash_path = os.path.join(user_hash_dir, f"{safe_name}_sha256.txt")

            with open(auto_hash_path, 'w') as hf:
                hf.write("File: " + file_name + "\n")
                hf.write("SHA-256: " + file_hash + "\n")
                hf.write("Generated: " + datetime.now().isoformat() + "\n")
                hf.write("By User: " + self.username + "\n")

            self.audit.add_user_file(
                username=self.username,
                file_type='hash',
                file_path=auto_hash_path,
                original_name=os.path.basename(auto_hash_path),
                file_size=os.path.getsize(auto_hash_path)
            )

            print(f" Hash auto-saved to: {auto_hash_path}")

            hash_dialog = ctk.CTkToplevel(self.root)
            hash_dialog.title(" SHA-256 File Hash")
            hash_dialog.geometry("700x320")
            hash_dialog.configure(fg_color=self.BG)
            hash_dialog.resizable(False, False)
            hash_dialog.transient(self.root)
            hash_dialog.grab_set()

            hash_dialog.update_idletasks()
            x = (hash_dialog.winfo_screenwidth() - 700) // 2
            y = (hash_dialog.winfo_screenheight() - 320) // 2
            hash_dialog.geometry(f"+{x}+{y}")

            ctk.CTkLabel(hash_dialog, text=" SHA-256 File Hash", 
                        font=("Inter", 20, "bold"), text_color=self.WARNING).pack(pady=(20, 5))

            ctk.CTkLabel(hash_dialog, text=f" {file_name}", 
                        font=("Inter", 12), text_color=self.TEXT_2).pack(pady=(0, 10))

            ctk.CTkLabel(hash_dialog, text=f" Auto-saved to: {auto_hash_path}", 
                        font=("Inter", 11), text_color=self.SUCCESS).pack(pady=(0, 10))

            hash_frame = ctk.CTkFrame(hash_dialog, fg_color=self.CARD, corner_radius=10)
            hash_frame.pack(fill="x", padx=30, pady=10)

            hash_entry = ctk.CTkEntry(hash_frame, width=620, height=42, font=("Courier", 13),
                                       fg_color=self.ROW_BG, border_color=self.BORDER,
                                       text_color=self.TEXT, corner_radius=8)
            hash_entry.insert(0, file_hash)
            hash_entry.pack(padx=15, pady=15)
            hash_entry.configure(state="readonly")

            btn_frame = ctk.CTkFrame(hash_dialog, fg_color="transparent")
            btn_frame.pack(pady=15)

            def copy_to_clipboard():
                self.root.clipboard_clear()
                self.root.clipboard_append(file_hash)
                self.root.update()
                messagebox.showinfo("Copied", "Hash copied to clipboard!", parent=hash_dialog)

            def save_hash_to_file():
                save_path = filedialog.asksaveasfilename(
                    defaultextension=".txt",
                    initialfile=f"{file_name}_sha256.txt",
                    filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                    title="Save Hash As"
                )
                if save_path:
                    with open(save_path, 'w') as f:
                        f.write("File: " + file_name + "\n")
                        f.write("SHA-256: " + file_hash + "\n")
                        f.write("Generated: " + datetime.now().isoformat() + "\n")
                        f.write("By User: " + self.username + "\n")

                    messagebox.showinfo("Saved", "Hash saved to: " + save_path, parent=hash_dialog)

            ctk.CTkButton(btn_frame, text=" Copy to Clipboard", width=180, height=38,
                         font=("Inter", 12, "bold"), fg_color=self.PRIMARY, 
                         hover_color="#4f46e5", corner_radius=8,
                         command=copy_to_clipboard).pack(side="left", padx=8)

            ctk.CTkButton(btn_frame, text=" Save As (Extra Copy)", width=180, height=38,
                         font=("Inter", 12, "bold"), fg_color=self.SUCCESS, 
                         hover_color="#059669", corner_radius=8,
                         command=save_hash_to_file).pack(side="left", padx=8)

            ctk.CTkButton(btn_frame, text="Close", width=100, height=38,
                         font=("Inter", 12), fg_color=self.MUTED, 
                         hover_color="#475569", corner_radius=8,
                         command=hash_dialog.destroy).pack(side="left", padx=8)

            self.audit.log(self.username, "HASH", "SUCCESS", 
                          file_name=file_name, 
                          file_hash=file_hash[:16],
                          details=f"File: {file_name}, Auto-saved: {auto_hash_path}")

            self.show_dashboard()

        except Exception as e:
            messagebox.showerror("Error", f"Hash calculation failed: {str(e)}")
            self.audit.log(self.username, "HASH", "FAILED", 
                          file_name=os.path.basename(file), 
                          details=str(e))


    def _is_revoked_operation_blocked(self, operation_text, audit_action, parent=None):
        """Block security operations when the user's certificate is revoked."""
        try:
            from core.revocation import is_revoked
            if is_revoked(self.username):
                msg = (
                    "Your signing certificate is revoked.\n\n"
                    f"You cannot {operation_text} until the admin re-issues or activates your certificate."
                )
                messagebox.showerror("Operation Blocked", msg, parent=parent)
                try:
                    self.audit.log(
                        self.username,
                        audit_action,
                        "BLOCKED",
                        details=f"Revoked certificate attempted to {operation_text}"
                    )
                except Exception:
                    pass
                self.refresh_alerts()
                return True
        except Exception as e:
            print(f"Revocation check warning: {e}")
        return False

    def _is_signing_blocked(self, parent=None):
        """Backward-compatible helper used by signing buttons/dialogs."""
        return self._is_revoked_operation_blocked("sign documents", "SIGN", parent)

    def quick_sign(self):
        if self._is_signing_blocked():
            return

        if not os.path.exists(f"storage/keystores/{self.username}_private.pem"):
            messagebox.showerror(" Keys Not Found", 
                "Please complete Setup Wizard first!")
            return

        self.show_sign_dialog()

    def show_sign_dialog(self):
        self.sign_mode.set("external")
        self.sign_file_path.set("")

        dialog = ctk.CTkToplevel(self.root)
        dialog.title(" Sign Document")
        dialog.geometry("520x500")
        dialog.configure(fg_color=self.BG)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 520) // 2
        y = (dialog.winfo_screenheight() - 500) // 2
        dialog.geometry(f"+{x}+{y}")

        ctk.CTkLabel(dialog, text=" Sign Document", 
                    font=("Inter", 22, "bold"), text_color=self.TEXT).pack(pady=(20, 5))
        ctk.CTkLabel(dialog, text="Choose mode and select file", 
                    font=("Inter", 12), text_color=self.TEXT_2).pack(pady=(0, 15))

        mode_frame = ctk.CTkFrame(dialog, fg_color=self.CARD, corner_radius=12)
        mode_frame.pack(fill="x", padx=25, pady=10)

        ctk.CTkLabel(mode_frame, text="Signature Mode", 
                    font=("Inter", 12, "bold"), text_color=self.TEXT).pack(anchor="w", padx=15, pady=(10, 5))

        ext_frame = ctk.CTkFrame(mode_frame, fg_color="transparent")
        ext_frame.pack(fill="x", padx=15, pady=3)
        ctk.CTkRadioButton(ext_frame, text="", variable=self.sign_mode, 
                          value="external", width=20, height=20,
                          fg_color=self.PRIMARY).pack(side="left")
        ctk.CTkLabel(ext_frame, text="External (.sig file)", 
                    font=("Inter", 12, "bold"), text_color=self.TEXT).pack(side="left", padx=10)
        ctk.CTkLabel(ext_frame, text="Separate signature file", 
                    font=("Inter", 10), text_color=self.MUTED).pack(side="left")

        emb_frame = ctk.CTkFrame(mode_frame, fg_color="transparent")
        emb_frame.pack(fill="x", padx=15, pady=3)
        ctk.CTkRadioButton(emb_frame, text="", variable=self.sign_mode, 
                          value="embedded", width=20, height=20,
                          fg_color=self.PRIMARY).pack(side="left")
        ctk.CTkLabel(emb_frame, text="Embedded (PDF only)", 
                    font=("Inter", 12, "bold"), text_color=self.TEXT).pack(side="left", padx=10)
        ctk.CTkLabel(emb_frame, text="Sign inside PDF with visual stamp", 
                    font=("Inter", 10), text_color=self.MUTED).pack(side="left")

        file_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        file_frame.pack(fill="x", padx=25, pady=15)

        ctk.CTkEntry(file_frame, textvariable=self.sign_file_path, 
                    width=300, height=40,
                    font=("Inter", 11), fg_color=self.CARD, 
                    border_color=self.BORDER,
                    text_color=self.TEXT, 
                    placeholder_text="Select file...").pack(side="left", padx=(0, 10))

        ctk.CTkButton(file_frame, text=" Browse", width=100, height=40,
                     font=("Inter", 11), fg_color=self.PRIMARY, 
                     hover_color="#4f46e5", corner_radius=8,
                     command=lambda: self.browse_sign_file(dialog)).pack(side="left")

        sign_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        sign_frame.pack(pady=20)

        ctk.CTkButton(sign_frame, text=" Sign Document", width=200, height=50,
                     font=("Inter", 16, "bold"), fg_color=self.SUCCESS, 
                     hover_color="#059669", corner_radius=12,
                     command=lambda: self.execute_sign(dialog)).pack(pady=5)

        ctk.CTkButton(sign_frame, text="Cancel", width=120, height=35,
                     font=("Inter", 12), fg_color=self.MUTED, 
                     hover_color="#475569", corner_radius=8,
                     command=dialog.destroy).pack(pady=5)

    def browse_sign_file(self, dialog):
        mode = self.sign_mode.get()

        if mode == "embedded":
            filetypes = [("PDF Files", "*.pdf"), ("All Files", "*.*")]
            title = "Select PDF Document to Sign"
        else:
            filetypes = [
                ("All Files", "*.*"),
                ("PDF Files", "*.pdf"),
                ("Word Files", "*.docx"),
                ("Excel Files", "*.xlsx"),
                ("Text Files", "*.txt"),
                ("Images", "*.png *.jpg *.jpeg")
            ]
            title = "Select Document to Sign"

        file = filedialog.askopenfilename(title=title, filetypes=filetypes)
        if file:
            self.sign_file_path.set(file)

    def execute_sign(self, dialog):
        file_path = self.sign_file_path.get()
        mode = self.sign_mode.get()

        if not file_path:
            messagebox.showerror("Error", "Please select a file!", parent=dialog)
            return

        if not os.path.exists(file_path):
            messagebox.showerror("Error", "Selected file not found!", parent=dialog)
            return

        if mode == "embedded" and not file_path.lower().endswith('.pdf'):
            messagebox.showerror("Invalid File", 
                "Embedded signing only works with PDF!\nSelect PDF or switch to External mode.", 
                parent=dialog)
            return

        if self._is_signing_blocked(dialog):
            return

        try:
            if mode == "external":
                self._sign_external(file_path, dialog)
            else:
                self._sign_embedded(file_path, dialog)

        except Exception as e:
            messagebox.showerror("Signing Failed", f"Error: {str(e)}", parent=dialog)
            self.audit.log(self.username, "SIGN", "FAILED", 
                          file_name=os.path.basename(file_path),
                          details=f"Mode: {mode}, Error: {str(e)}")

    def _sign_external(self, file_path, dialog):
        from core.smart_sign import smart_sign

        result = smart_sign(file_path, self.username, "external", None, audit_logger=self.audit)

        if isinstance(result, dict):
            if not result.get('success', False):
                raise Exception(result.get('message', 'Signing failed'))
            sig_path = result.get('output_file', '')
        else:
            sig_path = os.path.splitext(file_path)[0] + ".sig"

        if not os.path.exists(sig_path):
            sig_path = os.path.splitext(file_path)[0] + ".sig"

        self.audit.log(self.username, "SIGN", "SUCCESS", 
                      file_name=os.path.basename(file_path),
                      details=f"Mode: EXTERNAL, Sig: {os.path.basename(sig_path)}")

        messagebox.showinfo(" Signature Created", 
            f"External signature created!\n\n"
            f" Document: {os.path.basename(file_path)}\n"
            f" Signature: {os.path.basename(sig_path)}\n"
            f" Location: {os.path.dirname(os.path.abspath(sig_path))}", 
            parent=dialog)

        dialog.destroy()
        self.show_dashboard()

    def _sign_embedded(self, file_path, dialog):
        from core.smart_sign import smart_sign

        result = smart_sign(file_path, self.username, "embedded", None, audit_logger=self.audit)

        if isinstance(result, dict):
            if not result.get('success', False):
                raise Exception(result.get('message', 'Signing failed'))
            output_path = result.get('output_file') or file_path.replace(".pdf", "_signed.pdf")
        else:
            output_path = result or file_path.replace(".pdf", "_signed.pdf")

        self.audit.log(self.username, "SIGN", "SUCCESS", 
                      file_name=os.path.basename(file_path),
                      details=f"Mode: EMBEDDED, Output: {os.path.basename(output_path)}")

        messagebox.showinfo(" PDF Signed", 
            f"PDF signed with embedded signature!\n\n"
            f" Original: {os.path.basename(file_path)}\n"
            f" Signed PDF: {os.path.basename(output_path)}\n"
            f" Saved to: {os.path.dirname(os.path.abspath(output_path))}\n\n"
            f"Visual signature stamp added to last page!", 
            parent=dialog)

        dialog.destroy()
        self.show_dashboard()

    def quick_verify(self):
        # In this project policy, a revoked certificate blocks verification actions too.
        # This prevents a revoked account from continuing cryptographic workflows.
        if self._is_revoked_operation_blocked("verify documents", "VERIFY"):
            self.show_dashboard()
            return

        if not os.path.exists(f"storage/keystores/{self.username}_private.pem"):
            messagebox.showerror("Error", "Please setup your keys first!")
            return

        file = filedialog.askopenfilename(title="Select file to verify")
        if file:
            try:
                from core.verify_engine import verify_document
                result = verify_document(file, f"storage/keystores/{self.username}_public.pem", self.username)
                messagebox.showinfo("Verify", f"Result: {result}")
                self.audit.log(self.username, "VERIFY", result, file_name=os.path.basename(file))
                self.show_dashboard()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def quick_encrypt(self):
        # Project policy: revoked users cannot encrypt files.
        if self._is_revoked_operation_blocked("encrypt files", "ENCRYPT"):
            self.show_dashboard()
            return

        if not os.path.exists(f"storage/keystores/{self.username}_private.pem"):
            messagebox.showerror("Error", "Please setup your keys first!")
            return

        file = filedialog.askopenfilename(title="Select file to encrypt")
        if file:
            try:
                from core.encrypt_engine import encrypt_file
                public_key = f"storage/keystores/{self.username}_public.pem"
                enc_path = encrypt_file(file, public_key, self.username)

                self.audit.add_user_file(
                    username=self.username,
                    file_type='encrypted',
                    file_path=enc_path,
                    original_name=os.path.basename(file),
                    file_size=os.path.getsize(enc_path)
                )

                messagebox.showinfo("Encrypt", f"File encrypted successfully!\n\nSaved to: {enc_path}")
                self.audit.log(self.username, "ENCRYPT", "SUCCESS", file_name=os.path.basename(file))
                self.show_dashboard()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def quick_decrypt(self):
        # Project policy: revoked users cannot decrypt files.
        if self._is_revoked_operation_blocked("decrypt files", "DECRYPT"):
            self.show_dashboard()
            return

        if not os.path.exists(f"storage/keystores/{self.username}_private.pem"):
            messagebox.showerror("Error", "Please setup your keys first!")
            return

        file = filedialog.askopenfilename(
            title="Select Encrypted File to Decrypt",
            filetypes=[
                ("Encrypted Files", "*.bin"),
                ("All Files", "*.*")
            ],
            initialdir=f"storage/encrypted/{self.username}"
        )

        if not file:
            return

        try:
            from core.decrypt_engine import decrypt_file

            output_path = decrypt_file(self.username, file, "")

            self.audit.add_user_file(
                username=self.username,
                file_type='decrypted',
                file_path=output_path,
                original_name=os.path.basename(output_path),
                file_size=os.path.getsize(output_path)
            )

            messagebox.showinfo(
                " Decrypt Success", 
                f"File decrypted successfully!\n\n"
                f" Encrypted: {os.path.basename(file)}\n"
                f" Decrypted: {os.path.basename(output_path)}\n"
                f" Location: {os.path.dirname(os.path.abspath(output_path))}\n\n"
                f"Note: This restores the ORIGINAL unsigned file.\n"
                f"To verify signature, use the _signed.pdf version."
            )

            self.audit.log(
                self.username, 
                "DECRYPT", 
                "SUCCESS", 
                file_name=os.path.basename(file),
                details=f"Output: {os.path.basename(output_path)}"
            )

            self.show_dashboard()

        except Exception as e:
            messagebox.showerror(" Decrypt Failed", str(e))
            self.audit.log(
                self.username, 
                "DECRYPT", 
                "FAILED", 
                file_name=os.path.basename(file),
                details=str(e)
            )

    def change_password(self):
        old = simpledialog.askstring("Current Password", "Enter current password:", show='*')
        if old:
            new = simpledialog.askstring("New Password", "Enter new password:", show='*')
            if new and len(new) >= 6:
                success, msg = self.auth.change_password(self.username, new)
                if success:
                    messagebox.showinfo("Success", "Password changed!")
                else:
                    messagebox.showerror("Error", msg)
            else:
                messagebox.showerror("Error", "Min 6 characters!")

    def export_my_logs(self):
        import csv
        from datetime import datetime

        filepath = f"storage/my_logs_{self.username}_{datetime.now().strftime('%Y%m%d')}.csv"

        try:
            conn = sqlite3.connect("storage/audit.db")
            cursor = conn.execute("""
                SELECT * FROM audit_log WHERE username = ? ORDER BY timestamp DESC
            """, (self.username,))
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
        if messagebox.askyesno("Logout", "Are you sure?"):
            self.root.destroy()
        from main import show_login
        show_login()

    def delete_my_account(self):
        if messagebox.askyesno(" DANGER", 
            f"PERMANENTLY delete your account '{self.username}'?\n\n"
            f"This will delete ALL your files, signatures, keys, and certificates.\n"
            f"This action CANNOT be undone!",
            icon='warning'):

            conn = sqlite3.connect(self.auth.db_path)
            conn.execute("DELETE FROM users WHERE username = ?", (self.username,))
            conn.commit()
            conn.close()

            user_enc_dir = f"storage/encrypted/{self.username}"
            if os.path.exists(user_enc_dir):
                try:
                    shutil.rmtree(user_enc_dir)
                    print(f" Deleted encrypted folder: {user_enc_dir}")
                except Exception as e:
                    print(f" Could not delete encrypted folder: {e}")

            user_sig_dir = f"storage/signatures/{self.username}"
            if os.path.exists(user_sig_dir):
                try:
                    shutil.rmtree(user_sig_dir)
                    print(f" Deleted signatures folder: {user_sig_dir}")
                except Exception as e:
                    print(f" Could not delete signatures folder: {e}")

            user_priv_key = f"storage/keystores/{self.username}_private.pem"
            user_pub_key = f"storage/keystores/{self.username}_public.pem"
            for key_file in [user_priv_key, user_pub_key]:
                if os.path.exists(key_file):
                    try:
                        os.remove(key_file)
                        print(f" Deleted key: {key_file}")
                    except Exception as e:
                        print(f" Could not delete key: {e}")

            user_cert = f"storage/certs/{self.username}_cert.pem"
            if os.path.exists(user_cert):
                try:
                    os.remove(user_cert)
                    print(f" Deleted certificate: {user_cert}")
                except Exception as e:
                    print(f" Could not delete certificate: {e}")

            try:
                conn = sqlite3.connect("storage/audit.db")
                conn.execute("DELETE FROM audit_log WHERE username = ?", (self.username,))
                conn.execute("DELETE FROM user_files WHERE username = ?", (self.username,))
                conn.execute("DELETE FROM user_activity WHERE username = ?", (self.username,))
                conn.commit()
                conn.close()
                print(f" Cleaned audit data for: {self.username}")
            except Exception as e:
                print(f" Could not clean audit data: {e}")

            messagebox.showinfo("Account Deleted", 
                f"Your account '{self.username}' has been permanently deleted.\n"
                f"All your data has been cleaned up.")

            self.root.destroy()
            from main import show_login
            show_login()