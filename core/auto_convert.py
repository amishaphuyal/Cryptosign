import os

try:
    from docx2pdf import convert  # type: ignore[import]
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


def convert_to_pdf(input_file):

    base, ext = os.path.splitext(input_file)
    ext = ext.lower()


    if ext == ".pdf":
        return input_file

   
    elif ext in [".docx", ".xlsx", ".pptx"]:

        output_pdf = base + ".pdf"

        if DOCX_AVAILABLE:
            try:
                print("📄 Auto converting to PDF...")
                convert(input_file, output_pdf)
                print(f"✅ Converted → {output_pdf}")
                return output_pdf
            except Exception as e:
                print(f"⚠️ Conversion failed: {e}")

    
        print("\n⚠️ AUTO-CONVERT NOT AVAILABLE")
        print("👉 Please convert manually:")
        print("   Open file → Save As → PDF ✅")

        return None


    else:
        print("⚠️ Unsupported file type for conversion")
        return None