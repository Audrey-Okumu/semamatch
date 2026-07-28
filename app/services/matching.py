from app.models.db import db
from app.models.caller import Caller


def find_match(caller):
    """
    Looks for another caller who is queued, matches on intent and language,
    and isn't the same person. Returns the matched Caller, or None if nobody fits yet.
    """
    candidate = (
        Caller.query
        .filter(Caller.status == "queued")
        .filter(Caller.session_id != caller.session_id)
        .filter(Caller.intent == caller.intent)
        .filter(Caller.language == caller.language)
        .order_by(Caller.created_at.asc())
        .first()
    )
    return candidate


def try_match(caller):
    """
    Attempts to match `caller` with someone already waiting.
    If found, marks both as matched and links them to each other.
    Returns the matched Caller, or None if caller must keep waiting.
    """
    match = find_match(caller)

    if match is None:
        return None

    caller.status = "matched"
    caller.match_session_id = match.session_id

    match.status = "matched"
    match.match_session_id = caller.session_id

    db.session.commit()
    return match