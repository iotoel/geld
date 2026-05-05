# Geld-Tracker Streamlit App

Eine einfache Webanwendung zur Verwaltung von Ausgaben mit Passwort-Schutz und Email-Reset.

## 🚀 Schnellstart

1. **Dependencies installieren:**
   ```bash
   pip install -r requirements.txt
   ```

2. **App starten:**
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Erstkonfiguration:**
   - Öffnen Sie http://localhost:8501
   - Folgen Sie dem Setup-Assistenten
   - Konfigurieren Sie Email und Passwort

## 📋 Funktionen

- **🔐 Passwort-Schutz** - Sicherer Login
- **📧 Email-Reset** - Passwort per Email zurücksetzen
- **📊 Ausgaben verwalten** - Hinzufügen, Bearbeiten, Löschen
- **📈 Monatsübersicht** - Statistiken und Auswertungen
- **💾 Persistente Speicherung** - Daten bleiben erhalten

## 📁 Dateien

- `streamlit_app.py` - Hauptanwendung
- `requirements.txt` - Python-Dependencies
- `geld_data.json` - Datenbank (wird automatisch erstellt)
- `.gitignore` - Schützt sensible Dateien

## 🔧 Konfiguration

Die Erstkonfiguration erfolgt über den Setup-Assistenten:

- **Email-Einstellungen:** SMTP-Server, Sender-Email, App-Passwort
- **Admin-Email:** Für Passwort-Reset
- **App-Passwort:** Login-Passwort

**Wichtig:** Die Konfiguration wird nur einmal gespeichert und kann später nicht mehr geändert werden.

## 🚀 Deployment

### Streamlit Cloud
1. Code auf GitHub pushen
2. Auf Streamlit Cloud verbinden
3. `streamlit_app.py` als Hauptdatei festlegen

### Eigener Server
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py --server.port 8501
```

## 🔒 Sicherheit

- Passwörter und Email-Konfiguration werden lokal gespeichert
- Keine sensiblen Daten im Code
- Passwort-Reset nur per konfigurierte Email

## 📞 Support

Bei Problemen mit dem Email-Versand:
- Gmail: App-Passwort (nicht normales Passwort) verwenden
- 2-Faktor-Authentifizierung aktivieren
- SMTP-Port 587 prüfen
