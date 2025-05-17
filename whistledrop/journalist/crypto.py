from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes
import base64
import json
import logging

logger = logging.getLogger(__name__)

def generate_rsa_keypair(bits=2048):
    """
    Generate a new RSA key pair.
    
    Args:
        bits: Key size in bits (default: 2048)
        
    Returns:
        tuple: (private_key, public_key) as bytes
    """
    try:
        # Generate a new RSA key pair
        key = RSA.generate(bits)
        
        # Export keys in PEM format
        private_key = key.export_key()
        public_key = key.publickey().export_key()
        
        return private_key, public_key
    except Exception as e:
        logger.error(f"Error generating RSA key pair: {e}")
        return None, None

def encrypt_with_rsa(data, public_key_str):
    """
    Encrypt data using an RSA public key.
    
    Args:
        data: The data to encrypt (bytes)
        public_key_str: The public key as a string
        
    Returns:
        bytes: The encrypted data
    """
    try:
        # Import the public key
        public_key = RSA.import_key(public_key_str)
        
        # Create a cipher object using the public key
        cipher = PKCS1_OAEP.new(public_key)
        
        # Encrypt the data
        encrypted_data = cipher.encrypt(data)
        
        return encrypted_data
    except Exception as e:
        logger.error(f"Error encrypting with RSA: {e}")
        return None

def decrypt_with_rsa(encrypted_data, private_key_str):
    """
    Decrypt data using an RSA private key.
    
    Args:
        encrypted_data: The data to decrypt (bytes)
        private_key_str: The private key as a string
        
    Returns:
        bytes: The decrypted data
    """
    try:
        # Import the private key
        private_key = RSA.import_key(private_key_str)
        
        # Create a cipher object using the private key
        cipher = PKCS1_OAEP.new(private_key)
        
        # Decrypt the data
        decrypted_data = cipher.decrypt(encrypted_data)
        
        return decrypted_data
    except Exception as e:
        logger.error(f"Error decrypting with RSA: {e}")
        return None

def save_keypair_to_file(private_key, public_key, private_key_path, public_key_path):
    """
    Save RSA key pair to files.
    
    Args:
        private_key: The private key as bytes
        public_key: The public key as bytes
        private_key_path: Path to save the private key
        public_key_path: Path to save the public key
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(private_key_path, 'wb') as f:
            f.write(private_key)
            
        with open(public_key_path, 'wb') as f:
            f.write(public_key)
            
        return True
    except Exception as e:
        logger.error(f"Error saving keys to files: {e}")
        return False

def load_private_key(key_path):
    """
    Load a private key from a file.
    
    Args:
        key_path: Path to the private key file
        
    Returns:
        str: The private key as a string
    """
    try:
        with open(key_path, 'rb') as f:
            key_data = f.read()
        return key_data.decode('utf-8')
    except Exception as e:
        logger.error(f"Error loading private key from {key_path}: {e}")
        return None

def encrypt_aes_key_with_rsa(aes_key, public_key_str):
    """
    Encrypt an AES key using an RSA public key.
    
    Args:
        aes_key: The AES key to encrypt (bytes)
        public_key_str: The RSA public key as a string
        
    Returns:
        str: The encrypted AES key as a base64-encoded string
    """
    encrypted_key = encrypt_with_rsa(aes_key, public_key_str)
    return base64.b64encode(encrypted_key).decode('utf-8')

def decrypt_aes_key_with_rsa(encrypted_aes_key, private_key_str):
    """
    Decrypt an AES key using an RSA private key.
    
    Args:
        encrypted_aes_key: The encrypted AES key as a base64-encoded string
        private_key_str: The RSA private key as a string
        
    Returns:
        bytes: The decrypted AES key
    """
    encrypted_key = base64.b64decode(encrypted_aes_key)
    return decrypt_with_rsa(encrypted_key, private_key_str)

def decrypt_file(encrypted_data_json, aes_key):
    """
    Decrypt a file using an AES key.
    
    Args:
        encrypted_data_json: JSON string containing IV and ciphertext
        aes_key: The AES key (bytes)
        
    Returns:
        bytes: The decrypted file data
    """
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad
    
    try:
        # Parse the encrypted data
        if isinstance(encrypted_data_json, str):
            encrypted_data = json.loads(encrypted_data_json)
        else:
            encrypted_data = encrypted_data_json
            
        # Extract IV and ciphertext
        iv = base64.b64decode(encrypted_data['iv'])
        ciphertext = base64.b64decode(encrypted_data['ciphertext'])
        
        # Create a cipher object and decrypt
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        padded_data = cipher.decrypt(ciphertext)
        
        # Remove padding
        data = unpad(padded_data, AES.block_size)
        
        return data
    except Exception as e:
        logger.error(f"Error decrypting file: {e}")
        return None

def format_keypair_for_json(private_key, public_key, key_id):
    """
    Format a key pair for storage in a JSON file.
    
    Args:
        private_key: The private key as bytes
        public_key: The public key as bytes
        key_id: The ID for this key pair
        
    Returns:
        dict: A dictionary containing the formatted key pair
    """
    return {
        'id': key_id,
        'private_key': private_key.decode('utf-8'),
        'public_key': public_key.decode('utf-8')
    }

def create_keypair_json(count=10, output_path=None):
    """
    Create multiple RSA key pairs and save them to a JSON file.
    
    Args:
        count: Number of key pairs to generate
        output_path: Path to save the JSON file
        
    Returns:
        dict: A dictionary containing all key pairs
    """
    key_pairs = {}
    for i in range(1, count + 1):
        private_key, public_key = generate_rsa_keypair()
        if private_key and public_key:
            key_pairs[str(i)] = private_key.decode('utf-8')
    
    if output_path and key_pairs:
        try:
            with open(output_path, 'w') as f:
                json.dump(key_pairs, f, indent=2)
            logger.info(f"Saved {len(key_pairs)} key pairs to {output_path}")
        except Exception as e:
            logger.error(f"Error saving key pairs to {output_path}: {e}")
    
    return key_pairs