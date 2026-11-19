import os
import logging
from flask import Flask, redirect, url_for, request, send_from_directory
from flask_login import current_user, login_required
from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config
from extensions import csrf, db, limiter, login_manager, socketio
from models import CampusCategory, CampusLocation, Notification, Report, User
from auth.routes import auth_bp
from student.routes import student_bp
from moderator.routes import moderator_bp
from admin.routes import admin_bp
from messaging import messages_bp
from notifications import notifications_bp

STARTER_CATEGORIES = (
    "Electronics",
    "Bags & accessories",
    "Drinkware",
    "Documents & IDs",
    "Clothing",
    "Sports equipment",
    "Other items",
)
STARTER_LOCATIONS = (
    "Library · Main campus",
    "Student center · Main campus",
    "Engineering building · Main campus",
    "Cafeteria · Main campus",
    "University grounds · Main campus",
    "Gymnasium · Main campus",
)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    if app.config["ENVIRONMENT"] == "production" and not app.config["SECRET_KEY"]:
        raise RuntimeError("Set a strong SECRET_KEY before starting in production.")
    if app.config["ENVIRONMENT"] == "production" and not app.config["TRUSTED_HOSTS"]:
        raise RuntimeError("Set ALLOWED_HOSTS to the production host names.")
    if (
        app.config["ENVIRONMENT"] == "production"
        and app.config["RATELIMIT_STORAGE_URI"] == "memory://"
    ):
        raise RuntimeError("Set RATELIMIT_STORAGE_URI to a shared Redis URL in production.")
    static_root = os.path.realpath(app.static_folder)
    upload_root = os.path.realpath(app.config["UPLOAD_FOLDER"])
    try:
        uploads_are_public = os.path.commonpath((static_root, upload_root)) == static_root
    except ValueError:
        uploads_are_public = False
    if uploads_are_public:
        raise RuntimeError(
            "UPLOAD_FOLDER must be outside the public static directory; use instance/uploads."
        )
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    if app.config["TRUST_PROXY"]:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    socketio.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp, url_prefix="/student")
    app.register_blueprint(moderator_bp, url_prefix="/moderator")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(messages_bp, url_prefix="/messages")
    app.register_blueprint(notifications_bp)

    @app.context_processor
    def notification_context():
        if not current_user.is_authenticated:
            return {"unread_notification_count": 0}
        return {
            "unread_notification_count": Notification.query.filter_by(
                recipient_id=current_user.id,
                is_read=False,
            ).count()
        }

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("X-Permitted-Cross-Domain-Policies", "none")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self' https://cdn.socket.io; "
            "style-src 'self' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https://omsu.edu.ph https://images.unsplash.com; "
            "connect-src 'self' ws: wss:; object-src 'none'; base-uri 'self'; "
            "form-action 'self'; frame-ancestors 'none'",
        )
        if app.config["ENVIRONMENT"] == "production" and request.is_secure:
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000")
        return response

    @app.before_request
    def require_production_https():
        if app.config["ENVIRONMENT"] == "production" and not request.is_secure:
            return redirect(request.url.replace("http://", "https://", 1), code=308)

    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    @app.route("/report-images/<int:report_id>")
    @login_required
    def report_image(report_id):
        report = Report.query.get_or_404(report_id)
        if not report.photo_filename:
            return "This report has no photo.", 404
        response = send_from_directory(
            app.config["UPLOAD_FOLDER"],
            report.photo_filename,
            conditional=True,
        )
        response.headers["Cache-Control"] = "private, no-store"
        return response

    @app.errorhandler(413)
    def too_large(_error):
        return "File too large. Maximum upload size is 5 MB.", 413

    with app.app_context():
        db.create_all()
        if CampusCategory.query.count() == 0:
            db.session.add_all(CampusCategory(name=name) for name in STARTER_CATEGORIES)
        if CampusLocation.query.count() == 0:
            db.session.add_all(CampusLocation(name=name) for name in STARTER_LOCATIONS)
        db.session.commit()

    return app

@login_manager.user_loader
def load_user(user_id):
    user = db.session.get(User, int(user_id))
    return user if user and user.status == "Active" else None

app = create_app()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    socketio.run(
        app,
        debug=app.config["ENVIRONMENT"] != "production",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
    )
