import os
import uuid
from datetime import datetime

from flask import Blueprint, current_app, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename
from extensions import db
from models import (
    CampusCategory,
    CampusLocation,
    Report,
    Claim,
    ClaimTransaction,
    ClaimTransactionReversal,
    AuditLog,
    User,
)
from notification_service import create_notification, email_notification

moderator_bp = Blueprint("moderator", __name__)

@moderator_bp.before_request
@login_required
def protect():
    if current_user.role not in ("moderator", "admin"):
        return redirect(url_for("auth.login"))

@moderator_bp.route("/")
@moderator_bp.route("/queue")
def queue():
    reports = Report.query.filter_by(status="Awaiting review").order_by(Report.created_at.asc()).all()
    claims = Claim.query.filter(
        Claim.status.in_(("Under review", "More proof requested"))
    ).order_by(Claim.created_at.asc()).all()
    return render_template("moderator/queue.html", reports=reports, claims=claims)

@moderator_bp.route("/items", methods=["GET", "POST"])
def items():
    if request.method == "POST":
        report_type = request.form.get("report_type", "")
        owner_id = request.form.get("owner_id", type=int)
        item_name = request.form.get("item_name", "").strip()
        category = request.form.get("category", "").strip()
        item_type = request.form.get("item_type", "").strip()
        color = request.form.get("color", "").strip()
        campus_location = request.form.get("campus_location", "").strip()
        description = request.form.get("description", "").strip()
        owner = User.query.filter_by(id=owner_id, role="user", status="Active").first()
        if report_type not in ("Lost", "Found") or owner is None:
            flash("Choose a valid report type and active student owner.", "error")
        elif not item_name or len(item_name) > 120 or len(category) > 80:
            flash("Enter an item name and a valid category.", "error")
        elif not CampusCategory.query.filter_by(name=category, is_active=True).first():
            flash("Choose an active category.", "error")
        elif not CampusLocation.query.filter_by(name=campus_location, is_active=True).first():
            flash("Choose an active campus location.", "error")
        elif not description:
            flash("Add a short description for the report.", "error")
        else:
            try:
                event_date = datetime.strptime(request.form.get("event_date", ""), "%Y-%m-%d").date()
            except ValueError:
                event_date = None
            if event_date is None:
                flash("Enter a valid report date.", "error")
            else:
                photo = request.files.get("photo")
                filename = None
                if photo and photo.filename:
                    extension = os.path.splitext(secure_filename(photo.filename))[1].lower()
                    if extension not in (".jpg", ".jpeg", ".png", ".webp"):
                        flash("Upload JPG, PNG, or WEBP images only.", "error")
                        return redirect(url_for("moderator.items"))
                    try:
                        image = Image.open(photo.stream)
                        if image.format not in ("JPEG", "PNG", "WEBP") or image.width * image.height > 25_000_000:
                            raise ValueError("Unsupported image format or dimensions.")
                        image.verify()
                        photo.stream.seek(0)
                    except (UnidentifiedImageError, OSError, ValueError):
                        flash("The uploaded file is not a valid JPG, PNG, or WEBP image under 25 megapixels.", "error")
                        return redirect(url_for("moderator.items"))
                    filename = f"{uuid.uuid4().hex}{extension}"
                    photo.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))

                prefix = "L" if report_type == "Lost" else "F"
                report_code = f"{prefix}-{datetime.now().year}-{uuid.uuid4().hex[:6].upper()}"
                report = Report(
                    report_code=report_code,
                    report_type=report_type,
                    item_name=item_name,
                    category=category,
                    item_type=item_type[:100],
                    color=color[:60],
                    description=description,
                    campus_location=campus_location,
                    event_date=event_date,
                    photo_filename=filename,
                    status="Verified report",
                    user_id=owner.id,
                )
                db.session.add(report)
                db.session.flush()
                create_notification(
                    owner,
                    "Report added by authorized personnel",
                    f"A {report_type.lower()} report for {item_name} was added to FindBack on your behalf.",
                    f"/student/item/{report.id}",
                )
                db.session.add(AuditLog(
                    actor_id=current_user.id,
                    action=f"Created {report_type.lower()} report {report_code} for user #{owner.id}",
                ))
                db.session.commit()
                flash(f"{report_type} item {report_code} was added to the campus board.", "success")
                return redirect(url_for("moderator.items"))

    claims_by_report = {}
    for claim in Claim.query.filter(
        Claim.status.in_(("Under review", "More proof requested"))
    ).order_by(Claim.created_at.desc()).all():
        claims_by_report.setdefault(claim.report_id, []).append(claim)
    return render_template(
        "moderator/items.html",
        reports=Report.query.order_by(Report.created_at.desc()).limit(200).all(),
        owners=User.query.filter_by(role="user", status="Active").order_by(User.full_name).all(),
        categories=CampusCategory.query.filter_by(is_active=True).order_by(CampusCategory.name).all(),
        locations=CampusLocation.query.filter_by(is_active=True).order_by(CampusLocation.name).all(),
        claims_by_report=claims_by_report,
    )


