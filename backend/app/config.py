import os

base_dir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "tma-secret-key-change-in-prod"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(base_dir, "..", "tma.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECURITY_PASSWORD_SALT = "tma-password-salt"
    SECURITY_TOKEN_AUTHENTICATION_HEADER = "Authentication-Token"
    SECURITY_PASSWORD_HASH = "bcrypt"
    WTF_CSRF_ENABLED = False