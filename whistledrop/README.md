# WhistleDrop - Secure Whistleblower Platform

---

# TEIL 1: BEDIENUNGSANLEITUNG

## 1. Installation und Voraussetzungen

### Systemvoraussetzungen
- Python 3.8 oder höher
- Tor-Dienst (installiert und konfiguriert)
- Internetverbindung

### Tor-Konfiguration
1. **Tor Browser installieren** von [https://www.torproject.org/download/](https://www.torproject.org/download/)
2. **Tor konfigurieren**: Bearbeiten Sie die `torrc`-Datei im Tor-Installationsverzeichnis und fügen Sie folgende Zeilen hinzu:
   ```
   ControlPort 9051
   CookieAuthentication 1
   ```
3. **Tor neustarten** um die Änderungen zu übernehmen

### WhistleDrop installieren
1. **Repository klonen oder entpacken**:
   ```bash
   git clone <repository-url>
   cd whistledrop
   ```
2. **Abhängigkeiten installieren**:
   ```bash
   pip install -r requirements.txt
   ```

## 2. Systemstart und Konfiguration

### Datenbank initialisieren
```bash
# Grundlegende Initialisierung
python manage.py init

# Initialisierung mit automatischer Schlüsselgenerierung
python manage.py init --with-keys --count 10
```

### Schlüssel verwalten
```bash
# Schlüsselstatus prüfen
python manage.py status

# Neue Schlüssel generieren (erstellt auch keys.json für Journalisten)
python manage.py generate --count 10

# Alle Schlüssel zurücksetzen und neue generieren
python manage.py generate --reset --count 10
```

### WhistleDrop-Server starten
```bash
python -m server.app
```

Nach dem Start zeigt der Server wichtige Informationen an:
- Die lokale URL (typischerweise http://127.0.0.1:5000)
- Die .onion-Adresse für den Zugriff über das Tor-Netzwerk
- Status der verfügbaren Schlüssel

## 3. Benutzerrollen und Anwendungsfälle

### Für Whistleblower
1. **Tor Browser öffnen** und zur angezeigten .onion-Adresse navigieren
2. Auf der Startseite **"Upload a Document" auswählen**
3. **Datei auswählen** und hochladen
4. Nach erfolgreichen Upload erscheint eine Bestätigungsseite

### Für Journalisten
#### Verfügbare Dateien anzeigen
```bash
python -m journalist.client list --server http://127.0.0.1:5000
```

#### Datei abrufen und entschlüsseln
```bash
python -m journalist.client retrieve --server http://127.0.0.1:5000 --keys keys.json --file-id 1 --output entschluesselt.txt
```

#### Serverstatus prüfen
```bash
python -m journalist.client status --server http://127.0.0.1:5000
```

## 4. Kommandoreferenz

### Datenbank-Management (manage.py)
| Befehl | Beschreibung | Parameter |
|--------|--------------|-----------|
| `init` | Initialisiert die Datenbank | `--with-keys`, `--count N` |
| `status` | Zeigt Status der Datenbank und Schlüssel | - |
| `generate` | Generiert neue RSA-Schlüsselpaare | `--count N`, `--reset` |
| `reset` | Setzt die Datenbank zurück | `--confirm`, `--with-keys` |
| `list` | Listet alle Dateien auf | - |
| `clear` | Entfernt alle hochgeladenen Dateien | `--confirm` |

### Journalist-Client
| Befehl | Beschreibung | Parameter |
|--------|--------------|-----------|
| `list` | Listet verfügbare Dateien auf | `--server URL` |
| `retrieve` | Ruft Datei ab und entschlüsselt sie | `--server URL`, `--keys FILE`, `--file-id ID`, `--output FILE` |
| `status` | Prüft Serverstatus | `--server URL` |

## 5. Fehlerbehebung

### Tor-Verbindungsprobleme
**Problem**: "Tor control connection failed"
**Lösungen**:
1. Tor-Konfiguration prüfen (`ControlPort 9051`, `CookieAuthentication 1`)
2. Tor neustarten

### Keine verfügbaren Schlüssel
**Problem**: "No available RSA keys!"
**Lösung**: `python manage.py generate --count 10`

### Entschlüsselungsfehler
**Lösung**: Neue Schlüssel generieren:
```bash
python manage.py reset --confirm --with-keys --count 10
```

## 6. Sicherheitshinweise

### Für Whistleblower
- **Verwenden Sie immer den Tor Browser**
- **Entfernen Sie Metadaten** aus Dokumenten
- **Schließen Sie den Browser** nach der Nutzung
- **Vermeiden Sie persönliche Geräte**

### Für Journalisten
- **Private Schlüssel sicher aufbewahren** (`keys.json`)
- **Entschlüsselte Dokumente sicher speichern**
- **Sichere Kommunikation** verwenden

---

# TEIL 2: PROJEKTDOKUMENTATION

## 1. Erklärung des Whistleblowing-Prozesses

### Überblick
WhistleDrop ist eine sichere, anonyme Plattform für Whistleblower, die sensible Informationen an Journalisten übermitteln möchten. Der Prozess basiert auf Ende-zu-Ende-Verschlüsselung und dem Tor-Netzwerk für maximale Anonymität.

### Prozessablauf

1. **Whistleblower-Zugang**
   - Zugriff über Tor Browser auf den WhistleDrop Hidden Service
   - Die .onion-Adresse gewährleistet vollständige Anonymität

2. **Datei-Upload**
   - Auswahl der zu übertragenden Datei
   - Unterstützte Formate: PDF, TXT, DOCX, XLSX, PNG, JPG
   - Maximale Dateigröße: 16MB

3. **Automatische Verschlüsselung**
   - Server generiert zufälligen AES-256 Schlüssel
   - Sofortige AES-Verschlüsselung der Datei
   - RSA-Verschlüsselung des AES-Schlüssels mit verfügbarem Public Key
   - Speicherung beider verschlüsselter Komponenten in der Datenbank

4. **Schlüssel-Management**
   - Markierung des verwendeten RSA-Public-Keys als "verwendet"
   - Einmalige Schlüsselverwendung für Forward Secrecy

5. **Journalist-Zugriff**
   - Client-Tool zum Auflisten verfügbarer Dateien
   - Abruf verschlüsselter Datei und AES-Schlüssel
   - RSA-Entschlüsselung des AES-Schlüssels mit Private Key
   - AES-Entschlüsselung der Datei

## 2. Systemarchitektur

### Komponenten-Übersicht

```
┌─────────────────┐    Tor Network    ┌─────────────────┐    Local Network     ┌─────────────────┐
│   Whistleblower │ ◄──────────────►  │ WhistleDrop     │ ◄──────────────────► │   Journalist    │
│                 │                   │ Server          │                      │                 │
│ - Tor Browser   │                   │ - Flask App     │                      │ - Client Tool   │
│ - File Upload   │                   │ - SQLite DB     │                      │ - Private Keys  │
│                 │                   │ - Crypto Module │                      │ - Decryption    │
└─────────────────┘                   └─────────────────┘                      └─────────────────┘
```

### Kryptographische Prozesse

```
Upload-Prozess:
Datei → AES-Verschlüsselung → Verschlüsselte Datei
        ↓
    AES-Schlüssel → RSA-Verschlüsselung (Public Key) → Verschlüsselter AES-Schlüssel
        
Datenbank-Speicherung:
[Verschlüsselte Datei] + [Verschlüsselter AES-Schlüssel] + [Schlüssel-ID]

Abruf-Prozess:
Verschlüsselter AES-Schlüssel → RSA-Entschlüsselung (Private Key) → AES-Schlüssel
                                                                          ↓
Verschlüsselte Datei ←─────────── AES-Entschlüsselung ←─────────────── AES-Schlüssel
        ↓
Original-Datei
```

### Datenbank-Schema

**RSA_Keys Tabelle:**
- id (Primary Key)
- public_key (RSA Public Key PEM)
- is_used (Boolean)
- used_at (Timestamp)
- created_at (Timestamp)

**Uploaded_Files Tabelle:**
- id (Primary Key)
- filename (Original filename)
- encrypted_data (AES encrypted file data)
- aes_key (RSA encrypted AES key)
- key_id (Foreign Key zu RSA_Keys)
- created_at (Timestamp)

## 3. Schlüsselmanagement

### Konzept
Hybride Verschlüsselung mit einmaliger Schlüsselverwendung für maximale Sicherheit:

### RSA-Schlüsselpaare
- **Generierung**: RSA-2048 Schlüsselpaare werden vorab generiert
- **Verteilung**: Public Keys → Server, Private Keys → Journalist
- **Einmalige Verwendung**: Jeder Public Key nur für einen Upload
- **Forward Secrecy**: Verwendete Keys werden als "verwendet" markiert

### AES-Schlüssel
- **Generierung**: Zufälliger AES-256 Schlüssel pro Upload
- **Verschlüsselung**: Mit verfügbarem RSA Public Key verschlüsselt
- **Speicherung**: Nur verschlüsselt in der Datenbank
- **Vernichtung**: Unverschlüsselter Schlüssel wird aus Speicher gelöscht

### Schlüssel-Workflow

```bash
# 1. Initialisierung - Generiert Schlüsselpaare
python manage.py generate --count 10

# 2. Upload-Prozess - Automatische Schlüsselwahl und -verwendung
# 3. Schlüssel-Rotation - Regelmäßige Erneuerung
```

## 4. Quellcode-Repository

Der vollständige Quellcode ist verfügbar unter:
**GitHub Repository**: https://github.com/[username]/whistledrop

### Projekt-Struktur
```
whistledrop/
├── server/           # Flask-Server und Tor-Integration
│   ├── app.py       # Hauptanwendung
│   ├── routes.py    # Web-Routen
│   ├── crypto.py    # Verschlüsselungslogik
│   ├── models.py    # Datenbankmodelle
│   └── tor_service.py # Tor Hidden Service
├── journalist/      # Journalist-Client
│   ├── client.py    # Client-Tool
│   └── crypto.py    # Entschlüsselungslogik
├── templates/       # HTML-Templates
├── static/         # CSS/JavaScript
├── manage.py       # Verwaltungsskript
└── requirements.txt # Python-Abhängigkeiten
```

## 5. Anforderungen aus Whistleblower-Sicht

### Primäre Anforderungen

**Anonymität und Schutz:**
- Vollständige Anonymität ohne Registrierung
- Tor Hidden Service für Netzwerk-Anonymität
- Keine Speicherung von IP-Adressen oder Metadaten
- Automatische Sicherheitswarnungen

**Benutzerfreundlichkeit:**
- Intuitive Web-Oberfläche
- Einfacher Upload-Prozess
- Klare Sicherheitsanweisungen
- Unterstützung verschiedener Dateiformate

**Sicherheit:**
- Ende-zu-Ende-Verschlüsselung ohne Benutzerinteraktion
- Sofortige Verschlüsselung nach Upload
- Sichere Schlüsselgenerierung
- Keine Server-seitige Entschlüsselung möglich

### Sekundäre Anforderungen

**Transparenz:**
- Open Source für Vertrauensbildung
- Dokumentierte Verschlüsselungsverfahren
- Regelmäßige Sicherheitsaudits

**Verfügbarkeit:**
- 24/7 Service-Verfügbarkeit
- Redundante Infrastruktur
- Schnelle Upload-Verarbeitung

## 6. Angriffsszenario und Gegenmaßnahmen

### Angriffsszenario: Server-Kompromittierung mit Traffic-Analyse

**Angriffspfad:**
1. **Server-Infiltration**: Angreifer erlangt Root-Zugriff auf WhistleDrop-Server
2. **Datenbank-Zugriff**: Zugriff auf verschlüsselte Dateien und Metadaten
3. **Traffic-Analyse**: Korrelation von Upload-Zeiten mit Tor-Traffic-Mustern
4. **Side-Channel-Attacks**: Timing-Angriffe auf Verschlüsselungsoperationen
5. **Metadaten-Analyse**: Kombination mit externen Datenquellen

**Potenzielle Auswirkungen:**
- Kompromittierung der Whistleblower-Anonymität
- Zugriff auf Upload-Metadaten (Zeiten, Dateigrößen)
- Mögliche Korrelation mit anderen Datenquellen

### Gegenmaßnahmen

**1. Server-Härtung:**
Rate-Limiting: Begrenzung der Anzahl von Upload-Versuchen pro Zeitraum, um Brute-Force-Angriffe und automatisierte Attacken zu verhindern. Dies schützt vor Denial-of-Service-Angriffen und verhindert, dass Angreifer das System durch massive Anfragen überlasten.

Sichere HTTP-Headers: Implementierung von Sicherheits-Headern, die Cross-Site-Scripting-Angriffe verhindern, das Einbetten der Seite in fremde Frames unterbinden und Content-Type-Sniffing-Attacken abwehren. Diese Maßnahmen schützen vor clientseitigen Angriffen.

**2. Anti-Traffic-Analysis:**
Dummy Traffic: Generierung von gefälschten Upload-Aktivitäten in regelmäßigen Abständen, um echte Whistleblower-Uploads zu verschleiern. Dies macht es für Angreifer schwierig, zwischen echten und falschen Aktivitäten zu unterscheiden.

Upload-Batching: Sammlung mehrerer Uploads und deren zeitgleiche Verarbeitung, um Timing-Korrelationen zu erschweren. Anstatt Uploads sofort zu verarbeiten, werden sie in Gruppen zusammengefasst.

Zeitliche Randomisierung: Einführung zufälliger Verzögerungen bei der Upload-Verarbeitung, um vorhersagbare Timing-Muster zu eliminieren und Traffic-Analyse zu erschweren.

**3. Enhanced Forward Secrecy:**
Automatische Schlüssel-Rotation: Regelmäßige Entfernung alter, verwendeter RSA-Schlüssel aus der Datenbank nach einer bestimmten Zeitspanne (z.B. 30 Tage). Dies stellt sicher, dass selbst bei einer Kompromittierung des Servers keine alten Kommunikationen entschlüsselt werden können.

Sichere Schlüssel-Vernichtung: Vollständige Löschung verwendeter Schlüssel aus dem System, anstatt sie nur als "verwendet" zu markieren, um das Risiko einer späteren Wiederherstellung zu minimieren.

**4. Sichere Speicherbehandlung:**
Memory Cleanup: Sicheres Überschreiben von Speicherinhalten mit Zufallsdaten, nachdem sensible Informationen wie AES-Schlüssel oder Dateiinhalte verarbeitet wurden. Dies verhindert, dass Angreifer durch Speicher-Dumps an sensible Daten gelangen.

Sofortige Löschung: Unmittelbare Entfernung temporärer Daten aus dem Arbeitsspeicher nach der Verschlüsselung, um die Zeitspanne zu minimieren, in der unverschlüsselte Daten im System vorhanden sind.

**5. Monitoring und Intrusion Detection:**
Anomalie-Erkennung: Kontinuierliche Überwachung des Systems auf ungewöhnliche Zugriffsmuster, wie beispielsweise ungewöhnlich hohe Upload-Frequenzen, verdächtige IP-Adressen oder abnormale Systemressourcen-Nutzung.

Automatische Benachrichtigung: Sofortige Alarmierung bei verdächtigen Aktivitäten, um schnelle Reaktionen auf potenzielle Sicherheitsvorfälle zu ermöglichen.

Integritätschecks: Regelmäßige Überprüfung der Datenbank-Integrität und der verschlüsselten Daten, um Manipulationen oder Korruption frühzeitig zu erkennen.

## 7. Prozess-Dokumentation

### Whistleblower-Upload-Prozess

**Schritt 1: Tor Browser-Zugang**
- Navigation zur .onion-Adresse
- Anzeige der Startseite mit Sicherheitsinformationen

**Schritt 2: Upload-Vorgang**
- Auswahl "Upload a Document"
- Dateiauswahl (z.B. `sensitive_document.pdf`)
- Upload-Button bestätigen
- Erfolgsbestätigung wird angezeigt

**Schritt 3: Server-seitige Verarbeitung**
```python
# Automatische Verschlüsselung (vereinfacht)
aes_key = generate_aes_key()  # 32 Byte Zufallsschlüssel
encrypted_data = encrypt_file(file_contents, aes_key)
encrypted_aes_key = encrypt_aes_key(aes_key, unused_key.public_key)

# Datenbank-Speicherung
new_file = UploadedFile(
    filename=file.filename,
    encrypted_data=encrypted_data_bytes,
    aes_key=encrypted_aes_key,
    key_id=unused_key.id
)
```

### Journalist-Abruf-Prozess

**Schritt 1: Dateien auflisten**
```bash
python -m journalist.client list --server http://127.0.0.1:5000
```
*Beispiel-Ausgabe:*
```
Found 1 files on the server:
--------------------------------------------------
ID: 1
Filename: sensitive_document.pdf
Uploaded: 2024-01-15T10:30:00
--------------------------------------------------
```

**Schritt 2: Datei abrufen und entschlüsseln**
```bash
python -m journalist.client retrieve \
  --server http://127.0.0.1:5000 \
  --keys keys.json \
  --file-id 1 \
  --output decrypted_document.pdf
```

**Schritt 3: Entschlüsselungsprozess**
```python
# Client-seitige Entschlüsselung
# 1. RSA-Entschlüsselung des AES-Schlüssels
private_key = keys[str(key_id)]
aes_key = decrypt_with_rsa(encrypted_aes_key, private_key)

# 2. AES-Entschlüsselung der Datei
decrypted_data = decrypt_file(encrypted_data, aes_key)

# 3. Speicherung der entschlüsselten Datei
with open(output_path, 'wb') as f:
    f.write(decrypted_data)
```

### Sicherheitsvalidierung

**Datenbank-Inspektion:**
```bash
python manage.py status
```
*Ausgabe zeigt verschlüsselte Daten:*
```
=== WhistleDrop Status ===
Database status: OK
Total RSA keys: 10
Available keys: 9
Used keys: 1
Uploaded files: 1

Key usage:
  Key ID 1: Used for file 'sensitive_document.pdf' on 2024-01-15 10:30:00
```

**Sicherheitsbestätigung:**
- ✅ Originaldatei nicht mehr im Arbeitsspeicher
- ✅ Nur verschlüsselte Daten in der Datenbank
- ✅ AES-Schlüssel existiert nur verschlüsselt
- ✅ Verwendeter RSA-Key als "verwendet" markiert

## 7 Doku Video

**Videolink:** 

## 8. Projektaufwand

**Gesamtaufwand**: 15 Stunden