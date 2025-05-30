from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify, current_app, send_file
from datetime import datetime
import os
import io
import logging
from .crypto import generate_aes_key, encrypt_file, encrypt_aes_key
from .models import db, UploadedFile, RSAKey
import base64

main = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

@main.route('/')
def index():
    """Homepage for whistleblowers."""
    return render_template('index.html')

@main.route('/upload', methods=['GET'])
def upload():
    """File upload form page."""
    # Check if there are available keys first
    available_keys = RSAKey.query.filter_by(is_used=False).first()
    if not available_keys:
        return render_template('error.html', 
                              message="The service is currently unable to accept new uploads. Please try again later.")
    
    return render_template('upload.html')

@main.route('/upload_file', methods=['POST'])
def upload_file():
    """Handle file uploads from whistleblowers."""
    # Check if a file was uploaded
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    # Check if the file is allowed
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in current_app.config.get('ALLOWED_EXTENSIONS', 
                                                                            {'pdf', 'txt', 'docx', 'xlsx', 'png', 'jpg'})
    
    if not allowed_file(file.filename):
        flash('File type not allowed')
        return redirect(request.url)
    
    try:
        # Get an unused RSA public key
        unused_key = RSAKey.query.filter_by(is_used=False).first()
        if unused_key is None:
            flash('No available keys for encryption')
            return redirect(request.url)
        
        # Read the file content first
        file_contents = file.read()
        
        # Generate a random AES key for file encryption
        # Encrypt the file
        aes_key = generate_aes_key()
        encrypted_data = encrypt_file(file_contents, aes_key)
        
        # Ensure encrypted_data is a proper JSON string, then encode to bytes
        if isinstance(encrypted_data, bytes):
            # If it's already bytes, decode it to string first so we can ensure consistent format
            encrypted_data = encrypted_data.decode('utf-8')
        
        # Convert to bytes before storing in the database
        encrypted_data_bytes = encrypted_data.encode('utf-8')
        
        # Encrypt the AES key with the RSA public key
        encrypted_aes_key = encrypt_aes_key(aes_key, unused_key.public_key)
        
        # Save to database - with encrypted_data as bytes
        new_file = UploadedFile(
            filename=file.filename,
            encrypted_data=encrypted_data_bytes,  # Now this is bytes
            aes_key=encrypted_aes_key,            # This should already be bytes
            key_id=unused_key.id,
            created_at=datetime.now()
        )
        
        # Mark the RSA key as used
        unused_key.is_used = True
        unused_key.used_at = datetime.now()
        
        # Commit changes to the database
        db.session.add(new_file)
        db.session.commit()
        
        logger.info(f"File '{file.filename}' uploaded and encrypted successfully")
        return render_template('success.html')
    
    except Exception as e:
        logger.error(f"Error during file upload: {e}")
        db.session.rollback()
        flash('An error occurred during upload. Please try again.')
        return redirect(url_for('main.upload'))

@main.route('/retrieve/<int:file_id>', methods=['GET'])
def retrieve_file(file_id):
    """API endpoint for journalists to retrieve encrypted files."""
    try:
        # Get the file from the database
        file = UploadedFile.query.get_or_404(file_id)
        
        # Get the corresponding key
        key = RSAKey.query.get_or_404(file.key_id)
        
        # Prepare the response
        response_data = {
            'id': file.id,
            'filename': file.filename,
            'key_id': file.key_id,
            'created_at': file.created_at.isoformat() if file.created_at else None
        }
        
        # Handle encrypted_data based on its type
        if isinstance(file.encrypted_data, bytes):
            response_data['encrypted_data'] = file.encrypted_data.decode('utf-8')
        else:
            response_data['encrypted_data'] = file.encrypted_data
            
        # Handle aes_key based on its type
        if isinstance(file.aes_key, bytes):
            response_data['encrypted_aes_key'] = base64.b64encode(file.aes_key).decode('utf-8')
        else:
            response_data['encrypted_aes_key'] = file.aes_key
            
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error retrieving file {file_id}: {e}")
        return jsonify({'error': 'File not found or error retrieving file'}), 404

@main.route('/files', methods=['GET'])
def list_files():
    """
    API endpoint for journalists to list all available files.
    This should only be accessed through the journalist client.
    """
    # Basic authentication could be added here
    
    try:
        files = UploadedFile.query.all()
        file_list = [{
            'id': file.id,
            'filename': file.filename,
            'key_id': file.key_id,
            'created_at': file.created_at.isoformat() if file.created_at else None
        } for file in files]
        
        return jsonify({
            'total': len(file_list),
            'files': file_list
        })
    
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return jsonify({'error': 'Error retrieving file list'}), 500

@main.route('/keys/status', methods=['GET'])
def key_status():
    """
    API endpoint to check the status of available encryption keys.
    This is used by both the web interface and journalist client.
    """
    try:
        total_keys = RSAKey.query.count()
        available_keys = RSAKey.query.filter_by(is_used=False).count()
        
        return jsonify({
            'total': total_keys,
            'available': available_keys,
            'used': total_keys - available_keys,
            'accepting_uploads': available_keys > 0
        })
    
    except Exception as e:
        logger.error(f"Error checking key status: {e}")
        return jsonify({'error': 'Error checking key status'}), 500

@main.route('/status', methods=['GET'])
def status():
    """General service status endpoint."""
    try:
        available_keys = RSAKey.query.filter_by(is_used=False).count()
        
        # Get the onion address if available
        onion_address = current_app.config.get('ONION_DOMAIN', 'Not available as Tor hidden service')
        
        return jsonify({
            'status': 'running',
            'available_keys': available_keys,
            'accepting_uploads': available_keys > 0,
            'onion_address': onion_address,
            'version': '0.1.0'
        })
    
    except Exception as e:
        logger.error(f"Error checking service status: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@main.route('/success')
def success():
    """Display success message after file upload."""
    return render_template('success.html')