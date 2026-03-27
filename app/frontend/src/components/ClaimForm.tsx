import { useCallback, useRef, useState } from "react";
import type { ClaimRequest, ScenarioPreset, WorkflowStatus } from "../types";
import "./ClaimForm.css";

const PRESETS: ScenarioPreset[] = [
  {
    id: "1",
    label: "Maria Huber",
    description: "Wasserschaden — Auto-Process",
    data: {
      sender: "maria.huber@gmail.com",
      subject: "Schadensmeldung - Wasserschaden Polizze Nr. WH-2024-881234",
      pdf_path: "playground/sample_data/kostenvoranschlag_wasserschaden.pdf",
      body: `Sehr geehrte Damen und Herren,

hiermit melde ich einen Wasserschaden in meiner versicherten Wohnung.

Polizzennummer: WH-2024-881234
Name: Maria Huber
Schadensdatum: 15. März 2026
Schadensort: Musterstraße 12, 1020 Wien

Am 15. März 2026 ist ein Rohrbruch in der Küche aufgetreten. Das Wasser hat den Boden und die Küchenmöbel beschädigt. Ich habe sofort den Hauptwasserhahn abgedreht und einen Installateur gerufen.

Die geschätzten Reparaturkosten belaufen sich auf EUR 3.200,00. Im Anhang finden Sie den Kostenvoranschlag des Installateurs.

Mit freundlichen Grüßen,
Maria Huber
Tel: +43 664 1234567`,
    },
  },
  {
    id: "2",
    label: "Thomas Wagner",
    description: "Brandschaden — Escalate",
    data: {
      sender: "thomas.wagner@aon.at",
      subject: "DRINGEND - Brandschaden Gewerbeobjekt - Polizze GW-2023-445566",
      pdf_path: "playground/sample_data/kostenvoranschlag_brandschaden.pdf",
      body: `Sehr geehrte Damen und Herren,

ich muss leider einen schweren Brandschaden an meinem Gewerbeobjekt melden.

Polizzennummer: GW-2023-445566
Name: Thomas Wagner, Wagner GmbH
Schadensdatum: 22. März 2026
Schadensort: Industriestraße 45, 4020 Linz

In der Nacht vom 22. März ist ein Brand in der Lagerhalle ausgebrochen. Die Feuerwehr war im Einsatz. Das gesamte Lager mit Warenbestand wurde zerstört. Auch das Dach und die Seitenwände der Halle sind schwer beschädigt.

Vorläufige Schadensschätzung: EUR 85.000,00
Ein Gutachter wurde bereits beauftragt. Den Kostenvoranschlag für die Sofortmaßnahmen finden Sie im Anhang.

Ich bitte um dringendste Bearbeitung.

Mit freundlichen Grüßen,
Thomas Wagner
Tel: +43 660 9876543`,
    },
  },
  {
    id: "3",
    label: "Anna Berger",
    description: "Autoschaden — Request Info",
    data: {
      sender: "anna.berger@hotmail.com",
      subject: "Autoschaden",
      body: `Hallo,

ich hatte letzte Woche einen Schaden an meinem Auto. Jemand hat mein Auto auf dem Parkplatz beschädigt. Ich weiß nicht genau wann es passiert ist, ich habe es erst bemerkt als ich vom Einkaufen zurückkam.

Können Sie mir bitte sagen was ich tun muss?

Danke,
Anna Berger`,
    },
  },
  {
    id: "4",
    label: "James Carter",
    description: "Water Damage (EN) — Auto-Process",
    data: {
      sender: "james.carter@outlook.com",
      subject: "Claim Report - Water Damage Policy No. WH-2025-990012",
      pdf_path: "playground/sample_data/kostenvoranschlag_wasserschaden_en.pdf",
      body: `Dear Sir or Madam,

I would like to report water damage in my insured apartment.

Policy number: WH-2025-990012
Name: James Carter
Date of incident: 20 March 2026
Location: Ringstrasse 8, 1010 Vienna

On 20 March 2026, a pipe burst in the bathroom causing significant water damage to the floor and walls. I immediately shut off the main water supply and contacted a plumber.

The estimated repair cost is EUR 2,800.00. Please find the cost estimate attached.

Kind regards,
James Carter
Tel: +43 699 1112233`,
    },
  },
  {
    id: "5",
    label: "Sophie Martinez",
    description: "Car Damage (EN) — Request Info",
    data: {
      sender: "sophie.martinez@gmail.com",
      subject: "Car damage",
      body: `Hello,

Someone hit my parked car last week while I was at work. I noticed the damage on the driver side door when I came back. I'm not sure exactly when it happened.

Could you please let me know what steps I need to take?

Thanks,
Sophie Martinez`,
    },
  },
];

