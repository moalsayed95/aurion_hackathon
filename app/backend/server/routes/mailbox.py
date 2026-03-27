"""Microsoft Graph API routes — Live Mailbox integration.

Provides endpoints for:
- Checking Graph configuration status
- Listing unread emails from the configured mailbox
- Processing a live email through the claim workflow (SSE)
"""

import base64
import os
import re
import tempfile
from html import unescape
from pathlib import Path

import httpx
from azure.identity import ClientSecretCredential
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from aurion_claim_workflow.models import EmailInput
from server.routes.claims_stream import _stream_workflow

router = APIRouter(tags=["mailbox"])

GRAPH_BASE = "https://graph.microsoft.com/v1.0"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_graph_config() -> dict | None:
    """Return Graph config dict or None if not fully configured."""
    tenant = os.getenv("GRAPH_TENANT_ID")
    client_id = os.getenv("GRAPH_CLIENT_ID")
    secret = os.getenv("GRAPH_CLIENT_SECRET")
    mailbox = os.getenv("GRAPH_MAILBOX")
    if not all([tenant, client_id, secret, mailbox]):
        return None
    return {
        "tenant_id": tenant,
        "client_id": client_id,
        "client_secret": secret,
        "mailbox": mailbox,
    }


def _get_token(config: dict) -> str:
    """Obtain an access token via client-credentials flow."""
    credential = ClientSecretCredential(
        tenant_id=config["tenant_id"],
        client_id=config["client_id"],
        client_secret=config["client_secret"],
    )
    return credential.get_token("https://graph.microsoft.com/.default").token


def _html_to_text(html: str) -> str:
    """Crude but sufficient HTML → plain-text conversion."""
    text = re.sub(r"<br\s*/?\s*>", "\n", html, flags=re.IGNORECASE)
    text = re.sub(r"</(p|div|tr|li)>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/mailbox/status")
async def mailbox_status():
    """Check whether Graph API is configured."""
    config = _get_graph_config()
    return {
        "configured": config is not None,
        "mailbox": config["mailbox"] if config else None,
    }


@router.get("/mailbox/emails")
async def list_emails():
    """Return up to 20 unread emails from the configured mailbox."""
    config = _get_graph_config()
    if not config:
        raise HTTPException(503, "Graph API not configured")

    token = _get_token(config)
    url = f"{GRAPH_BASE}/users/{config['mailbox']}/messages"

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            url,
            params={
                "$filter": "isRead eq false",
                "$top": "20",
                "$orderby": "receivedDateTime desc",
                "$select": "id,subject,from,receivedDateTime,hasAttachments,bodyPreview",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        if resp.status_code != 200:
            raise HTTPException(resp.status_code, resp.text)

    emails = []
    for msg in resp.json().get("value", []):
        emails.append({
            "id": msg["id"],
            "subject": msg.get("subject", "(no subject)"),
            "sender": msg.get("from", {}).get("emailAddress", {}).get("address", "unknown"),
            "sender_name": msg.get("from", {}).get("emailAddress", {}).get("name", ""),
            "received": msg.get("receivedDateTime", ""),
            "has_attachments": msg.get("hasAttachments", False),
            "preview": msg.get("bodyPreview", "")[:200],
        })
    return {"emails": emails}


class _LiveEmailRequest(BaseModel):
    message_id: str


@router.post("/claims/process/live")
async def process_live_email(req: _LiveEmailRequest):
    """Fetch a real email via Graph API and stream it through the claim workflow."""
    config = _get_graph_config()
    if not config:
        raise HTTPException(503, "Graph API not configured")

    token = _get_token(config)
    headers = {"Authorization": f"Bearer {token}"}
    user = config["mailbox"]

    async with httpx.AsyncClient(timeout=15.0) as client:
        # 1. Fetch the email
        msg_resp = await client.get(
            f"{GRAPH_BASE}/users/{user}/messages/{req.message_id}",
            params={"$select": "id,subject,from,body,receivedDateTime,hasAttachments"},
            headers=headers,
        )
        if msg_resp.status_code != 200:
            raise HTTPException(msg_resp.status_code, "Failed to fetch email from Graph API")

        msg = msg_resp.json()
        sender = msg.get("from", {}).get("emailAddress", {}).get("address", "unknown")
        subject = msg.get("subject", "")

        # Body may be HTML — convert to plain text for the LLM
        body_obj = msg.get("body", {})
        body = body_obj.get("content", "")
        if body_obj.get("contentType", "").lower() == "html":
            body = _html_to_text(body)

        # 2. Download first PDF attachment to a temp file
        pdf_path: str | None = None
        if msg.get("hasAttachments"):
            att_resp = await client.get(
                f"{GRAPH_BASE}/users/{user}/messages/{req.message_id}/attachments",
                headers=headers,
            )
            if att_resp.status_code == 200:
                for att in att_resp.json().get("value", []):
                    ct = att.get("contentType", "")
                    if "pdf" in ct.lower() and att.get("contentBytes"):
                        tmp_dir = Path(tempfile.mkdtemp(prefix="aurion_graph_"))
                        tmp_file = tmp_dir / (att.get("name", "attachment.pdf"))
                        tmp_file.write_bytes(base64.b64decode(att["contentBytes"]))
                        pdf_path = str(tmp_file)
                        break  # use first PDF

    email_input = EmailInput(
        sender=sender,
        subject=subject,
        body=body,
        pdf_path=pdf_path,
    )

    return StreamingResponse(
        _stream_workflow(email_input),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
