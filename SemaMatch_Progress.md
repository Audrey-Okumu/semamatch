# SemaMatch — Build Progress


## Done

###  Project Scaffold
- Flask app factory (`app/__init__.py`) — config, database init, blueprint registration
- `Caller` model (`app/models/caller.py`) — one row per call session: phone number, language, intent, age bracket, status (`collecting → queued → matched → completed`), match reference, consent answer
- Health check + `/api/callers` debug endpoint (`app/routes/dashboard.py`)
- `requirements.txt`, `.env.example`, `.gitignore`
- Verified: server runs locally, database auto-creates, endpoints respond correctly

###  IVR Menu Logic
- `app/routes/voice.py`  handle the  call flow:
  1. First hit → creates a `Caller` row, asks for **language** (English/Kiswahili)
  2. Second hit → saves language, asks for **intent** (serious/friendship/casual)
  3. Third hit → saves intent, asks for **age bracket** (18–25 / 26–35 / 36+)
  4. Fourth hit → saves age bracket, sets `status = "queued"`
- Uses Africa's Talking's `<GetDigits>` XML tag to capture keypad (DTMF) input at each step


###  Matching Queue Logic
- New file: `app/services/matching.py`
- `find_match()` — looks for another `queued` caller with the same `intent` and `language`, oldest-waiting-first
- `try_match()` — if a match is found, marks both callers `status = "matched"` and links their `match_session_id` to each other
- Wired into `voice.py`: after the age-bracket step, `try_match()` runs automatically and the caller is told whether a match was found

---

##  Not Started

### Live Call Bridging
- Not built yet. This is the next step: using Africa's Talking's `<Dial>` XML tag to actually connect two matched callers' audio into one live call.
- **Known design challenge to solve here:** the caller who completes their questions *first* is left waiting with nothing happening after their "please hold" message — only the caller who completes *second* can trigger a live `<Dial>` in their own response. Properly holding the first caller until a bridge happens needs either Africa's Talking's queue/hold handling or a polling approach — this is a real complexity step up from Sections 1–3 and needs to be worked through carefully, not rushed.

###  Consent Check + SMS Reveal
- Not started. Post-call: privately ask each caller if they want to reconnect; only send contact info via SMS if both say yes.



