import os
import json
from journalist.crypto import generate_rsa_keypair
from server.app import create_app
from server.models import db, RSAKey, UploadedFile

def reset_database_and_keys():
    """Complete reset of the database and regeneration of all keys."""
    print("Starting complete system reset...")
    
    # Create application context
    app = create_app()
    
    with app.app_context():
        print("Clearing existing database...")
        # Drop all tables
        db.drop_all()
        # Recreate tables
        db.create_all()
        print("Database tables recreated.")
        
        # Generate new keypairs
        print("Generating new RSA keypairs...")
        key_pairs = {}
        
        # Create key objects first without setting IDs
        keys_objects = []
        for i in range(1, 11):  # Generate 10 keypairs
            private_key, public_key = generate_rsa_keypair()
            if private_key and public_key:
                # Convert from bytes to string
                private_key_str = private_key.decode('utf-8')
                public_key_str = public_key.decode('utf-8')
                
                # Create a new key object
                new_key = RSAKey(
                    public_key=public_key_str,
                    is_used=False
                )
                
                # Add to our list
                keys_objects.append((i, new_key, private_key_str))
                
                # Add to the session
                db.session.add(new_key)
        
        # Commit the keys to get their IDs assigned
        db.session.commit()
        
        # Now create our keys.json with the actual database IDs
        for i, key_obj, private_key_str in keys_objects:
            key_pairs[str(key_obj.id)] = private_key_str
        
        # Save private keys to keys.json
        with open("keys.json", 'w') as f:
            json.dump(key_pairs, f, indent=2)
        print(f"Private keys saved to keys.json with {len(key_pairs)} entries")
        
        # Verify keys were added
        key_count = RSAKey.query.count()
        print(f"Database now has {key_count} RSA keys")
        
    print("Reset complete! You can now upload and download files with matching keys.")

if __name__ == "__main__":
    reset_database_and_keys()