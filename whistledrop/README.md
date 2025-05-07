# WhistleDrop - Anonymes Whistleblower-Plattform

WhistleDrop ist eine sichere Plattform, die es Whistleblowern ermöglicht, sensible Informationen anonym und verschlüsselt an Journalisten zu übermitteln. Die Anwendung nutzt moderne kryptographische Prinzipien und wird als Tor Hidden Service bereitgestellt.

## Projektstruktur

Die Projektstruktur ist wie folgt:

```
whistledrop
├── server
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   ├── models.py
│   ├── routes.py
│   ├── crypto.py
│   ├── tor_service.py
│   └── utils.py
├── journalist
│   ├── __init__.py
│   ├── client.py
│   ├── crypto.py
│   └── key_manager.py
├── templates
│   ├── index.html
│   ├── upload.html
│   └── success.html
├── static
│   ├── css
│   │   └── style.css
│   └── js
│       └── main.js
├── tests
│   ├── __init__.py
│   ├── test_crypto.py
│   └── test_app.py
├── .gitignore
├── README.md
├── requirements.txt
└── setup.py
```

## Installation

Um WhistleDrop lokal auszuführen, folgen Sie diesen Schritten:

1. Klonen Sie das Repository:
   ```
   git clone <repository-url>
   cd whistledrop
   ```

2. Installieren Sie die Abhängigkeiten:
   ```
   pip install -r requirements.txt
   ```

3. Starten Sie den Server:
   ```
   python -m server.app
   ```

## Nutzung

- Whistleblower können Dateien über die Upload-Seite hochladen.
- Journalisten können die hochgeladenen Dateien abrufen und entschlüsseln.

## Sicherheit

WhistleDrop verwendet AES für die symmetrische Verschlüsselung der hochgeladenen Dateien und RSA für das Schlüsselmanagement. Alle sensiblen Daten werden sicher gespeichert und nur verschlüsselt auf der Festplatte abgelegt.

## TODOs

- Implementierung der Serverinitialisierung und Routen in `server/app.py`.
- Definition der Konfigurationsvariablen in `server/config.py`.
- Implementierung der Datenmodelle in `server/models.py`.
- Implementierung der Routenhandler in `server/routes.py`.
- Implementierung der kryptographischen Funktionen in `server/crypto.py`.
- Implementierung des Tor-Dienstmanagements in `server/tor_service.py`.
- Implementierung von Hilfsfunktionen in `server/utils.py`.
- Implementierung der Client-Logik in `journalist/client.py`.
- Implementierung der RSA-Funktionen in `journalist/crypto.py`.
- Implementierung der Schlüsselmanagementfunktionen in `journalist/key_manager.py`.
- Gestaltung der HTML-Vorlagen in `templates/`.
- Definition der CSS-Stile in `static/css/style.css`.
- Implementierung der clientseitigen Skripte in `static/js/main.js`.
- Schreiben von Tests für die kryptographischen Funktionen in `tests/test_crypto.py`.
- Schreiben von Tests für die Anwendungslogik in `tests/test_app.py`.
- Definition der Paketmetadaten und Abhängigkeiten in `setup.py`.

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert. Weitere Informationen finden Sie in der LICENSE-Datei.