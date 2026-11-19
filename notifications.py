from flask import Blueprint, abort, redirect, render_template, url_for
from flask_login import current_user, login_required

from extensions import db
from models import Notification

notifications_bp = Blueprint("notifications", __name__, url_prefix="/notifications")


@notifications_bp.route("/")
@login_required
def index():
    notifications = Notification.query.filter_by(
        recipient_id=current_user.id
    ).order_by(Notification.created_at.desc()).limit(100).all()
    return render_template(
        "notifications/index.html",
        notifications=notifications,
    )


@notifications_bp.route("/<int:notification_id>/open", methods=["POST"])
@login_required
def open_notification(notification_id):
    notification = Notification.query.filter_by(
        id=notification_id,
        recipient_id=current_user.id,
    ).first()
    if notification is None:
        abort(404)
    notification.is_read = True
    db.session.commit()
    if (
        notification.target_url
        and notification.target_url.startswith("/")
        and not notification.target_url.startswith("//")
    ):
        return redirect(notification.target_url)
    return redirect(url_for("notifications.index"))