def create_claim_transaction(report, claim):
    owner = report.reporter
    claimant = claim.claimant
    transaction = ClaimTransaction(
        claim_id=claim.id,
        claim_code=claim.claim_code,
        report_id=report.id,
        report_code=report.report_code,
        report_type=report.report_type,
        item_name=report.item_name,
        category=report.category,
        color=report.color,
        item_type=report.item_type,
        description=report.description,
        campus_location=report.campus_location,
        event_date=report.event_date,
        photo_filename=report.photo_filename,
        owner_id=owner.id,
        owner_name=owner.full_name,
        owner_email=owner.email,
        owner_affiliation=owner.affiliation,
        claimant_id=claimant.id,
        claimant_name=claimant.full_name,
        claimant_email=claimant.email,
        claimant_affiliation=claimant.affiliation,
        identifying_details=claim.identifying_details,
        last_used_details=claim.last_used_details,
        handover_location="SSG Office",
        approved_by_id=current_user.id,
    )
    db.session.add(transaction)
    return transaction


def notify_completed_handover(report, claim):
    owner = report.reporter
    claimant = claim.claimant
    create_notification(
        owner,
        "Item handover completed",
        f"Claim {claim.claim_code} for {report.item_name} was verified. "
        "The report is marked Already claimed and the transaction was recorded.",
        f"/student/item/{report.id}",
    )
    if claimant.id != owner.id:
        create_notification(
            claimant,
            "Item handover completed",
            f"Your claim for {report.item_name} was verified by "
            f"{current_user.full_name}; the handover was recorded at the SSG Office.",
            "/student/recovery",
        )


