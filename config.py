import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent

# Load .env file if it exists
load_dotenv(BASE_DIR / '.env')


class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'skillbridge-dev-secret-key-3.14-2026')
    
    # Ensure instance folder exists for SQLite
    INSTANCE_DIR = BASE_DIR / 'instance'
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Database Configuration - defaults to SQLite inside instance/
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{INSTANCE_DIR / 'skillbridge.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Admin Provisioning Secret Key
    ADMIN_SECRET_KEY = os.environ.get('ADMIN_SECRET_KEY', 'skillbridge-admin-secret-2026')
    
    # AI Service Configuration
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '').strip()
    
    # Session Cookie Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400 * 7  # 7 days if "remember me" checked

