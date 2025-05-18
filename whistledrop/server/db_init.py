import os
import logging
from flask import Flask
from .models import db, RSAKey
from .config import Config

logger = logging.getLogger(__name__)

def init_db(app):
    """Initialize the database and create tables."""
    with app.app_context():
        # Create all tables defined in models.py
        db.create_all()
        logger.info("Database tables created")

def add_public_key(app, public_key_data):
    """Add a new RSA public key to the database."""
    with app.app_context():
        # Check if the key already exists
        existing_key = RSAKey.query.filter_by(public_key=public_key_data).first()
        if existing_key:
            logger.warning("Public key already exists in database")
            return False
            
        # Add the new key
        new_key = RSAKey(public_key=public_key_data)
        db.session.add(new_key)
        db.session.commit()
        logger.info(f"Added new RSA public key (ID: {new_key.id})")
        return True

def load_keys_from_file(app, key_file_path):
    """Load RSA public keys from a file."""
    if not os.path.exists(key_file_path):
        logger.error(f"Key file not found: {key_file_path}")
        return 0
        
    count = 0
    try:
        with open(key_file_path, 'r') as f:
            import json
            keys_data = json.load(f)
            
            if isinstance(keys_data, dict) and 'public_keys' in keys_data:
                # Format: {"public_keys": ["-----BEGIN PUBLIC KEY-----...", "..."]}
                keys = keys_data['public_keys']
            elif isinstance(keys_data, list):
                # Format: ["-----BEGIN PUBLIC KEY-----...", "..."]
                keys = keys_data
            else:
                # Try to parse as a single key
                keys = [keys_data]
                
            with app.app_context():
                for key_data in keys:
                    if add_public_key(app, key_data.strip()):
                        count += 1
                        
            logger.info(f"Loaded {count} RSA public keys from {key_file_path}")
            return count
            
    except Exception as e:
        logger.error(f"Error loading keys from {key_file_path}: {str(e)}")
        return 0

def check_keys_available(app):
    """Check if any RSA public keys are available for use."""
    with app.app_context():
        available_keys = RSAKey.query.filter_by(is_used=False).count()
        total_keys = RSAKey.query.count()
        
        logger.info(f"Database has {available_keys}/{total_keys} available RSA keys")
        
        if available_keys == 0:
            logger.warning("No available RSA keys! Uploads will fail until keys are added.")
            
        return available_keys

def generate_test_keys(app, count=5):
    """Generate test RSA keys for development/testing purposes."""
    from Crypto.PublicKey import RSA
    
    generated = 0
    for i in range(count):
        try:
            # Generate a new RSA key pair
            key = RSA.generate(2048)
            public_key = key.publickey().export_key().decode('utf-8')
            
            # Save the public key to the database
            if add_public_key(app, public_key):
                generated += 1
                
            # In a real scenario, the private key would be securely provided to the journalist
            # For test purposes, we can save it to a file
            if app.config.get('DEBUG', False):
                os.makedirs('test_keys', exist_ok=True)
                private_key = key.export_key().decode('utf-8')
                with open(f'test_keys/private_key_{i+1}.pem', 'w') as f:
                    f.write(private_key)
                    
        except Exception as e:
            logger.error(f"Error generating test key {i+1}: {str(e)}")
            
    logger.info(f"Generated {generated} test RSA keys")
    return generated

def setup_database(app, key_file=None, generate_keys=False, key_count=5):
    """Complete database setup process."""
    # Initialize the database
    init_db(app)
    
    # Load keys from file if provided
    if key_file and os.path.exists(key_file):
        load_keys_from_file(app, key_file)
        
    # Check if we have any keys
    available_keys = check_keys_available(app)
    
    # Generate test keys if needed and requested
    if available_keys == 0 and generate_keys:
        logger.info("Generating test RSA keys...")
        generate_test_keys(app, key_count)
        
    # Final check
    return check_keys_available(app)