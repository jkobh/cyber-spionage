import os
import json

keys_dict = {}
test_keys_dir = "test_keys"

# Für jede Datei im test_keys Verzeichnis
if os.path.exists(test_keys_dir):
    for filename in os.listdir(test_keys_dir):
        if filename.startswith("private_key_") and filename.endswith(".pem"):
            # Extrahiere die Schlüssel-ID aus dem Dateinamen
            key_id = filename.replace("private_key_", "").replace(".pem", "")
            
            # Lese den privaten Schlüssel
            with open(os.path.join(test_keys_dir, filename), 'r') as f:
                private_key = f.read()
                
            # Füge den Schlüssel zum Dictionary hinzu
            keys_dict[key_id] = private_key
    
    # Speichere das Dictionary als JSON
    with open("keys.json", 'w') as f:
        json.dump(keys_dict, f, indent=2)
    
    print(f"keys.json mit {len(keys_dict)} Schlüsseln erstellt.")
else:
    print(f"Verzeichnis {test_keys_dir} nicht gefunden.")