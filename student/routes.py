import os, uuid
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename
from extensions import db, limiter
from models import AIRecognitionEvent, CampusCategory, CampusLocation, Conversation, Report, Claim, User
from notification_service import create_notification, email_notification

student_bp = Blueprint("student", __name__)

def user_required():
    return current_user.role == "user"

@student_bp.before_request
@login_required
def protect_student():
    if not user_required():
        return redirect(url_for("auth.login"))

@student_bp.route("/")
@student_bp.route("/dashboard")
def dashboard():
    reports = Report.query.filter(
        Report.status.notin_(("Recovered", "Rejected"))
    ).order_by(Report.created_at.desc()).limit(12).all()
    mine = Report.query.filter_by(user_id=current_user.id).count()
    return render_template("student/dashboard.html", reports=reports, mine=mine)

@student_bp.route("/reports")
def my_reports():
    reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.created_at.desc()).all()
    return render_template("student/my_reports.html", reports=reports)

@student_bp.route("/report/<kind>", methods=["GET", "POST"])
def create_report(kind):
    if kind not in ("lost", "found"):
        return redirect(url_for("student.dashboard"))
    if request.method == "POST":
        required = ["item_name", "category", "description", "campus_location", "event_date"]
        if any(not request.form.get(k, "").strip() for k in required):
            flash("Please complete all required fields.", "error")
            return redirect(request.url)
        try:
            event_date = datetime.strptime(
                request.form["event_date"], "%Y-%m-%d"
            ).date()
        except ValueError:
            flash("Enter a valid event date.", "error")
            return redirect(request.url)
        category = request.form["category"].strip()
        location = request.form["campus_location"].strip()
        if not CampusCategory.query.filter_by(name=category, is_active=True).first():
            flash("Choose an active category from the list.", "error")
            return redirect(request.url)
        if not CampusLocation.query.filter_by(name=location, is_active=True).first():
            flash("Choose an active campus location from the list.", "error")
            return redirect(request.url)
        photo = request.files.get("photo")
        filename = None
        if photo and photo.filename:
            ext = os.path.splitext(secure_filename(photo.filename))[1].lower()
            if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
                flash("Upload JPG, PNG, or WEBP images only.", "error")
                return redirect(request.url)
            try:
                image = Image.open(photo.stream)
                if image.format not in ("JPEG", "PNG", "WEBP"):
                    raise UnidentifiedImageError
                if image.width * image.height > 25_000_000:
                    raise ValueError("Image dimensions exceed the safety limit.")
                ext = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}[image.format]
                image.verify()
            except (UnidentifiedImageError, OSError, ValueError):
                flash("The uploaded file is not a valid JPG, PNG, or WEBP image.", "error")
                return redirect(request.url)
            photo.stream.seek(0)
            filename = f"{uuid.uuid4().hex}{ext}"
            photo.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
        prefix = "L" if kind == "lost" else "F"
        code = f"{prefix}-{datetime.now().year}-{uuid.uuid4().hex[:6].upper()}"
        report = Report(
            report_code=code, report_type=kind.title(),
            item_name=request.form["item_name"].strip(),
            category=category,
            color=request.form.get("color", "").strip(),
            item_type=request.form.get("item_type", "").strip(),
            description=request.form["description"].strip(),
            campus_location=location,
            event_date=event_date,
            photo_filename=filename, user_id=current_user.id
        )
        db.session.add(report)
        staff = User.query.filter(
            User.role.in_(("moderator", "admin")),
            User.status == "Active",
        ).all()
        for recipient in staff:
            create_notification(
                recipient,
                "New report awaiting review",
                f"{report.report_code} is ready for moderator review.",
                "/moderator/queue",
            )
        db.session.commit()
        for recipient in staff:
            email_notification(
                recipient,
                "New OMSU FindBack report",
                f"{report.report_code} is ready for moderator review.",
            )
        flash(f"Report {code} submitted and is awaiting moderator review.", "success")
        return redirect(url_for("student.my_reports"))
    return render_template(
        "student/report_form.html",
        kind=kind.title(),
        categories=CampusCategory.query.filter_by(is_active=True).order_by(CampusCategory.name).all(),
        locations=CampusLocation.query.filter_by(is_active=True).order_by(CampusLocation.name).all(),
    )

@student_bp.route("/ai/suggest", methods=["POST"])
@limiter.limit("10 per minute")
def suggest_photo_details():
    photo = request.files.get("photo")
    if not photo or not photo.filename:
        return jsonify(error="Choose an image to analyze."), 400
    try:
        image = Image.open(photo.stream)
        if image.format not in ("JPEG", "PNG", "WEBP"):
            return jsonify(error="Use a JPG, PNG, or WEBP image."), 400
        if image.width * image.height > 25_000_000:
            return jsonify(error="The image exceeds the 25-megapixel limit."), 400
        image.verify()
        photo.stream.seek(0)
        image = Image.open(photo.stream).convert("RGB")
    except (UnidentifiedImageError, OSError, ValueError):
        return jsonify(error="The uploaded file is not a valid image."), 400

    try:
        from ai_engine.image_detection import suggest_details
    except ModuleNotFoundError:
        current_app.logger.exception("The local AI model dependencies are unavailable.")
        return jsonify(error="Install the project requirements before using image recognition."), 503

    result = suggest_details(image, current_app.config["AI_MODEL_PATH"])
    detection = result["detections"][0] if result["detections"] else None
    db.session.add(AIRecognitionEvent(
        user_id=current_user.id,
        class_label=detection["label"] if detection else "No object detected",
        suggested_category=detection["category"] if detection else "None",
        confidence=detection["confidence"] if detection else 0.0,
    ))
    db.session.commit()
    active_categories = {
        category.name
        for category in CampusCategory.query.filter_by(is_active=True).all()
    }
    if result["category"] and result["category"] not in active_categories:
        result["category"] = "Other items" if "Other items" in active_categories else ""
    return jsonify(result)

