import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import io
import os
import tempfile
from extractor import extract_from_pdf

st.set_page_config(
    page_title="Document OCR Extractor",
    page_icon="🧾",
    layout="centered"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"], .stMarkdown, .stTextInput, label,
    .stButton > button, [data-testid="stFileUploader"],
    [data-testid="metric-container"], .stDataFrame, .stAlert {
        font-family: 'Inter', sans-serif !important;
    }

    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 2.5rem;
        max-width: 760px;
    }

    /* Input testo */
    .stTextInput > div > div > input {
        background-color: #0A1628 !important;
        border: 1px solid #1E3A5F !important;
        border-radius: 8px !important;
        color: #F1F5F9 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.9rem !important;
        padding: 0.55rem 0.9rem !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #3B82F6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
    }

    /* Label degli input */
    .stTextInput label, .stFileUploader label {
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        color: #94A3B8 !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #0A1628 !important;
        border: 1px dashed #1E3A5F !important;
        border-radius: 10px !important;
        padding: 0.4rem 0.8rem !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #3B82F6 !important;
    }

    /* Bottone principale */
    .stButton > button {
        background: linear-gradient(135deg, #2563EB, #1D4ED8) !important;
        color: #F8FAFC !important;
        border: none !important;
        border-radius: 9px !important;
        padding: 0.65rem 1.4rem !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.01em !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.35) !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #1D4ED8, #1E40AF) !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.45) !important;
        transform: translateY(-1px) !important;
    }

    /* Box metriche */
    [data-testid="metric-container"] {
        background: #0C1829 !important;
        border: 1px solid #1E3A5F !important;
        border-radius: 10px !important;
        padding: 0.9rem 1.1rem !important;
    }
    [data-testid="metric-container"] label {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.7rem !important;
        font-weight: 600 !important;
        color: #64748B !important;
        text-transform: uppercase !important;
        letter-spacing: 0.07em !important;
    }
    [data-testid="metric-container"] [data-testid="metric-value"] {
        font-family: 'Inter', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #E2E8F0 !important;
    }

    /* Tabella */
    [data-testid="stDataFrame"] {
        border-radius: 10px !important;
        overflow: hidden !important;
        border: 1px solid #1E3A5F !important;
    }

    /* Titoli sezioni (h3) */
    h3 {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: #94A3B8 !important;
        letter-spacing: 0.07em !important;
        text-transform: uppercase !important;
    }

    /* Bottoni download */
    [data-testid="stDownloadButton"] > button {
        background: #0C1829 !important;
        color: #3B82F6 !important;
        border: 1px solid #2563EB !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        background: #1E3A5F !important;
        color: #93C5FD !important;
    }

    /* Alert */
    [data-testid="stAlert"] {
        border-radius: 9px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.88rem !important;
    }

    hr {
        border-color: #1E3A5F !important;
        margin: 1.2rem 0 !important;
    }

    /* Tipo documento badge */
    .doc-type-badge {
        display: inline-block;
        border-radius: 6px;
        padding: 2px 10px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
    }
    .badge-invoice {
        background: rgba(34, 197, 94, 0.12);
        border: 1px solid rgba(34, 197, 94, 0.35);
        color: #86EFAC;
    }
    .badge-ddt {
        background: rgba(251, 191, 36, 0.12);
        border: 1px solid rgba(251, 191, 36, 0.35);
        color: #FCD34D;
    }
    .badge-unknown {
        background: rgba(148, 163, 184, 0.12);
        border: 1px solid rgba(148, 163, 184, 0.35);
        color: #94A3B8;
    }

    header[data-testid="stHeader"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# ─── Header ───────────────────────────────────────────────────────────────────
components.html("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <div style="font-family: 'Inter', sans-serif; padding: 4px 0 8px 0; background: transparent;">
        <div style="
            display: inline-block;
            background: rgba(59,130,246,0.12);
            border: 1px solid rgba(59,130,246,0.38);
            border-radius: 20px;
            padding: 3px 12px;
            font-size: 0.7rem;
            font-weight: 600;
            color: #93C5FD;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 10px;
        ">Gemini 2.5 Flash Vision</div>
        <div style="
            font-size: 2rem;
            font-weight: 700;
            color: #F1F5F9;
            letter-spacing: -0.6px;
            line-height: 1.2;
            margin-bottom: 8px;
        ">Document OCR Extractor</div>
        <div style="
            font-size: 0.93rem;
            color: #64748B;
            font-weight: 400;
            line-height: 1.5;
        ">Upload a PDF — invoices and delivery notes (DDT) are detected automatically and exported to JSON and Excel.</div>
    </div>
""", height=135, scrolling=False)

st.divider()

# ─── Input ────────────────────────────────────────────────────────────────────
api_key = st.text_input(
    "GEMINI API KEY",
    type="password",
    placeholder="Paste your Gemini API key here"
)

uploaded_file = st.file_uploader(
    "DOCUMENT PDF",
    type=["pdf"]
)

st.divider()

# ─── Helpers UI ───────────────────────────────────────────────────────────────

def _v(data: dict, key: str) -> str:
    """Restituisce il valore come stringa o '—' se assente/null."""
    val = data.get(key)
    return str(val) if val not in (None, "", []) else "—"


def render_download_buttons(data: dict, doc_type: str):
    st.subheader("Export")
    col_j, col_x = st.columns(2)

    with col_j:
        json_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        st.download_button(
            label="Download JSON",
            data=json_bytes,
            file_name=f"{doc_type}_data.json",
            mime="application/json",
            use_container_width=True
        )

    with col_x:
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            items_key = "items" if doc_type == "invoice" else "goods"
            items = data.get(items_key, [])
            header_data = {k: v for k, v in data.items() if k != items_key}
            pd.DataFrame([header_data]).to_excel(writer, sheet_name="Summary", index=False)
            if items:
                pd.DataFrame(items).to_excel(writer, sheet_name="Lines", index=False)
        st.download_button(
            label="Download Excel",
            data=excel_buffer.getvalue(),
            file_name=f"{doc_type}_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )


def render_invoice(data: dict):
    st.markdown('<span class="doc-type-badge badge-invoice">Invoice / Fattura</span>',
                unsafe_allow_html=True)

    # ── Dati principali ───────────────────────────────────────────────────────
    st.subheader("Invoice Details")
    c1, c2, c3 = st.columns(3)
    c1.metric("Invoice Number", _v(data, "invoice_number"))
    c2.metric("Date", _v(data, "date"))
    c3.metric("Currency", _v(data, "currency"))

    st.markdown("<br>", unsafe_allow_html=True)
    c4, c5, c6 = st.columns(3)
    c4.metric("Vendor", _v(data, "vendor_name"))
    c5.metric("Vendor VAT", _v(data, "vendor_vat"))
    c6.metric("Client", _v(data, "client_name"))

    st.divider()

    # ── Righe ─────────────────────────────────────────────────────────────────
    st.subheader("Line Items")
    items = data.get("items", [])
    if items:
        st.dataframe(pd.DataFrame(items), use_container_width=True)
    else:
        st.info("No line items found.")

    st.divider()

    # ── Totali ────────────────────────────────────────────────────────────────
    st.subheader("Totals")
    c7, c8, c9 = st.columns(3)
    c7.metric("Subtotal", _v(data, "subtotal"))
    vat_pct = data.get("vat_percentage") or "?"
    c8.metric(f"VAT ({vat_pct}%)", _v(data, "vat_amount"))
    c9.metric("Total", _v(data, "total"))

    st.divider()
    render_download_buttons(data, "invoice")


def render_ddt(data: dict):
    st.markdown('<span class="doc-type-badge badge-ddt">DDT / Delivery Note</span>',
                unsafe_allow_html=True)

    # ── Dati documento ────────────────────────────────────────────────────────
    st.subheader("Document Details")
    c1, c2, c3 = st.columns(3)
    c1.metric("DDT Number", _v(data, "ddt_number"))
    c2.metric("Date", _v(data, "date"))
    c3.metric("Port", _v(data, "port"))

    st.markdown("<br>", unsafe_allow_html=True)
    c4, c5 = st.columns(2)
    c4.metric("Transport Reason", _v(data, "transport_reason"))
    c5.metric("Goods Appearance", _v(data, "goods_appearance"))

    st.divider()

    # ── Mittente / Destinatario ───────────────────────────────────────────────
    st.subheader("Parties")
    col_s, col_r = st.columns(2)

    with col_s:
        st.markdown("**Sender / Mittente**")
        st.metric("Name", _v(data, "sender_name"))
        st.metric("Address", _v(data, "sender_address"))
        st.metric("VAT", _v(data, "sender_vat"))

    with col_r:
        st.markdown("**Recipient / Destinatario**")
        st.metric("Name", _v(data, "recipient_name"))
        st.metric("Address", _v(data, "recipient_address"))
        st.metric("VAT", _v(data, "recipient_vat"))

    st.divider()

    # ── Vettore ───────────────────────────────────────────────────────────────
    st.subheader("Carrier")
    st.metric("Carrier / Vettore", _v(data, "carrier"))

    st.divider()

    # ── Merci ─────────────────────────────────────────────────────────────────
    st.subheader("Goods / Merci")
    goods = data.get("goods", [])
    if goods:
        st.dataframe(pd.DataFrame(goods), use_container_width=True)
    else:
        st.info("No goods lines found.")

    st.markdown("<br>", unsafe_allow_html=True)
    c_w1, c_w2 = st.columns([1, 3])
    c_w1.metric("Total Weight (kg)", _v(data, "total_weight_kg"))

    notes = data.get("notes")
    if notes:
        st.divider()
        st.subheader("Notes")
        st.caption(notes)

    st.divider()
    render_download_buttons(data, "ddt")


def render_unknown(data: dict):
    st.markdown('<span class="doc-type-badge badge-unknown">Unknown Document</span>',
                unsafe_allow_html=True)
    st.warning("The document type could not be determined. "
               "Please check that the PDF is a valid invoice or DDT.")
    raw = data.get("raw_text")
    if raw:
        st.caption(f"AI note: {raw}")

    st.divider()
    render_download_buttons(data, "unknown")


# ─── Logica principale ────────────────────────────────────────────────────────
if uploaded_file and api_key:

    if st.button("Extract Document Data", use_container_width=True):

        # Scrive il PDF in un file temporaneo della OS (sempre scrivibile)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        with st.spinner("Analyzing document with Gemini AI..."):
            try:
                data = extract_from_pdf(tmp_path, api_key)

                st.success("Extraction complete.")
                st.divider()

                doc_type = data.get("document_type", "unknown")

                if doc_type == "invoice":
                    render_invoice(data)
                elif doc_type == "ddt":
                    render_ddt(data)
                else:
                    render_unknown(data)

            except json.JSONDecodeError:
                st.error("Gemini returned an invalid response. Please try again.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
            finally:
                # Rimuove il file temporaneo in ogni caso
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

else:
    if not api_key:
        st.caption("Insert your Gemini API key to get started.")
    elif not uploaded_file:
        st.caption("Upload a PDF document to continue.")
