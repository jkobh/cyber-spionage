#!/usr/bin/env python
import os
import sys
import argparse
import logging
import json
from server.app import create_app
from server.db_init import init_db, check_keys_available  # Remove add_test_keys
from server.models import db, RSAKey, UploadedFile
from journalist.crypto import create_keypair_json, generate_rsa_keypair
from Crypto.PublicKey import RSA
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('manage')

app = create_app()

def init_database(args):
    """Initialize the database with tables."""
    with app.app_context():
        db.create_all()
        logger.info("Database tables created successfully.")
        
        if args.with_keys:
            count = args.count if hasattr(args, 'count') else 5
            generate_keys(argparse.Namespace(count=count, reset=False))

def status(args):
    """Show the current status of the database and keys."""
    with app.app_context():
        total_keys = RSAKey.query.count()
        available_keys = RSAKey.query.filter_by(is_used=False).count()
        total_files = UploadedFile.query.count()
        
        print("\n=== WhistleDrop Status ===")
        print(f"Database status: {'OK' if db else 'Not connected'}")
        print(f"Total RSA keys: {total_keys}")
        print(f"Available keys: {available_keys}")
        print(f"Used keys: {total_keys - available_keys}")
        print(f"Uploaded files: {total_files}")
        
        if total_keys == 0:
            print("\nWARNING: No RSA keys in database. Run 'python manage.py generate' to add keys.")
        elif available_keys == 0:
            print("\nWARNING: No available RSA keys! Uploads will fail until keys are added.")
        
        print("\nKey usage:")
        used_keys = RSAKey.query.filter_by(is_used=True).all()
        for key in used_keys:
            file = UploadedFile.query.filter_by(key_id=key.id).first()
            if file:
                print(f"  Key ID {key.id}: Used for file '{file.filename}' on {file.created_at}")
            else:
                print(f"  Key ID {key.id}: Marked as used but no file found")
        
        # Check if keys.json exists and contains keys
        if os.path.exists('keys.json'):
            try:
                with open('keys.json', 'r') as f:
                    private_keys = json.load(f)
                print(f"\nPrivate keys in keys.json: {len(private_keys)}")
            except:
                print("\nERROR: keys.json exists but could not be parsed")
        else:
            print("\nWARNING: No keys.json file found. Journalists will not be able to decrypt files.")

def generate_keys(args):
    """Generate new RSA test keys and save them to keys.json."""
    # Generate key pairs and save to keys.json
    key_pairs = create_keypair_json(count=args.count, output_path="keys.json")
    logger.info(f"Generated {len(key_pairs)} RSA key pairs and saved private keys to keys.json")
    
    # Update database with public keys
    with app.app_context():
        # Delete existing keys if requested
        if args.reset:
            RSAKey.query.delete()
            db.session.commit()
            logger.info("Cleared existing RSA keys from database")
        
        # Add new keys to database
        added_keys = 0
        for key_id, private_key in key_pairs.items():
            # Extract public key from private key
            key = RSA.import_key(private_key)
            public_key = key.publickey().export_key().decode('utf-8')
            
            # Add to database
            new_key = RSAKey(public_key=public_key, is_used=False)
            db.session.add(new_key)
            added_keys += 1
        
        db.session.commit()
        logger.info(f"Added {added_keys} public keys to database")
        
        # Now update keys.json with actual database IDs
        keys = RSAKey.query.all()
        updated_keys = {}
        
        for i, key in enumerate(keys[-args.count:]):  # Only process the new keys
            if str(i+1) in key_pairs:
                private_key = key_pairs[str(i+1)]
                # Save with actual database ID
                updated_keys[str(key.id)] = private_key
        
        # Overwrite keys.json with updated IDs
        with open("keys.json", 'w') as f:
            json.dump(updated_keys, f, indent=2)
        
        logger.info(f"Updated keys.json with {len(updated_keys)} keys (IDs matched to database)")
        
        # Return the number of keys added
        return added_keys

def reset_database(args):
    """Reset the database by dropping all tables and recreating them."""
    with app.app_context():
        if args.confirm:
            db.drop_all()
            logger.info("All database tables dropped.")
            db.create_all()
            logger.info("Database tables recreated.")
            
            if args.with_keys:
                count = args.count if hasattr(args, 'count') else 5
                generate_keys(argparse.Namespace(count=count, reset=False))
        else:
            logger.warning("Database reset canceled. Use --confirm to proceed.")

def list_files(args):
    """List all files in the database."""
    with app.app_context():
        files = UploadedFile.query.all()
        
        if not files:
            print("No files found in the database.")
            return
        
        print("\n=== Files in Database ===")
        for file in files:
            print(f"ID: {file.id}")
            print(f"Filename: {file.filename}")
            print(f"Uploaded: {file.created_at}")
            print(f"Key ID: {file.key_id}")
            print("-" * 30)

def clear_files(args):
    """Remove all uploaded files from the database."""
    with app.app_context():
        if args.confirm:
            count = UploadedFile.query.count()
            UploadedFile.query.delete()
            
            # Reset used status on keys
            RSAKey.query.filter_by(is_used=True).update({RSAKey.is_used: False, RSAKey.used_at: None})
            
            db.session.commit()
            logger.info(f"Removed {count} files from database and reset key usage.")
        else:
            logger.warning("File purge canceled. Use --confirm to proceed.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='WhistleDrop Management Tool')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # init command
    init_parser = subparsers.add_parser('init', help='Initialize the database')
    init_parser.add_argument('--with-keys', action='store_true', help='Generate keys after initialization')
    init_parser.add_argument('--count', type=int, default=5, help='Number of keys to generate (default: 5)')
    init_parser.set_defaults(func=init_database)
    
    # status command
    status_parser = subparsers.add_parser('status', help='Show database and key status')
    status_parser.set_defaults(func=status)
    
    # generate command
    generate_parser = subparsers.add_parser('generate', help='Generate RSA key pairs')
    generate_parser.add_argument('--count', type=int, default=5, help='Number of keys to generate (default: 5)')
    generate_parser.add_argument('--reset', action='store_true', help='Clear existing keys before adding new ones')
    generate_parser.set_defaults(func=generate_keys)
    
    # reset command
    reset_parser = subparsers.add_parser('reset', help='Reset the database (drop all tables and recreate)')
    reset_parser.add_argument('--confirm', action='store_true', help='Confirm database reset')
    reset_parser.add_argument('--with-keys', action='store_true', help='Generate keys after reset')
    reset_parser.add_argument('--count', type=int, default=5, help='Number of keys to generate (default: 5)')
    reset_parser.set_defaults(func=reset_database)
    
    # list command
    list_parser = subparsers.add_parser('list', help='List all files in the database')
    list_parser.set_defaults(func=list_files)
    
    # clear command
    clear_parser = subparsers.add_parser('clear', help='Remove all uploaded files')
    clear_parser.add_argument('--confirm', action='store_true', help='Confirm file removal')
    clear_parser.set_defaults(func=clear_files)
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()