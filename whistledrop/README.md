# WhistleDrop - Anonymes Whistleblower-Plattform

WhistleDrop ist eine sichere Plattform, die es Whistleblowern ermöglicht, sensible Informationen anonym und verschlüsselt an Journalisten zu übermitteln. Die Anwendung nutzt moderne kryptographische Prinzipien und wird als Tor Hidden Service bereitgestellt.

## Aufgabenstellung

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

## Projektstruktur

## Installation

Um WhistleDrop lokal auszuführen, folgen Sie diesen Schritten:

- Tor Browser installieren

torrc
Fügen Sie folgende Zeilen hinzu:
ControlPort 9051
CookieAuthentication 1


1. Klonen Sie das Repository:
   ```
   git clone <repository-url>
   cd whistledrop
   ```

2. Installieren Sie die Abhängigkeiten:
   ```
   pip install -r requirements.txt
   ```

3. Datenbank initialisieren
   ```
   python manage.py init
   ```

4. Testschlüssel generieren
   ```
   python manage.py generate --count 10
   ```

5. Schlüsselstatus überprüfen
   ```
   python manage.py status
   ```

6. Server starten
   ```
   python -m server.app
   ```

7. Seite Aufrufen
   ```
   http://127.0.0.1:5000
   ```

### Journalist-Client

#### Zeigen Sie alle verfügbaren Dateien an
python -m journalist.client list --server http://127.0.0.1:5000

#### Datei abrufen und entschlüsseln
python -m journalist.client retrieve --server http://127.0.0.1:5000 --file-id 1 --output entschluesselt.pdf --key-file privater_schluessel.pem



#### Checks the server status
python -m journalist.client status --server http://127.0.0.1:5000