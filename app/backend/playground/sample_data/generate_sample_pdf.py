"""Generate scenario-specific sample PDFs for testing.

Usage (from app/backend):
    uv run python playground/sample_data/generate_sample_pdf.py
"""

from pathlib import Path

from fpdf import FPDF

_OUT_DIR = Path(__file__).resolve().parent


def _make_kostenvoranschlag(
    output_path: str,
    *,
    title: str,
    company_name: str,
    company_address: str,
    company_phone: str,
    date: str,
    customer_line: str,
    subject_line: str,
    items: list[tuple[str, str, str, str, str]],
    net_total: str,
    vat: str,
    gross_total: str,
) -> None:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align="C")

    pdf.set_font("Helvetica", "", 10)
    pdf.ln(5)
    pdf.cell(0, 6, company_name, new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, company_address, new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Tel: {company_phone}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Datum: {date}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, f"Kunde: {customer_line}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Betreff: {subject_line}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # Table header
    pdf.set_font("Helvetica", "B", 10)
    col_widths = [10, 80, 30, 20, 30]
    headers = ["Pos.", "Beschreibung", "Einzelpreis", "Menge", "Gesamt"]
    for w, h in zip(col_widths, headers):
        pdf.cell(w, 8, h, border=1)
    pdf.ln()

    # Table rows
    pdf.set_font("Helvetica", "", 10)
    for row in items:
        for w, val in zip(col_widths, row):
            pdf.cell(w, 7, val, border=1)
        pdf.ln()

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, f"Nettobetrag:    EUR  {net_total}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"USt. 20%:       EUR  {vat}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Bruttobetrag:   EUR  {gross_total}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(10)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "Dieser Kostenvoranschlag ist 30 Tage gueltig.", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "Alle Preise in EUR.", new_x="LMARGIN", new_y="NEXT")

    pdf.output(output_path)
    print(f"PDF generated: {output_path}")


# --- Scenario 1: Water damage (Maria Huber) — auto-process ---

def generate_wasserschaden():
    _make_kostenvoranschlag(
        str(_OUT_DIR / "kostenvoranschlag_wasserschaden.pdf"),
        title="Kostenvoranschlag",
        company_name="Installateur Meister GmbH",
        company_address="Handwerkerstrasse 7, 1020 Wien",
        company_phone="+43 1 234 5678",
        date="16. Maerz 2026",
        customer_line="Maria Huber, Musterstrasse 12, 1020 Wien",
        subject_line="Reparatur Wasserschaden Kueche",
        items=[
            ("1", "Demontage beschaedigter Bodenbelag", "450,00", "1", "450,00"),
            ("2", "Trocknung und Entfeuchtung (3 Tage)", "180,00", "3", "540,00"),
            ("3", "Neuer Bodenbelag inkl. Verlegung", "1.200,00", "1", "1.200,00"),
            ("4", "Reparatur Kuechenmoebel (Unterschrank)", "680,00", "1", "680,00"),
            ("5", "Malerarbeiten Waende und Decke", "330,00", "1", "330,00"),
        ],
        net_total="3.200,00",
        vat="640,00",
        gross_total="3.840,00",
    )


# --- Scenario 2: Fire damage (Thomas Wagner) — escalate ---

def generate_brandschaden():
    _make_kostenvoranschlag(
        str(_OUT_DIR / "kostenvoranschlag_brandschaden.pdf"),
        title="Kostenvoranschlag - Sofortmassnahmen Brandschaden",
        company_name="Brandschutz & Sanierung Obermaier GmbH",
        company_address="Industriestrasse 22, 4020 Linz",
        company_phone="+43 732 654 321",
        date="23. Maerz 2026",
        customer_line="Thomas Wagner, Wagner GmbH, Industriestrasse 45, 4020 Linz",
        subject_line="Sofortmassnahmen Brandschaden Lagerhalle",
        items=[
            ("1", "Absicherung und Absperrung Brandstelle", "2.500,00", "1", "2.500,00"),
            ("2", "Entruempelung und Entsorgung Brandschutt", "8.400,00", "1", "8.400,00"),
            ("3", "Provisorische Dachabdeckung (Notplane)", "4.200,00", "1", "4.200,00"),
            ("4", "Statische Pruefung Tragwerk", "3.800,00", "1", "3.800,00"),
            ("5", "Reinigung und Entrussung Hallenstruktur", "6.500,00", "1", "6.500,00"),
            ("6", "Elektrische Anlage Sicherheitspruefung", "2.100,00", "1", "2.100,00"),
            ("7", "Warenbestand Schaetzung (zerstoert)", "55.000,00", "1", "55.000,00"),
            ("8", "Baustelleneinrichtung und Koordination", "2.500,00", "1", "2.500,00"),
        ],
        net_total="85.000,00",
        vat="17.000,00",
        gross_total="102.000,00",
    )


# --- Scenario 3: Car damage (Anna Berger) — no PDF ---
# Anna Berger has no attachment — this scenario tests the "no PDF" path.


# --- Scenario 4 (EN): Water damage (James Carter) — auto-process ---

def generate_wasserschaden_en():
    _make_kostenvoranschlag(
        str(_OUT_DIR / "kostenvoranschlag_wasserschaden_en.pdf"),
        title="Cost Estimate",
        company_name="Wiener Installateur Service GmbH",
        company_address="Ringstrasse 15, 1010 Wien",
        company_phone="+43 1 987 6543",
        date="21 March 2026",
        customer_line="James Carter, Ringstrasse 8, 1010 Wien",
        subject_line="Repair Water Damage Bathroom",
        items=[
            ("1", "Removal of damaged floor tiles", "380,00", "1", "380,00"),
            ("2", "Drying and dehumidification (2 days)", "180,00", "2", "360,00"),
            ("3", "New floor tiles incl. installation", "950,00", "1", "950,00"),
            ("4", "Wall repair and replastering", "620,00", "1", "620,00"),
            ("5", "Painting walls and ceiling", "490,00", "1", "490,00"),
        ],
        net_total="2.800,00",
        vat="560,00",
        gross_total="3.360,00",
    )


# --- Scenario 5 (EN): Car damage (Sophie Martinez) — no PDF ---
# Sophie Martinez has no attachment — this scenario tests the "no PDF" path.


def generate_all():
    generate_wasserschaden()
    generate_brandschaden()
    generate_wasserschaden_en()
    print("\nAll scenario PDFs generated.")
    print("Note: Scenario 3 (Anna Berger) and 5 (Sophie Martinez) have no PDF.")


if __name__ == "__main__":
    generate_all()
