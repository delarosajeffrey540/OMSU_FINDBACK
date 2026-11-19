from flask import Blueprint, abort, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from extensions import db
from models import AIRecognitionEvent, CampusCategory, CampusLocation, User, Report, Claim, ClaimTransaction, AuditLog
from datetime import date, datetime, timedelta

admin_bp = Blueprint("admin", __name__)
USER_ROLES = ("user", "moderator", "admin")
USER_STATUSES = ("Active", "Inactive")
DELETED_STATUSES = ("Deleted-Active", "Deleted-Inactive")

@admin_bp.before_request
@login_required
def protect():
    if current_user.role != "admin" or current_user.status != "Active":
        return redirect(url_for("auth.login"))

@admin_bp.route("/")
@admin_bp.route("/overview")
def overview():
    stats = {
        "reports": Report.query.count(),
        "recovered": Report.query.filter_by(status="Recovered").count(),
        "users": User.query.filter_by(status="Active").count(),
        "ai_analyses": AIRecognitionEvent.query.count(),
    }
    recent = Report.query.order_by(Report.created_at.desc()).limit(6).all()
    return render_template("admin/overview.html", stats=stats, recent=recent)

@admin_bp.route("/users")
def users():
    q = request.args.get("q", "").strip()
    query = User.query.filter(User.status.in_(USER_STATUSES))
    if q:
        query = query.filter(User.full_name.ilike(f"%{q}%") | User.email.ilike(f"%{q}%"))
    return render_template("admin/users.html", users=query.order_by(User.created_at.desc()).all())

@admin_bp.route("/users/deleted")
def deleted_users():
    users = User.query.filter(User.status.in_(DELETED_STATUSES)).order_by(User.created_at.desc()).all()
    return render_template("admin/deleted_users.html", users=users)

def active_admin_count():
    return User.query.filter_by(role="admin", status="Active").count()

def valid_user_fields(form, password_required=False):
    full_name = form.get("full_name", "").strip()
    email = form.get("email", "").strip().lower()
    affiliation = form.get("affiliation", "").strip()
    role = form.get("role", "")
    status = form.get("status", "Active")
    password = form.get("password", "")

    if not full_name or len(full_name) > 120:
        return None, "Enter a name of 1 to 120 characters."
    if not email or len(email) > 150 or "@" not in email:
        return None, "Enter a valid email address (maximum 150 characters)."
    if not affiliation or len(affiliation) > 40:
        return None, "Enter an affiliation of 1 to 40 characters."
    if role not in USER_ROLES or status not in USER_STATUSES:
        return None, "Choose a valid role and account status."
    if password_required and len(password) < 8:
        return None, "Password must be at least 8 characters."
    if password and len(password) < 8:
        return None, "Password must be at least 8 characters."

    return {
        "full_name": full_name,
        "email": email,
        "affiliation": affiliation,
        "role": role,
        "status": status,
        "password": password,
    }, None

@admin_bp.route("/users/new", methods=["GET", "POST"])
def create_user():
    if request.method == "POST":
        values, error = valid_user_fields(request.form, password_required=True)
        if error:
            flash(error, "error")
        elif User.query.filter_by(email=values["email"]).first():
            flash("An account with this email already exists.", "error")
        else:
            user = User(
                full_name=values["full_name"],
                email=values["email"],
                affiliation=values["affiliation"],
                role=values["role"],
                status=values["status"],
            )
            user.set_password(values["password"])
            db.session.add(user)
            db.session.add(AuditLog(
                actor_id=current_user.id,
                action=f"Created {user.role} account for {user.email}",
            ))
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash("An account with this email already exists.", "error")
            else:
                flash("User account created.", "success")
                return redirect(url_for("admin.users"))
    return render_template("admin/user_form.html", user=None)

@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.status in DELETED_STATUSES:
        abort(404)
    if request.method == "POST":
        values, error = valid_user_fields(request.form)
        if error:
            flash(error, "error")
        elif User.query.filter(User.email == values["email"], User.id != user.id).first():
            flash("An account with this email already exists.", "error")
        elif user.id == current_user.id and (
            values["role"] != user.role or values["status"] != user.status
        ):
            flash("You cannot change your own role or account status.", "error")
        elif (
            user.role == "admin"
            and user.status == "Active"
            and (values["role"] != "admin" or values["status"] != "Active")
            and active_admin_count() <= 1
        ):
            flash("The last active administrator cannot be demoted or deactivated.", "error")
        else:
            user.full_name = values["full_name"]
            user.email = values["email"]
            user.affiliation = values["affiliation"]
            user.role = values["role"]
            user.status = values["status"]
            if values["password"]:
                user.set_password(values["password"])
            db.session.add(AuditLog(
                actor_id=current_user.id,
                action=f"Updated account for user #{user.id}",
            ))
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash("An account with this email already exists.", "error")
            else:
                flash("User account updated.", "success")
                return redirect(url_for("admin.users"))
    return render_template("admin/user_form.html", user=user)

