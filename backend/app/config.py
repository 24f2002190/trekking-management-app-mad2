import os

base_dir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "tma-secret-key-change-in-prod"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(base_dir, "..", "tma.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Security
    SECURITY_PASSWORD_SALT  = "tma-password-salt"
    SECURITY_TOKEN_AUTHENTICATION_HEADER = "Authentication-Token"
    SECURITY_PASSWORD_HASH  = "sha256_crypt"
    WTF_CSRF_ENABLED        = False

    # Redis + Celery
    CELERY_BROKER_URL        = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND    = "redis://localhost:6379/0"
    CELERY_TIMEZONE          = "Asia/Kolkata"

    # Redis Caching
    CACHE_TYPE             = "RedisCache"
    CACHE_REDIS_URL        = "redis://localhost:6379/1"  
    CACHE_DEFAULT_TIMEOUT  = 300  

    # Mail (using Gmail)
    MAIL_SERVER   = "smtp.gmail.com"
    MAIL_PORT     = 587
    MAIL_USE_TLS  = True
    MAIL_USERNAME = "agarwalvedika28@gmail.com"       
    MAIL_PASSWORD = "epurdehhwnyautyi"    
    MAIL_DEFAULT_SENDER = "agarwalvedika28@gmail.com" 