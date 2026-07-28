from datetime import datetime
from app.models.db import db


class Caller(db.Model):
    __tablename__ = "callers"

    session_id = db.Column(db.String(64), primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False)

    language = db.Column(db.String(20))
    intent = db.Column(db.String(20))       # serious | friendship | casual
    age_bracket = db.Column(db.String(10))  # 18-25 | 26-35 | 36+

    status = db.Column(db.String(20), default="collecting", nullable=False)
    match_session_id = db.Column(db.String(64), nullable=True)
    wants_reconnect = db.Column(db.Boolean, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "phone_number": self.phone_number,
            "language": self.language,
            "intent": self.intent,
            "age_bracket": self.age_bracket,
            "status": self.status,
            "match_session_id": self.match_session_id,
            "wants_reconnect": self.wants_reconnect,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }