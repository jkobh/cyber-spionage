from flask import Flask, request, url_for
import os
import logging
from .config import Config
from .routes import main as main_routes
from .tor_service import TorService
from .models import db
from .db_init import setup_database

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config_class=Config):
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    app.config.from_object(config_class)
    
    # Initialize database
    db.init_app(app)
    
    # Register routes
    app.register_blueprint(main_routes)
    
    # Override the url_for function to use .onion domain for external URLs
    if app.config.get('ONION_DOMAIN'):
        def override_url_for():
            return dict(url_for=_url_for)
        
        def _url_for(endpoint, **values):
            if endpoint == 'static' or 'external' in values:
                values['_external'] = False
            return url_for(endpoint, **values)
        
        app.context_processor(override_url_for)
    
    return app

def main():
    app = create_app()
    
    # Initialize the database and load RSA keys
    logger.info("Initializing database...")
    key_file = app.config.get('RSA_PUBLIC_KEYS_FILE')
    generate_test_keys = app.config.get('GENERATE_TEST_KEYS', app.config.get('DEBUG', False))
    key_count = app.config.get('TEST_KEY_COUNT', 5)
    
    available_keys = setup_database(
        app, 
        key_file=key_file, 
        generate_keys=generate_test_keys,
        key_count=key_count
    )
    
    if available_keys == 0:
        logger.warning("No RSA keys available. The system won't be able to accept uploads!")
    else:
        logger.info(f"{available_keys} RSA public keys available for encryption")
    
    # Initialize Tor service
    if app.config.get('USE_TOR', True):
        logger.info("Initializing Tor service...")
        tor_service = TorService(
            tor_control_port=app.config.get('TOR_CONTROL_PORT', 9051),
            web_port=app.config.get('PORT', 5000),
            hidden_service_dir=app.config.get('HIDDEN_SERVICE_DIR')
        )
        
        try:
            # Start the Tor hidden service
            onion_address = tor_service.start()
            if onion_address:
                app.config['ONION_DOMAIN'] = f"{onion_address}.onion"
                logger.info(f"WhistleDrop is available at: http://{onion_address}.onion")
            else:
                logger.warning("Failed to start Tor hidden service. Running in clearnet mode.")
        except Exception as e:
            logger.error(f"Error starting Tor service: {e}")
            logger.warning("Running in clearnet mode only")
    else:
        logger.info("Tor integration disabled. Running in clearnet mode.")
    
    # Run the Flask app
    host = app.config.get('HOST', '127.0.0.1')
    port = app.config.get('PORT', 5000)
    debug = app.config.get('DEBUG', False)
    
    logger.info(f"Starting WhistleDrop server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)

# Make the app importable
app = create_app()

if __name__ == '__main__':
    main()