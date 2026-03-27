import os

from agent_framework import WorkflowContext, executor

from ..models import EmailInput, ProcessedDocument


@executor(id="doc_intelligence")
async def doc_intelligence(email: EmailInput, ctx: WorkflowContext[ProcessedDocument]) -> None:
    pdf_text = ""
    pdf_tables: list[str] = []

    try:
        from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
        from azure.identity import DefaultAzureCredential

        endpoint = os.environ["AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"]
        credential = DefaultAzureCredential()

        # Resolve relative paths from project root
        pdf_path = email.pdf_path
        if not os.path.isabs(pdf_path):
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            pdf_path = os.path.join(project_root, pdf_path)

        async with DocumentIntelligenceClient(endpoint=endpoint, credential=credential) as client:
            with open(pdf_path, "rb") as f:
                poller = await client.begin_analyze_document(
                    "prebuilt-layout",
                    body=f,
                    content_type="application/octet-stream",
                )
            result = await poller.result()

            if result.content:
                pdf_text = result.content

            if result.tables:
                for i, table in enumerate(result.tables):
                    rows: dict[int, dict[int, str]] = {}
                    for cell in table.cells:
                        rows.setdefault(cell.row_index, {})[cell.column_index] = cell.content
                    lines = []
                    for row_idx in sorted(rows.keys()):
                        row = rows[row_idx]
                        lines.append(" | ".join(row[c] for c in sorted(row.keys())))
                    pdf_tables.append(f"Tabelle {i + 1}:\n" + "\n".join(lines))

    except Exception as e:
        pdf_text = f"[Dokument konnte nicht verarbeitet werden: {e}]"

    doc = ProcessedDocument(
        sender=email.sender,
        subject=email.subject,
        body=email.body,
        pdf_text=pdf_text,
        pdf_tables=pdf_tables,
    )
    await ctx.send_message(doc)
