#!/usr/bin/env python
import os
import json
import argparse
import requests
import logging
import base64
from .crypto import decrypt_with_rsa
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('journalist.client')

class JournalistClient:
    def __init__(self, server_url, keys_file=None):
        """
        Initialize the journalist client.
        
        Args:
            server_url: The URL of the WhistleDrop server
            keys_file: Path to file containing private RSA keys
        """
        self.server_url = server_url.rstrip('/')
        self.keys = {}
        
        # Load keys if provided
        if keys_file and os.path.exists(keys_file):
            try:
                with open(keys_file, 'r') as f:
                    self.keys = json.load(f)
                logger.info(f"Loaded {len(self.keys)} keys from {keys_file}")
            except Exception as e:
                logger.error(f"Error loading keys from {keys_file}: {e}")
    
    def list_files(self):
        """List all available files on the server."""
        try:
            response = requests.get(f"{self.server_url}/files")
            if response.status_code == 200:
                files = response.json()
                if 'files' in files and 'total' in files:
                    print(f"Found {files['total']} files on the server:")
                    print("-" * 50)
                    
                    for file in files['files']:
                        print(f"ID: {file['id']}")
                        print(f"Filename: {file['filename']}")
                        print(f"Uploaded: {file['created_at']}")
                        print("-" * 50)
                        
                    return True
                else:
                    logger.error("Unexpected response format")
                    return False
            else:
                logger.error(f"Error listing files: {response.status_code} {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error connecting to server: {e}")
            return False
    
    def retrieve_file(self, file_id, output_path):
        """Retrieve and decrypt a file from the server."""
        if not self.keys:
            logger.error("No keys loaded. Cannot decrypt files.")
            return False
            
        try:
            # Get the encrypted file from the server
            response = requests.get(f"{self.server_url}/retrieve/{file_id}")
            if response.status_code != 200:
                logger.error(f"Error retrieving file {file_id}: {response.status_code} {response.text}")
                return False
                
            file_data = response.json()
            logger.info(f"Retrieved file: {file_data['filename']}")
            
            # Find the right key for decryption
            key_id = str(file_data.get('key_id'))
            if key_id not in self.keys:
                logger.error(f"No matching private key found for key_id {key_id}")
                return False
                
            private_key = self.keys[key_id]
            
            # Decrypt the AES key using the private RSA key
            encrypted_aes_key = base64.b64decode(file_data['encrypted_aes_key'])
            aes_key = decrypt_with_rsa(encrypted_aes_key, private_key)
            
            # Debug the encrypted_data format
            logger.info(f"Encrypted data type: {type(file_data['encrypted_data'])}")
            logger.info(f"Encrypted data preview: {str(file_data['encrypted_data'])[:50]}...")
            
            # Use the decrypt_file function directly from journalist.crypto
            from journalist.crypto import decrypt_file
            data = decrypt_file(file_data['encrypted_data'], aes_key)
            
            if not data:
                logger.error("Failed to decrypt the file")
                return False
            
            # Save the decrypted file
            with open(output_path, 'wb') as f:
                f.write(data)
                
            logger.info(f"File {file_data['filename']} successfully decrypted and saved to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error retrieving and decrypting file: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def check_server_status(self):
        """Check the status of the WhistleDrop server."""
        try:
            response = requests.get(f"{self.server_url}/status")
            if response.status_code == 200:
                status = response.json()
                print("Server Status:")
                print(f"Status: {status.get('status', 'Unknown')}")
                print(f"Version: {status.get('version', 'Unknown')}")
                print(f"Available keys: {status.get('available_keys', 'Unknown')}")
                print(f"Accepting uploads: {status.get('accepting_uploads', False)}")
                print(f"Onion address: {status.get('onion_address', 'Not available')}")
                return True
            else:
                logger.error(f"Error checking server status: {response.status_code} {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error connecting to server: {e}")
            return False

def main():
    """Command-line interface for the journalist client."""
    parser = argparse.ArgumentParser(description='WhistleDrop Journalist Client')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Common arguments
    server_arg = lambda p: p.add_argument('--server', required=True, help='WhistleDrop server URL')
    keys_arg = lambda p: p.add_argument('--keys', help='Path to journalist keys file (JSON)')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available files')
    server_arg(list_parser)
    keys_arg(list_parser)
    
    # Retrieve command
    retrieve_parser = subparsers.add_parser('retrieve', help='Retrieve and decrypt a file')
    server_arg(retrieve_parser)
    keys_arg(retrieve_parser)
    retrieve_parser.add_argument('--file-id', required=True, type=int, help='ID of the file to retrieve')
    retrieve_parser.add_argument('--output', required=True, help='Output path for decrypted file')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check server status')
    server_arg(status_parser)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize client
    client = JournalistClient(args.server, args.keys if hasattr(args, 'keys') else None)
    
    # Execute the requested command
    if args.command == 'list':
        return 0 if client.list_files() else 1
    elif args.command == 'retrieve':
        return 0 if client.retrieve_file(args.file_id, args.output) else 1
    elif args.command == 'status':
        return 0 if client.check_server_status() else 1
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    exit(main())