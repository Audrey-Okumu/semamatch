
# SemaMatch

**Call a Number, Meet a Stranger** — an anonymous, voice-first matchmaking service
for the African market, built on Africa's Talking Voice & SMS APIs.

A caller dials the SemaMatch number, answers three keypad prompts (language, intent,
age bracket), and is bridged live into an anonymous phone call with a matching
stranger. Neither party's phone number is ever revealed. No smartphone, app, or data
bundle required.

> Hackathon MVP — Africa's Talking Dating & Social Networks Hackathon.

## How it works

1. A caller dials the Africa's Talking voice number.
2. An IVR menu collects language, relationship intent, and age bracket via the
   keypad (DTMF).
3. The caller is placed in a matching queue (`<Enqueue>`) and hears a hold message.
4. When a second caller matches on **language + intent**, the two calls are bridged
   (`<Dequeue>`) through the Africa's Talking number — so neither party sees the
   other's number.
5. *(Roadmap)* After the call, each party is privately asked whether to reconnect;
   contact details are shared by SMS only on mutual consent.

The live bridge is implemented entirely with Africa's Talking **callback XML** — no
outbound call API or SDK credentials are needed for the core matchmaking loop.

## Tech stack

- **Backend:** Python + Flask
- **Database:** SQLite via Flask-SQLAlchemy (zero setup, single file)
- **Telephony:** Africa's Talking Voice API (IVR, DTMF capture, Enqueue/Dequeue bridging)
- **Tunnel:** ngrok (exposes the local server to Africa's Talking webhooks)
- **Dashboard:** single-file HTML + vanilla JS (live queue view for judges)

## Project structure

```
semamatch/
├── app/
│   ├── __init__.py          # app factory, config, db init
│   ├── models/
│   │   ├── __init__.py
│   │   ├── db.py            # SQLAlchemy instance
│   │   └── caller.py       # Caller model (session, prefs, status, match link)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── voice.py        # IVR flow + Enqueue/Dequeue bridge (AT voice webhook)
│   │   └── dashboard.py    # health check, /api/callers, live /dashboard
│   └── services/
│       ├── __init__.py
│       └── matching.py     # queue matching logic
├── run.py                   # entry point
├── requirements.txt
└── .env                     # your secrets (do NOT commit)
```

Every folder under `app/` needs an `__init__.py` (they can be empty) so Python treats
them as packages.

## Prerequisites

- Python 3.10 or newer
- For live calls: an Africa's Talking account with a **live voice number** and
  account **credit**
- For live calls: [ngrok](https://ngrok.com/) installed

## Setup & run (local)

Run these from the **project root** — the folder that contains `run.py` and the `app`
folder.

**Windows (PowerShell):**

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

The server starts on `http://localhost:5000`. Open:

- `http://localhost:5000/` — health-check JSON
- `http://localhost:5000/dashboard` — live queue dashboard

Stop the server with **Ctrl+C**. To start again later, just re-activate the venv and
run `python run.py`.

## Environment variables

Create a `.env` file in the project root:

```
SECRET_KEY=change-me
AT_USERNAME=your_production_username
AT_API_KEY=your_production_api_key
AT_VOICE_NUMBER=+254XXXXXXXXX
PUBLIC_BASE_URL=https://your-id.ngrok-free.app
# optional:
AT_HOLD_MUSIC_URL=
AT_SENDER_ID=
```

- `AT_VOICE_NUMBER` — your live number in full international format; the bridge's
  `<Dequeue>` needs it.
- `PUBLIC_BASE_URL` — your current ngrok HTTPS URL, no trailing slash; keeps DTMF
  callbacks pointed at the right host.
- The rest are only used by post-hackathon features (SMS reveal). For local dashboard
  testing you can leave most of these blank.

> **Required code change:** `python run.py` does not auto-load `.env`. Add these two
> lines at the very top of `app/__init__.py`:
>
> ```python
> from dotenv import load_dotenv
> load_dotenv()
> ```

## Going live (real phone calls)

1. Start the app: `python run.py`
2. In a second terminal: `ngrok http 5000`
3. Copy the `https://...ngrok-free.app` URL into `PUBLIC_BASE_URL` in `.env`, then
   **restart the app**.
4. In the Africa's Talking dashboard, set your voice number's callback URL to:
   `https://your-id.ngrok-free.app/voice/incoming`
5. Point judges at: `https://your-id.ngrok-free.app/dashboard`

## Live demo script

1. **Phone 1** calls the number, answers the three prompts, and **stays on the line**
   → appears under "Waiting in queue" on the dashboard.
2. **Phone 2** calls and picks the **same language and intent** → hears
   "Connecting you now"; both phones are bridged into one anonymous call; the
   dashboard shows them as a connected pair.

Matching is on **language + intent** (age bracket is captured but not currently used
to match — this keeps demo matches easy to trigger).

---

## API endpoints

| Method | Path                | Purpose                                            |
| ------ | ------------------- | -------------------------------------------------- |
| GET    | `/`               | Health check                                       |
| GET    | `/api/callers`    | All caller sessions as JSON (powers the dashboard) |
| GET    | `/dashboard`      | Live judge-facing queue view                       |
| POST   | `/voice/incoming` | Africa's Talking voice callback (IVR + bridge)     |

## Troubleshooting

- **`ModuleNotFoundError: No module named 'app'`** — run `python run.py` from the
  project root (the folder containing the `app` folder), not from inside `app/`.
- **PowerShell blocks venv activation** — run
  `Set-ExecutionPolicy -Scope Process Bypass` then activate again, or use
  `venv\Scripts\activate.bat` in a cmd terminal.
- **IVR keeps repeating / DTMF never comes back** — make sure `PUBLIC_BASE_URL` is
  your current ngrok HTTPS URL and the app was restarted after setting it.
- **Bridge does nothing when phone 2 matches** — confirm `AT_VOICE_NUMBER` is set in
  full international format (`+254...`) and that phone 1 did not hang up.
- **Env vars appear empty** — confirm the `load_dotenv()` lines are at the very top of
  `app/__init__.py`.

## Roadmap (post-hackathon)

- Post-call private consent check + SMS contact reveal on mutual opt-in
- Lightweight content moderation (speech-to-text flagging)
- Interest-based (non-dating) call lines
- Voice-match-as-a-service SDK for embedding in other apps
