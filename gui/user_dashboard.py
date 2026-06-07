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

        # Sign dialog variables
        self.sign_mode = ctk.StringVar(value="external")
        self.sign_file_path = ctk.StringVar(value="")

        self.root.title(f"CryptoSign - User Dashboard ({self.username})")
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
            ("📝", "My Documents", "documents"),
            ("📦", "Batch Sign", "batch_sign"),
            ("📈", "Activity Log", "activity"),
            ("👤", "My Profile", "profile"),
            ("⚙️", "Settings", "settings"),
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

        ctk.CTkLabel(self.sidebar, text=f"👤 {self.username}", 
                    font=("Inter", 12, "bold"), text_color="#f8fafc").pack(pady=5)
        ctk.CTkLabel(self.sidebar, text="Standard User", 
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

        ctk.CTkButton(self.header, text="🔔", width=40, height=40,
                     font=("Inter", 16), fg_color="#1e293b", hover_color="#334155",
                     text_color="#f59e0b", corner_radius=8).pack(side="right", padx=5)

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

        has_keys = os.path.exists(f"storage/keystores/{self.username}_private.pem")

        if not has_keys:
            self.show_setup_wizard()
            return

        # Welcome
        welcome = ctk.CTkFrame(self.content_frame, fg_color="#1e293b", corner_radius=12)
        welcome.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(welcome, text=f"👋 Welcome back, {self.username}!", 
                    font=("Inter", 20, "bold"), text_color="#f8fafc").pack(anchor="w", padx=20, pady=(15, 5))
        ctk.CTkLabel(welcome, text="Here's your document signing overview", 
                    font=("Inter", 12), text_color="#94a3b8").pack(anchor="w", padx=20, pady=(0, 15))

        # Stats - FIXED: Include BATCH_SIGN in Signed count
        stats_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))

        try:
            conn = sqlite3.connect("storage/audit.db")
            cursor = conn.execute("""
                SELECT action, COUNT(*) FROM audit_log 
                WHERE username = ? GROUP BY action
            """, (self.username,))
            stats = dict(cursor.fetchall())
            conn.close()
        except:
            stats = {}

        # FIXED: BATCH_SIGN + SIGN = Total Signed
        signed_count = stats.get("SIGN", 0) + stats.get("BATCH_SIGN", 0)
        self.create_stat_card(stats_frame, "📝 Signed", str(signed_count), "#6366f1")
        self.create_stat_card(stats_frame, "✅ Verified", str(stats.get("VERIFY", 0)), "#10b981")
        self.create_stat_card(stats_frame, "🔐 Encrypted", str(stats.get("ENCRYPT", 0)), "#f59e0b")
        self.create_stat_card(stats_frame, "🔓 Decrypted", str(stats.get("DECRYPT", 0)), "#ef4444")

        # Quick Actions
        actions_frame = ctk.CTkFrame(self.content_frame, fg_color="#1e293b", corner_radius=12)
        actions_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(actions_frame, text="⚡ Quick Actions", 
                    font=("Inter", 16, "bold"), text_color="#f8fafc").pack(anchor="w", padx=20, pady=(15, 10))

        grid = ctk.CTkFrame(actions_frame, fg_color="transparent")
        grid.pack(fill="x", padx=20, pady=(0, 15))

        row1 = ctk.CTkFrame(grid, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        self.create_action_btn(row1, "📝 Sign Document", self.quick_sign, "#6366f1")
        self.create_action_btn(row1, "✅ Verify Document", self.quick_verify, "#10b981")

        row2 = ctk.CTkFrame(grid, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        self.create_action_btn(row2, "🔐 Encrypt File", self.quick_encrypt, "#f59e0b")
        self.create_action_btn(row2, "🔓 Decrypt File", self.quick_decrypt, "#ef4444")

        row3 = ctk.CTkFrame(grid, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        self.create_action_btn(row3, "📦 Batch Sign", self.show_batch_sign, "#6366f1")
        self.create_action_btn(row3, "🔍 File Hash", self.quick_hash, "#f59e0b")

        # Recent Activity
        activity_frame = ctk.CTkFrame(self.content_frame, fg_color="#1e293b", corner_radius=12)
        activity_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(activity_frame, text="📈 Recent Activity", 
                    font=("Inter", 16, "bold"), text_color="#f8fafc").pack(anchor="w", padx=20, pady=(15, 10))

        scroll = ctk.CTkScrollableFrame(activity_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        try:
            conn = sqlite3.connect("storage/audit.db")
            cursor = conn.execute("""
                SELECT timestamp, action, file_name, result 
                FROM audit_log WHERE username = ? ORDER BY timestamp DESC LIMIT 10
            """, (self.username,))
            activities = cursor.fetchall()
            conn.close()

            for activity in activities:
                timestamp, action, file_name, result = activity
                self.create_activity_item(scroll, action, file_name, result, timestamp)
        except:
            ctk.CTkLabel(scroll, text="No recent activity", 
                        font=("Inter", 12), text_color="#64748b").pack(pady=20)

    # ═══════════════════════════════════════════════════════════════════════
    # ✅ BATCH SIGN - Full Working Implementation
    # ═══════════════════════════════════════════════════════════════════════
    def show_batch_sign(self):
        """Show Batch Sign interface with modern folder selection"""
        self.header_title.configure(text="📦 Batch Sign Documents")

        # Check if keys exist
        if not os.path.exists(f"storage/keystores/{self.username}_private.pem"):
            self.show_setup_wizard()
            return

        # Main container
        container = ctk.CTkFrame(self.content_frame, fg_color="#1e293b", corner_radius=12)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(container, text="📦 Batch Document Signing", 
                    font=("Inter", 24, "bold"), text_color="#f8fafc").pack(pady=(30, 10))

        ctk.CTkLabel(container, text="Sign multiple documents at once from a folder", 
                    font=("Inter", 14), text_color="#94a3b8").pack(pady=(0, 20))

        # Settings Frame
        settings_frame = ctk.CTkFrame(container, fg_color="#0f172a", corner_radius=10)
        settings_frame.pack(fill="x", padx=40, pady=10)

        # Signature Mode
        mode_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        mode_frame.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkLabel(mode_frame, text="Signature Mode:", 
                    font=("Inter", 13, "bold"), text_color="#f8fafc").pack(side="left", padx=(0, 15))

        self.batch_mode = ctk.StringVar(value="external")
        
        ctk.CTkRadioButton(mode_frame, text="External (.sig file)", 
                          variable=self.batch_mode, value="external",
                          font=("Inter", 12), text_color="#f8fafc",
                          fg_color="#6366f1").pack(side="left", padx=10)
        
        ctk.CTkRadioButton(mode_frame, text="Embedded (PDF only)", 
                          variable=self.batch_mode, value="embedded",
                          font=("Inter", 12), text_color="#f8fafc",
                          fg_color="#6366f1").pack(side="left", padx=10)

        # File Types
        types_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        types_frame.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(types_frame, text="File Types:", 
                    font=("Inter", 13, "bold"), text_color="#f8fafc").pack(side="left", padx=(0, 15))

        self.pdf_var = ctk.BooleanVar(value=True)
        self.docx_var = ctk.BooleanVar(value=True)
        self.xlsx_var = ctk.BooleanVar(value=False)
        self.txt_var = ctk.BooleanVar(value=True)

        ctk.CTkCheckBox(types_frame, text="PDF", variable=self.pdf_var,
                       font=("Inter", 11), text_color="#94a3b8",
                       fg_color="#6366f1").pack(side="left", padx=8)
        ctk.CTkCheckBox(types_frame, text="DOCX", variable=self.docx_var,
                       font=("Inter", 11), text_color="#94a3b8",
                       fg_color="#6366f1").pack(side="left", padx=8)
        ctk.CTkCheckBox(types_frame, text="XLSX", variable=self.xlsx_var,
                       font=("Inter", 11), text_color="#94a3b8",
                       fg_color="#6366f1").pack(side="left", padx=8)
        ctk.CTkCheckBox(types_frame, text="TXT", variable=self.txt_var,
                       font=("Inter", 11), text_color="#94a3b8",
                       fg_color="#6366f1").pack(side="left", padx=8)

        # Folder Selection - MODERN DIALOG STYLE
        folder_frame = ctk.CTkFrame(container, fg_color="transparent")
        folder_frame.pack(fill="x", padx=40, pady=15)

        self.folder_path_var = ctk.StringVar(value="")
        
        ctk.CTkEntry(folder_frame, textvariable=self.folder_path_var,
                    width=500, height=40, font=("Inter", 12),
                    fg_color="#0f172a", border_color="#334155",
                    text_color="#f8fafc", placeholder_text="Select folder...").pack(side="left", padx=(0, 10))

        ctk.CTkButton(folder_frame, text="📁 Browse", width=100, height=40,
                     font=("Inter", 12), fg_color="#6366f1", 
                     hover_color="#4f46e5", corner_radius=8,
                     command=self.browse_batch_folder).pack(side="left")

        # Progress Section
        self.progress_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.progress_frame.pack(fill="x", padx=40, pady=10)

        self.progress_label = ctk.CTkLabel(self.progress_frame, text="Ready to start", 
                                          font=("Inter", 12), text_color="#94a3b8")
        self.progress_label.pack(pady=5)

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, width=600, height=20,
                                            fg_color="#0f172a", progress_color="#6366f1")
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0)

        # Result Label
        self.batch_result_label = ctk.CTkLabel(container, text="", 
                                                font=("Inter", 14), text_color="#f8fafc")
        self.batch_result_label.pack(pady=10)

        # Action Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(btn_frame, text="🚀 Start Batch Sign", width=200, height=50,
                     font=("Inter", 16, "bold"), fg_color="#10b981", 
                     hover_color="#059669", corner_radius=12,
                     command=self.execute_batch_sign).pack(side="left", padx=10)

        ctk.CTkButton(btn_frame, text="🔄 Reset", width=120, height=50,
                     font=("Inter", 14), fg_color="#64748b", 
                     hover_color="#475569", corner_radius=12,
                     command=self.reset_batch_sign).pack(side="left", padx=10)

    def browse_batch_folder(self):
        """Browse for folder using modern file dialog style"""
        file = filedialog.askopenfilename(
            title="📁 Select Any File in Target Folder",
            filetypes=[("All Files", "*.*")],
            parent=self.root
        )
        if file:
            folder = os.path.dirname(file)
            self.folder_path_var.set(folder)
            try:
                files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
                messagebox.showinfo("Folder Selected", 
                    f"📁 Folder: {os.path.basename(folder)}\n"
                    f"📄 Total Files: {len(files)}\n\n"
                    f"Supported files will be signed based on your selection.")
            except:
                pass

    def reset_batch_sign(self):
        """Reset batch sign form"""
        self.folder_path_var.set("")
        self.progress_bar.set(0)
        self.progress_label.configure(text="Ready to start")
        self.batch_result_label.configure(text="")

    def execute_batch_sign(self):
        """Execute batch signing with progress updates"""
        folder_path = self.folder_path_var.get()
        
        if not folder_path:
            messagebox.showerror("Error", "Please select a folder first!")
            return

        if not os.path.exists(folder_path):
            messagebox.showerror("Error", "Selected folder does not exist!")
            return

        # Build file types list
        extensions = []
        if self.pdf_var.get(): extensions.append('.pdf')
        if self.docx_var.get(): extensions.append('.docx')
        if self.xlsx_var.get(): extensions.append('.xlsx')
        if self.txt_var.get(): extensions.append('.txt')

        if not extensions:
            messagebox.showerror("Error", "Please select at least one file type!")
            return

        mode = self.batch_mode.get()

        # Disable buttons during processing
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
            # Call batch_sign from core/batch_sign.py
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

            # Update UI with results
            signed = results['signed']
            failed = results['failed']
            total = signed + failed

            if failed == 0:
                self.batch_result_label.configure(
                    text=f"✅ Success! Signed {signed}/{total} documents",
                    text_color="#10b981"
                )
                self.audit.log(self.username, "BATCH_SIGN", "SUCCESS", 
                              details=f"Signed {signed} files in {folder_path}")
            else:
                self.batch_result_label.configure(
                    text=f"⚠️ Signed {signed}/{total} documents ({failed} failed)",
                    text_color="#f59e0b"
                )
                self.audit.log(self.username, "BATCH_SIGN", "PARTIAL", 
                              details=f"Signed {signed}/{total}, Failed {failed}")

            # Show errors if any
            if results['errors']:
                error_text = "\n".join([f"{os.path.basename(f)}: {e}" for f, e in results['errors'][:5]])
                if len(results['errors']) > 5:
                    error_text += f"\n... and {len(results['errors']) - 5} more errors"
                messagebox.showwarning("Batch Sign Complete", 
                    f"Completed with some errors:\n\n{error_text}")

            messagebox.showinfo("Batch Sign Complete", 
                f"Batch signing finished!\n\n"
                f"✅ Signed: {signed}\n"
                f"❌ Failed: {failed}\n"
                f"📁 Folder: {folder_path}")

            # Refresh dashboard
            self.show_dashboard()

        except Exception as e:
            self.progress_label.configure(text=f"Error: {str(e)}")
            self.batch_result_label.configure(text=f"❌ Error: {str(e)}", text_color="#ef4444")
            messagebox.showerror("Batch Sign Error", str(e))
            self.audit.log(self.username, "BATCH_SIGN", "FAILED", details=str(e))

    def show_setup_wizard(self):
        wizard = ctk.CTkFrame(self.content_frame, fg_color="#1e293b", corner_radius=12)
        wizard.pack(fill="both", expand=True, padx=50, pady=50)

        ctk.CTkLabel(wizard, text="🔐 Welcome to CryptoSign!", 
                    font=("Inter", 24, "bold"), text_color="#f8fafc").pack(pady=(30, 10))

        ctk.CTkLabel(wizard, text="You need to set up your cryptographic keys to start signing documents.", 
                    font=("Inter", 14), text_color="#94a3b8").pack(pady=(0, 20))

        features = ctk.CTkFrame(wizard, fg_color="transparent")
        features.pack(pady=20)

        for icon, text in [("📝", "Sign Documents"), ("✅", "Verify Documents"), 
                           ("🔐", "Encrypt Files"), ("🔓", "Decrypt Files"), ("📦", "Batch Sign")]:
            ctk.CTkLabel(features, text=f"{icon} {text}", 
                        font=("Inter", 14), text_color="#f8fafc").pack(pady=5)

        ctk.CTkButton(wizard, text="⚙️ Setup My Keys", width=250, height=50,
                     font=("Inter", 16, "bold"), fg_color="#6366f1", hover_color="#4f46e5",
                     corner_radius=12, command=self.setup_keys).pack(pady=30)

        ctk.CTkLabel(wizard, text="This will create your private key, public key, and certificate.", 
                    font=("Inter", 11), text_color="#64748b").pack()

    def setup_keys(self):
        from core.ca_engine import create_root_ca, load_ca_private_key
        from core.key_manager import generate_key_pair
        from core.cert_manager import issue_certificate

        try:
            if not os.path.exists("storage/ca/ca_private.pem"):
                create_root_ca()

            private, public = generate_key_pair(self.username, None)
            ca_key = load_ca_private_key()
            issue_certificate(ca_key, public, self.username)

            self.audit.log(self.username, "SETUP", "SUCCESS", 
                          details="Keys and certificate generated")

            messagebox.showinfo("Success", "Your keys have been generated!\n\nYou can now sign, verify, encrypt, and decrypt documents.")

            self.show_dashboard()

        except Exception as e:
            messagebox.showerror("Error", f"Setup failed: {str(e)}")
            self.audit.log(self.username, "SETUP", "FAILED", details=str(e))

    def create_stat_card(self, parent, title, value, color):
        card = ctk.CTkFrame(parent, fg_color="#1e293b", corner_radius=12, width=250)
        card.pack(side="left", expand=True, fill="both", padx=5, pady=5)

        ctk.CTkLabel(card, text=title, font=("Inter", 12), 
                    text_color="#94a3b8").pack(pady=(15, 5))
        ctk.CTkLabel(card, text=value, font=("Inter", 32, "bold"), 
                    text_color=color).pack(pady=(0, 15))

    def create_action_btn(self, parent, text, command, color):
        btn = ctk.CTkButton(parent, text=text, width=300, height=50,
                           font=("Inter", 14, "bold"), fg_color=color,
                           hover_color="#4f46e5" if color == "#6366f1" else "#059669" if color == "#10b981" else "#d97706" if color == "#f59e0b" else "#dc2626",
                           text_color="#ffffff", corner_radius=12, command=command)
        btn.pack(side="left", padx=8, expand=True, fill="x")
        return btn

    def create_activity_item(self, parent, action, file_name, result, time):
        frame = ctk.CTkFrame(parent, fg_color="#0f172a", corner_radius=8)
        frame.pack(fill="x", pady=3)

        icons = {"SIGN": "📝", "VERIFY": "✅", "ENCRYPT": "🔐", "DECRYPT": "🔓", "HASH": "🔍", "SETUP": "⚙️", "BATCH_SIGN": "📦"}
        icon = icons.get(action, "📋")

        ctk.CTkLabel(frame, text=f"{icon} {action}", 
                    font=("Inter", 12, "bold"), text_color="#6366f1").pack(side="left", padx=15, pady=10)

        ctk.CTkLabel(frame, text=file_name or "-", 
                    font=("Inter", 11), text_color="#94a3b8").pack(side="left", padx=10)

        result_color = "#10b981" if result in ["SUCCESS", "VALID"] else "#ef4444"
        ctk.CTkLabel(frame, text=result, 
                    font=("Inter", 11), text_color=result_color).pack(side="right", padx=15)

        ctk.CTkLabel(frame, text=time[:10], 
                    font=("Inter", 10), text_color="#64748b").pack(side="right", padx=10)

    def show_documents(self):
        self.header_title.configure(text="My Documents")

        # Get files from database
        signed_files = self.audit.get_user_files(self.username, 'signed')
        encrypted_files = self.audit.get_user_files(self.username, 'encrypted')

        # Also scan directories for files not in database (backward compat)
        signed_files += self._scan_signed_files()
        encrypted_files += self._scan_encrypted_files()

        # Document sections
        doc_types = [
            ("📝 Signed Documents", signed_files, "#6366f1", "signed"),
            ("🔐 Encrypted Files", encrypted_files, "#f59e0b", "encrypted"),
            ("🏛 Certificates", self._get_cert_files(), "#10b981", "cert"),
        ]

        for title, files, color, ftype in doc_types:
            frame = ctk.CTkFrame(self.content_frame, fg_color="#1e293b", corner_radius=12)
            frame.pack(fill="x", pady=10)

            # Header with count
            header = ctk.CTkFrame(frame, fg_color="transparent")
            header.pack(fill="x", padx=20, pady=(15, 10))

            ctk.CTkLabel(header, text=title, 
                        font=("Inter", 16, "bold"), text_color=color).pack(side="left")

            count_badge = ctk.CTkLabel(header, text=f"{len(files)} files", 
                                      font=("Inter", 11), text_color="#64748b")
            count_badge.pack(side="right")

            # File list
            scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent", height=180)
            scroll.pack(fill="x", padx=20, pady=(0, 15))

            if not files:
                ctk.CTkLabel(scroll, text="No files found", 
                            font=("Inter", 11), text_color="#64748b").pack(pady=20)
            else:
                for file_info in files[:10]:  # Show max 10
                    self.create_file_item(scroll, file_info, ftype)

    def _scan_signed_files(self):
        """Scan directories for signed files not in database"""
        files = []

        # Scan user signatures directory
        sig_dir = f"storage/signatures/{self.username}"
        if os.path.exists(sig_dir):
            for f in os.listdir(sig_dir):
                if f.endswith('.sig') or f.endswith('_signed.pdf'):
                    fpath = os.path.join(sig_dir, f)
                    files.append((
                        datetime.fromtimestamp(os.path.getmtime(fpath)).isoformat(),
                        'signed', fpath, f, os.path.getsize(fpath), 'active'
                    ))

        # Scan embedded directory
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
        """Scan directories for encrypted files not in database"""
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

    def _get_cert_files(self):
        """Get certificate files"""
        files = []
        cert_path = f"storage/certs/{self.username}_cert.pem"
        if os.path.exists(cert_path):
            files.append((
                datetime.fromtimestamp(os.path.getmtime(cert_path)).isoformat(),
                'cert', cert_path, f"{self.username}_cert.pem", 
                os.path.getsize(cert_path), 'active'
            ))
        return files

    def create_file_item(self, parent, file_info, ftype):
        """Create file row with working buttons"""
        timestamp, file_type, file_path, original_name, file_size, status = file_info

        frame = ctk.CTkFrame(parent, fg_color="#0f172a", corner_radius=6)
        frame.pack(fill="x", pady=2)

        # File icon based on type
        icons = {"signed": "📝", "encrypted": "🔐", "cert": "🏛"}
        icon = icons.get(ftype, "📄")

        # File name (truncated if too long)
        display_name = original_name[:40] + "..." if len(original_name) > 40 else original_name

        ctk.CTkLabel(frame, text=f"{icon} {display_name}", 
                    font=("Inter", 11), text_color="#f8fafc").pack(side="left", padx=15, pady=8)

        # File size
        size_str = self._format_size(file_size)
        ctk.CTkLabel(frame, text=size_str, 
                    font=("Inter", 10), text_color="#64748b").pack(side="left", padx=5)

        # Action buttons
        actions = ctk.CTkFrame(frame, fg_color="transparent")
        actions.pack(side="right", padx=10)

        # View/Open button
        ctk.CTkButton(actions, text="👁 Open", width=60, height=25,
                     font=("Inter", 10), fg_color="#6366f1", hover_color="#4f46e5",
                     corner_radius=6, command=lambda p=file_path: self._open_file(p)).pack(side="left", padx=2)

        # Download/Copy button
        ctk.CTkButton(actions, text="⬇ Save As", width=70, height=25,
                     font=("Inter", 10), fg_color="#10b981", hover_color="#059669",
                     corner_radius=6, command=lambda p=file_path, n=original_name: self._save_file_as(p, n)).pack(side="left", padx=2)

        # Delete button
        ctk.CTkButton(actions, text="🗑", width=30, height=25,
                     font=("Inter", 10), fg_color="#ef4444", hover_color="#dc2626",
                     corner_radius=6, command=lambda p=file_path, f=frame: self._delete_file(p, f)).pack(side="left", padx=2)

    def _format_size(self, size):
        """Format file size"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f} KB"
        else:
            return f"{size/(1024*1024):.1f} MB"

    def _open_file(self, file_path):
        """Open file with default application"""
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "File not found!")
            return

        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # macOS/Linux
                import subprocess
                subprocess.run(['xdg-open', file_path], check=True)
            messagebox.showinfo("Open", f"Opening: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {str(e)}")

    def _save_file_as(self, file_path, original_name):
        """Save file to user chosen location"""
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
        """Delete file with confirmation"""
        if messagebox.askyesno("Confirm Delete", f"Delete {os.path.basename(file_path)}?"):
            try:
                # Mark as deleted in database
                self.audit.delete_user_file(self.username, file_path)

                # Actually delete file
                if os.path.exists(file_path):
                    os.remove(file_path)

                # Remove from UI
                frame_widget.destroy()

                messagebox.showinfo("Deleted", "File deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete: {str(e)}")

    def show_activity(self):
        self.header_title.configure(text="Activity Log")

        toolbar = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 15))

        ctk.CTkButton(toolbar, text="📥 Export My Logs", width=150, height=35,
                     font=("Inter", 12), fg_color="#6366f1", hover_color="#4f46e5",
                     corner_radius=8, command=self.export_my_logs).pack(side="right")

        table_frame = ctk.CTkFrame(self.content_frame, fg_color="#1e293b", corner_radius=12)
        table_frame.pack(fill="both", expand=True)

        headers = ctk.CTkFrame(table_frame, fg_color="#334155", corner_radius=8)
        headers.pack(fill="x", padx=20, pady=15)

        for col, width in [("Time", 150), ("Action", 120), ("File", 200), ("Result", 100), ("Details", 300)]:
            ctk.CTkLabel(headers, text=col, font=("Inter", 12, "bold"), 
                        text_color="#94a3b8", width=width).pack(side="left", padx=10, pady=10)

        scroll = ctk.CTkScrollableFrame(table_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        try:
            conn = sqlite3.connect("storage/audit.db")
            cursor = conn.execute("""
                SELECT * FROM audit_log WHERE username = ? ORDER BY timestamp DESC
            """, (self.username,))
            logs = cursor.fetchall()
            conn.close()

            for log in logs:
                self.create_log_row(scroll, log)
        except:
            ctk.CTkLabel(scroll, text="No activity found", 
                        font=("Inter", 12), text_color="#64748b").pack(pady=20)

    def create_log_row(self, parent, log):
        id, timestamp, username, action, file_name, file_hash, result, details, ip = log

        row = ctk.CTkFrame(parent, fg_color="#0f172a", corner_radius=6)
        row.pack(fill="x", pady=2)

        ctk.CTkLabel(row, text=timestamp[:19], font=("Courier", 10), 
                    text_color="#64748b", width=150).pack(side="left", padx=5, pady=8)
        ctk.CTkLabel(row, text=action, font=("Inter", 10, "bold"), 
                    text_color="#6366f1", width=120).pack(side="left", padx=5)
        ctk.CTkLabel(row, text=file_name or "-", font=("Inter", 10), 
                    text_color="#94a3b8", width=200).pack(side="left", padx=5)

        result_color = "#10b981" if result in ["SUCCESS", "VALID"] else "#ef4444"
        ctk.CTkLabel(row, text=result, font=("Inter", 10), 
                    text_color=result_color, width=100).pack(side="left", padx=5)
        ctk.CTkLabel(row, text=details or "", font=("Inter", 9), 
                    text_color="#64748b", width=300).pack(side="left", padx=5)

    def show_profile(self):
        self.header_title.configure(text="My Profile")

        profile_frame = ctk.CTkFrame(self.content_frame, fg_color="#1e293b", corner_radius=12)
        profile_frame.pack(fill="both", expand=True)

        info = ctk.CTkFrame(profile_frame, fg_color="transparent")
        info.pack(fill="x", padx=30, pady=30)

        ctk.CTkLabel(info, text="👤", font=("Inter", 64)).pack()
        ctk.CTkLabel(info, text=self.username, 
                    font=("Inter", 24, "bold"), text_color="#f8fafc").pack()
        ctk.CTkLabel(info, text="Standard User", 
                    font=("Inter", 14), text_color="#94a3b8").pack()

        stats = ctk.CTkFrame(profile_frame, fg_color="transparent")
        stats.pack(fill="x", padx=30, pady=20)

        try:
            conn = sqlite3.connect("storage/audit.db")
            total = conn.execute("SELECT COUNT(*) FROM audit_log WHERE username = ?", 
                               (self.username,)).fetchone()[0]
            conn.close()
        except:
            total = 0

        ctk.CTkLabel(stats, text=f"Total Activities: {total}", 
                    font=("Inter", 16), text_color="#6366f1").pack(pady=10)

        ctk.CTkButton(profile_frame, text="🔑 Change Password", width=200, height=40,
                     font=("Inter", 14), fg_color="#6366f1", hover_color="#4f46e5",
                     corner_radius=10, command=self.change_password).pack(pady=20)

    def show_settings(self):
        self.header_title.configure(text="Settings")

        settings_frame = ctk.CTkFrame(self.content_frame, fg_color="#1e293b", corner_radius=12)
        settings_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(settings_frame, text="⚙️ Application Settings", 
                    font=("Inter", 20, "bold"), text_color="#f8fafc").pack(pady=30)

        theme_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        theme_frame.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(theme_frame, text="🌙 Dark Mode", 
                    font=("Inter", 14), text_color="#f8fafc").pack(side="left")

        self.dark_mode = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(theme_frame, variable=self.dark_mode, 
                     command=self.toggle_theme).pack(side="right")

        notif_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        notif_frame.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(notif_frame, text="🔔 Notifications", 
                    font=("Inter", 14), text_color="#f8fafc").pack(side="left")

        self.notifications = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(notif_frame, variable=self.notifications).pack(side="right")

    def toggle_theme(self):
        if self.dark_mode.get():
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")

    def quick_hash(self):
        """Calculate SHA-256 hash of selected file"""
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

            # Calculate hash
            file_hash = generate_hash(file)

            # Create hash display dialog (same style as main_app.py)
            hash_dialog = ctk.CTkToplevel(self.root)
            hash_dialog.title("🔍 SHA-256 File Hash")
            hash_dialog.geometry("700x280")
            hash_dialog.configure(fg_color="#0f172a")
            hash_dialog.resizable(False, False)
            hash_dialog.transient(self.root)
            hash_dialog.grab_set()

            # Center dialog
            hash_dialog.update_idletasks()
            x = (hash_dialog.winfo_screenwidth() - 700) // 2
            y = (hash_dialog.winfo_screenheight() - 280) // 2
            hash_dialog.geometry(f"+{x}+{y}")

            # Title
            ctk.CTkLabel(hash_dialog, text="🔍 SHA-256 File Hash", 
                        font=("Inter", 20, "bold"), text_color="#f59e0b").pack(pady=(25, 10))

            # File info
            file_name = os.path.basename(file)
            ctk.CTkLabel(hash_dialog, text=f"📄 {file_name}", 
                        font=("Inter", 12), text_color="#94a3b8").pack(pady=(0, 15))

            # Hash display
            hash_frame = ctk.CTkFrame(hash_dialog, fg_color="#1e293b", corner_radius=10)
            hash_frame.pack(fill="x", padx=30, pady=10)

            hash_entry = ctk.CTkEntry(hash_frame, width=620, height=42, font=("Courier", 13),
                                       fg_color="#0f172a", border_color="#334155",
                                       text_color="#f8fafc", corner_radius=8)
            hash_entry.insert(0, file_hash)
            hash_entry.pack(padx=15, pady=15)
            hash_entry.configure(state="readonly")

            # Buttons frame
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
                        f.write(f"File: {file_name}\n")
                        f.write(f"SHA-256: {file_hash}\n")
                        f.write(f"Generated: {datetime.now().isoformat()}\n")
                    messagebox.showinfo("Saved", f"Hash saved to:\n{save_path}", parent=hash_dialog)

            ctk.CTkButton(btn_frame, text="📋 Copy to Clipboard", width=180, height=38,
                         font=("Inter", 12, "bold"), fg_color="#6366f1", 
                         hover_color="#4f46e5", corner_radius=8,
                         command=copy_to_clipboard).pack(side="left", padx=8)

            ctk.CTkButton(btn_frame, text="💾 Save to File", width=160, height=38,
                         font=("Inter", 12, "bold"), fg_color="#10b981", 
                         hover_color="#059669", corner_radius=8,
                         command=save_hash_to_file).pack(side="left", padx=8)

            ctk.CTkButton(btn_frame, text="Close", width=100, height=38,
                         font=("Inter", 12), fg_color="#64748b", 
                         hover_color="#475569", corner_radius=8,
                         command=hash_dialog.destroy).pack(side="left", padx=8)

            # Log to audit
            self.audit.log(self.username, "HASH", "SUCCESS", 
                          file_name=file_name, 
                          file_hash=file_hash[:16],
                          details=f"File: {file_name}")

        except Exception as e:
            messagebox.showerror("Error", f"Hash calculation failed: {str(e)}")
            self.audit.log(self.username, "HASH", "FAILED", 
                          file_name=os.path.basename(file), 
                          details=str(e))

    def quick_sign(self):
        """Open sign dialog with mode selection"""
        if not os.path.exists(f"storage/keystores/{self.username}_private.pem"):
            messagebox.showerror("🔐 Keys Not Found", 
                "Please complete Setup Wizard first!")
            return

        self.show_sign_dialog()

    def show_sign_dialog(self):
        """Sign document popup with mode selection"""
        # Reset variables
        self.sign_mode.set("external")
        self.sign_file_path.set("")

        dialog = ctk.CTkToplevel(self.root)
        dialog.title("📝 Sign Document")
        dialog.geometry("520x500")
        dialog.configure(fg_color="#0f172a")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # Center
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 520) // 2
        y = (dialog.winfo_screenheight() - 500) // 2
        dialog.geometry(f"+{x}+{y}")

        # Title
        ctk.CTkLabel(dialog, text="📝 Sign Document", 
                    font=("Inter", 22, "bold"), text_color="#f8fafc").pack(pady=(20, 5))
        ctk.CTkLabel(dialog, text="Choose mode and select file", 
                    font=("Inter", 12), text_color="#94a3b8").pack(pady=(0, 15))

        # Mode Selection
        mode_frame = ctk.CTkFrame(dialog, fg_color="#1e293b", corner_radius=12)
        mode_frame.pack(fill="x", padx=25, pady=10)

        ctk.CTkLabel(mode_frame, text="Signature Mode", 
                    font=("Inter", 12, "bold"), text_color="#f8fafc").pack(anchor="w", padx=15, pady=(10, 5))

        # External
        ext_frame = ctk.CTkFrame(mode_frame, fg_color="transparent")
        ext_frame.pack(fill="x", padx=15, pady=3)
        ctk.CTkRadioButton(ext_frame, text="", variable=self.sign_mode, 
                          value="external", width=20, height=20,
                          fg_color="#6366f1").pack(side="left")
        ctk.CTkLabel(ext_frame, text="External (.sig file)", 
                    font=("Inter", 12, "bold"), text_color="#f8fafc").pack(side="left", padx=10)
        ctk.CTkLabel(ext_frame, text="Separate signature file", 
                    font=("Inter", 10), text_color="#64748b").pack(side="left")

        # Embedded
        emb_frame = ctk.CTkFrame(mode_frame, fg_color="transparent")
        emb_frame.pack(fill="x", padx=15, pady=3)
        ctk.CTkRadioButton(emb_frame, text="", variable=self.sign_mode, 
                          value="embedded", width=20, height=20,
                          fg_color="#6366f1").pack(side="left")
        ctk.CTkLabel(emb_frame, text="Embedded (PDF only)", 
                    font=("Inter", 12, "bold"), text_color="#f8fafc").pack(side="left", padx=10)
        ctk.CTkLabel(emb_frame, text="Sign inside PDF with visual stamp", 
                    font=("Inter", 10), text_color="#64748b").pack(side="left")

        # File Selection
        file_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        file_frame.pack(fill="x", padx=25, pady=15)

        ctk.CTkEntry(file_frame, textvariable=self.sign_file_path, 
                    width=300, height=40,
                    font=("Inter", 11), fg_color="#1e293b", 
                    border_color="#334155",
                    text_color="#f8fafc", 
                    placeholder_text="Select file...").pack(side="left", padx=(0, 10))

        ctk.CTkButton(file_frame, text="📁 Browse", width=100, height=40,
                     font=("Inter", 11), fg_color="#6366f1", 
                     hover_color="#4f46e5", corner_radius=8,
                     command=lambda: self.browse_sign_file(dialog)).pack(side="left")

        # SIGN BUTTON
        sign_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        sign_frame.pack(pady=20)

        ctk.CTkButton(sign_frame, text="✍️ Sign Document", width=200, height=50,
                     font=("Inter", 16, "bold"), fg_color="#10b981", 
                     hover_color="#059669", corner_radius=12,
                     command=lambda: self.execute_sign(dialog)).pack(pady=5)

        ctk.CTkButton(sign_frame, text="Cancel", width=120, height=35,
                     font=("Inter", 12), fg_color="#64748b", 
                     hover_color="#475569", corner_radius=8,
                     command=dialog.destroy).pack(pady=5)

    def browse_sign_file(self, dialog):
        """Browse for file based on selected mode"""
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
        """Execute signing based on mode"""
        file_path = self.sign_file_path.get()
        mode = self.sign_mode.get()

        # Validation
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
        """External mode - create .sig file"""
        from core.smart_sign import smart_sign

        result = smart_sign(file_path, self.username, "external", None, audit_logger=self.audit)

        # Handle different return types
        if isinstance(result, dict):
            if not result.get('success', False):
                raise Exception(result.get('message', 'Signing failed'))
            sig_path = result.get('output_file', '')
        else:
            sig_path = os.path.splitext(file_path)[0] + ".sig"

        # Verify .sig was created
        if not os.path.exists(sig_path):
            sig_path = os.path.splitext(file_path)[0] + ".sig"

        self.audit.log(self.username, "SIGN", "SUCCESS", 
                      file_name=os.path.basename(file_path),
                      details=f"Mode: EXTERNAL, Sig: {os.path.basename(sig_path)}")

        messagebox.showinfo("✅ Signature Created", 
            f"External signature created!\n\n"
            f"📄 Document: {os.path.basename(file_path)}\n"
            f"🔏 Signature: {os.path.basename(sig_path)}\n"
            f"📁 Location: {os.path.dirname(os.path.abspath(sig_path))}", 
            parent=dialog)

        dialog.destroy()
        self.show_dashboard()

    def _sign_embedded(self, file_path, dialog):
        """Embedded mode - sign inside PDF with visual stamp"""
        from core.embed_pdf import embed_pdf_signature

        output_path = embed_pdf_signature(file_path, self.username, None, audit_logger=self.audit)

        # If function doesn't return path, construct it
        if not output_path:
            output_path = file_path.replace(".pdf", "_signed.pdf")

        self.audit.log(self.username, "SIGN", "SUCCESS", 
                      file_name=os.path.basename(file_path),
                      details=f"Mode: EMBEDDED, Output: {os.path.basename(output_path)}")

        messagebox.showinfo("✅ PDF Signed", 
            f"PDF signed with embedded signature!\n\n"
            f"📄 Original: {os.path.basename(file_path)}\n"
            f"✍️ Signed PDF: {os.path.basename(output_path)}\n"
            f"📁 Saved to: {os.path.dirname(os.path.abspath(output_path))}\n\n"
            f"Visual signature stamp added to last page!", 
            parent=dialog)

        dialog.destroy()
        self.show_dashboard()

    def quick_verify(self):
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
        if not os.path.exists(f"storage/keystores/{self.username}_private.pem"):
            messagebox.showerror("Error", "Please setup your keys first!")
            return

        file = filedialog.askopenfilename(title="Select file to encrypt")
        if file:
            try:
                from core.encrypt_engine import encrypt_file
                public_key = f"storage/keystores/{self.username}_public.pem"
                enc_path = encrypt_file(file, public_key, self.username)

                # Track in database
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
        """Decrypt encrypted file with proper file dialog and output path"""
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

            messagebox.showinfo(
                "✅ Decrypt Success", 
                f"File decrypted successfully!\n\n"
                f"📄 Encrypted: {os.path.basename(file)}\n"
                f"📁 Decrypted: {os.path.basename(output_path)}\n"
                f"📂 Location: {os.path.dirname(os.path.abspath(output_path))}\n\n"
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
            messagebox.showerror("❌ Decrypt Failed", str(e))
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
        # ✅ Go back to login screen
        from main import show_login
        show_login()