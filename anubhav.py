import streamlit as st
import fitz  # PyMuPDF
import io

# =========================
# 🔐 PASSWORD
# =========================
APP_PASSWORD = "mlc123"

def check_password():
    st.sidebar.title("🔐 Login")
    password = st.sidebar.text_input("Enter Password", type="password")

    if password != APP_PASSWORD:
        st.warning("Enter correct password")
        st.stop()

check_password()

# =========================
# UI
# =========================
st.set_page_config(page_title="Smart PDF Cleaner", layout="wide")

st.title("📄 Smart PDF Field Remover")

# ✅ MULTIPLE FILE UPLOAD
uploaded_files = st.file_uploader(
    "Upload PDF",
    type=["pdf"],
    accept_multiple_files=True
)

remove_barcode = st.checkbox("Remove Barcode (optional)", value=False)

# =========================
# SETTINGS
# =========================
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
    file_bytes = file.read()
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    for page in doc:

        # Remove LEFT side content only
        for keyword in REMOVE_KEYWORDS:
            areas = page.search_for(keyword)

            for rect in areas:
                expanded = fitz.Rect(
                    max(0, rect.x0 - 5),
                    max(0, rect.y0 - 2),
                    page.rect.width * LEFT_LIMIT,
                    min(page.rect.height, rect.y1 + 5)
                )
                page.add_redact_annot(expanded, fill=(1, 1, 1))

        # Optional barcode removal
        if remove_barcode:
            barcode_area = fitz.Rect(
                page.rect.width * 0.6,
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

# =========================
# MAIN FLOW
# =========================
if uploaded_files:

    st.success(f"✅ {len(uploaded_files)} PDFs Uploaded")

    if st.button("🚀 Clean PDF"):

        for uploaded_file in uploaded_files:
            try:
                # Validation
                if uploaded_file.type != "application/pdf":
                    st.error(f"❌ {uploaded_file.name} is not a PDF")
                    continue

                if uploaded_file.size > 5 * 1024 * 1024:
                    st.error(f"❌ {uploaded_file.name} too large (Max 5MB)")
                    continue

                cleaned_pdf = clean_pdf(uploaded_file, remove_barcode)

                st.success(f"✔ Processed: {uploaded_file.name}")

                # Preview first page
                preview_doc = fitz.open(stream=cleaned_pdf.getvalue(), filetype="pdf")
                page = preview_doc[0]
                pix = page.get_pixmap()

                st.image(
                    pix.tobytes(),
                    caption=f"Preview: {uploaded_file.name}",
                    use_container_width=True
                )

                # Download button (same name)
                st.download_button(
                    label=f"📥 Download {uploaded_file.name}",
                    data=cleaned_pdf,
                    file_name=uploaded_file.name,
                    mime="application/pdf"
                )

            except Exception as e:
                st.error(f"❌ Error in {uploaded_file.name}: {str(e)}")
