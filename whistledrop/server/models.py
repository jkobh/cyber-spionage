from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class UploadedFile(db.Model):
    __tablename__ = 'uploaded_files'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    encrypted_data = db.Column(db.LargeBinary, nullable=False)
    aes_key = db.Column(db.LargeBinary, nullable=False)
    key_id = db.Column(db.Integer, db.ForeignKey('rsa_keys.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __init__(self, filename, encrypted_data, aes_key, key_id, created_at=None):
        self.filename = filename
        self.encrypted_data = encrypted_data
        self.aes_key = aes_key
        self.key_id = key_id
        self.created_at = created_at or datetime.now()
        
    def __repr__(self):
        return f'<UploadedFile {self.filename}>'

class RSAKey(db.Model):
    __tablename__ = 'rsa_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    public_key = db.Column(db.Text, nullable=False, unique=True)
    is_used = db.Column(db.Boolean, default=False, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    
    def __init__(self, public_key, is_used=False, used_at=None):
        self.public_key = public_key
        self.is_used = is_used
        self.used_at = used_at
        
    def __repr__(self):
        return f'<RSAKey {self.id} {"used" if self.is_used else "available"}>'