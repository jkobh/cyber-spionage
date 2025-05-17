from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64
import json

def generate_aes_key():
    """Generate a random AES key."""
    return get_random_bytes(16)  # AES-128

def encrypt_file(file_data, aes_key):
    """Encrypt the file data using AES encryption."""
    cipher = AES.new(aes_key, AES.MODE_CBC)
    padded_data = pad(file_data, AES.block_size)
    ct_bytes = cipher.encrypt(padded_data)
    
    # Return IV and ciphertext for storage
    result = {
        'iv': base64.b64encode(cipher.iv).decode('utf-8'),
        'ciphertext': base64.b64encode(ct_bytes).decode('utf-8')
    }
    return json.dumps(result)

def decrypt_file(encrypted_data_json, aes_key):
    """Decrypt the file data using AES encryption."""
    data = json.loads(encrypted_data_json)
    iv = base64.b64decode(data['iv'])
    ct = base64.b64decode(data['ciphertext'])
    
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt

def encrypt_aes_key(aes_key, public_key_str):
    """Encrypt the AES key using the journalist's public RSA key."""
    public_key = RSA.import_key(public_key_str)
    cipher_rsa = PKCS1_OAEP.new(public_key)
    encrypted_key = cipher_rsa.encrypt(aes_key)
    # Rückgabe als Bytes
    return encrypted_key

def decrypt_aes_key(encrypted_key_str, private_key_str):
    """Decrypt the AES key using the journalist's private RSA key."""
    private_key = RSA.import_key(private_key_str)
    cipher_rsa = PKCS1_OAEP.new(private_key)
    encrypted_key = base64.b64decode(encrypted_key_str)
    decrypted_key = cipher_rsa.decrypt(encrypted_key)
    return decrypted_key