import os
import json
from datetime import datetime
from Crypto.PublicKey import RSA

class KeyManager:
    def __init__(self, key_storage_path):
        self.key_storage_path = key_storage_path
        os.makedirs(os.path.dirname(key_storage_path), exist_ok=True)
        self.keys = self.load_keys()

    def load_keys(self):
        """Load RSA key pairs from storage."""
        if not os.path.exists(self.key_storage_path):
            return {}
            
        try:
            with open(self.key_storage_path, 'r') as f:
                keys_data = json.load(f)
            return keys_data
        except Exception as e:
            print(f"Error loading keys: {e}")
            return {}

    def save_keys(self):
        """Save RSA key pairs to storage."""
        with open(self.key_storage_path, 'w') as f:
            json.dump(self.keys, f)

    def get_public_key(self, identifier):
        """Retrieve a public key by identifier."""
        if identifier in self.keys:
            return self.keys[identifier]["public_key"]
        return None

    def mark_key_as_used(self, identifier):
        """Mark a public key as used."""
        if identifier in self.keys:
            self.keys[identifier]["used"] = True
            self.keys[identifier]["used_at"] = datetime.now().isoformat()
            self.save_keys()
            return True
        return False

    def generate_new_key_pair(self):
        """Generate a new RSA key pair."""
        key = RSA.generate(2048)
        private_key = key.export_key().decode('utf-8')
        public_key = key.publickey().export_key().decode('utf-8')
        
        identifier = f"key_{len(self.keys) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.keys[identifier] = {
            "private_key": private_key,
            "public_key": public_key,
            "created_at": datetime.now().isoformat(),
            "used": False
        }
        self.save_keys()
        return identifier

    def get_private_key(self, identifier):
        """Retrieve a private key by identifier."""
        if identifier in self.keys:
            return self.keys[identifier]["private_key"]
        return None