import os
import secrets
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

class Config:
    ENVIRONMENT = os.getenv("APP_ENV", "development").lower()
    SECRET_KEY = os.getenv("SECRET_KEY") or (
        secrets.token_hex(32) if ENVIRONMENT != "production" else ""
    )
    TRUSTED_HOSTS = [
        host.strip()
        for host in os.getenv("ALLOWED_HOSTS", "").split(",")
        if host.strip()
    ] or None
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "omsu_findback")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_URL = os.getenv("DATABASE_URL")
    SQLALCHEMY_DATABASE_URI = (
        DB_URL or
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(PROJECT_ROOT, "instance", "uploads"))
    if not os.path.isabs(UPLOAD_FOLDER):
        UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, UPLOAD_FOLDER)
    AI_MODEL_PATH = os.getenv("AI_MODEL_PATH", os.path.join(PROJECT_ROOT, "yolov8n.pt"))
    if not os.path.isabs(AI_MODEL_PATH):
        AI_MODEL_PATH = os.path.join(PROJECT_ROOT, AI_MODEL_PATH)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = ENVIRONMENT == "production"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SECURE = ENVIRONMENT == "production"
    PREFERRED_URL_SCHEME = "https" if ENVIRONMENT == "production" else "http"
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_SENDER = os.getenv("SMTP_SENDER", "")
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
    RATELIMIT_HEADERS_ENABLED = True
    TRUST_PROXY = os.getenv("TRUST_PROXY", "false").lower() == "true"
