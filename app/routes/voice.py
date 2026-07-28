from flask import Blueprint, Response

voice_bp = Blueprint("voice", __name__)


@voice_bp.route("/voice/incoming", methods=["POST"])
def incoming_call():
    xml_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="woman">Welcome to Sema Match. This flow is under construction.</Say>
</Response>"""
    return Response(xml_response, mimetype="text/xml")