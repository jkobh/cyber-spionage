import os
import secrets

class Config:
    """Configuration settings for the WhistleDrop application."""
    
    # Generate a random secret key if not set in environment
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # Database settings
    DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///whistledrop.db'
    SQLALCHEMY_DATABASE_URI = DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # RSA Key settings
    RSA_PUBLIC_KEYS_FILE = os.environ.get('RSA_PUBLIC_KEYS_FILE')
    GENERATE_TEST_KEYS = os.environ.get('GENERATE_TEST_KEYS', 'False').lower() == 'true'
    TEST_KEY_COUNT = int(os.environ.get('TEST_KEY_COUNT', 5))
    
    # Server settings
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    HOST = os.environ.get('HOST', '127.0.0.1')
    PORT = int(os.environ.get('PORT', 5000))
    
    # Tor settings
    USE_TOR = os.environ.get('USE_TOR', 'True').lower() == 'true'
    TOR_CONTROL_PORT = int(os.environ.get('TOR_CONTROL_PORT', 9051))
    TOR_SERVICE_HOST = os.environ.get('TOR_SERVICE_HOST', '127.0.0.1')
    TOR_SERVICE_PORT = int(os.environ.get('TOR_SERVICE_PORT', 9050))
    HIDDEN_SERVICE_DIR = os.environ.get('HIDDEN_SERVICE_DIR', None)
    
    # Encryption settings
    AES_KEY_SIZE = 32  # AES-256
    RSA_KEY_SIZE = 2048  # RSA key size in bits
    
    # Upload settings
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'xlsx', 'png', 'jpg', 'jpeg', 'gif'}

    @staticmethod
    def init_app(app):
        """Initialize the app with the configuration."""
        # Create upload folder if it doesn't exist
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)