import customtkinter as ctk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.login_dialog import LoginDialog
from gui.main_app import CryptoSignApp
from gui.admin_dashboard import AdminDashboard
from gui.user_dashboard import UserDashboard


def start_app(user):
    """Login success pachi check role"""
    if user.get("role") == "admin":
        # Admin → Admin Dashboard
        root = ctk.CTk()
        AdminDashboard(root, user)
        root.mainloop()
    else:
        # User → User Dashboard (NEW!)
        root = ctk.CTk()
        UserDashboard(root, user)
        root.mainloop()


def show_login():
    """Show login dialog - used after logout"""
    login = LoginDialog(on_login_success=start_app)
    login.run()


if __name__ == "__main__":
    show_login()