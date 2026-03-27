from aurion_claim_workflow.models import EmailInput

# Scenario 1: Auto-process — complete data, low amount, normal urgency
SCENARIO_AUTO_PROCESS = EmailInput(
    sender="maria.huber@gmail.com",
    subject="Schadensmeldung - Wasserschaden Polizze Nr. WH-2024-881234",
    body=(
        "Sehr geehrte Damen und Herren,\n\n"
        "hiermit melde ich einen Wasserschaden in meiner versicherten Wohnung.\n\n"
        "Polizzennummer: WH-2024-881234\n"
        "Name: Maria Huber\n"
        "Schadensdatum: 15. März 2026\n"
        "Schadensort: Musterstraße 12, 1020 Wien\n\n"
        "Am 15. März 2026 ist ein Rohrbruch in der Küche aufgetreten. "
        "Das Wasser hat den Boden und die Küchenmöbel beschädigt. "
        "Ich habe sofort den Hauptwasserhahn abgedreht und einen Installateur gerufen.\n\n"
        "Die geschätzten Reparaturkosten belaufen sich auf EUR 3.200,00. "
        "Im Anhang finden Sie den Kostenvoranschlag des Installateurs.\n\n"
        "Mit freundlichen Grüßen,\n"
        "Maria Huber\n"
        "Tel: +43 664 1234567"
    ),
    pdf_path="playground/sample_data/kostenvoranschlag_wasserschaden.pdf",
)

# Scenario 2: Escalate — high amount, fire damage, critical urgency
SCENARIO_ESCALATE = EmailInput(
    sender="thomas.wagner@aon.at",
    subject="DRINGEND - Brandschaden Gewerbeobjekt - Polizze GW-2023-445566",
    body=(
        "Sehr geehrte Damen und Herren,\n\n"
        "ich muss leider einen schweren Brandschaden an meinem Gewerbeobjekt melden.\n\n"
        "Polizzennummer: GW-2023-445566\n"
        "Name: Thomas Wagner, Wagner GmbH\n"
        "Schadensdatum: 22. März 2026\n"
        "Schadensort: Industriestraße 45, 4020 Linz\n\n"
        "In der Nacht vom 22. März ist ein Brand in der Lagerhalle ausgebrochen. "
        "Die Feuerwehr war im Einsatz. Das gesamte Lager mit Warenbestand wurde zerstört. "
        "Auch das Dach und die Seitenwände der Halle sind schwer beschädigt.\n\n"
        "Vorläufige Schadensschätzung: EUR 85.000,00\n"
        "Ein Gutachter wurde bereits beauftragt. Den Kostenvoranschlag für die "
        "Sofortmaßnahmen finden Sie im Anhang.\n\n"
        "Ich bitte um dringendste Bearbeitung.\n\n"
        "Mit freundlichen Grüßen,\n"
        "Thomas Wagner\n"
        "Tel: +43 660 9876543"
    ),
    pdf_path="playground/sample_data/kostenvoranschlag_brandschaden.pdf",
)

# Scenario 3: Request more info — vague description, missing policy number, no PDF
SCENARIO_REQUEST_INFO = EmailInput(
    sender="anna.berger@hotmail.com",
    subject="Autoschaden",
    body=(
        "Hallo,\n\n"
        "ich hatte letzte Woche einen Schaden an meinem Auto. "
        "Jemand hat mein Auto auf dem Parkplatz beschädigt. "
        "Ich weiß nicht genau wann es passiert ist, "
        "ich habe es erst bemerkt als ich vom Einkaufen zurückkam.\n\n"
        "Können Sie mir bitte sagen was ich tun muss?\n\n"
        "Danke,\n"
        "Anna Berger"
    ),
)

# Scenario 4 (EN): Auto-process — complete data, English email, water damage
SCENARIO_AUTO_PROCESS_EN = EmailInput(
    sender="james.carter@outlook.com",
    subject="Claim Report - Water Damage Policy No. WH-2025-990012",
    body=(
        "Dear Sir or Madam,\n\n"
        "I would like to report water damage in my insured apartment.\n\n"
        "Policy number: WH-2025-990012\n"
        "Name: James Carter\n"
        "Date of incident: 20 March 2026\n"
        "Location: Ringstrasse 8, 1010 Vienna\n\n"
        "On 20 March 2026, a pipe burst in the bathroom causing significant "
        "water damage to the floor and walls. I immediately shut off the main "
        "water supply and contacted a plumber.\n\n"
        "The estimated repair cost is EUR 2,800.00. "
        "Please find the cost estimate attached.\n\n"
        "Kind regards,\n"
        "James Carter\n"
        "Tel: +43 699 1112233"
    ),
    pdf_path="playground/sample_data/kostenvoranschlag_wasserschaden_en.pdf",
)

# Scenario 5 (EN): Request more info — vague, missing details, no PDF
SCENARIO_REQUEST_INFO_EN = EmailInput(
    sender="sophie.martinez@gmail.com",
    subject="Car damage",
    body=(
        "Hello,\n\n"
        "Someone hit my parked car last week while I was at work. "
        "I noticed the damage on the driver side door when I came back. "
        "I'm not sure exactly when it happened.\n\n"
        "Could you please let me know what steps I need to take?\n\n"
        "Thanks,\n"
        "Sophie Martinez"
    ),
)

SCENARIOS = {
    "1": ("Auto-Process DE (Maria Huber, Wasserschaden)", SCENARIO_AUTO_PROCESS),
    "2": ("Escalate DE (Thomas Wagner, Brandschaden)", SCENARIO_ESCALATE),
    "3": ("Request Info DE (Anna Berger, Autoschaden)", SCENARIO_REQUEST_INFO),
    "4": ("Auto-Process EN (James Carter, Water Damage)", SCENARIO_AUTO_PROCESS_EN),
    "5": ("Request Info EN (Sophie Martinez, Car Damage)", SCENARIO_REQUEST_INFO_EN),
}
