from datetime import datetime, timedelta
from flask import Blueprint, abort, render_template, request
from flask_login import current_user, login_required
from flask_socketio import emit, join_room
from sqlalchemy import or_

from extensions import db, socketio
from models import Claim, Conversation, Message, Report, User
from notification_service import create_notification, email_notification

messages_bp = Blueprint("messages", __name__)


def can_access_conversation(user, conversation):
    if not user.is_authenticated or user.status != "Active":
        return False
    if user.role in ("admin", "moderator"):
        return True
    claim = conversation.claim
    return user.id in (claim.claimant_id, claim.report.user_id)


def conversation_room(conversation_id):
    return f"conversation:{conversation_id}"


def message_payload(message):
    return {
        "id": message.id,
        "sender_id": message.sender_id,
        "sender_name": message.sender.full_name,
        "body": message.body,
        "created_at": message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    }


def message_recipients(conversation, sender):
    claim = conversation.claim
    participants = (claim.report.reporter, claim.claimant)
    return [person for person in participants if person.id != sender.id]

def active_socket_user():
    if not current_user.is_authenticated:
        return None
    try:
        user_id = int(current_user.get_id())
    except (TypeError, ValueError):
        return None
    user = db.session.get(User, user_id)
    return user if user and user.status == "Active" else None


@messages_bp.route("/")
@login_required
def inbox():
    if current_user.role in ("admin", "moderator"):
        conversations = Conversation.query.order_by(Conversation.created_at.desc()).all()
    else:
        conversations = (
            Conversation.query.join(Claim)
            .join(Report)
            .filter(or_(
                Claim.claimant_id == current_user.id,
                Report.user_id == current_user.id,
            ))
            .order_by(Conversation.created_at.desc())
            .all()
        )
    return render_template("messages/inbox.html", conversations=conversations)


@messages_bp.route("/<int:conversation_id>")
@login_required
def thread(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    if not can_access_conversation(current_user, conversation):
        abort(403)
    messages = Message.query.filter_by(conversation_id=conversation.id).order_by(
        Message.created_at.desc()
    ).limit(100).all()
    messages.reverse()
    return render_template(
        "messages/thread.html",
        conversation=conversation,
        messages=messages,
        report=conversation.claim.report,
    )


@messages_bp.route("/<int:conversation_id>/history")
@login_required
def history(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    if not can_access_conversation(current_user, conversation):
        abort(403)
    after_id = request.args.get("after", 0, type=int)
    messages = Message.query.filter(
        Message.conversation_id == conversation.id,
        Message.id > after_id,
    ).order_by(Message.id.asc()).limit(100).all()
    return {"messages": [message_payload(message) for message in messages]}


@socketio.on("join_conversation")
def join_conversation(data):
    user = active_socket_user()
    if user is None:
        emit("chat_error", {"message": "Sign in with an active account to chat."})
        return
    conversation_id = data.get("conversation_id") if isinstance(data, dict) else None
    if type(conversation_id) is not int:
        emit("chat_error", {"message": "Invalid conversation."})
        return
    conversation = db.session.get(Conversation, conversation_id)
    if not conversation or not can_access_conversation(user, conversation):
        emit("chat_error", {"message": "You are not allowed to access this conversation."})
        return
    join_room(conversation_room(conversation.id))
    emit("chat_joined", {"conversation_id": conversation.id})


@socketio.on("send_message")
def send_message(data):
    user = active_socket_user()
    if user is None:
        emit("chat_error", {"message": "Sign in with an active account to chat."})
        return
    conversation_id = data.get("conversation_id") if isinstance(data, dict) else None
    body_value = data.get("body", "") if isinstance(data, dict) else ""
    body = body_value.strip() if isinstance(body_value, str) else ""
    if type(conversation_id) is not int or not body or len(body) > 2000:
        emit("chat_error", {"message": "Messages must contain 1 to 2000 characters."})
        return
    conversation = db.session.get(Conversation, conversation_id)
    if not conversation or not can_access_conversation(user, conversation):
        emit("chat_error", {"message": "You are not allowed to send messages here."})
        return
    recent_count = Message.query.filter(
        Message.sender_id == user.id,
        Message.created_at >= datetime.utcnow() - timedelta(minutes=1),
    ).count()
    if recent_count >= 30:
        emit("chat_error", {"message": "Message limit reached. Please wait a minute and try again."})
        return

    message = Message(
        conversation_id=conversation.id,
        sender_id=user.id,
        body=body,
    )
    db.session.add(message)
    recipients = message_recipients(conversation, current_user)
    if user.role == "user":
        staff_recipients = User.query.filter(
            User.role.in_(("moderator", "admin")),
            User.status == "Active",
        ).all()
        recipient_ids = {recipient.id for recipient in recipients}
        recipients.extend(
            recipient for recipient in staff_recipients
            if recipient.id not in recipient_ids
        )
    for recipient in recipients:
        create_notification(
            recipient,
            "New private message",
            f"{user.full_name} sent a message about {conversation.claim.report.item_name}.",
            f"/messages/{conversation.id}",
        )
    db.session.commit()
    for recipient in recipients:
        email_notification(
            recipient,
            "New OMSU FindBack message",
            f"{user.full_name} sent you a private message about "
            f"{conversation.claim.report.item_name}. Sign in to reply.",
        )
    emit(
        "new_message",
        message_payload(message),
        room=conversation_room(conversation.id),
    )