@moderator_bp.route("/items/<int:report_id>/claimed", methods=["POST"])
def mark_claimed(report_id):
    report = Report.query.get_or_404(report_id)
    if report.status != "Verified report":
        flash("Only a verified, unclaimed report can be marked claimed.", "error")
        return redirect(url_for("moderator.items"))

    selected_claim_id = request.form.get("claim_id", type=int)
    claim = None
    if selected_claim_id:
        claim = Claim.query.filter(
            Claim.id == selected_claim_id,
            Claim.report_id == report.id,
            Claim.status.in_(("Under review", "More proof requested")),
        ).first()
        if claim is None:
            flash("Choose a current claim for this report.", "error")
            return redirect(url_for("moderator.items"))
        claimant = claim.claimant
    else:
        claimant_id = request.form.get("claimant_id", type=int)
        claimant = User.query.filter_by(id=claimant_id, role="user", status="Active").first()
        identifying_details = request.form.get("identifying_details", "").strip()
        last_used_details = request.form.get("last_used_details", "").strip()
        invalid_claimant = (
            claimant is None
            or (report.report_type == "Found" and claimant.id == report.user_id)
            or (report.report_type == "Lost" and claimant.id != report.user_id)
        )
        if invalid_claimant:
            flash("Choose the original reporter for a Lost item, or a different active student for a Found item.", "error")
            return redirect(url_for("moderator.items"))
        if not identifying_details or not last_used_details:
            flash("Record both ownership details verified at the handover.", "error")
            return redirect(url_for("moderator.items"))
        claim = Claim(
            claim_code=f"C-{datetime.now().year}-{uuid.uuid4().hex[:6].upper()}",
            report_id=report.id,
            claimant_id=claimant.id,
            identifying_details=identifying_details,
            last_used_details=last_used_details,
            status="Ownership verified",
        )
        db.session.add(claim)
        db.session.flush()
    claim.status = "Ownership verified"

    report.status = "Recovered"
    create_claim_transaction(report, claim)
    notify_completed_handover(report, claim)
    db.session.add(AuditLog(
        actor_id=current_user.id,
        action=f"Marked report {report.report_code} claimed by user #{claimant.id}",
    ))
    db.session.commit()
    email_notification(report.reporter, "OMSU FindBack item claimed", f"{report.item_name} was verified and recorded as claimed at the SSG Office.")
    if claimant.id != report.user_id:
        email_notification(claimant, "OMSU FindBack claim verified", f"Your claim for {report.item_name} was verified by authorized personnel.")
    flash(f"{report.item_name} is now marked already claimed.", "success")
    return redirect(url_for("moderator.items"))


@moderator_bp.route("/items/<int:report_id>/undo-claimed", methods=["POST"])
def undo_claim(report_id):
    report = Report.query.get_or_404(report_id)
    if report.status != "Recovered":
        flash("This report is not currently marked claimed.", "error")
        return redirect(url_for("moderator.items"))
    reason = request.form.get("reason", "").strip()
    if not reason:
        flash("Enter a reason for reopening this item.", "error")
        return redirect(url_for("moderator.items"))

    transaction = ClaimTransaction.query.filter_by(report_id=report.id).order_by(
        ClaimTransaction.completed_at.desc()
    ).first()
    if transaction is None:
        flash("No claim transaction was found; item status was not changed.", "error")
        return redirect(url_for("moderator.items"))

    report.status = "Verified report"
    transaction.claim.status = "Reversed"
    db.session.add(ClaimTransactionReversal(
        transaction_id=transaction.id,
        reversed_by_id=current_user.id,
        reason=reason,
    ))
    create_notification(
        transaction.owner,
        "Claim status reversed",
        f"The claim for {transaction.item_name} was reversed by authorized personnel. "
        "The item is available again on the lost-and-found board.",
        f"/student/item/{report.id}",
    )
    if transaction.claimant_id != transaction.owner_id:
        create_notification(
            transaction.claimant,
            "Claim status reversed",
            f"Your claim for {transaction.item_name} was reopened by authorized personnel. "
            f"Reason: {reason}",
            "/student/recovery",
        )
    db.session.add(AuditLog(
        actor_id=current_user.id,
        action=f"Reopened claimed report {report.report_code}: {reason}",
    ))
    db.session.commit()
    flash(f"{report.item_name} is unclaimed and visible on the campus board again.", "success")
    return redirect(url_for("moderator.items"))

