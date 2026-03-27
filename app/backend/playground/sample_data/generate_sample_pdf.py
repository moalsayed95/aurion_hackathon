"""Generate a sample Kostenvoranschlag (cost estimate) PDF for testing."""

from fpdf import FPDF


def generate_kostenvoranschlag(output_path: str = "playground/sample_data/kostenvoranschlag.pdf") -> None:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Kostenvoranschlag", new_x="LMARGIN", new_y="NEXT", align="C")

    pdf.set_font("Helvetica", "", 10)
    pdf.ln(5)
    pdf.cell(0, 6, "Installateur Meister GmbH", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "Handwerkerstrasse 7, 1020 Wien", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "Tel: +43 1 234 5678", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "Datum: 16. Maerz 2026", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Kunde: Maria Huber, Musterstrasse 12, 1020 Wien", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "Betreff: Reparatur Wasserschaden Kueche", new_x="LMARGIN", new_y="NEXT")
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
    items = [
        ("1", "Demontage beschaedigter Bodenbelag", "450,00", "1", "450,00"),
        ("2", "Trocknung und Entfeuchtung (3 Tage)", "180,00", "3", "540,00"),
        ("3", "Neuer Bodenbelag inkl. Verlegung", "1.200,00", "1", "1.200,00"),
        ("4", "Reparatur Kuechenmöbel (Unterschrank)", "680,00", "1", "680,00"),
        ("5", "Malerarbeiten Waende und Decke", "330,00", "1", "330,00"),
    ]
    for row in items:
        for w, val in zip(col_widths, row):
            pdf.cell(w, 7, val, border=1)
        pdf.ln()

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "Nettobetrag:    EUR  3.200,00", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "USt. 20%:       EUR    640,00", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Bruttobetrag:   EUR  3.840,00", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(10)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "Dieser Kostenvoranschlag ist 30 Tage gueltig.", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "Alle Preise in EUR.", new_x="LMARGIN", new_y="NEXT")

    pdf.output(output_path)
    print(f"PDF generated: {output_path}")


if __name__ == "__main__":
    generate_kostenvoranschlag()
