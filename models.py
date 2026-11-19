from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    affiliation = db.Column(db.String(40), nullable=False, default="Student")
    role = db.Column(db.String(20), nullable=False, default="user")  # user, moderator, admin
    status = db.Column(db.String(20), nullable=False, default="Active")
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reports = db.relationship("Report", backref="reporter", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    report_type = db.Column(db.String(10), nullable=False)  # Lost / Found
    item_name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    color = db.Column(db.String(60), nullable=True)
    item_type = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=False)
    campus_location = db.Column(db.String(150), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    photo_filename = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(30), nullable=False, default="Awaiting review")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Claim(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    claim_code = db.Column(db.String(30), unique=True, nullable=False)
    report_id = db.Column(db.Integer, db.ForeignKey("report.id"), nullable=False)
    claimant_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    identifying_details = db.Column(db.Text, nullable=False)
    last_used_details = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default="Under review")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    report = db.relationship("Report", backref="claims")
    claimant = db.relationship("User")

class ClaimTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    claim_id = db.Column(db.Integer, db.ForeignKey("claim.id"), unique=True, nullable=False)
    claim_code = db.Column(db.String(30), nullable=False, index=True)
    report_id = db.Column(db.Integer, db.ForeignKey("report.id"), nullable=False)
    report_code = db.Column(db.String(30), nullable=False)
    report_type = db.Column(db.String(10), nullable=False)
    item_name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    color = db.Column(db.String(60), nullable=True)
    item_type = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=False)
    campus_location = db.Column(db.String(150), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    photo_filename = db.Column(db.String(255), nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    owner_name = db.Column(db.String(120), nullable=False)
    owner_email = db.Column(db.String(150), nullable=False)
    owner_affiliation = db.Column(db.String(40), nullable=False)
    claimant_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    claimant_name = db.Column(db.String(120), nullable=False)
    claimant_email = db.Column(db.String(150), nullable=False)
    claimant_affiliation = db.Column(db.String(40), nullable=False)
    identifying_details = db.Column(db.Text, nullable=False)
    last_used_details = db.Column(db.Text, nullable=False)
    handover_location = db.Column(db.String(120), nullable=False, default="SSG Office")
    approved_by_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    reversals = db.relationship(
        "ClaimTransactionReversal",
        back_populates="transaction",
        order_by="ClaimTransactionReversal.reversed_at.desc()",
    )
    claim = db.relationship("Claim")
    report = db.relationship("Report")
    owner = db.relationship("User", foreign_keys=[owner_id])
    claimant = db.relationship("User", foreign_keys=[claimant_id])
    approved_by = db.relationship("User", foreign_keys=[approved_by_id])

class ClaimTransactionReversal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey("claim_transaction.id"), nullable=False, index=True)
    reversed_by_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    reversed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    transaction = db.relationship("ClaimTransaction", back_populates="reversals")
    reversed_by = db.relationship("User")

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    action = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CampusCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CampusLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    claim_id = db.Column(db.Integer, db.ForeignKey("claim.id"), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    claim = db.relationship("Claim", backref=db.backref("conversation", uselist=False))
    messages = db.relationship(
        "Message", backref="conversation", lazy=True, order_by="Message.created_at"
    )

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversation.id"), nullable=False, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    body = db.Column(db.String(2000), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sender = db.relationship("User")

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    body = db.Column(db.String(500), nullable=False)
    target_url = db.Column(db.String(255), nullable=True)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    recipient = db.relationship("User")

class AIRecognitionEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    class_label = db.Column(db.String(80), nullable=False)
    suggested_category = db.Column(db.String(80), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user = db.relationship("User")
