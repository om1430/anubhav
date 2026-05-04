import streamlit as st
import fitz  # PyMuPDF
import io
import zipfile

# =========================
# 🔐 PASSWORD
# =========================
APP_PASSWORD = "mlc123"

def check_password():
    st.sidebar.title("🔐 Login")
    password = st.sidebar.text_input("Enter Password", type="password")

    if password != APP_PASSWORD:
        st.stop()

check_password()

# =========================
# UI
# =========================
st.set_page_config(page_title="PDF Cleaner", layout="wide")

st.title("📄 Multi PDF Cleaner")

uploaded_files = st.file_uploader(
    "Upload PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

remove_barcode = st.checkbox("Remove Barcode", value=False)

LEFT_LIMIT = 0.55

REMOVE_KEYWORDS = [
    "ASPEN",
    "Doctor ID",
    "Office :",
    "Route :"
]

# =========================
# PROCESS FUNCTION
# =========================
def clean_pdf(file, remove_barcode):
    doc = fitz.open(stream=file.read(), filetype="pdf")

    for page in doc:
        for keyword in REMOVE_KEYWORDS:
            areas = page.search_for(keyword)

            for rect in areas:
                expanded = fitz.Rect(
                    rect.x0 - 5,
                    rect.y0 - 2,
                    page.rect.width * LEFT_LIMIT,
                    rect.y1 + 5
                )
                page.add_redact_annot(expanded, fill=(1, 1, 1))

        if remove_barcode:
            barcode_area = fitz.Rect(
                page.rect.width * 0.6,
                0,
                page.rect.width,
                page.rect.height * 0.15
            )
            page.add_redact_annot(barcode_area, fill=(1, 1, 1))

        page.apply_redactions()

    buffer = io.BytesIO()
    doc.save(buffer)
    doc.close()
    buffer.seek(0)

    return buffer


# =========================
# MAIN
# =========================
if uploaded_files:

    st.success(f"✅ {len(uploaded_files)} PDFs uploaded")

    if st.button("🚀 Process All PDFs"):

        zip_buffer = io.BytesIO()
        zip_file = zipfile.ZipFile(zip_buffer, "w")

        for file in uploaded_files:

            # Validation
            if file.type != "application/pdf":
                st.warning(f"Skipped {file.name} (not PDF)")
                continue

            cleaned_pdf = clean_pdf(file, remove_barcode)

            # Add to zip (same name)
            zip_file.writestr(file.name, cleaned_pdf.getvalue())

        zip_file.close()
        zip_buffer.seek(0)

        st.success("✅ All PDFs processed!")

        st.download_button(
            label="📥 Download All (ZIP)",
            data=zip_buffer,
            file_name="cleaned_pdfs.zip",
            mime="application/zip"
        )
