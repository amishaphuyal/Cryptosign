import os
from tkinter import filedialog
import customtkinter as ctk

from core.smart_sign import smart_sign


def batch_sign_folder(username, mode, password=None, folder_path=None, file_types=None, progress_callback=None):
    """
    Sign multiple files in a folder.

    Args:
        username: User to sign as
        mode: 'external' or 'embedded'
        password: Password for encrypted private key (optional)
        folder_path: Folder to process (None = show dialog)
        file_types: List of extensions ['.pdf', '.docx'] (None = all)
        progress_callback: Function(current, total, filename) for progress updates

    Returns:
        dict: {'signed': count, 'failed': count, 'errors': list}
    """
    if folder_path is None:
        folder_path = filedialog.askdirectory(title="Select Folder for Batch Signing")

    if not folder_path:
        return None

    if file_types is None:
        file_types = ['.pdf', '.docx', '.xlsx', '.txt']

    file_types = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' for ext in file_types]

    results = {'signed': 0, 'failed': 0, 'errors': [], 'files_processed': []}

    files_to_sign = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in file_types):
                files_to_sign.append(os.path.join(root, file))

    total = len(files_to_sign)

    for i, file_path in enumerate(files_to_sign):
        try:
            smart_sign(file_path, username, mode, password)
            results['signed'] += 1
            results['files_processed'].append((file_path, 'SUCCESS'))
        except Exception as e:
            results['failed'] += 1
            results['errors'].append((file_path, str(e)))
            results['files_processed'].append((file_path, 'FAILED'))

        if progress_callback:
            progress_callback(i + 1, total, os.path.basename(file_path))

    return results


def create_batch_dialog(parent, username, mode, password=None, colors=None):
    """Create a batch signing dialog window."""
    if colors is None:
        colors = {
            "bg": "#0a0e1a", "card": "#111827", "accent": "#6366f1",
            "accent_hover": "#4f46e5", "text": "#f8fafc",
            "text_muted": "#94a3b8", "success": "#10b981", "danger": "#ef4444"
        }

    dialog = ctk.CTkToplevel(parent)
    dialog.title("Batch Sign Documents")
    dialog.geometry("500x400")
    dialog.configure(fg_color=colors["bg"])
    dialog.resizable(False, False)

    ctk.CTkLabel(dialog, text="Batch Sign Documents", font=("Inter", 20, "bold"),
                text_color=colors["accent"]).pack(pady=(20, 15))

    ctk.CTkLabel(dialog, text="Select file types to sign:", font=("Inter", 14),
                text_color=colors["text"]).pack(anchor="w", padx=30, pady=(10, 5))

    pdf_var = ctk.BooleanVar(value=True)
    docx_var = ctk.BooleanVar(value=True)
    xlsx_var = ctk.BooleanVar(value=False)

    checkboxes = ctk.CTkFrame(dialog, fg_color="transparent")
    checkboxes.pack(fill="x", padx=30, pady=5)

    ctk.CTkCheckBox(checkboxes, text="PDF Files (.pdf)", variable=pdf_var,
                   text_color=colors["text"], fg_color=colors["accent"]).pack(anchor="w", pady=3)
    ctk.CTkCheckBox(checkboxes, text="Word Documents (.docx)", variable=docx_var,
                   text_color=colors["text"], fg_color=colors["accent"]).pack(anchor="w", pady=3)
    ctk.CTkCheckBox(checkboxes, text="Excel Files (.xlsx)", variable=xlsx_var,
                   text_color=colors["text"], fg_color=colors["accent"]).pack(anchor="w", pady=3)

    progress_label = ctk.CTkLabel(dialog, text="Ready to start", 
                                  font=("Inter", 12), text_color=colors["text_muted"])
    progress_label.pack(pady=(20, 5))

    progress_bar = ctk.CTkProgressBar(dialog, width=400, height=20,
                                     fg_color=colors["card"], progress_color=colors["accent"])
    progress_bar.pack(padx=30, pady=5)
    progress_bar.set(0)

    result_label = ctk.CTkLabel(dialog, text="", 
                               font=("Inter", 12), text_color=colors["text"])
    result_label.pack(pady=10)

    def on_progress(current, total, filename):
        progress = current / total if total > 0 else 0
        progress_bar.set(progress)
        progress_label.configure(text=f"Signing: {filename} ({current}/{total})")
        dialog.update()

    def start_batch():
        extensions = []
        if pdf_var.get(): extensions.append('.pdf')
        if docx_var.get(): extensions.append('.docx')
        if xlsx_var.get(): extensions.append('.xlsx')

        if not extensions:
            result_label.configure(text="Please select at least one file type", text_color=colors["danger"])
            return

        result_label.configure(text="Select folder...", text_color=colors["text_muted"])

        results = batch_sign_folder(username, mode, password, file_types=extensions, 
                                   progress_callback=on_progress)

        if results:
            result_label.configure(
                text=f"Complete! Signed: {results['signed']}, Failed: {results['failed']}",
                text_color=colors["success"] if results['failed'] == 0 else colors["danger"]
            )

    ctk.CTkButton(dialog, text="Start Batch Sign", command=start_batch,
                 fg_color=colors["accent"], hover_color=colors["accent_hover"],
                 font=("Inter", 14, "bold"), width=200, height=40).pack(pady=20)

    return dialog