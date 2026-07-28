from flask import Blueprint, jsonify
from app.models.caller import Caller

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def health_check():
    return jsonify({"status": "SemaMatch backend is running"})


@dashboard_bp.route("/api/callers")
def list_callers():
    callers = Caller.query.order_by(Caller.created_at.desc()).all()
    return jsonify([c.to_dict() for c in callers])