# Live Mailbox Integration (Microsoft Graph API)

Aurion Claim Intake can connect to a real Microsoft 365 mailbox to process incoming claim emails — no copy-pasting needed.

## How It Works

```
Real Mailbox ──► Graph API ──► Aurion Workflow Pipeline
                                  │
                  Same pipeline as Sample mode:
                  Email Intake → Document AI → Classify → Extract → Decide → Response
```

- **Sample mode** (default): use preset scenarios or type emails manually
- **Live mode**: fetch unread emails from a real mailbox, select one, process it
- A toggle in the UI header switches between modes (only visible when configured)
- PDF attachments from real emails are automatically downloaded and sent to Document Intelligence

## Setup

### 1. Create an App Registration

1. Go to **Azure Portal → App registrations → + New registration**
2. Name: `Aurion Claim Intake - Graph API`
3. Account type: **Single tenant**
4. Redirect URI: leave blank
5. Click **Register**

### 2. Add API Permissions

1. Open your new App Registration → **API permissions → + Add a permission**
2. Select **Microsoft Graph → Application permissions**
3. Add:
   - `Mail.Read`
   - `Mail.Send` *(optional — for future response sending)*
4. Click **Grant admin consent** and confirm

### 3. Create a Client Secret

1. Go to **Certificates & secrets → + New client secret**
2. Set a description and expiry
3. **Copy the Value immediately** (you can't see it again later)

### 4. Add Environment Variables

Add these to your `.env` file at the repo root:

```env
GRAPH_TENANT_ID=<Directory (tenant) ID from App Registration overview>
GRAPH_CLIENT_ID=<Application (client) ID from App Registration overview>
GRAPH_CLIENT_SECRET=<Client secret Value from step 3>
GRAPH_MAILBOX=<Email address to monitor, e.g. claims@yourtenant.onmicrosoft.com>
```

### 5. Run

Start both servers as usual. The **Sample | Live** toggle appears in the header automatically.

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/mailbox/status` | GET | Check if Graph is configured |
| `/api/mailbox/emails` | GET | List up to 20 unread emails |
| `/api/claims/process/live` | POST | Fetch email by ID via Graph, run through workflow (SSE) |

## Architecture Notes

- Uses **client credentials flow** (app-level access, no user login required)
- PDF attachments are saved to a temp directory and passed to the existing Document Intelligence executor
- The live endpoint reuses the exact same workflow pipeline and SSE streaming as sample mode
- If Graph env vars are missing, everything works as before — sample mode only, no toggle shown
- All Graph code is additive — zero changes to existing sample mode logic

## Files

| File | Purpose |
|---|---|
| `backend/server/routes/mailbox.py` | Graph API routes + helpers |
| `frontend/src/hooks/useMailbox.ts` | Email fetching hook |
| `frontend/src/components/MailboxView.tsx` | Live email list UI |
| `frontend/src/App.tsx` | Mode toggle |
