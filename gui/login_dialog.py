import customtkinter as ctk
from tkinter import messagebox
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.auth_system import AuthSystem


class LoginDialog:
    def __init__(self, on_login_success):
        self.auth = AuthSystem()
        self.on_login_success = on_login_success
        
        self.dialog = ctk.CTk()
        self.dialog.title("CryptoSign - Secure Login")
        self.dialog.geometry("420x680")
        self.dialog.configure(fg_color="#0a0e1a")
        self.dialog.resizable(True, True) 
        
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - 420) // 2
        y = (self.dialog.winfo_screenheight() - 680) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        self.scroll_frame = ctk.CTkScrollableFrame(self.dialog, fg_color="#0a0e1a")
        self.scroll_frame.pack(fill="both", expand=True)
        
        self.build_ui()
    
    def build_ui(self):
        # Logo & Header
        ctk.CTkLabel(self.scroll_frame, text="", font=("Inter", 48)).pack(pady=(30, 5))
        ctk.CTkLabel(self.scroll_frame, text="CryptoSign", font=("Inter", 26, "bold"), 
                    text_color="#6366f1").pack()
        ctk.CTkLabel(self.scroll_frame, text="Secure Digital Document Signing",
                    font=("Inter", 12), text_color="#64748b").pack(pady=(5, 25))
        
        toggle = ctk.CTkFrame(self.scroll_frame, fg_color="#111827", corner_radius=25)
        toggle.pack(fill="x", padx=35, pady=15)
        
        self.login_btn = ctk.CTkButton(toggle, text="Login", width=0,
                                      fg_color="#6366f1", hover_color="#4f46e5",
                                      font=("Inter", 13, "bold"), corner_radius=20,
                                      command=self.show_login)
        self.login_btn.pack(side="left", expand=True, padx=5, pady=5)
        
        self.register_btn = ctk.CTkButton(toggle, text="Register", width=0,
                                         fg_color="transparent", hover_color="#1e293b",
                                         font=("Inter", 13, "bold"), corner_radius=20,
                                         command=self.show_register)
        self.register_btn.pack(side="right", expand=True, padx=5, pady=5)
        
        self.form_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.form_frame.pack(fill="both", expand=True, padx=35, pady=(0, 20))
        
        self.show_login()
    
    def show_login(self):
        self.login_btn.configure(fg_color="#6366f1", text_color="white")
        self.register_btn.configure(fg_color="transparent", text_color="#94a3b8")
        
        for w in self.form_frame.winfo_children():
            w.destroy()
        
        ctk.CTkLabel(self.form_frame, text="Username", font=("Inter", 12, "bold"),
                    text_color="#f8fafc").pack(anchor="w", pady=(10, 5))
        self.l_user = ctk.CTkEntry(self.form_frame, height=48, font=("Inter", 14),
                                    fg_color="#0a0e1a", border_color="#1e293b",
                                    text_color="#f8fafc", corner_radius=10,
                                    placeholder_text="Enter your username")
        self.l_user.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(self.form_frame, text="Password", font=("Inter", 12, "bold"),
                    text_color="#f8fafc").pack(anchor="w", pady=(5, 5))
        
        pass_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        pass_frame.pack(fill="x", pady=(0, 5))
        
        self.l_pass = ctk.CTkEntry(pass_frame, height=48, font=("Inter", 14),
                                    fg_color="#0a0e1a", border_color="#1e293b",
                                    text_color="#f8fafc", show="*", corner_radius=10,
                                    placeholder_text="Enter your password")
        self.l_pass.pack(side="left", fill="x", expand=True)
        
        self.eye_btn = ctk.CTkButton(pass_frame, text="👁", width=42, height=48,
                                    fg_color="#0a0e1a", hover_color="#1e293b",
                                    border_color="#1e293b", border_width=1,
                                    font=("Inter", 14), corner_radius=10,
                                    command=self.toggle_login_pass)
        self.eye_btn.pack(side="right", padx=(5, 0))
        
        options = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        options.pack(fill="x", pady=(10, 15))
        
        self.remember_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(options, text="Remember me", variable=self.remember_var,
                       font=("Inter", 11), text_color="#94a3b8",
                       fg_color="#6366f1", hover_color="#4f46e5").pack(side="left")
        
        ctk.CTkButton(options, text="Forgot Password?", width=0, height=25,
                     font=("Inter", 11), fg_color="transparent", hover_color="#1e293b",
                     text_color="#6366f1", command=self.forgot_password).pack(side="right")
        
        ctk.CTkButton(self.form_frame, text="Sign In", height=50,
                     font=("Inter", 15, "bold"), fg_color="#6366f1",
                     hover_color="#4f46e5", corner_radius=12,
                     command=self.do_login).pack(fill="x", pady=(5, 15))
    
    def show_register(self):
        self.login_btn.configure(fg_color="transparent", text_color="#94a3b8")
        self.register_btn.configure(fg_color="#6366f1", text_color="white")
        
        for w in self.form_frame.winfo_children():
            w.destroy()
        
        ctk.CTkLabel(self.form_frame, text="Username", font=("Inter", 12, "bold"),
                    text_color="#f8fafc").pack(anchor="w", pady=(8, 5))
        self.r_user = ctk.CTkEntry(self.form_frame, height=48, font=("Inter", 14),
                                      fg_color="#0a0e1a", border_color="#1e293b", 
                                      corner_radius=10, placeholder_text="Choose a username")
        self.r_user.pack(fill="x", pady=(0, 3))
        self.r_user.bind("<KeyRelease>", lambda e: self.validate_username())
        
        self.user_status = ctk.CTkLabel(self.form_frame, text="", font=("Inter", 11))
        self.user_status.pack(anchor="w", pady=(0, 5))
        
        ctk.CTkLabel(self.form_frame, text="Email", font=("Inter", 12, "bold"),
                    text_color="#f8fafc").pack(anchor="w", pady=(5, 5))
        self.r_email = ctk.CTkEntry(self.form_frame, height=48, font=("Inter", 14),
                                     fg_color="#0a0e1a", border_color="#1e293b",
                                     corner_radius=10, placeholder_text="your@email.com")
        self.r_email.pack(fill="x", pady=(0, 3))
        self.r_email.bind("<KeyRelease>", lambda e: self.validate_email())
        
        self.email_status = ctk.CTkLabel(self.form_frame, text="", font=("Inter", 11))
        self.email_status.pack(anchor="w", pady=(0, 5))
        
        ctk.CTkLabel(self.form_frame, text="Password", font=("Inter", 12, "bold"),
                    text_color="#f8fafc").pack(anchor="w", pady=(5, 5))
        
        pass_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        pass_frame.pack(fill="x", pady=(0, 3))
        
        self.r_pass = ctk.CTkEntry(pass_frame, height=48, font=("Inter", 14),
                                      fg_color="#0a0e1a", border_color="#1e293b", 
                                      show="*", corner_radius=10,
                                      placeholder_text="Create a strong password")
        self.r_pass.pack(side="left", fill="x", expand=True)
        self.r_pass.bind("<KeyRelease>", lambda e: self.check_password_strength())
        
        self.r_eye_btn = ctk.CTkButton(pass_frame, text="👁", width=42, height=48,
                                        fg_color="#0a0e1a", hover_color="#1e293b",
                                        border_color="#1e293b", border_width=1,
                                        font=("Inter", 14), corner_radius=10,
                                        command=self.toggle_reg_pass)
        self.r_eye_btn.pack(side="right", padx=(5, 0))
        
        self.strength_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.strength_frame.pack(fill="x", pady=(5, 2))
        
        self.strength_bar = ctk.CTkProgressBar(self.strength_frame, width=400, height=5,
                                              fg_color="#1e293b", progress_color="#ef4444")
        self.strength_bar.pack(fill="x")
        self.strength_bar.set(0)
        
        self.strength_label = ctk.CTkLabel(self.form_frame, text="Enter password", 
                                          font=("Inter", 11), text_color="#64748b")
        self.strength_label.pack(anchor="w", pady=(0, 5))
        
        ctk.CTkLabel(self.form_frame, text="Confirm Password", font=("Inter", 12, "bold"),
                    text_color="#f8fafc").pack(anchor="w", pady=(5, 5))
        
        conf_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        conf_frame.pack(fill="x", pady=(0, 3))
        
        self.r_confirm = ctk.CTkEntry(conf_frame, height=48, font=("Inter", 14),
                                         fg_color="#0a0e1a", border_color="#1e293b", 
                                         show="*", corner_radius=10,
                                         placeholder_text="Repeat your password")
        self.r_confirm.pack(side="left", fill="x", expand=True)
        
        self.conf_eye_btn = ctk.CTkButton(conf_frame, text="👁", width=42, height=48,
                                           fg_color="#0a0e1a", hover_color="#1e293b",
                                           border_color="#1e293b", border_width=1,
                                           font=("Inter", 14), corner_radius=10,
                                           command=self.toggle_conf_pass)
        self.conf_eye_btn.pack(side="right", padx=(5, 0))
        
        self.match_label = ctk.CTkLabel(self.form_frame, text="", font=("Inter", 11))
        self.match_label.pack(anchor="w", pady=(0, 5))
        self.r_confirm.bind("<KeyRelease>", lambda e: self.check_match())
        
        self.terms_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self.form_frame, text="I agree to Terms & Conditions", variable=self.terms_var,
                       font=("Inter", 11), text_color="#94a3b8",
                       fg_color="#6366f1", hover_color="#4f46e5").pack(anchor="w", pady=(5, 12))
        
        ctk.CTkButton(self.form_frame, text="Create Account", height=50,
                     font=("Inter", 15, "bold"), fg_color="#10b981",
                     hover_color="#059669", corner_radius=12,
                     command=self.do_register).pack(fill="x", pady=(5, 0))
    
    def toggle_login_pass(self):
        show = "" if self.l_pass.cget("show") == "*" else "*"
        self.l_pass.configure(show=show)
        self.eye_btn.configure(text="" if show == "" else "👁")
    
    def toggle_reg_pass(self):
        show = "" if self.r_pass.cget("show") == "*" else "*"
        self.r_pass.configure(show=show)
        self.r_eye_btn.configure(text="" if show == "" else "👁")
    
    def toggle_conf_pass(self):
        show = "" if self.r_confirm.cget("show") == "*" else "*"
        self.r_confirm.configure(show=show)
        self.conf_eye_btn.configure(text="" if show == "" else "👁")
    
    def validate_username(self):
        username = self.r_user.get().strip()
        if len(username) < 3:
            self.user_status.configure(text="Min 3 characters", text_color="#ef4444")
            return False
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            self.user_status.configure(text="Letters, numbers, underscore only", text_color="#ef4444")
            return False
        self.user_status.configure(text="Valid username", text_color="#10b981")
        return True
    
    def validate_email(self):
        email = self.r_email.get().strip()
        if not email:
            self.email_status.configure(text="Email required", text_color="#ef4444")
            return False
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            self.email_status.configure(text="Invalid email format", text_color="#ef4444")
            return False
        self.email_status.configure(text="Valid email", text_color="#10b981")
        return True
    
    def check_password_strength(self):
        password = self.r_pass.get()
        score = 0
        
        if len(password) >= 8: score += 1
        if len(password) >= 12: score += 1
        if re.search(r'[A-Z]', password): score += 1
        if re.search(r'[a-z]', password): score += 1
        if re.search(r'[0-9]', password): score += 1
        if re.search(r'[^A-Za-z0-9]', password): score += 1
        
        display_score = min(score, 5)
        
        colors = {0: "#ef4444", 1: "#ef4444", 2: "#f59e0b", 3: "#f59e0b", 4: "#10b981", 5: "#10b981"}
        labels = {0: "Very Weak", 1: "Weak", 2: "Fair", 3: "Good", 4: "Strong", 5: "Very Strong"}
        
        self.strength_bar.set(display_score / 5)
        self.strength_bar.configure(progress_color=colors.get(display_score, "#10b981"))
        self.strength_label.configure(text=labels.get(display_score, "Very Strong"), 
                                     text_color=colors.get(display_score, "#10b981"))
        
        return score >= 2
    
    def check_match(self):
        if self.r_pass.get() == self.r_confirm.get() and self.r_pass.get():
            self.match_label.configure(text="Passwords match", text_color="#10b981")
            return True
        else:
            self.match_label.configure(text="Passwords don't match", text_color="#ef4444")
            return False
    
    def do_login(self):
        username = self.l_user.get().strip()
        password = self.l_pass.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Fill all fields!")
            return
        
        if len(password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters!")
            return
        
        user, msg = self.auth.login(username, password)
        
        if user:
            self.dialog.destroy()
            self.on_login_success(user)
        else:
            messagebox.showerror("Error", msg)
    
    def do_register(self):
        username = self.r_user.get().strip()
        email = self.r_email.get().strip()
        password = self.r_pass.get()
        confirm = self.r_confirm.get()
        
        if not username or not email or not password:
            messagebox.showerror("Error", "Fill all fields!")
            return
        
        if not self.validate_username():
            messagebox.showerror("Error", "Invalid username!")
            return
        
        if not self.validate_email():
            messagebox.showerror("Error", "Invalid email!")
            return
        
        if len(password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters!")
            return
        
        if not self.check_password_strength():
            messagebox.showerror("Error", "Password too weak! Use mix of uppercase, lowercase, numbers and symbols.")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords don't match!")
            return
        
        if not self.terms_var.get():
            messagebox.showerror("Error", "Please accept Terms & Conditions!")
            return
        
        success, msg = self.auth.register(username, password)
        
        if success:
            messagebox.showinfo("Success", f"Account created for {email}!\n\nPlease login.")
            self.show_login()
        else:
            messagebox.showerror("Error", msg)
    
    def forgot_password(self):
        messagebox.showinfo("Forgot Password", 
            "Please contact administrator to reset your password.\n\n"
            "Email: admin@cryptosign.com")
    
    def run(self):
        self.dialog.mainloop()