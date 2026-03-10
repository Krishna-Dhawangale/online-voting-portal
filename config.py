import os
from datetime import timedelta
from dotenv import load_dotenv, find_dotenv

# Load .env from project root or app folder
_env_path = find_dotenv(filename='.env', usecwd=True) or find_dotenv(filename='app/.env', usecwd=True)
load_dotenv(_env_path, override=False)

class Config:
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'

    # SQLite configuration (active backend)
    SQLITE_DB_PATH = os.environ.get('SQLITE_DB_PATH', os.path.join('instance', 'online_voting.sqlite'))

    # Legacy MySQL configuration (unused after SQLite migration)
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', '3306'))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'online_voting')
    MYSQL_CURSORCLASS = 'DictCursor'

    # Toggle to avoid initializing DB at app startup (prevents crash if DB is down)
    DB_INIT_ON_STARTUP = os.environ.get('DB_INIT_ON_STARTUP', 'true').lower() in ('1', 'true', 'yes')

    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_COOKIE_SECURE = False  # allow HTTP in dev
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Security
    PASSWORD_SALT = os.environ.get('PASSWORD_SALT', 'dev-salt-change-in-production')

    # OTP configuration
    OTP_EXPIRATION = 300  # 5 minutes in seconds
    MAX_OTP_ATTEMPTS = 5

    # Application settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    TESTING = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLITE_DB_PATH = os.environ.get('TEST_SQLITE_DB_PATH', os.path.join('instance', 'test_online_voting.sqlite'))


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        # Log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