@admin_bp.route("/users/<int:user_id>/deactivate", methods=["POST"])
def deactivate_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot deactivate your own account.", "error")
    elif user.status != "Active":
        flash("This account is already inactive.", "error")
    elif user.role == "admin" and active_admin_count() <= 1:
        flash("The last active administrator cannot be deactivated.", "error")
    else:
        user.status = "Inactive"
        db.session.add(AuditLog(
            actor_id=current_user.id,
            action=f"Deactivated account for user #{user.id}",
        ))
        db.session.commit()
        flash("User account deactivated. Its reports and claims were kept.", "success")
    return redirect(url_for("admin.users"))

@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot delete your own account.", "error")
    elif user.status in DELETED_STATUSES:
        flash("This account is already in deleted accounts.", "error")
    elif user.role == "admin" and user.status == "Active" and active_admin_count() <= 1:
        flash("The last active administrator cannot be deleted.", "error")
    else:
        previous_status = user.status
        user.status = "Deleted-Active" if previous_status == "Active" else "Deleted-Inactive"
        db.session.add(AuditLog(
            actor_id=current_user.id,
            action=f"Moved account for user #{user.id} to deleted accounts",
        ))
        db.session.commit()
        flash("Account moved to deleted accounts. You can restore it later.", "success")
    return redirect(url_for("admin.users"))

@admin_bp.route("/users/<int:user_id>/restore", methods=["POST"])
def restore_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.status not in DELETED_STATUSES:
        flash("This account is not in deleted accounts.", "error")
    else:
        user.status = "Active" if user.status == "Deleted-Active" else "Inactive"
        db.session.add(AuditLog(
            actor_id=current_user.id,
            action=f"Restored account for user #{user.id} as {user.status}",
        ))
        db.session.commit()
        flash("Account restored. Its reports and claims are still available.", "success")
    return redirect(url_for("admin.deleted_users"))

@admin_bp.route("/users/<int:user_id>/role", methods=["POST"])
def change_role(user_id):
    user = User.query.get_or_404(user_id)
    role = request.form.get("role")
    if role not in USER_ROLES or user.id == current_user.id or user.status in DELETED_STATUSES:
        flash("Invalid role change.", "error")
    elif (
        user.role == "admin"
        and user.status == "Active"
        and role != "admin"
        and active_admin_count() <= 1
    ):
        flash("The last active administrator cannot be demoted.", "error")
    else:
        user.role = role
        db.session.add(AuditLog(actor_id=current_user.id, action=f"Changed role for user #{user.id} to {role}"))
        db.session.commit()
        flash("User role updated.", "success")
    return redirect(url_for("admin.users"))

@admin_bp.route("/records")
def records():
    reports = Report.query.order_by(Report.created_at.desc()).all()
    claims_by_report = {}
    for claim in Claim.query.filter(
        Claim.status.in_(("Under review", "More proof requested"))
    ).order_by(Claim.created_at.desc()).all():
        claims_by_report.setdefault(claim.report_id, []).append(claim)
    return render_template(
        "admin/records.html",
        reports=reports,
        owners=User.query.filter_by(role="user", status="Active").order_by(User.full_name).all(),
        claims_by_report=claims_by_report,
    )

@admin_bp.route("/claim-history")
def claim_history():
    transactions = ClaimTransaction.query.order_by(ClaimTransaction.completed_at.desc()).all()
    return render_template("admin/claim_history.html", transactions=transactions)

@admin_bp.route("/audit")
def audit():
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(100).all()
    return render_template("admin/audit.html", logs=logs)

@admin_bp.route("/catalogs", methods=["GET", "POST"])
def catalogs():
    if request.method == "POST":
        kind = request.form.get("kind", "")
        name = request.form.get("name", "").strip()
        catalog_model = {
            "category": CampusCategory,
            "location": CampusLocation,
        }.get(kind)
        limit = 80 if kind == "category" else 150
        if catalog_model is None or not name or len(name) > limit:
            flash("Enter a valid category or campus location.", "error")
        elif catalog_model.query.filter_by(name=name).first():
            flash("That entry already exists.", "error")
        else:
            db.session.add(catalog_model(name=name))
            db.session.add(AuditLog(
                actor_id=current_user.id,
                action=f"Added campus {kind}: {name}",
            ))
            db.session.commit()
            flash("Campus list updated.", "success")
        return redirect(url_for("admin.catalogs"))
    return render_template(
        "admin/catalogs.html",
        categories=CampusCategory.query.order_by(CampusCategory.name).all(),
        locations=CampusLocation.query.order_by(CampusLocation.name).all(),
    )

