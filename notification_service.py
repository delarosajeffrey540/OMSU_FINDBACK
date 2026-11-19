import logging
import smtplib
import ssl
from email.message import EmailMessage

from flask import current_app

from extensions import db
from models import Notification

logger = logging.getLogger(__name__)


def create_notification(recipient, title, body, target_url=None):
    notification = Notification(
        recipient_id=recipient.id,
        title=title,
        body=body,
        target_url=target_url,
    )
    db.session.add(notification)
    return notification


def notify_possible_matches(pairs):
    title = "Possible item match found"
    notified_pairs = set()
    for lost_report, found_report, score, visual_similarity in pairs:
        recipient = lost_report.reporter
        target_url = (
            f"/student/matches?lost_report_id={lost_report.id}"
            f"&found_report_id={found_report.id}"
        )
        pair_key = (recipient.id, lost_report.id, found_report.id)
        if pair_key in notified_pairs:
            continue
        notified_pairs.add(pair_key)
        if Notification.query.filter_by(
            recipient_id=recipient.id,
            title=title,
            target_url=target_url,
        ).first():
            continue

        photo_note = (
            f" Photo similarity: {visual_similarity}%."
            if visual_similarity is not None else ""
        )
        create_notification(
            recipient,
            title,
            f"Your lost report {lost_report.report_code} may match "
            f"{found_report.item_name} ({found_report.report_code}), with a "
            f"{score}% match score.{photo_note} Review the suggestion; it is not proof of ownership.",
            target_url,
        )


def email_notification(recipient, subject, body):
    host = current_app.config.get("SMTP_HOST")
    sender = current_app.config.get("SMTP_SENDER")
    if not host or not sender:
        return

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = recipient.email
    message.set_content(body)

    port = current_app.config["SMTP_PORT"]
    username = current_app.config.get("SMTP_USER")
    password = current_app.config.get("SMTP_PASSWORD")
    try:
        with smtplib.SMTP(host, port, timeout=15) as server:
            server.starttls(context=ssl.create_default_context())
            if username:
                server.login(username, password)
            server.send_message(message)
    except (OSError, smtplib.SMTPException):
        logger.exception("Could not send an email notification to user %s.", recipient.id)
