Monitories.com ist ein lizenziertes IT-Management-Tool, das Unternehmen, Agenturen und Freiberuflern umfassende Analyse- und Überwachungsmöglichkeiten bietet. Es kombiniert Funktionen aus bestehenden Tools wie Wappalyzer, UptimeRobot und Burp Suite, erweitert durch KI-gestützte Analyse- und Vorschlagsfunktionen.

🚀 Funktionen

1. Systemanalyse:

Analyse von CMS-/Shop-Systemen und deren Versionen.

Analyse der Frontend- und Backend-Programmiersprachen.

Analyse von Integrationen (z. B. Google Tag Manager, Google Analytics, Matomo, Hotjar, Mouseflow).

2. Datenbankanalyse:

Analyse von Datenbanktypen und deren Versionen.

3. Serverüberwachung:

Server-Ping-Checks und Überwachung von Antwortzeiten.

Überprüfung der SSL-Zertifikate.

Sicherheitschecks: Offene Ports, Fehlkonfigurationen.

Überwachung der HTTP-Header und Compliance.

Automatisierte Backups und Wiederherstellung.

4. KI-Integration:

Generierung von Verbesserungsvorschlägen basierend auf den Analysen.

Proaktive Risikoanalysen und Performance-Optimierungen.

Automatische Benachrichtigungen per E-Mail und Push.

5. Admin UI:

Verwaltung der Preispakete, Benutzerlizenzen und Limits.

Statistiken über Nutzungsaktivität und Analysen.

Manuelle Anpassungen von Limits und Paketen.

🛠️ Technologien

Frontend:

React mit TypeScript

Tailwind CSS

Backend:

Node.js oder Python (FastAPI)

PostgreSQL

GraphQL

Zusätzlich:

Mollie-Integration

OpenAI für KI-gestützte Analysen

Redis für Caching

📦 Installation

Voraussetzungen

Node.js >= 16

PostgreSQL >= 13

Redis >= 6

Setup

Repository klonen:

git clone https://github.com/bow-ph/monitories.git
cd monitories

Abhängigkeiten installieren:

npm install

Umgebungsvariablen konfigurieren:
Erstelle eine .env-Datei mit den folgenden Variablen:

DATABASE_URL=postgresql://<user>:<password>@localhost/monitories_db
REDIS_URL=redis://localhost:6379
MOLLIE_API_KEY=<your_mollie_api_key>
OPENAI_API_KEY=<your_openai_api_key>

Datenbank migrieren:

npm run migrate

Entwicklungsserver starten:

npm run dev

📊 Lizenzierungsstufen & Preisgestaltung

Freelancer: Bis 50.000 Requests/Monat = 9,95 €

Agenturen/Unternehmen: Bis 100.000 Requests/Monat = 19,95 €

Enterprise: Individuelle Anfrage

Zusatzrequests: 10.000 Requests/Monat = 4,95 €

🤝 Beitrag leisten

Forke dieses Repository.

Erstelle einen neuen Branch (feature/my-feature).

Committe deine Änderungen (git commit -m 'Add my feature').

Push den Branch (git push origin feature/my-feature).

Öffne einen Pull-Request.

📧 Support

Für Fragen oder Unterstützung, kontaktiere uns unter support@monitories.com.

⚖️ Lizenz

Dieses Projekt steht unter der MIT-Lizenz.