interface Props {
  onSubmit: (req: ClaimRequest, file?: File) => void;
  workflowStatus: WorkflowStatus;
  onReset: () => void;
}

export function ClaimForm({ onSubmit, workflowStatus, onReset }: Props) {
  const [form, setForm] = useState<ClaimRequest>({
    sender: "",
    subject: "",
    body: "",
  });
  const [file, setFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handlePreset = (preset: ScenarioPreset) => {
    setForm({ ...preset.data });
    setFile(null);
  };

  const handleFile = useCallback((f: File | undefined) => {
    if (f && f.type === "application/pdf") {
      setFile(f);
    }
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const f = e.dataTransfer.files[0];
      handleFile(f);
    },
    [handleFile]
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.sender || !form.body) return;
    onSubmit(form, file ?? undefined);
  };

  const isRunning = workflowStatus === "running";

  return (
    <div className="claim-form">
      <h2>📧 Email Input</h2>

      <div className="presets">
        <span className="presets-label">Scenarios:</span>
        {PRESETS.map((p) => (
          <button
            key={p.id}
            className="preset-btn"
            onClick={() => handlePreset(p)}
            disabled={isRunning}
            title={p.description}
          >
            {p.label}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit}>
        <label>
          From
          <input
            type="email"
            value={form.sender}
            onChange={(e) => setForm({ ...form, sender: e.target.value })}
            placeholder="customer@example.com"
            disabled={isRunning}
          />
        </label>

        <label>
          Subject
          <input
            type="text"
            value={form.subject}
            onChange={(e) => setForm({ ...form, subject: e.target.value })}
            placeholder="Schadensmeldung..."
            disabled={isRunning}
          />
        </label>

        <label>
          Body
          <textarea
            value={form.body}
            onChange={(e) => setForm({ ...form, body: e.target.value })}
            rows={10}
            placeholder="Sehr geehrte Damen und Herren..."
            disabled={isRunning}
          />
        </label>

        <div
          className={`drop-zone${dragOver ? " drag-over" : ""}${file ? " has-file" : ""}`}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => !isRunning && fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            hidden
            disabled={isRunning}
            onChange={(e) => handleFile(e.target.files?.[0])}
          />
          {file ? (
            <div className="drop-zone-file">
              <span className="drop-zone-icon">📄</span>
              <span className="drop-zone-name">{file.name}</span>
              <button
                type="button"
                className="drop-zone-remove"
                onClick={(e) => { e.stopPropagation(); setFile(null); }}
                disabled={isRunning}
              >
                ✕
              </button>
            </div>
          ) : (
            <div className="drop-zone-placeholder">
              <span className="drop-zone-icon">📎</span>
              <span>Drop PDF here or click to upload</span>
              <span className="drop-zone-hint">Optional — sample PDF used if empty</span>
            </div>
          )}
        </div>

        <div className="form-actions">
          <button
            type="submit"
            className="submit-btn"
            disabled={isRunning || !form.sender || !form.body}
          >
            {isRunning ? "Processing..." : "▶ Process Claim"}
          </button>
          {(workflowStatus === "completed" || workflowStatus === "failed") && (
            <button type="button" className="reset-btn" onClick={onReset}>
              ↺ Reset
            </button>
          )}
        </div>
      </form>
    </div>
  );
}
