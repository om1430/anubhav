import streamlit as st
import fitz  # PyMuPDF
import io

st.set_page_config(page_title="Smart PDF Cleaner", layout="wide")

st.title("📄 Smart PDF Field Remover")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

remove_barcode = st.checkbox("Remove Barcode (optional)", value=False)

# Keywords to remove
REMOVE_KEYWORDS = [
    "ASPEN",
    "Doctor ID",
    "Office :",
    "Route :"
]

def clean_pdf(file, remove_barcode):
    file_bytes = file.read()
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    for page in doc:
        # 🔹 Remove text fields
        for keyword in REMOVE_KEYWORDS:
            areas = page.search_for(keyword)

            for rect in areas:
                # Expand box to cover full line
                expanded = fitz.Rect(
                    rect.x0 - 5,
                    rect.y0 - 2,
                    page.rect.width,
                    rect.y1 + 5
                )
                page.add_redact_annot(expanded, fill=(1, 1, 1))

        # 🔹 Remove barcode (top area)
        if remove_barcode:
            barcode_area = fitz.Rect(
                page.rect.width * 0.5,  # right side
                0,
                page.rect.width,
                page.rect.height * 0.15
            )
            page.add_redact_annot(barcode_area, fill=(1, 1, 1))

        page.apply_redactions()

    output = io.BytesIO()
    doc.save(output)
    doc.close()
    output.seek(0)

    return output


if uploaded_file:
    st.success("✅ PDF Uploaded")

    if st.button("🚀 Clean PDF"):
        cleaned_pdf = clean_pdf(uploaded_file, remove_barcode)

        st.success("✅ Fields Removed Successfully")

        # Preview
        preview_doc = fitz.open(stream=cleaned_pdf.getvalue(), filetype="pdf")
        pix = preview_doc[0].get_pixmap()

        st.image(pix.tobytes(), caption="Preview", use_container_width=True)

        # Download
        st.download_button(
            "📥 Download Cleaned PDF",
            cleaned_pdf,
            file_name="cleaned.pdf",
            mime="application/pdf"
        )