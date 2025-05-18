# WhistleDrop - Ausführliche Bedienungsanleitung

## Inhaltsverzeichnis

1. Einführung
2. Installation und Voraussetzungen
3. Systemstart und Konfiguration
4. Benutzerrollen und Anwendungsfälle
5. Komplette Kommandoreferenz
6. Fehlerbehebung
7. Sicherheitshinweise

## 1. Einführung

WhistleDrop ist eine sichere Plattform für Whistleblower, die sensible Informationen anonym und verschlüsselt an Journalisten übermitteln möchten. Die Anwendung wurde entwickelt, um höchste Sicherheits- und Anonymitätsstandards zu erfüllen und nutzt:

- **Ende-zu-Ende-Verschlüsselung** mit AES und RSA
- **Tor Hidden Service** für maximale Anonymität
- **Einmalige Schlüsselverwendung** zur Erhöhung der Sicherheit
- **Keine Speicherung von Metadaten** oder persönlichen Informationen

## 2. Installation und Voraussetzungen

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

## 3. Systemstart und Konfiguration

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

## 4. Benutzerrollen und Anwendungsfälle

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

## 5. Komplette Kommandoreferenz

### Datenbank-Management (manage.py)

| Befehl | Beschreibung | Parameter |
|--------|--------------|-----------|
| `init` | Initialisiert die Datenbank und erstellt alle erforderlichen Tabellen | `--with-keys`: Generiert Schlüssel nach der Initialisierung<br>`--count N`: Anzahl der zu generierenden Schlüssel (Standard: 5) |
| `status` | Zeigt den Status der Datenbank, verfügbare Schlüssel und hochgeladene Dateien | - |
| `generate` | Generiert neue RSA-Schlüsselpaare | `--count N`: Anzahl der zu generierenden Schlüssel (Standard: 5)<br>`--reset`: Löscht vorhandene Schlüssel vor der Generierung |
| `reset` | Setzt die Datenbank zurück (löscht alle Tabellen und erstellt sie neu) | `--confirm`: Bestätigt die Datenbankzurücksetzung<br>`--with-keys`: Generiert Schlüssel nach dem Zurücksetzen<br>`--count N`: Anzahl der zu generierenden Schlüssel |
| `list` | Listet alle Dateien in der Datenbank auf | - |
| `clear` | Entfernt alle hochgeladenen Dateien und setzt die Schlüsselverwendung zurück | `--confirm`: Bestätigt die Dateientfernung |

### Server-Befehle

| Befehl | Beschreibung |
|--------|--------------|
| `python -m server.app` | Startet den WhistleDrop-Server |

### Journalist-Client (`journalist.client`)

| Befehl | Beschreibung | Parameter |
|--------|--------------|-----------|
| `list` | Listet alle verfügbaren Dateien auf dem Server auf | `--server URL`: URL des WhistleDrop-Servers |
| `retrieve` | Ruft eine Datei ab und entschlüsselt sie | `--server URL`: URL des WhistleDrop-Servers<br>`--keys FILE`: Pfad zur JSON-Datei mit den privaten Schlüsseln<br>`--file-id ID`: ID der abzurufenden Datei<br>`--output FILE`: Ausgabepfad für die entschlüsselte Datei |
| `status` | Prüft den Status des WhistleDrop-Servers | `--server URL`: URL des WhistleDrop-Servers |

### Vollständiger Workflow mit Befehlen

```bash
# 1. Datenbank und Schlüssel initialisieren
python manage.py reset --confirm --with-keys --count 10

# 2. Status prüfen
python manage.py status

# 3. Server starten
python -m server.app

# 4. (Whistleblower) Datei über Web-Interface hochladen
# Navigiere im Tor Browser zu der angezeigten .onion Adresse

# 5. (Journalist) Verfügbare Dateien auflisten
python -m journalist.client list --server http://127.0.0.1:5000

# 6. (Journalist) Datei abrufen und entschlüsseln
python -m journalist.client retrieve --server http://127.0.0.1:5000 --keys keys.json --file-id 1 --output entschluesselt.txt
```

## 6. Fehlerbehebung

### Tor-Verbindungsprobleme

**Problem**: "Tor control connection failed"

**Lösungen**:
1. Stellen Sie sicher, dass Tor läuft: `tor --verify-config` (Linux/macOS)
2. Überprüfen Sie, ob die Zeilen `ControlPort 9051` und `CookieAuthentication 1` in Ihrer torrc-Datei stehen
3. Starten Sie Tor neu

### Keine verfügbaren Schlüssel

**Problem**: "No available RSA keys! Uploads will fail until keys are added."

**Lösung**: Neue Schlüssel generieren:
```bash
python manage.py generate --count 10
```

### Entschlüsselungsfehler

**Problem**: "Error decrypting with RSA: Incorrect decryption."

**Lösung**: Die keys.json muss zu den Schlüsseln in der Datenbank passen. Generieren Sie neue Schlüssel:
```bash
python manage.py reset --confirm --with-keys --count 10
```

### Datenbankfehler

**Lösung**: Datenbank zurücksetzen und neu initialisieren:
```bash
python manage.py reset --confirm
python manage.py init
```

## 7. Sicherheitshinweise

### Für Whistleblower

- **Verwenden Sie immer den Tor Browser** für maximale Anonymität
- **Entfernen Sie Metadaten** aus Dokumenten vor dem Hochladen
- **Schließen Sie den Browser** nach der Nutzung und löschen Sie den Browserverlauf
- **Vermeiden Sie die Nutzung persönlicher Geräte** für sensible Uploads

