import os
from flask import Blueprint, Response, request, current_app
from app.models.db import db
from app.models.caller import Caller
from app.services.matching import try_match

voice_bp = Blueprint("voice", __name__)

QUEUE_NAME = "semamatch"


def say(text):
    return f'<Say voice="woman">{text}</Say>'


def callback_base():
    return (os.environ.get("PUBLIC_BASE_URL") or request.url_root).rstrip("/")


def get_digits(prompt, num_digits=1):
    callback = callback_base() + "/voice/incoming"
    return (
        f'<GetDigits timeout="10" numDigits="{num_digits}" callbackUrl="{callback}">'
        f'{say(prompt)}'
        f'</GetDigits>'
    )


def enqueue():
    hold_music = os.environ.get("AT_HOLD_MUSIC_URL")
    hold = f' holdMusic="{hold_music}"' if hold_music else ""
    return f'<Enqueue name="{QUEUE_NAME}"{hold}/>'


def dequeue():
    at_number = current_app.config.get("AT_VOICE_NUMBER", "")
    return f'<Dequeue phoneNumber="{at_number}" name="{QUEUE_NAME}"/>'


def xml(*blocks):
    body = "\n".join(blocks)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<Response>\n{body}\n</Response>'


@voice_bp.route("/voice/incoming", methods=["POST"])
def incoming_call():
    session_id = request.values.get("sessionId")
    phone_number = request.values.get("callerNumber") or request.values.get("phoneNumber")
    digits = request.values.get("dtmfDigits", "").strip()

    caller = Caller.query.get(session_id)

    if caller is None:
        caller = Caller(session_id=session_id, phone_number=phone_number)
        db.session.add(caller)
        db.session.commit()
        return Response(
            xml(get_digits(
                "Welcome to Sema Match. Press 1 for English. Press 2 for Kiswahili."
            )),
            mimetype="text/xml",
        )

    if caller.language is None:
        caller.language = "english" if digits == "1" else "kiswahili"
        db.session.commit()
        return Response(
            xml(get_digits(
                "Press 1 for a serious relationship. Press 2 for friendship. "
                "Press 3 for casual chat."
            )),
            mimetype="text/xml",
        )

    if caller.intent is None:
        intent_map = {"1": "serious", "2": "friendship", "3": "casual"}
        caller.intent = intent_map.get(digits, "casual")
        db.session.commit()
        return Response(
            xml(get_digits(
                "Press 1 for ages 18 to 25. Press 2 for 26 to 35. "
                "Press 3 for 36 and above."
            )),
            mimetype="text/xml",
        )

    if caller.age_bracket is None:
        age_map = {"1": "18-25", "2": "26-35", "3": "36+"}
        caller.age_bracket = age_map.get(digits, "26-35")
        caller.status = "queued"
        db.session.commit()

        match = try_match(caller)

        if match:
            response = xml(
                say("A match has been found. Connecting you now."),
                dequeue()
            )
        else:
            response = xml(
                say(
                    "Thank you. You have been added to the matching queue. "
                    "Please hold while we find someone for you."
                ),
                enqueue()
            )
        return Response(response, mimetype="text/xml")

    return Response(xml(say("You are already in the queue.")), mimetype="text/xml")