@moderator_bp.route("/report/<int:report_id>/<action>", methods=["POST"])
def review_report(report_id, action):
    report = Report.query.get_or_404(report_id)
    if action == "approve":
        report.status = "Verified report"
        log_action = f"Approved report {report.report_code}"
    elif action == "reject":
        report.status = "Rejected"
        log_action = f"Rejected report {report.report_code}"
    else:
        return redirect(url_for("moderator.queue"))
    match_pairs = []
    if action == "approve":
        from ai_engine.matching import match_reports
        from notification_service import notify_possible_matches

        if report.report_type == "Lost":
            lost_reports = [report]
            found_reports = (
                Report.query.filter_by(report_type="Found", status="Verified report")
                .order_by(Report.created_at.desc())
                .limit(100)
                .all()
            )
        else:
            lost_reports = (
                Report.query.filter_by(report_type="Lost", status="Verified report")
                .order_by(Report.created_at.desc())
                .limit(100)
                .all()
            )
            found_reports = [report]
        match_pairs = match_reports(
            lost_reports,
            found_reports,
            current_app.config["UPLOAD_FOLDER"],
            current_app.config["AI_MODEL_PATH"],
            current_app.logger,
        )
        notify_possible_matches(match_pairs)
    create_notification(
        report.reporter,
        "Report status updated",
        f"Your report {report.report_code} was {report.status.lower()}.",
        "/student/reports",
    )
    db.session.add(AuditLog(actor_id=current_user.id, action=log_action))
    db.session.commit()
    email_notification(
        report.reporter,
        "OMSU FindBack report update",
        f"Your report {report.report_code} was {report.status.lower()}.",
    )
    flash(f"{report.report_code} updated.", "success")
    return redirect(url_for("moderator.queue"))

@moderator_bp.route("/claim/<int:claim_id>/<action>", methods=["POST"])
def review_claim(claim_id, action):
    claim = Claim.query.get_or_404(claim_id)
    if action == "approve":
        existing_transaction = ClaimTransaction.query.filter_by(claim_id=claim.id).first()
        if existing_transaction:
            flash("This claim already has a completed handover record.", "info")
            return redirect(url_for("moderator.queue"))
        claim.status = "Ownership verified"
        claim.report.status = "Recovered"
        owner = claim.report.reporter
        claimant = claim.claimant
        transaction = ClaimTransaction(
            claim_id=claim.id,
            claim_code=claim.claim_code,
            report_id=claim.report.id,
            report_code=claim.report.report_code,
            report_type=claim.report.report_type,
            item_name=claim.report.item_name,
            category=claim.report.category,
            color=claim.report.color,
            item_type=claim.report.item_type,
            description=claim.report.description,
            campus_location=claim.report.campus_location,
            event_date=claim.report.event_date,
            photo_filename=claim.report.photo_filename,
            owner_id=owner.id,
            owner_name=owner.full_name,
            owner_email=owner.email,
            owner_affiliation=owner.affiliation,
            claimant_id=claimant.id,
            claimant_name=claimant.full_name,
            claimant_email=claimant.email,
            claimant_affiliation=claimant.affiliation,
            identifying_details=claim.identifying_details,
            last_used_details=claim.last_used_details,
            handover_location="SSG Office",
            approved_by_id=current_user.id,
        )
        db.session.add(transaction)
        create_notification(
            owner,
            "Item handover completed",
            f"Claim {claim.claim_code} for {claim.report.item_name} was verified. "
            "The report is marked Already claimed and the transaction was recorded.",
            f"/student/item/{claim.report.id}",
        )
        create_notification(
            claimant,
            "Item handover completed",
            f"Your claim for {claim.report.item_name} was verified by "
            f"{current_user.full_name}; the handover was recorded at the SSG Office.",
            "/student/recovery",
        )
    elif action == "more":
        claim.status = "More proof requested"
    elif action == "reject":
        claim.status = "Rejected"
    else:
        return redirect(url_for("moderator.queue"))
    create_notification(
        claim.claimant,
        "Claim status updated",
        f"Your claim {claim.claim_code} is now {claim.status.lower()}.",
        "/student/recovery",
    )
    audit_action = (
        f"Completed SSG Office handover for claim {claim.claim_code}"
        if action == "approve"
        else f"{action.title()} claim {claim.claim_code}"
    )
    db.session.add(AuditLog(actor_id=current_user.id, action=audit_action))
    db.session.commit()
    email_notification(
        claim.claimant,
        "OMSU FindBack claim update",
        f"Your claim {claim.claim_code} is now {claim.status.lower()}.",
    )
    flash("Claim review saved.", "success")
    return redirect(url_for("moderator.queue"))
