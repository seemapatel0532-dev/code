import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///careersetudb.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload settings
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS = {"pdf", "docx"}

    # Storage (inside app/)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "storage", "uploads")