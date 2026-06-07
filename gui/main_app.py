import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from tkinter import filedialog, messagebox
import hashlib

# Core imports
from core.key_manager import generate_key_pair, load_private_key, is_key_encrypted
from core.ca_engine import create_root_ca, load_ca_private_key
from core.cert_manager import issue_certificate
from core.verify_engine import verify_document
from core.encrypt_engine import encrypt_file
from core.decrypt_engine import decrypt_file
from core.revocation import revoke_user
from core.smart_sign import smart_sign
from core.audit_logger import AuditLogger
from core.batch_sign import create_batch_dialog
from core.history_viewer import show_history_dialog

# Colors
COLORS = {
    "bg": "#0a0e1a", "card": "#111827", "accent": "#6366f1",
    "accent_hover": "#4f46e5", "accent_text": "#ffffff",
    "success": "#10b981", "success_hover": "#059669", "success_text": "#ffffff",
    "danger": "#ef4444", "danger_hover": "#dc2626", "danger_text": "#ffffff",
    "warning": "#f59e0b", "warning_hover": "#d97706", "warning_text": "#1a1a2e",
    "text": "#f8fafc", "text_muted": "#94a3b8", "border": "#1e293b"
}


class CryptoSignApp:
    def __init__(self, root, user=None):
        self.root = root
        self.current_user = user or {"username": "", "role": "user"}
        self.is_admin = self.current_user.get("role") == "admin"
        self.username = self.current_user.get("username", "")
        self.password = ""
        self.mode = ctk.StringVar(value="none")
        self.audit = AuditLogger()

        self.root.title("CryptoSign - Digital Document Signing Tool")
        self.root.geometry("850x780")
        self.root.configure(fg_color=COLORS["bg"])
        self.root.minsize(850, 780)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.build_ui()
        self.setup_shortcuts()

        # Auto-fill username if logged in
        if self.username:
            self.username_entry.insert(0, self.username)
            self.user_info.configure(text=f"User: {self.username}")
            self.update_status(f"Logged in as {self.username}", "success")

    def build_ui(self):
        self.main_frame = ctk.CTkFrame(self.root, fg_color=COLORS["bg"])
        self.main_frame.pack(fill="both", expand=True, padx=30, pady=20)

        # ===== HEADER =====
        header = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="CryptoSign  |  Digital Document Signing Tool",
                    font=("Inter", 20, "bold"), text_color=COLORS["text"]).pack(side="left")

        accent_line = ctk.CTkFrame(self.main_frame, fg_color=COLORS["accent"], height=3)
        accent_line.pack(fill="x", pady=(0, 20))

        # ===== USER SETUP (with Password) =====
        user_frame = ctk.CTkFrame(self.main_frame, fg_color=COLORS["card"], corner_radius=12)
        user_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(user_frame, text="👤  User Setup", font=("Inter", 16, "bold"),
                    text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(15, 10))

        # Username row
        user_row = ctk.CTkFrame(user_frame, fg_color="transparent")
        user_row.pack(fill="x", padx=20, pady=(0, 8))

        ctk.CTkLabel(user_row, text="Username:", font=("Inter", 13),
                    text_color=COLORS["text_muted"]).pack(side="left", padx=(0, 10))
        self.username_entry = ctk.CTkEntry(user_row, width=200, height=36, font=("Inter", 13),
                                          fg_color=COLORS["bg"], border_color=COLORS["border"],
                                          text_color=COLORS["text"], corner_radius=8)
        self.username_entry.pack(side="left", padx=(0, 10))

        # Password row
        pass_row = ctk.CTkFrame(user_frame, fg_color="transparent")
        pass_row.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(pass_row, text="Password:", font=("Inter", 13),
                    text_color=COLORS["text_muted"]).pack(side="left", padx=(0, 10))
        self.password_entry = ctk.CTkEntry(pass_row, width=200, height=36, font=("Inter", 13),
                                          fg_color=COLORS["bg"], border_color=COLORS["border"],
                                          text_color=COLORS["text"], corner_radius=8, show="*")
        self.password_entry.pack(side="left", padx=(0, 10))

        # Show password checkbox
        self.show_pass_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(pass_row, text="Show", variable=self.show_pass_var,
                       command=self.toggle_password_visibility, font=("Inter", 11),
                       text_color=COLORS["text_muted"], fg_color=COLORS["accent"],
                       hover_color=COLORS["accent_hover"]).pack(side="left", padx=(5, 10))

        ctk.CTkButton(pass_row, text="Set User", width=100, height=36,
                     font=("Inter", 12, "bold"), fg_color=COLORS["accent"],
                     hover_color=COLORS["accent_hover"], text_color=COLORS["accent_text"],
                     corner_radius=8, command=self.set_user).pack(side="left")

        # ===== SIGNATURE MODE =====
        mode_frame = ctk.CTkFrame(self.main_frame, fg_color=COLORS["card"], corner_radius=12)
        mode_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(mode_frame, text="📝  Signature Mode", font=("Inter", 16, "bold"),
                    text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(15, 10))

        dropdown_row = ctk.CTkFrame(mode_frame, fg_color="transparent")
        dropdown_row.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(dropdown_row, text="Select mode:", font=("Inter", 13),
                    text_color=COLORS["text_muted"]).pack(side="left", padx=(0, 10))

        self.mode_dropdown = ctk.CTkOptionMenu(
            dropdown_row, values=["-- Select Mode --", "External (.sig file)", "Embedded (PDF / Office)"],
            width=250, height=36, font=("Inter", 13), dropdown_font=("Inter", 12),
            fg_color=COLORS["bg"], button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"], dropdown_fg_color=COLORS["card"],
            dropdown_hover_color=COLORS["accent"], dropdown_text_color=COLORS["text"],
            text_color=COLORS["text"], corner_radius=8, command=self.on_mode_change
        )
        self.mode_dropdown.pack(side="left")
        self.mode_dropdown.set("-- Select Mode --")

        # ===== QUICK ACTIONS =====
        actions_frame = ctk.CTkFrame(self.main_frame, fg_color=COLORS["card"], corner_radius=12)
        actions_frame.pack(fill="both", expand=True, pady=10)

        ctk.CTkLabel(actions_frame, text="⚡  Quick Actions", font=("Inter", 16, "bold"),
                    text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(15, 12))

        grid = ctk.CTkFrame(actions_frame, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Row 1
        row1 = ctk.CTkFrame(grid, fg_color="transparent")
        row1.pack(fill="x", pady=6)
        self.create_btn(row1, "⚙️  Setup User", self.setup, COLORS["accent"], COLORS["accent_hover"], COLORS["accent_text"])
        self.create_btn(row1, "📝  Sign File", self.sign, COLORS["accent"], COLORS["accent_hover"], COLORS["accent_text"])

        # Row 2
        row2 = ctk.CTkFrame(grid, fg_color="transparent")
        row2.pack(fill="x", pady=6)
        self.create_btn(row2, "✅  Verify File", self.verify, COLORS["success"], COLORS["success_hover"], COLORS["success_text"])
        self.create_btn(row2, "🔐  Encrypt File", self.encrypt, COLORS["accent"], COLORS["accent_hover"], COLORS["accent_text"])

        # Row 3
        row3 = ctk.CTkFrame(grid, fg_color="transparent")
        row3.pack(fill="x", pady=6)
        self.create_btn(row3, "🔓  Decrypt File", self.decrypt, COLORS["accent"], COLORS["accent_hover"], COLORS["accent_text"])
        self.create_btn(row3, "🔍  File Hash", self.generate_hash, COLORS["warning"], COLORS["warning_hover"], COLORS["warning_text"])

        # Row 4 - Batch + History
        row4 = ctk.CTkFrame(grid, fg_color="transparent")
        row4.pack(fill="x", pady=6)
        self.create_btn(row4, "📦  Batch Sign", self.batch_sign, COLORS["accent"], COLORS["accent_hover"], COLORS["accent_text"])
        self.create_btn(row4, "📜  History", self.show_history, COLORS["accent"], COLORS["accent_hover"], COLORS["accent_text"])

        # Row 5 - Revoke + Admin Panel (if admin)
        row5 = ctk.CTkFrame(grid, fg_color="transparent")
        row5.pack(fill="x", pady=6)

        # Revoke User (always)
        self.create_btn(row5, "❌  Revoke User", self.revoke, COLORS["danger"], COLORS["danger_hover"], COLORS["danger_text"])

        # Admin Panel (only if admin)
        if self.is_admin:
            self.create_btn(row5, "⚙️  Admin Panel", self.open_admin, "#ef4444", "#dc2626", "#ffffff")

        # ===== STATUS BAR =====
        status_frame = ctk.CTkFrame(self.main_frame, fg_color=COLORS["card"], corner_radius=10)
        status_frame.pack(fill="x", pady=(15, 0))

        status_left = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_left.pack(side="left", padx=15, pady=12)

        self.status_dot = ctk.CTkLabel(status_left, text="●", font=("Inter", 16),
                                      text_color=COLORS["success"])
        self.status_dot.pack(side="left", padx=(0, 8))

        self.status_label = ctk.CTkLabel(status_left, text="Ready - Set username and password",
                                        font=("Inter", 13), text_color=COLORS["text"])
        self.status_label.pack(side="left")

        self.user_info = ctk.CTkLabel(status_frame, text="No user", font=("Inter", 12),
                                     text_color=COLORS["text_muted"])
        self.user_info.pack(side="right", padx=15, pady=12)

    def create_btn(self, parent, text, command, color, hover, text_color):
        btn = ctk.CTkButton(parent, text=text, width=180, height=45, font=("Inter", 14, "bold"),
                           fg_color=color, hover_color=hover, text_color=text_color,
                           corner_radius=10, command=command)
        btn.pack(side="left", padx=8, expand=True, fill="x")
        return btn

    def toggle_password_visibility(self):
        show = "" if self.show_pass_var.get() else "*"
        self.password_entry.configure(show=show)

    def on_mode_change(self, choice):
        if choice == "External (.sig file)":
            self.mode.set("external")
        elif choice == "Embedded (PDF / Office)":
            self.mode.set("embedded")
        else:
            self.mode.set("none")

    def setup_shortcuts(self):
        self.root.bind("<Control-s>", lambda e: self.sign())
        self.root.bind("<Control-v>", lambda e: self.verify())
        self.root.bind("<Control-e>", lambda e: self.encrypt())
        self.root.bind("<Control-d>", lambda e: self.decrypt())
        self.root.bind("<Control-h>", lambda e: self.generate_hash())
        self.root.bind("<Control-b>", lambda e: self.batch_sign())
        self.root.bind("<Control-l>", lambda e: self.show_history())

    def set_user(self):
        self.username = self.username_entry.get().strip()
        self.password = self.password_entry.get()

        if not self.username:
            messagebox.showerror("Error", "Please enter a username!")
            return

        self.user_info.configure(text=f"User: {self.username}")

        if self.check_user_setup() and is_key_encrypted(self.username):
            self.update_status(f"User: {self.username} (key encrypted)", "success")
        else:
            self.update_status("User set successfully", "success")

        self.audit.log(self.username, "USER_SET", "SUCCESS", details=f"Password: {bool(self.password)}")

    def check_user_setup(self):
        return os.path.exists(f"storage/keystores/{self.username}_private.pem")

    def choose_file(self):
        return filedialog.askopenfilename(filetypes=[
            ("All Files", "*.*"), ("Encrypted data", "*.bin"),
            ("PDF Files", "*.pdf"), ("Word Files", "*.docx"), ("Excel Files", "*.xlsx"),
        ])

    def update_status(self, message, status_type="normal"):
        self.status_label.configure(text=message)
        colors = {"success": COLORS["success"], "error": COLORS["danger"],
                 "warning": COLORS["warning"]}
        self.status_dot.configure(text_color=colors.get(status_type, COLORS["text_muted"]))

    def setup(self):
        if not self.username:
            messagebox.showerror("Error", "Enter username first!")
            self.update_status("No username set", "error")
            return

        if not os.path.exists("storage/ca/ca_private.pem"):
            create_root_ca()

        private, public = generate_key_pair(self.username, self.password if self.password else None)
        ca_key = load_ca_private_key()
        issue_certificate(ca_key, public, self.username)

        self.audit.log(self.username, "SETUP", "SUCCESS",
                      details=f"Password protected: {bool(self.password)}")
        self.update_status("User setup complete (keys secured)", "success")

    def sign(self):
        if not self.check_user_setup():
            messagebox.showerror("Error", "User not setup!")
            self.update_status("User not setup", "error")
            return

        if self.mode.get() == "none":
            messagebox.showerror("Error", "Please select a signature mode first!")
            self.update_status("Select signature mode", "warning")
            return

        file = self.choose_file()
        if file:
            try:
                smart_sign(file, self.username, self.mode.get(), self.password, audit_logger=self.audit)
                file_hash = hashlib.sha256(open(file, "rb").read()).hexdigest()[:16]
                self.audit.log(self.username, "SIGN", "SUCCESS",
                              file_name=os.path.basename(file), file_hash=file_hash,
                              details=f"Mode: {self.mode.get()}")
                self.update_status(f"Signed ({self.mode.get()})", "success")
            except Exception as e:
                self.audit.log(self.username, "SIGN", "FAILED",
                              file_name=os.path.basename(file), details=str(e))
                messagebox.showerror("Error", str(e))
                self.update_status("Signing failed", "error")

    def verify(self):
        file = self.choose_file()
        if file:
            result = verify_document(file, f"storage/keystores/{self.username}_public.pem", self.username)
            self.audit.log(self.username, "VERIFY", result, file_name=os.path.basename(file))

            if result == "VALID":
                self.update_status("Document verified - Authentic", "success")
                messagebox.showinfo("Verification", "Document is authentic!")
            elif result == "INVALID":
                self.update_status("Document tampered!", "error")
                messagebox.showerror("Warning", "File has been tampered!")
            elif result == "NOT_SIGNED":
                self.update_status("Document not signed", "warning")
                messagebox.showwarning("Warning", "Document is not signed")
            else:
                self.update_status("Verification error", "warning")

    def encrypt(self):
        file = self.choose_file()
        if not file:
            return

        public_key_path = f"storage/keystores/{self.username}_public.pem"
        if not os.path.exists(public_key_path):
            messagebox.showerror("Error", "Setup user first!")
            self.update_status("User not setup", "error")
            return

        try:
            enc_path = encrypt_file(file, public_key_path, self.username)
            self.audit.add_user_file(
                username=self.username,
                file_type='encrypted',
                file_path=enc_path,
                original_name=os.path.basename(file),
                file_size=os.path.getsize(enc_path)
            )
            self.audit.log(self.username, "ENCRYPT", "SUCCESS", file_name=os.path.basename(file))
            self.update_status("File encrypted", "success")
            messagebox.showinfo("Success", f"File encrypted!\nSaved to: {enc_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.update_status("Encryption failed", "error")

    def decrypt(self):
        if not self.check_user_setup():
            messagebox.showerror("Error", "User not setup!")
            self.update_status("User not setup", "error")
            return

        file = self.choose_file()
        if not file:
            return

        if not file.endswith(".bin"):
            messagebox.showerror("Error", "Select encrypted .bin file!")
            return

        try:
            decrypt_file(self.username, file, self.password)
            self.audit.log(self.username, "DECRYPT", "SUCCESS")
            messagebox.showinfo("Success", "File decrypted!\nCheck: storage/encrypted/{}/decrypted/".format(self.username))
            self.update_status("File decrypted", "success")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.update_status("Decryption failed", "error")

    def generate_hash(self):
        file = self.choose_file()
        if not file:
            return

        try:
            with open(file, "rb") as f:
                data = f.read()

            sha256_hash = hashlib.sha256(data).hexdigest()
            self.audit.log(self.username, "HASH", "SUCCESS",
                          file_name=os.path.basename(file), file_hash=sha256_hash[:16])

            hash_dialog = ctk.CTkToplevel(self.root)
            hash_dialog.title("SHA-256 File Hash")
            hash_dialog.geometry("650x200")
            hash_dialog.configure(fg_color=COLORS["bg"])
            hash_dialog.resizable(False, False)

            ctk.CTkLabel(hash_dialog, text="🔍 SHA-256 Hash", font=("Inter", 18, "bold"),
                        text_color=COLORS["accent"]).pack(pady=(25, 15))

            hash_display = ctk.CTkEntry(hash_dialog, width=600, height=42, font=("Courier", 12),
                                       fg_color=COLORS["card"], border_color=COLORS["border"],
                                       text_color=COLORS["text"], corner_radius=8)
            hash_display.insert(0, sha256_hash)
            hash_display.pack(pady=10)
            hash_display.configure(state="readonly")

            ctk.CTkButton(hash_dialog, text="📋 Copy to Clipboard", width=200, height=38,
                         font=("Inter", 13), fg_color=COLORS["accent"],
                         hover_color=COLORS["accent_hover"], text_color=COLORS["accent_text"],
                         corner_radius=8, command=lambda: self.root.clipboard_append(sha256_hash)).pack(pady=15)

            self.update_status("Hash generated", "success")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.update_status("Hash generation failed", "error")

    def batch_sign(self):
        if not self.check_user_setup():
            messagebox.showerror("Error", "User not setup!")
            return

        if self.mode.get() == "none":
            messagebox.showerror("Error", "Please select a signature mode first!")
            return

        create_batch_dialog(self.root, self.username, self.mode.get(), self.password, COLORS)

    def show_history(self):
        if not self.username:
            messagebox.showerror("Error", "Set a user first!")
            return

        show_history_dialog(self.root, self.username, self.audit, COLORS)

    def revoke(self):
        revoke_user(self.username)
        self.audit.log(self.username, "REVOKE", "SUCCESS")
        self.update_status("User revoked", "error")

    # ===== ADMIN PANEL - FIXED =====
    def open_admin(self):
        """Open admin dashboard in new window"""
        from gui.admin_dashboard import AdminDashboard
        admin_root = ctk.CTkToplevel(self.root)
        admin_root.geometry("1200x800")
        AdminDashboard(admin_root, self.current_user)