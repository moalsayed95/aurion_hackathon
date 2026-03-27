"""Standalone test for Azure Document Intelligence — verify PDF extraction works.

Usage (from app/backend):
    uv run python playground/test_doc_intelligence.py
    uv run python playground/test_doc_intelligence.py path/to/other.pdf
"""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env from repo root
_repo_root = Path(__file__).resolve().parents[3]
load_dotenv(_repo_root / ".env")


async def test_doc_intelligence(pdf_path: str) -> None:
    from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
    from azure.identity import DefaultAzureCredential

    endpoint = os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    if not endpoint:
        print("ERROR: AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT not set in .env")
        sys.exit(1)

    # Resolve relative paths from backend/
    if not os.path.isabs(pdf_path):
        pdf_path = str(Path(__file__).resolve().parent.parent / pdf_path)

    if not os.path.exists(pdf_path):
        print(f"ERROR: PDF not found: {pdf_path}")
        sys.exit(1)

    print(f"Endpoint:  {endpoint}")
    print(f"PDF:       {pdf_path}")
    print(f"File size: {os.path.getsize(pdf_path):,} bytes")
    print(f"\nSending to Azure Document Intelligence (prebuilt-layout)...")

    credential = DefaultAzureCredential()

    async with DocumentIntelligenceClient(endpoint=endpoint, credential=credential) as client:
        with open(pdf_path, "rb") as f:
            poller = await client.begin_analyze_document(
                "prebuilt-layout",
                body=f,
                content_type="application/octet-stream",
            )
        result = await poller.result()

    # --- Extracted text ---
    print(f"\n{'='*60}")
    print("  EXTRACTED TEXT")
    print(f"{'='*60}")
    if result.content:
        print(result.content)
    else:
        print("(no text extracted)")

    # --- Tables ---
    print(f"\n{'='*60}")
    print("  TABLES")
    print(f"{'='*60}")
    if result.tables:
        for i, table in enumerate(result.tables):
            rows: dict[int, dict[int, str]] = {}
            for cell in table.cells:
                rows.setdefault(cell.row_index, {})[cell.column_index] = cell.content
            print(f"\nTabelle {i + 1} ({table.row_count} rows x {table.column_count} cols):")
            for row_idx in sorted(rows.keys()):
                row = rows[row_idx]
                print("  " + " | ".join(row[c] for c in sorted(row.keys())))
    else:
        print("(no tables found)")

    # --- Summary ---
    print(f"\n{'='*60}")
    print("  SUMMARY")
    print(f"{'='*60}")
    print(f"  Text length:  {len(result.content) if result.content else 0} chars")
    print(f"  Tables found: {len(result.tables) if result.tables else 0}")
    print(f"  Pages:        {len(result.pages) if result.pages else 0}")
    print(f"\n  Document Intelligence is working correctly.")


if __name__ == "__main__":
    pdf = sys.argv[1] if len(sys.argv) > 1 else "playground/sample_data/kostenvoranschlag.pdf"
    asyncio.run(test_doc_intelligence(pdf))
