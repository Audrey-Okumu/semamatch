from flask import Blueprint, Response, current_app, request
from app.models.db import db
from app.models.caller import Caller
from app.services.matching import try_match

voice_bp = Blueprint("voice", __name__)


def say(text):
    return f'<Say voice="woman">{text}</Say>'


def get_digits(prompt, num_digits=1):
    # GetDigits block that asks a question and waits for keypad input.

    callback = request.url_root.rstrip("/") + "/voice/incoming"
    return f'''<GetDigits timeout="10" numDigits="{num_digits}" callbackUrl="{callback}">
        {say(prompt)}
    </GetDigits>'''


def xml(*blocks):
    body = "\n".join(blocks)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<Response>\n{body}\n</Response>'


@voice_bp.route("/voice/incoming", methods=["POST"])
def incoming_call():
    session_id = request.values.get("sessionId")
    phone_number = request.values.get("phoneNumber")
    digits = request.values.get("dtmfDigits", "").strip()

    caller = Caller.query.get(session_id)

    #  create the row, ask for language
    if caller is None:
        caller = Caller(session_id=session_id, phone_number=phone_number)
        db.session.add(caller)
        db.session.commit()

        response = xml(get_digits(
            "Welcome to Sema Match. Press 1 for English. Press 2 for Kiswahili."
        ))
        return Response(response, mimetype="text/xml")

    if caller.language is None:
        caller.language = "english" if digits == "1" else "kiswahili"
        db.session.commit()

        response = xml(get_digits(
            "Press 1 for a serious relationship. Press 2 for friendship. Press 3 for casual chat."
        ))
        return Response(response, mimetype="text/xml")

    if caller.intent is None:
        intent_map = {"1": "serious", "2": "friendship", "3": "casual"}
        caller.intent = intent_map.get(digits, "casual")
        db.session.commit()

        response = xml(get_digits(
            "Press 1 for ages 18 to 25. Press 2 for 26 to 35. Press 3 for 36 and above."
        ))
        return Response(response, mimetype="text/xml")

    if caller.age_bracket is None:
        age_map = {"1": "18-25", "2": "26-35", "3": "36+"}
        caller.age_bracket = age_map.get(digits, "26-35")
        caller.status = "queued"
        db.session.commit()

        from app.services.bridge import enqueue, dequeue, queue_name_for

        match = try_match(caller)
        queue_name = queue_name_for(caller.intent, caller.language)

        if match:
            # Someone was already waiting - pull them out of hold and bridge live
            response = xml(
                say("A match has been found. Connecting you now."),
                dequeue(match.phone_number, queue_name)
            )
        else:
            # Nobody waiting yet - go on hold ourselves until someone matches us
            response = xml(
                say("Please hold while we find someone for you."),
                enqueue(current_app.config["HOLD_MUSIC_URL"], queue_name)
            )
        return Response(response, mimetype="text/xml")

    response = xml(say("You are already in the queue."))
    return Response(response, mimetype="text/xml")