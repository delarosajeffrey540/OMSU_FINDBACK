from getpass import getpass
from app import app
from extensions import db
from models import User

with app.app_context():
    email = input("Administrator email: ").strip().lower()
    name = input("Administrator full name: ").strip()
    password = getpass("Administrator password (minimum 12 characters): ")
    if len(password) < 12:
        raise SystemExit("Use at least 12 characters.")
    if User.query.filter_by(email=email).first():
        raise SystemExit("An account with this email already exists.")
    admin = User(full_name=name, email=email, affiliation="University personnel", role="admin")
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    print("Administrator created. Keep these credentials private.")