@student_bp.route("/matches")
def matches():
    from ai_engine.matching import match_reports
    from notification_service import notify_possible_matches

    lost_query = Report.query.filter_by(
        user_id=current_user.id,
        report_type="Lost",
        status="Verified report",
    )
    lost_report_id = request.args.get("lost_report_id", type=int)
    found_report_id = request.args.get("found_report_id", type=int)
    if lost_report_id:
        lost_query = lost_query.filter_by(id=lost_report_id)
    found_query = Report.query.filter_by(
        report_type="Found",
        status="Verified report",
    )
    if found_report_id:
        found_query = found_query.filter_by(id=found_report_id)
    found = found_query.order_by(Report.created_at.desc()).limit(100).all()
    lost = lost_query.order_by(Report.created_at.desc()).limit(100).all()
    pairs = match_reports(
        lost,
        found,
        current_app.config["UPLOAD_FOLDER"],
        current_app.config["AI_MODEL_PATH"],
        current_app.logger,
    )
    notify_possible_matches(pairs)
    if pairs:
        db.session.commit()
    return render_template("student/matches.html", pairs=pairs)

@student_bp.route("/item/<int:report_id>")
def item_detail(report_id):
    report = Report.query.get_or_404(report_id)
    return render_template("student/item_detail.html", report=report)

@student_bp.route("/claim/<int:report_id>", methods=["GET", "POST"])
def claim(report_id):
    report = Report.query.get_or_404(report_id)
    if (
        report.report_type != "Found"
        or report.status != "Verified report"
        or report.user_id == current_user.id
    ):
        return redirect(url_for("student.dashboard"))
    if request.method == "POST":
        details = request.form.get("identifying_details", "").strip()
        last_used = request.form.get("last_used_details", "").strip()
        if not details or not last_used or not request.form.get("confirm"):
            flash("Complete both answers and confirm your claim.", "error")
        else:
            existing_claim = Claim.query.filter_by(
                report_id=report.id,
                claimant_id=current_user.id,
            ).filter(Claim.status.in_(("Under review", "More proof requested", "Ownership verified"))).first()
            if existing_claim:
                if existing_claim.conversation is None:
                    existing_claim.conversation = Conversation()
                    db.session.commit()
                return redirect(url_for(
                    "student.recovery",
                ))
            code = f"C-{datetime.now().year}-{uuid.uuid4().hex[:6].upper()}"
            claim = Claim(
                claim_code=code,
                report_id=report.id,
                claimant_id=current_user.id,
                identifying_details=details,
                last_used_details=last_used,
            )
            conversation = Conversation(claim=claim)
            db.session.add_all([claim, conversation])
            db.session.flush()
            create_notification(
                report.reporter,
                "Claim submitted - bring item to SSG Office",
                f"{current_user.full_name} submitted a claim for {report.item_name}. "
                "Please bring the item to the SSG Office so a moderator or administrator "
                "can verify the handover with the claimant.",
                f"/student/item/{report.id}",
            )
            create_notification(
                current_user,
                "Claim submitted - meet at SSG Office",
                f"Your claim for {report.item_name} was submitted. Coordinate with the "
                "item owner at the SSG Office. A moderator or administrator must verify "
                "the handover before the item is marked claimed.",
                "/student/recovery",
            )
            staff = User.query.filter(
                User.role.in_(("moderator", "admin")),
                User.status == "Active",
            ).all()
            for recipient in staff:
                create_notification(
                    recipient,
                    "New ownership claim to review",
                    f"Claim {claim.claim_code} for {report.item_name} is ready for moderator review.",
                    "/moderator/queue",
                )
            db.session.commit()
            email_notification(
                report.reporter,
                "New OMSU FindBack claim",
                f"{current_user.full_name} submitted an ownership claim for {report.item_name}. "
                "Sign in to review and message them.",
            )
            for recipient in staff:
                email_notification(
                    recipient,
                    "New OMSU FindBack ownership claim",
                    f"Claim {claim.claim_code} for {report.item_name} is ready for review.",
                )
            flash("Private claim submitted for moderator verification.", "success")
            return redirect(url_for("student.recovery"))
    return render_template("student/claim.html", report=report)

@student_bp.route("/recovery")
def recovery():
    claims = Claim.query.filter_by(claimant_id=current_user.id).order_by(Claim.created_at.desc()).all()
    return render_template("student/recovery.html", claims=claims)
