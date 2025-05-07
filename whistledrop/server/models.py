from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UploadedFile(db.Model):
    __tablename__ = 'uploaded_files'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    encrypted_data = db.Column(db.LargeBinary, nullable=False)
    aes_key = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, filename, encrypted_data, aes_key):
        self.filename = filename
        self.encrypted_data = encrypted_data
        self.aes_key = aes_key
        self.created_at = datetime.utcnow()  # TODO: Import datetime

class RSAKey(db.Model):
    __tablename__ = 'rsa_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    public_key = db.Column(db.Text, nullable=False, unique=True)
    is_used = db.Column(db.Boolean, default=False)

    def __init__(self, public_key):
        self.public_key = public_key
        self.is_used = False  # TODO: Implement logic for marking keys as used