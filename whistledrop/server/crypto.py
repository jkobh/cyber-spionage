from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64

# TODO: Implement cryptographic functions

def generate_aes_key():
    """Generate a random AES key."""
    return get_random_bytes(16)  # AES-128

def encrypt_file(file_data, aes_key):
    """Encrypt the file data using AES encryption."""
    cipher = AES.new(aes_key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(file_data, AES.block_size))
    iv = base64.b64encode(cipher.iv).decode('utf-8')
    ct = base64.b64encode(ct_bytes).decode('utf-8')
    return iv, ct

def decrypt_file(iv, ct, aes_key):
    """Decrypt the file data using AES encryption."""
    iv = base64.b64decode(iv)
    ct = base64.b64decode(ct)
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt

def encrypt_aes_key(aes_key, public_key):
    """Encrypt the AES key using the journalist's public RSA key."""
    rsa_key = RSA.import_key(public_key)
    encrypted_key = rsa_key.encrypt(aes_key, None)[0]
    return base64.b64encode(encrypted_key).decode('utf-8')

def decrypt_aes_key(encrypted_key, private_key):
    """Decrypt the AES key using the journalist's private RSA key."""
    rsa_key = RSA.import_key(private_key)
    decrypted_key = rsa_key.decrypt(base64.b64decode(encrypted_key))
    return decrypted_key