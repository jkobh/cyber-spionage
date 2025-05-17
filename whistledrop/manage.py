#!/usr/bin/env python
import os
import sys
import argparse
import logging
from server.app import create_app
from server.db_init import init_db, add_public_key, load_keys_from_file, check_keys_available, generate_test_keys
from server.models import db, RSAKey

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('manage')

app = create_app()

def init_database(args):
    """Initialize the database and create tables."""
    with app.app_context():
        init_db(app)
        logger.info("Database initialized successfully.")

def import_keys(args):
    """Import RSA public keys from a file."""
    if not os.path.exists(args.file):
        logger.error(f"File not found: {args.file}")
        sys.exit(1)
        
    count = load_keys_from_file(app, args.file)
    logger.info(f"Imported {count} RSA public keys.")

def add_key(args):
    """Add a single RSA public key to the database."""
    if args.key:
        key_data = args.key
    elif args.key_file:
        if not os.path.exists(args.key_file):
            logger.error(f"File not found: {args.key_file}")
            sys.exit(1)
        with open(args.key_file, 'r') as f:
            key_data = f.read().strip()
    else:
        logger.error("Either --key or --key-file must be provided.")
        sys.exit(1)
        
    if add_public_key(app, key_data):
        logger.info("RSA public key added successfully.")
    else:
        logger.error("Failed to add RSA public key (may already exist).")

def list_keys(args):
    """List all RSA keys in the database."""
    with app.app_context():
        keys = RSAKey.query.all()
        
        if not keys:
            logger.info("No RSA keys found in the database.")
            return
            
        print(f"Found {len(keys)} RSA keys:")
        print("-" * 50)
        
        for key in keys:
            status = "Used" if key.is_used else "Available"
            used_at = f" (Used at: {key.used_at})" if key.is_used and key.used_at else ""
            print(f"Key ID: {key.id}")
            print(f"Status: {status}{used_at}")
            print(f"Created: {key.created_at}")
            
            # Print the first and last 20 characters of the key
            key_preview = key.public_key[:20] + "..." + key.public_key[-20:]
            print(f"Key: {key_preview}")
            print("-" * 50)
            
        # Summary
        available = sum(1 for k in keys if not k.is_used)
        print(f"Summary: {available} available, {len(keys) - available} used")

def generate_keys(args):
    """Generate new RSA test keys."""
    count = generate_test_keys(app, args.count)
    logger.info(f"Generated {count} RSA test keys.")

def reset_key(args):
    """Reset a used key to available status."""
    with app.app_context():
        key = RSAKey.query.get(args.id)
        if not key:
            logger.error(f"Key with ID {args.id} not found.")
            sys.exit(1)
            
        key.is_used = False
        key.used_at = None
        db.session.commit()
        logger.info(f"Key {args.id} reset to available status.")

def delete_key(args):
    """Delete a key from the database."""
    with app.app_context():
        key = RSAKey.query.get(args.id)
        if not key:
            logger.error(f"Key with ID {args.id} not found.")
            sys.exit(1)
            
        db.session.delete(key)
        db.session.commit()
        logger.info(f"Key {args.id} deleted from the database.")

def status(args):
    """Show database status."""
    with app.app_context():
        total_keys = RSAKey.query.count()
        available_keys = RSAKey.query.filter_by(is_used=False).count()
        
        print("WhistleDrop Database Status:")
        print(f"Total RSA keys: {total_keys}")
        print(f"Available RSA keys: {available_keys}")
        print(f"Used RSA keys: {total_keys - available_keys}")
        
        if available_keys == 0:
            print("\nWARNING: No available RSA keys! Uploads will fail until keys are added.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='WhistleDrop Database Management Tool')
    subparsers = parser.add_subparsers(title='commands', dest='command')
    
    # init command
    init_parser = subparsers.add_parser('init', help='Initialize database')
    init_parser.set_defaults(func=init_database)
    
    # import command
    import_parser = subparsers.add_parser('import', help='Import RSA public keys from file')
    import_parser.add_argument('file', help='Path to key file (JSON format)')
    import_parser.set_defaults(func=import_keys)
    
    # add command
    add_parser = subparsers.add_parser('add', help='Add a single RSA public key')
    key_group = add_parser.add_mutually_exclusive_group(required=True)
    key_group.add_argument('--key', help='RSA public key as string')
    key_group.add_argument('--key-file', help='File containing RSA public key')
    add_parser.set_defaults(func=add_key)
    
    # list command
    list_parser = subparsers.add_parser('list', help='List all RSA keys')
    list_parser.set_defaults(func=list_keys)
    
    # generate command
    generate_parser = subparsers.add_parser('generate', help='Generate test RSA key pairs')
    generate_parser.add_argument('--count', type=int, default=5, help='Number of keys to generate (default: 5)')
    generate_parser.set_defaults(func=generate_keys)
    
    # reset command
    reset_parser = subparsers.add_parser('reset', help='Reset a used key to available status')
    reset_parser.add_argument('id', type=int, help='Key ID to reset')
    reset_parser.set_defaults(func=reset_key)
    
    # delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a key from the database')
    delete_parser.add_argument('id', type=int, help='Key ID to delete')
    delete_parser.set_defaults(func=delete_key)
    
    # status command
    status_parser = subparsers.add_parser('status', help='Show database status')
    status_parser.set_defaults(func=status)
    
    args = parser.parse_args()
    
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)
        
    args.func(args)