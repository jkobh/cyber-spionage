from journalist.crypto import create_keypair_json
from server.app import create_app
from server.models import db, RSAKey, UploadedFile
import os

# Generiere und speichere Schlüsselpaare
key_pairs = create_keypair_json(count=10, output_path="keys.json")
print(f"Generierte {len(key_pairs)} RSA-Schlüsselpaare und speicherte sie in keys.json")

# Speichere die öffentlichen Schlüssel in der Datenbank
app = create_app()
with app.app_context():
    # Alle Dateien in der Datenbank anzeigen
    files = UploadedFile.query.all()
    print(f"Gefundene Dateien: {len(files)}")
    
    for file in files:
        print(f"ID: {file.id}")
        print(f"Filename: {file.filename}")
        print(f"Key ID: {file.key_id}")
        print(f"Bytes in encrypted_data: {len(file.encrypted_data) if file.encrypted_data else 'None'}")
        print(f"Bytes in aes_key: {len(file.aes_key) if file.aes_key else 'None'}")
        print("-" * 40)
    
    # Lösche bestehende Schlüssel
    RSAKey.query.delete()
    db.session.commit()
    
    # Füge neue Schlüssel hinzu
    for key_id, private_key in key_pairs.items():
        # Extrahiere den öffentlichen Schlüssel
        from Crypto.PublicKey import RSA
        key = RSA.import_key(private_key)
        public_key = key.publickey().export_key().decode('utf-8')
        
        # Speichere in der Datenbank - ohne id zu setzen
        new_key = RSAKey(public_key=public_key, is_used=False)
        db.session.add(new_key)
    
    db.session.commit()
    print("Öffentliche Schlüssel in der Datenbank aktualisiert")
    
    # Jetzt müssen wir die IDs der Schlüssel abrufen, um die keys.json zu aktualisieren
    keys = RSAKey.query.all()
    updated_keys = {}
    
    for i, key in enumerate(keys):
        # Extrahiere den privaten Schlüssel aus unserem ursprünglichen Dictionary
        # using the positional index since we can't rely on the auto-generated IDs
        if str(i+1) in key_pairs:
            private_key = key_pairs[str(i+1)]
            # Speichere mit der tatsächlichen DB-ID
            updated_keys[str(key.id)] = private_key
    
    # Überschreibe die vorherige keys.json mit den aktualisierten IDs
    with open("keys.json", 'w') as f:
        import json
        json.dump(updated_keys, f, indent=2)
    
    print(f"keys.json mit {len(updated_keys)} Schlüsseln aktualisiert (IDs angepasst an Datenbank)")