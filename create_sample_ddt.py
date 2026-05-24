"""
Generatore di DDT (Documenti di Trasporto) fittizi — solo dati inventati.
Produce 3 PDF nella cartella sample_docs/.

Dipendenze: reportlab (già nel progetto)
Esegui: python create_sample_ddt.py
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas

# ─── Dati fittizi ─────────────────────────────────────────────────────────────

DDT_DATA = [
    {
        "ddt_number": "DDT/2024/00547",
        "date": "12/03/2024",
        "mittente": {
            "ragione_sociale": "Alfa Distribuzione S.r.l.",
            "indirizzo": "Via dell'Industria, 28",
            "cap_citta": "20090 Segrate (MI)",
            "piva": "IT03412789012",
        },
        "destinatario": {
            "ragione_sociale": "Beta Forniture S.p.A.",
            "indirizzo": "Corso Roma, 115",
            "cap_citta": "10128 Torino (TO)",
            "piva": "IT07823410023",
        },
        "vettore": "Trasporti Gamma Srl",
        "causale": "Vendita",
        "porto": "Franco",
        "aspetto_beni": "Scatole",
        "righe": [
            ("Interruttori automatici 16A 3P", "PZ", 50, 0.45),
            ("Cavi elettrici FG16OR16 3x2.5mm²", "MT", 200, 1.20),
            ("Quadro elettrico da incasso 24 moduli", "PZ", 10, 3.80),
            ("Pressacavi PG13.5 in ottone", "PZ", 100, 0.12),
            ("Morsettiere serie UK 2.5mm² (conf. 50 pz)", "CF", 8, 2.10),
        ],
    },
    {
        "ddt_number": "DDT/2024/01123",
        "date": "05/06/2024",
        "mittente": {
            "ragione_sociale": "Delta Materiali S.r.l.",
            "indirizzo": "Via Artigiani, 7",
            "cap_citta": "40139 Bologna (BO)",
            "piva": "IT02198340375",
        },
        "destinatario": {
            "ragione_sociale": "Epsilon Costruzioni S.r.l.",
            "indirizzo": "Via Napoli, 44",
            "cap_citta": "80143 Napoli (NA)",
            "piva": "IT05567890634",
        },
        "vettore": "Corriere Zeta Express",
        "causale": "Reso su ordine n. ORD-2024-0892",
        "porto": "Assegnato",
        "aspetto_beni": "Pallet",
        "righe": [
            ("Tegole marsigliesi rosse (conf. 10 pz)", "CF", 120, 18.00),
            ("Guaina bituminosa ardesiata 4mm 10m²", "RT", 30, 11.50),
            ("Listelli abete 50x30mm 3m", "PZ", 250, 0.90),
            ("Malta cementizia grigia 25kg", "SC", 40, 4.80),
        ],
    },
    {
        "ddt_number": "DDT/2024/00789",
        "date": "22/09/2024",
        "mittente": {
            "ragione_sociale": "Eta Solutions S.p.A.",
            "indirizzo": "Viale del Commercio, 3",
            "cap_citta": "50019 Sesto Fiorentino (FI)",
            "piva": "IT04321098765",
        },
        "destinatario": {
            "ragione_sociale": "Theta Office Forniture",
            "indirizzo": "Piazza Garibaldi, 12",
            "cap_citta": "16121 Genova (GE)",
            "piva": "IT01098765432",
        },
        "vettore": "Iota Logistics S.r.l.",
        "causale": "Conto visione",
        "porto": "Franco",
        "aspetto_beni": "Colli",
        "righe": [
            ("Monitor 27'' IPS 4K 60Hz", "PZ", 5, 8.60),
            ("Tastiera wireless compatta nera", "PZ", 10, 0.85),
            ("Mouse ergonomico verticale wireless", "PZ", 10, 0.72),
            ("Webcam HD 1080p con microfono", "PZ", 8, 1.30),
            ("Hub USB-C 7 in 1 (HDMI/USB3/SD)", "PZ", 6, 0.95),
            ("Supporto monitor doppio da scrivania", "PZ", 4, 2.80),
        ],
    },
]

# ─── Stile ────────────────────────────────────────────────────────────────────

NAVY       = colors.HexColor("#0D1B2A")
BLUE       = colors.HexColor("#1A56DB")
BLUE_LIGHT = colors.HexColor("#EBF3FF")
GRAY_LINE  = colors.HexColor("#D1D5DB")
GRAY_TEXT  = colors.HexColor("#6B7280")
WHITE      = colors.white
BLACK      = colors.black


def build_styles():
    base = getSampleStyleSheet()
    return {
        "company": ParagraphStyle(
            "company", fontName="Helvetica-Bold", fontSize=11,
            textColor=NAVY, leading=14
        ),
        "address": ParagraphStyle(
            "address", fontName="Helvetica", fontSize=8.5,
            textColor=colors.HexColor("#374151"), leading=12
        ),
        "piva": ParagraphStyle(
            "piva", fontName="Helvetica", fontSize=8,
            textColor=GRAY_TEXT, leading=11
        ),
        "label": ParagraphStyle(
            "label", fontName="Helvetica-Bold", fontSize=7,
            textColor=GRAY_TEXT, leading=9, spaceAfter=1
        ),
        "value": ParagraphStyle(
            "value", fontName="Helvetica", fontSize=9,
            textColor=NAVY, leading=11
        ),
        "section_title": ParagraphStyle(
            "section_title", fontName="Helvetica-Bold", fontSize=7.5,
            textColor=WHITE, leading=10
        ),
        "footer": ParagraphStyle(
            "footer", fontName="Helvetica", fontSize=7.5,
            textColor=GRAY_TEXT, leading=10, alignment=TA_CENTER
        ),
        "note": ParagraphStyle(
            "note", fontName="Helvetica", fontSize=8,
            textColor=GRAY_TEXT, leading=11
        ),
    }


def draw_page_border(canvas_obj, doc):
    """Aggiunge la barra di intestazione e il footer fissi."""
    canvas_obj.saveState()
    w, h = A4

    # Barra top navy
    canvas_obj.setFillColor(NAVY)
    canvas_obj.rect(0, h - 22*mm, w, 22*mm, fill=1, stroke=0)

    # Titolo nella barra top
    canvas_obj.setFont("Helvetica-Bold", 13)
    canvas_obj.setFillColor(WHITE)
    canvas_obj.drawString(15*mm, h - 14*mm, "DOCUMENTO DI TRASPORTO")

    canvas_obj.setFont("Helvetica", 8.5)
    canvas_obj.setFillColor(colors.HexColor("#93C5FD"))
    canvas_obj.drawRightString(w - 15*mm, h - 14*mm,
                               "D.P.R. 472/1996 — art. 1 c. 3")

    # Footer
    canvas_obj.setFillColor(GRAY_TEXT)
    canvas_obj.setFont("Helvetica", 7)
    canvas_obj.drawCentredString(
        w / 2, 8*mm,
        "Documento generato a fini dimostrativi — dati completamente fittizi"
    )
    canvas_obj.line(15*mm, 12*mm, w - 15*mm, 12*mm)

    canvas_obj.restoreState()


def build_ddt_pdf(data: dict, filepath: str):
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=27*mm, bottomMargin=18*mm,
    )
    s = build_styles()
    story = []

    # ── DDT numero e data ─────────────────────────────────────────────────────
    meta_table = Table(
        [[
            Paragraph("N° DDT", s["label"]),
            Paragraph("DATA", s["label"]),
            Paragraph("CAUSALE TRASPORTO", s["label"]),
            Paragraph("PORTO", s["label"]),
        ],
        [
            Paragraph(data["ddt_number"], s["value"]),
            Paragraph(data["date"], s["value"]),
            Paragraph(data["causale"], s["value"]),
            Paragraph(data["porto"], s["value"]),
        ]],
        colWidths=[45*mm, 28*mm, 80*mm, 27*mm],
    )
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE_LIGHT),
        ("ROWBACKGROUNDS", (0, 1), (-1, 1), [WHITE]),
        ("BOX", (0, 0), (-1, -1), 0.5, GRAY_LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, GRAY_LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 5*mm))

    # ── Mittente / Destinatario ───────────────────────────────────────────────
    m = data["mittente"]
    d = data["destinatario"]

    def company_block(label, info):
        return [
            [Paragraph(label, s["section_title"])],
            [Paragraph(info["ragione_sociale"], s["company"])],
            [Paragraph(info["indirizzo"], s["address"])],
            [Paragraph(info["cap_citta"], s["address"])],
            [Paragraph(f"P.IVA: {info['piva']}", s["piva"])],
        ]

    mitt_table = Table(company_block("  MITTENTE", m), colWidths=[88*mm])
    dest_table = Table(company_block("  DESTINATARIO", d), colWidths=[88*mm])

    for t in (mitt_table, dest_table):
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BLUE),
            ("BACKGROUND", (0, 1), (-1, -1), WHITE),
            ("BOX", (0, 0), (-1, -1), 0.5, GRAY_LINE),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ]))

    anag_wrapper = Table([[mitt_table, Spacer(4*mm, 1), dest_table]],
                         colWidths=[88*mm, 4*mm, 88*mm])
    anag_wrapper.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(anag_wrapper)
    story.append(Spacer(1, 4*mm))

    # ── Info trasporto ────────────────────────────────────────────────────────
    transp = Table(
        [[
            Paragraph("VETTORE", s["label"]),
            Paragraph("ASPETTO BENI", s["label"]),
        ],
        [
            Paragraph(data["vettore"], s["value"]),
            Paragraph(data["aspetto_beni"], s["value"]),
        ]],
        colWidths=[100*mm, 80*mm],
    )
    transp.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE_LIGHT),
        ("BOX", (0, 0), (-1, -1), 0.5, GRAY_LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, GRAY_LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(transp)
    story.append(Spacer(1, 5*mm))

    # ── Tabella righe ─────────────────────────────────────────────────────────
    header = [
        Paragraph("DESCRIZIONE ARTICOLO", s["label"]),
        Paragraph("U.M.", s["label"]),
        Paragraph("Q.TÀ", s["label"]),
        Paragraph("PESO (kg)", s["label"]),
    ]
    rows = [header]
    total_weight = 0.0
    for desc, um, qty, weight in data["righe"]:
        row_weight = round(qty * weight, 2)
        total_weight += row_weight
        rows.append([
            Paragraph(desc, s["value"]),
            Paragraph(um, s["value"]),
            Paragraph(str(qty), s["value"]),
            Paragraph(f"{row_weight:.2f}", s["value"]),
        ])

    # Riga totale
    rows.append([
        Paragraph("", s["value"]),
        Paragraph("", s["value"]),
        Paragraph("TOTALE", s["label"]),
        Paragraph(f"{total_weight:.2f} kg", s["value"]),
    ])

    items_table = Table(rows, colWidths=[112*mm, 18*mm, 18*mm, 32*mm])
    row_colors = [
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
    ]
    for i in range(1, len(rows) - 1):
        bg = BLUE_LIGHT if i % 2 == 0 else WHITE
        row_colors.append(("BACKGROUND", (0, i), (-1, i), bg))
    row_colors.append(("BACKGROUND", (0, -1), (-1, -1), BLUE_LIGHT))

    items_table.setStyle(TableStyle(row_colors + [
        ("BOX", (0, 0), (-1, -1), 0.5, GRAY_LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, GRAY_LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("ALIGN", (3, 0), (-1, -1), "RIGHT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 5*mm))

    # ── Note e firme ──────────────────────────────────────────────────────────
    note_text = (
        "Il destinatario è pregato di verificare l'integrità del collo al momento "
        "della consegna. In caso di danni o discrepanze, apporre riserva scritta "
        "sulla lettera di vettura prima della firma."
    )
    story.append(Paragraph(note_text, s["note"]))
    story.append(Spacer(1, 10*mm))

    firma_table = Table(
        [[
            Paragraph("Firma mittente / timbro", s["label"]),
            Paragraph("Firma vettore", s["label"]),
            Paragraph("Firma destinatario", s["label"]),
        ],
        [
            Paragraph("\n\n\n", s["value"]),
            Paragraph("", s["value"]),
            Paragraph("", s["value"]),
        ]],
        colWidths=[60*mm, 60*mm, 60*mm],
    )
    firma_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, GRAY_LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, GRAY_LINE),
        ("BACKGROUND", (0, 0), (-1, 0), BLUE_LIGHT),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(firma_table)

    doc.build(story, onFirstPage=draw_page_border, onLaterPages=draw_page_border)
    print(f"  Creato: {filepath}")


# ─── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "sample_docs")
    os.makedirs(out_dir, exist_ok=True)

    print("Generazione DDT fittizi...")
    for i, ddt in enumerate(DDT_DATA, 1):
        filename = f"DDT_sample_{i:02d}.pdf"
        filepath = os.path.join(out_dir, filename)
        build_ddt_pdf(ddt, filepath)

    print(f"\nFatto! {len(DDT_DATA)} DDT salvati in: {out_dir}")
    print("(Tutti i dati sono completamente inventati — nessun riferimento reale)")
