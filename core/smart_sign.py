import os
from core.sign_engine import sign_document
from core.pkcs_sign import sign_pdf_pkcs
from core.auto_convert import convert_to_pdf


def smart_sign(file_path, username, mode, password=None, audit_logger=None):
    """
    ✅ FIXED: Smart sign with auto mode selection.
    Returns dict with success status and file paths.
    Also tracks files in database for My Documents.
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    file_name = os.path.basename(file_path)

    print(f"\n🔐 Signing mode: {mode}")

    result = {
        'success': False,
        'mode': mode,
        'original_file': file_name,
        'output_file': None,
        'message': ''
    }

    try:
        # MODE 1 → EXTERNAL (.sig)
        if mode == "external":
            sig_path = sign_document(
                file_path,
                f"storage/keystores/{username}_private.pem",
                username,
                password,
                audit_logger=audit_logger
            )

            result['success'] = True
            result['output_file'] = sig_path
            result['message'] = f"External signature created: {os.path.basename(sig_path)}"

            print("✅ External signature created (.sig file)")
            return result

        # MODE 2 → EMBEDDED
        elif mode == "embedded":

            # PDF → Direct embed
            if file_ext == ".pdf":
                from core.embed_pdf import embed_pdf_signature
                output = embed_pdf_signature(file_path, username, password, audit_logger=audit_logger)

                result['success'] = True
                result['output_file'] = output
                result['message'] = f"PDF signed with embedded signature: {os.path.basename(output)}"
                return result

            # Office files → Convert then sign
            elif file_ext in [".docx", ".xlsx", ".pptx"]:
                print("📄 Office file detected")

                pdf_file = convert_to_pdf(file_path)

                if pdf_file:
                    print(f"✅ Converted → {pdf_file}")
                    from core.embed_pdf import embed_pdf_signature
                    output = embed_pdf_signature(pdf_file, username, password, audit_logger=audit_logger)

                    result['success'] = True
                    result['output_file'] = output
                    result['message'] = f"Office file converted and signed: {os.path.basename(output)}"
                    return output

                else:
                    print("⚠️ Conversion failed → using external signature")
                    sig_path = sign_document(
                        file_path,
                        f"storage/keystores/{username}_private.pem",
                        username,
                        password,
                        audit_logger=audit_logger
                    )

                    result['success'] = True
                    result['mode'] = 'external'
                    result['output_file'] = sig_path
                    result['message'] = f"Fallback to external signature: {os.path.basename(sig_path)}"
                    return result

            # Other files → External
            else:
                print("⚠️ Unsupported for embedded → external used")

                sig_path = sign_document(
                    file_path,
                    f"storage/keystores/{username}_private.pem",
                    username,
                    password,
                    audit_logger=audit_logger
                )

                result['success'] = True
                result['mode'] = 'external'
                result['output_file'] = sig_path
                result['message'] = f"External signature for unsupported file: {os.path.basename(sig_path)}"
                return result

        else:
            raise ValueError(f"Invalid mode: {mode}. Use 'external' or 'embedded'")

    except Exception as e:
        result['message'] = f"Signing failed: {str(e)}"
        print(f"❌ {result['message']}")
        return result