@admin_bp.route("/catalogs/<kind>/<int:entry_id>/toggle", methods=["POST"])
def toggle_catalog_entry(kind, entry_id):
    catalog_model = {
        "category": CampusCategory,
        "location": CampusLocation,
    }.get(kind)
    if catalog_model is None:
        return "Invalid campus list type.", 404
    entry = catalog_model.query.get_or_404(entry_id)
    entry.is_active = not entry.is_active
    db.session.add(AuditLog(
        actor_id=current_user.id,
        action=f"{'Activated' if entry.is_active else 'Deactivated'} campus {kind}: {entry.name}",
    ))
    db.session.commit()
    flash("Campus list updated.", "success")
    return redirect(url_for("admin.catalogs"))

@admin_bp.route("/catalogs/<kind>/<int:entry_id>/rename", methods=["POST"])
def rename_catalog_entry(kind, entry_id):
    catalog_model = {
        "category": CampusCategory,
        "location": CampusLocation,
    }.get(kind)
    if catalog_model is None:
        return "Invalid campus list type.", 404
    entry = catalog_model.query.get_or_404(entry_id)
    name = request.form.get("name", "").strip()
    limit = 80 if kind == "category" else 150
    duplicate = catalog_model.query.filter(
        catalog_model.name == name,
        catalog_model.id != entry.id,
    ).first()
    if not name or len(name) > limit or duplicate:
        flash("Enter a unique name within the allowed length.", "error")
    else:
        previous_name = entry.name
        entry.name = name
        db.session.add(AuditLog(
            actor_id=current_user.id,
            action=f"Renamed campus {kind} from {previous_name} to {name}",
        ))
        db.session.commit()
        flash("Campus list updated.", "success")
    return redirect(url_for("admin.catalogs"))

@admin_bp.route("/analytics")
def analytics():
    today = date.today()
    default_start = date(today.year, 1, 1)
    default_end = date(today.year, 12, 31)
    try:
        start = date.fromisoformat(request.args.get("start", default_start.isoformat()))
        end = date.fromisoformat(request.args.get("end", default_end.isoformat()))
        if start > end:
            raise ValueError
    except ValueError:
        flash("Choose a valid date range with the start on or before the end.", "error")
        start, end = default_start, default_end

    reports = Report.query.filter(Report.event_date >= start, Report.event_date <= end)
    total = reports.count()
    by_category = (
        db.session.query(Report.category, db.func.count(Report.id))
        .filter(Report.event_date >= start, Report.event_date <= end)
        .group_by(Report.category).order_by(db.func.count(Report.id).desc()).all()
    )
    by_location = (
        db.session.query(Report.campus_location, db.func.count(Report.id))
        .filter(Report.event_date >= start, Report.event_date <= end)
        .group_by(Report.campus_location).order_by(db.func.count(Report.id).desc()).all()
    )
    recovered = reports.filter(Report.status == "Recovered").count()
    ai_query = AIRecognitionEvent.query.filter(
        AIRecognitionEvent.created_at >= datetime.combine(start, datetime.min.time()),
        AIRecognitionEvent.created_at < datetime.combine(
            end + timedelta(days=1), datetime.min.time()
        ),
    )
    ai_count = ai_query.count()
    average_confidence = db.session.query(
        db.func.avg(AIRecognitionEvent.confidence)
    ).filter(
        AIRecognitionEvent.created_at >= datetime.combine(start, datetime.min.time()),
        AIRecognitionEvent.created_at < datetime.combine(
            end + timedelta(days=1), datetime.min.time()
        ),
        AIRecognitionEvent.confidence > 0,
    ).scalar()
    ai_labels = (
        db.session.query(AIRecognitionEvent.class_label, db.func.count(AIRecognitionEvent.id))
        .filter(
            AIRecognitionEvent.created_at >= datetime.combine(start, datetime.min.time()),
            AIRecognitionEvent.created_at < datetime.combine(
                end + timedelta(days=1), datetime.min.time()
            ),
        )
        .group_by(AIRecognitionEvent.class_label)
        .order_by(db.func.count(AIRecognitionEvent.id).desc())
        .limit(10)
        .all()
    )
    monthly_reports = (
        db.session.query(
            db.extract("year", Report.event_date),
            db.extract("month", Report.event_date),
            db.func.count(Report.id),
        )
        .filter(Report.event_date >= start, Report.event_date <= end)
        .group_by(
            db.extract("year", Report.event_date),
            db.extract("month", Report.event_date),
        )
        .order_by(
            db.extract("year", Report.event_date),
            db.extract("month", Report.event_date),
        )
        .all()
    )
    return render_template(
        "admin/analytics.html",
        start=start,
        end=end,
        total=total,
        recovered=recovered,
        by_category=by_category,
        by_location=by_location,
        ai_count=ai_count,
        average_confidence=round(average_confidence * 100, 1) if average_confidence else 0,
        ai_labels=ai_labels,
        monthly_reports=monthly_reports,
    )
