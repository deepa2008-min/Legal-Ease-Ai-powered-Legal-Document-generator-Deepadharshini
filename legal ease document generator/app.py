import base64
import os
from datetime import date

import requests

import streamlit as st

from dotenv import load_dotenv


load_dotenv()


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide"
)


st.markdown(
    """
    <style>

    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .subtitle {
        text-align: center;
        color: #777;
        margin-bottom: 25px;
    }

    .preview {
        background: #171717;
        color: #f2f2f2;
        padding: 24px;
        border-radius: 12px;
        white-space: pre-wrap;
        max-height: 650px;
        overflow-y: auto;
        font-family: Georgia, serif;
        line-height: 1.55;
    }

    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    '<div class="main-title">'
    '⚖️ LegalEase'
    '</div>',
    unsafe_allow_html=True
)


st.markdown(
    '<div class="subtitle">'
    'AI-Powered Legal Document Generator — '
    'College Project'
    '</div>',
    unsafe_allow_html=True
)


if "content" not in st.session_state:
    st.session_state.content = ""


if "document_type" not in st.session_state:
    st.session_state.document_type = (
        "Lease Agreement"
    )


if "logo_base64" not in st.session_state:
    st.session_state.logo_base64 = None


if "model" not in st.session_state:
    st.session_state.model = ""


with st.sidebar:

    st.header(
        "Document Details"
    )


    document_type = st.selectbox(
        "Document type",

        [
            "Lease Agreement",
            "Employment Contract",
            "Non-Disclosure Agreement (NDA)",
            "Freelance Work Contract",
            "Service Agreement",
            "Offer Letter",
            "General Agreement"
        ],

        index=0
    )


    parties = st.text_area(
        "Parties involved",

        placeholder=(
            "Jane Doe (Tenant), "
            "XYZ Realty (Landlord)"
        ),

        height=100
    )


    terms_raw = st.text_area(
        "Terms & Conditions",

        placeholder=(
            "Monthly rent is INR 20000; "
            "Security deposit is INR 40000; "
            "Either party may terminate "
            "with 30 days notice"
        ),

        height=150,

        help=(
            "Separate each term using "
            "a semicolon (;)."
        )
    )


    effective_date = st.date_input(
        "Effective date",
        value=date.today()
    )


    jurisdiction = st.text_input(
        "Jurisdiction",
        value="Tamil Nadu, India"
    )


    additional_instructions = st.text_area(
        "Additional instructions",

        placeholder=(
            "Use simple language and "
            "clear numbered clauses."
        ),

        height=100
    )


    logo = st.file_uploader(
        "Optional logo",

        type=[
            "png",
            "jpg",
            "jpeg"
        ]
    )


    if logo:

        logo_bytes = logo.read()

        st.session_state.logo_base64 = (
            "data:"
            + logo.type
            + ";base64,"
            + base64.b64encode(
                logo_bytes
            ).decode()
        )


    generate = st.button(
        "✨ Generate Document",
        type="primary",
        use_container_width=True
    )


if generate:

    if not parties.strip():

        st.error(
            "Please enter the parties involved."
        )

    else:

        terms = [
            term.strip()
            for term in terms_raw.split(";")
            if term.strip()
        ]


        payload = {

            "document_type":
                document_type,

            "parties":
                parties,

            "terms":
                terms,

            "effective_date":
                effective_date.isoformat(),

            "jurisdiction":
                jurisdiction,

            "additional_instructions":
                additional_instructions,

            "logo_base64":
                st.session_state.logo_base64
        }


        with st.spinner(
            "Generating your draft..."
        ):

            try:

                response = requests.post(

                    f"{BACKEND_URL}/generate",

                    json=payload,

                    timeout=120
                )


                response.raise_for_status()


                data = response.json()


                st.session_state.content = (
                    data["content"]
                )


                st.session_state.document_type = (
                    data["document_type"]
                )


                st.session_state.model = (
                    data["model"]
                )


                if data.get("mock_mode"):

                    st.info(
                        "Demo/fallback mode is active. "
                        "Configure GEMINI_API_KEY "
                        "for live Gemini generation."
                    )

                else:

                    st.success(
                        f"Generated with "
                        f"{data['model']}."
                    )


            except requests.RequestException as exc:

                st.error(
                    "Could not connect to FastAPI. "
                    "Make sure the backend is running."
                )

                st.caption(
                    str(exc)
                )


st.subheader(
    "Document Preview"
)


if st.session_state.content:

    safe_content = (
        st.session_state.content
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


    st.markdown(
        f"""
        <div class="preview">
        {safe_content}
        </div>
        """,
        unsafe_allow_html=True
    )


    st.subheader(
        "Edit Document"
    )


    edited = st.text_area(

        "Modify the generated text "
        "before export",

        value=st.session_state.content,

        height=500,

        label_visibility="collapsed"
    )


    st.session_state.content = edited


    col1, col2, col3 = st.columns(3)


    export_payload = {

        "document_type":
            st.session_state.document_type,

        "content":
            st.session_state.content,

        "logo_base64":
            st.session_state.logo_base64
    }


    with col1:

        if st.button(
            "Prepare TXT",
            use_container_width=True
        ):

            try:

                response = requests.post(

                    f"{BACKEND_URL}/export/txt",

                    json=export_payload,

                    timeout=30
                )

                response.raise_for_status()


                st.download_button(

                    "⬇️ Download TXT",

                    data=response.content,

                    file_name=(
                        "legal_document.txt"
                    ),

                    mime="text/plain",

                    use_container_width=True
                )

            except requests.RequestException as exc:

                st.error(
                    f"TXT export failed: {exc}"
                )


    with col2:

        if st.button(
            "Prepare DOCX",
            use_container_width=True
        ):

            try:

                response = requests.post(

                    f"{BACKEND_URL}/export/docx",

                    json=export_payload,

                    timeout=30
                )

                response.raise_for_status()


                st.download_button(

                    "⬇️ Download DOCX",

                    data=response.content,

                    file_name=(
                        "legal_document.docx"
                    ),

                    mime=(
                        "application/"
                        "vnd.openxmlformats-officedocument."
                        "wordprocessingml.document"
                    ),

                    use_container_width=True
                )

            except requests.RequestException as exc:

                st.error(
                    f"DOCX export failed: {exc}"
                )


    with col3:

        if st.button(
            "Prepare PDF",
            use_container_width=True
        ):

            try:

                response = requests.post(

                    f"{BACKEND_URL}/export/pdf",

                    json=export_payload,

                    timeout=30
                )

                response.raise_for_status()


                st.download_button(

                    "⬇️ Download PDF",

                    data=response.content,

                    file_name=(
                        "legal_document.pdf"
                    ),

                    mime="application/pdf",

                    use_container_width=True
                )

            except requests.RequestException as exc:

                st.error(
                    f"PDF export failed: {exc}"
                )

else:

    st.info(
        "Fill in the fields on the left "
        "and click Generate Document."
    )


st.divider()


st.caption(
    "LegalEase is an educational prototype. "
    "AI-generated documents require appropriate "
    "professional review before real-world use."
)