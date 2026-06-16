from pyhanko.sign import signers
from pyhanko.sign.signers import PdfSigner, PdfSignatureMetadata
from pyhanko.sign.fields import SigFieldSpec
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign.general import SigningError
from pypdf import PdfReader, PdfWriter
import os


def sign_pdf_pkcs(input_pdf, username, password=None):
    """
    Sign PDF with PKCS#7 embedded signature - Adobe compatible!
    Returns output path
    """
    output_pdf = input_pdf.replace(".pdf", "_signed.pdf")

    signer = signers.SimpleSigner.load(
        key_file=f"storage/keystores/{username}_private.pem",
        cert_file=f"storage/certs/{username}_cert.pem",
        key_passphrase=password.encode('utf-8') if password else None
    )

    meta = PdfSignatureMetadata(
        field_name="Signature1"
    )

    pdf_signer = PdfSigner(
        meta,
        signer=signer,
        new_field_spec=SigFieldSpec(
            sig_field_name="Signature1",
            box=(50, 50, 250, 150),  # Bigger box for signature
            on_page=0  # First page
        )
    )

    try:
        with open(input_pdf, "rb") as inf:
            writer = IncrementalPdfFileWriter(inf)

            with open(output_pdf, "wb") as outf:
                pdf_signer.sign_pdf(writer, output=outf)

        print("Direct PKCS signing successful")
        print(f"FINAL FILE: {output_pdf}")
        return output_pdf

    except SigningError:
        print("⚠️ Hybrid PDF detected → applying safe fix")

    temp_pdf = input_pdf.replace(".pdf", "_clean.pdf")

    reader = PdfReader(input_pdf)
    writer2 = PdfWriter()

    for page in reader.pages:
        writer2.add_page(page)

    writer2.add_metadata(reader.metadata or {})

    with open(temp_pdf, "wb") as f:
        writer2.write(f)

    with open(temp_pdf, "rb") as inf:
        writer = IncrementalPdfFileWriter(inf)

        with open(output_pdf, "wb") as outf:
            pdf_signer.sign_pdf(writer, output=outf)

    print("Clean PDF signed successfully")
    print(f"FINAL FILE: {output_pdf}")


    if os.path.exists(temp_pdf):
        os.remove(temp_pdf)
    
    return output_pdf