### Für Systemadministratoren

- **Private Schlüssel sicher aufbewahren**: Die `keys.json`-Datei enthält die privaten Schlüssel und sollte sicher verwahrt werden
- **Regelmäßige Sicherheitsaudits** durchführen
- **Tor und alle Komponenten aktualisieren**
- **In Produktionsumgebungen** zusätzliche Sicherheitsmaßnahmen implementieren:
  - HTTPS für lokale Verbindungen
  - Härtung des Servers
  - Regelmäßige Backups der verschlüsselten Daten

### Für Journalisten

- **Private Schlüssel schützen**: Der Zugriff auf `keys.json` sollte streng kontrolliert werden
- **Entschlüsselte Dokumente sicher speichern**: Nach dem Abrufen sind die Daten nicht mehr verschlüsselt
- **Sichere Kommunikation** mit Quellen und anderen Journalisten verwenden

---

Diese Anleitung bietet einen umfassenden Überblick über die Installation, Konfiguration und Verwendung von WhistleDrop. Bei spezifischen Fragen oder Problemen konsultieren Sie die Projektdokumentation oder wenden Sie sich an das Entwicklungsteam.


# Aufgabenstellung

Whistleblower-Plattform
Im Rahmen dieses Projekts entwickeln Sie ein sicheres Konzept und eine
prototypische Implementierung einer anonymen Whistleblower-Plattform
namens WhistleDrop, die als Tor Hidden Service bereitgestellt wird. Ziel ist
es, sensible Informationen verschlüsselt zwischen einem anonymen
Whistleblower und einem Journalisten zu übertragen – unter Einhaltung
moderner kryptographischer Prinzipien und unter Berücksichtigung
praktischer Aspekte der digitalen Geheimhaltung.

Es gibt in WhistleDrop drei Entitäten, die in der folgenden Tabelle dargestellt
werden:

| Entität | Erklärung |
|---|---|
| Whistleblower | Der Whistleblower lädt eine Datei, z. B. eine PDF-Datei mit Metadaten, über den Hidden Service hoch. Der WhistleDrop-Server verschlüsselt die Datei unmittelbar nach dem Upload mit einem zufällig generierten symmetrischen Schlüssel. |
| WhistleDrop-Server | Auf dem WhistleDrop-Server, der als Hidden Service im Tor-Netzwerk angeboten wird, werden die symmetrischen Schlüssel nur verschlüsselt gespeichert. Diese Schlüssel stammen aus einer Datenbank, die nur die öffentlichen Schlüssel von RSA-Schlüsselpaaren enthält. Die dazugehörigen privaten Schlüssel befinden sich ausschließlich beim Journalisten. |
| Journalist | Die über das Tor-Netzwerk hochgeladenen Daten können nur von dem Journalisten entschlüsselt werden. Bei ihm befindet sich die Datenbank mit den vollständigen RSA-Schlüsselpaaren. |

Entwickeln Sie ein sicheres xkryptographisches Konzept zur automatischen
Ende-zu-Ende-Verschlüsselung der hochgeladenen Dateien. Die
symmetrischen AES-Schlüssel, die beim Upload auf dem WhistleDrop-Server
generiert und zum Verschlüsseln der hochgeladenen Daten verwendet werden,
dürfen niemals unverschlüsselt auf die Festplatte geschrieben werden. Auch
die hochgeladenen Daten dürfen nur verschlüsselt auf die Festplatte
geschrieben werden.

Definieren Sie ein passendes Verfahren zum Schlüsselmanagement:
- Die Datenbank beim Journalisten enthält mehrere RSA-Schlüsselpaare.
- Nur die öffentlichen Schlüssel werden in der Datenbank auf dem
WhistleDrop-Server gespeichert.
- Jeder der öffentlichen Schlüssel darf beim Upload nur einmal verwendet
werden.
- Der verwendete Schlüssel wird markiert oder aus der Datenbank entfernt.
- Die zugehörigen privaten Schlüssel befinden sich ausschließlich beim
Journalisten.

Die Plattform soll in der Programmiersprache Python entwickelt werden.
Dokumentieren Sie Ihr Projekt in einem PDF-Dokument, das die folgenden
Informationen enthält:
- Eine Erklärung des Whistleblowing-Prozesses mit WhistleDrop.
- Eine grafische Darstellung der Systemarchitektur. Diese soll die
Interaktionen der drei Entitäten und die kryptographischen
Prozesse zeigen.
- Eine Erklärung des Schlüsselmanagements.
- Den Quellcode von WhistleDrop, z. B. als Link zu einem GitHub-
Repository.
- Denken Sie wie ein Whistleblower: Was würden Sie von einer solchen
Plattform erwarten? Dokumentieren Sie Ihre Überlegungen bzw.
Anforderungen an die Plattform.
- Überlegen Sie sich ein Szenario, wie ein Angreifer WhistleDrop
attackieren könnte und schlagen Sie eine Gegenmaßnahme vor.
- Dokumentieren Sie mit Screenshots und Text oder in Videoform, wie
eine PDF-Datei über WhistleDrop als Hidden Service im Tor-Netzwerk
hochgeladen wird, wie diese Datei automatisch verschlüsselt und
gespeichert wird und wie ein Journalist die Datei abruft und entschlüsselt.
- Geben Sie den kumulierten Zeitaufwand aller Gruppenmitglieder für
dieses Projekt an.