"""Quick smoke test for Graph API mailbox access."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx
from server.routes.mailbox import _get_graph_config, _get_token, GRAPH_BASE

config = _get_graph_config()
assert config, "Graph not configured"
print(f"Mailbox: {config['mailbox']}")

token = _get_token(config)
print(f"Token: {token[:20]}...")

resp = httpx.get(
    f"{GRAPH_BASE}/users/{config['mailbox']}/messages",
    params={"$top": "5", "$select": "subject,from,receivedDateTime,isRead"},
    headers={"Authorization": f"Bearer {token}"},
)
print(f"HTTP {resp.status_code}")

if resp.status_code == 200:
    emails = resp.json().get("value", [])
    print(f"Found {len(emails)} email(s):")
    for e in emails:
        subj = e.get("subject", "(no subject)")
        sender = e.get("from", {}).get("emailAddress", {}).get("address", "?")
        read = "read" if e.get("isRead") else "UNREAD"
        print(f"  [{read}] {subj} — from {sender}")
else:
    print(f"Error: {resp.text}")
