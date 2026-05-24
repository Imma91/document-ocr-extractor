import fitz                          # PyMuPDF — apre e converte PDF
import google.generativeai as genai  # Gemini API
import json
import re
from PIL import Image
import io


def pdf_to_images(pdf_path: str) -> list:
    """
    Apre il PDF e converte ogni pagina in un'immagine PIL.
    Zoom 2x per dare a Gemini una risoluzione migliore da leggere.
    """
    doc = fitz.open(pdf_path)
    images = []

    for page in doc:
        mat = fitz.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes))
        images.append(img)

    doc.close()
    return images


def extract_document_data(image: Image.Image, api_key: str) -> dict:
    """
    Manda l'immagine a Gemini Flash con un prompt che gestisce sia
    fatture (invoice) che DDT (delivery note / documento di trasporto).
    Rileva automaticamente il tipo e popola i campi pertinenti.
    Risponde SOLO con JSON valido.
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = """
Analyze this document image carefully.

First, identify the document type:
- "invoice"  → if it is a commercial invoice / fattura
- "ddt"      → if it is a delivery note / documento di trasporto / bolla di consegna
- "unknown"  → if it cannot be determined

Then extract the relevant fields based on the type.

Return ONLY a valid JSON object — no markdown, no backticks, no extra text.

For an INVOICE use this structure:
{
    "document_type": "invoice",
    "invoice_number": "string or null",
    "date": "string or null",
    "vendor_name": "string or null",
    "vendor_vat": "string or null",
    "client_name": "string or null",
    "client_vat": "string or null",
    "items": [
        {
            "description": "string",
            "quantity": null,
            "unit_price": null,
            "total": null
        }
    ],
    "subtotal": null,
    "vat_percentage": null,
    "vat_amount": null,
    "total": null,
    "currency": "string or null"
}

For a DDT (Documento di Trasporto / Delivery Note) use this structure:
{
    "document_type": "ddt",
    "ddt_number": "string or null",
    "date": "string or null",
    "sender_name": "string or null",
    "sender_address": "string or null",
    "sender_vat": "string or null",
    "recipient_name": "string or null",
    "recipient_address": "string or null",
    "recipient_vat": "string or null",
    "carrier": "string or null",
    "transport_reason": "string or null",
    "port": "string or null",
    "goods_appearance": "string or null",
    "goods": [
        {
            "description": "string",
            "unit": "string or null",
            "quantity": null,
            "weight_kg": null
        }
    ],
    "total_weight_kg": null,
    "notes": "string or null"
}

For an UNKNOWN document:
{
    "document_type": "unknown",
    "raw_text": "brief summary of what the document appears to be"
}

Rules:
- Use null for any field that cannot be found or is not applicable.
- Do not invent data — only extract what is visible in the document.
- Numbers should be returned as numbers (not strings), except for codes/IDs.
"""

    response = model.generate_content([prompt, image])

    text = response.text.strip()
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)

    return json.loads(text)


def extract_from_pdf(pdf_path: str, api_key: str) -> dict:
    """
    Funzione principale: apre il PDF, usa la prima pagina,
    rileva il tipo di documento ed estrae i dati.
    """
    images = pdf_to_images(pdf_path)

    if not images:
        raise ValueError("PDF vuoto o non leggibile")

    data = extract_document_data(images[0], api_key)
    return data
