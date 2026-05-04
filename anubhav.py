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

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

remove_barcode = st.checkbox("Remove Barcode (optional)", value=False)

# =========================
# SETTINGS
# =========================
LEFT_LIMIT = 0.55  # ✅ keeps right-side PAN block safe

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

        # 🔹 Remove only LEFT side content
        for keyword in REMOVE_KEYWORDS:
            areas = page.search_for(keyword)

            for rect in areas:
                expanded = fitz.Rect(
                    max(0, rect.x0 - 5),
                    max(0, rect.y0 - 2),
                    page.rect.width * LEFT_LIMIT,  # ✅ restrict width
                    min(page.rect.height, rect.y1 + 5)
                )
                page.add_redact_annot(expanded, fill=(1, 1, 1))

        # 🔹 Optional barcode removal (top-right only)
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
if uploaded_file:

    # Validation
    if uploaded_file.type != "application/pdf":
        st.error("❌ Only PDF allowed")
        st.stop()

    if uploaded_file.size > 5 * 1024 * 1024:
        st.error("❌ Max file size is 5MB")
        st.stop()

    st.success("✅ PDF Uploaded")

    if st.button("🚀 Clean PDF"):
        try:
            cleaned_pdf = clean_pdf(uploaded_file, remove_barcode)

            st.success("✅ Fields Removed Successfully")

            # Preview
            preview_doc = fitz.open(stream=cleaned_pdf.getvalue(), filetype="pdf")
            page = preview_doc[0]
            pix = page.get_pixmap()

            st.image(pix.tobytes(), caption="Preview", use_container_width=True)

            # Download
            st.download_button(
                "📥 Download Cleaned PDF",
                cleaned_pdf,
                file_name=uploaded_file.name,  # ✅ same name
                mime="application/pdf"
            )

        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
