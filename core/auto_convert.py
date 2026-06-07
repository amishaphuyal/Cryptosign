import os

# ✅ SAFE IMPORT (NO CRASH)
try:
    from docx2pdf import convert
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


def convert_to_pdf(input_file):

    base, ext = os.path.splitext(input_file)
    ext = ext.lower()

    # =====================================================
    # ✅ CASE 1: ALREADY PDF
    # =====================================================
    if ext == ".pdf":
        return input_file

    # =====================================================
    # ✅ CASE 2: OFFICE FILES
    # =====================================================
    elif ext in [".docx", ".xlsx", ".pptx"]:

        output_pdf = base + ".pdf"

        # ✅ if docx2pdf available
        if DOCX_AVAILABLE:
            try:
                print("📄 Auto converting to PDF...")
                convert(input_file, output_pdf)
                print(f"✅ Converted → {output_pdf}")
                return output_pdf
            except Exception as e:
                print(f"⚠️ Conversion failed: {e}")

        # =====================================================
        # ✅ FALLBACK (SAFE)
        # =====================================================
        print("\n⚠️ AUTO-CONVERT NOT AVAILABLE")
        print("👉 Please convert manually:")
        print("   Open file → Save As → PDF ✅")

        return None

    # =====================================================
    # ✅ CASE 3: OTHER FILE TYPES
    # =====================================================
    else:
        print("⚠️ Unsupported file type for conversion")
        return None