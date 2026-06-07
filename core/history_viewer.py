import customtkinter as ctk


def show_history_dialog(parent, username, audit_logger, colors=None):
    """Show audit history dialog for a user."""
    if colors is None:
        colors = {
            "bg": "#0a0e1a", "card": "#111827", "accent": "#6366f1",
            "text": "#f8fafc", "text_muted": "#94a3b8",
            "success": "#10b981", "danger": "#ef4444", "warning": "#f59e0b"
        }

    history = audit_logger.get_user_history(username, limit=50)

    dialog = ctk.CTkToplevel(parent)
    dialog.title(f"Audit History - {username}")
    dialog.geometry("750x550")
    dialog.configure(fg_color=colors["bg"])

    ctk.CTkLabel(dialog, text=f"Recent Activity for {username}",
                font=("Inter", 20, "bold"), text_color=colors["accent"]).pack(pady=(20, 15))

    # Stats
    if history:
        stats = audit_logger.get_statistics(username)
        if stats:
            stats_frame = ctk.CTkFrame(dialog, fg_color=colors["card"], corner_radius=8)
            stats_frame.pack(fill="x", padx=20, pady=(0, 10))
            stats_text = " | ".join([f"{row[0]}: {row[1]}" for row in stats])
            ctk.CTkLabel(stats_frame, text=stats_text, font=("Inter", 12),
                        text_color=colors["text_muted"]).pack(pady=10)

    # Scrollable list
    scroll_frame = ctk.CTkScrollableFrame(dialog, fg_color=colors["card"], width=700, height=380)
    scroll_frame.pack(padx=20, pady=10, fill="both", expand=True)

    # Headers
    header_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
    header_frame.pack(fill="x", padx=10, pady=5)
    headers = [("Time", 180), ("Action", 120), ("File", 220), ("Result", 100)]
    for h, w in headers:
        ctk.CTkLabel(header_frame, text=h, font=("Inter", 12, "bold"),
                    text_color=colors["text_muted"], width=w).pack(side="left", padx=5)

    # Data rows
    if not history:
        ctk.CTkLabel(scroll_frame, text="No activity found", font=("Inter", 14),
                    text_color=colors["text_muted"]).pack(pady=50)
    else:
        for row in history:
            timestamp, action, file_name, result, details = row
            row_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=10, pady=2)

            if result in ["SUCCESS", "VALID"]:
                result_color = colors["success"]
            elif result in ["FAILED", "INVALID"]:
                result_color = colors["danger"]
            else:
                result_color = colors["warning"]

            ctk.CTkLabel(row_frame, text=timestamp[:19], font=("Inter", 11),
                        text_color=colors["text"], width=180).pack(side="left", padx=5)
            ctk.CTkLabel(row_frame, text=action, font=("Inter", 11),
                        text_color=colors["text"], width=120).pack(side="left", padx=5)
            ctk.CTkLabel(row_frame, text=file_name or "-", font=("Inter", 11),
                        text_color=colors["text_muted"], width=220).pack(side="left", padx=5)
            ctk.CTkLabel(row_frame, text=result, font=("Inter", 11, "bold"),
                        text_color=result_color, width=100).pack(side="left", padx=5)

    # Export button
    def export_history():
        import tkinter.filedialog as fd
        filepath = fd.asksaveasfilename(defaultextension=".csv",
                                       filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if filepath:
            audit_logger.export_to_csv(filepath, username)
            ctk.CTkLabel(dialog, text=f"Exported to {filepath}", font=("Inter", 12),
                        text_color=colors["success"]).pack(pady=5)

    ctk.CTkButton(dialog, text="Export to CSV", width=150, height=35,
                 font=("Inter", 12), fg_color=colors["accent"],
                 command=export_history).pack(pady=15)

    return dialog