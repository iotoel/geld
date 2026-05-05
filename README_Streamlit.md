# Geld-Tracker Streamlit App

Eine Streamlit-Webanwendung mit derselben Funktionalität wie die Flutter-App.

## Funktionalität

- **Login mit Passwort** - Sicherer Zugang zur App
- **Ausgaben erfassen** - Datum, Preis und Beschreibung eingeben
- **Monatsübersicht** - Alle Ausgaben nach Monaten sortiert (ohne Bargeldbezüge)
- **Bargeldbezug-Statistiken** - Anzahl und Summe der Bargeldbezüge pro Monat
- **Bearbeiten/Löschen** - Einträge können jederzeit angepasst werden
- **Daten im Session State** - Alle Daten werden in der Streamlit-Session gespeichert

## Installation

1. Python 3.8+ installieren
2. Dependencies installieren:
   ```bash
   pip install -r requirements.txt
   ```
3. App starten:
   ```bash
   streamlit run streamlit_app.py
   ```

## Deployment

### Streamlit Cloud Deployment

1. Code auf GitHub pushen
2. Auf [Streamlit Cloud](https://share.streamlit.io/) gehen
3. Repository auswählen und `streamlit_app.py` als Hauptdatei festlegen
4. Dependencies werden automatisch aus `requirements.txt` installiert

### Lokaler Test

```bash
# App starten
streamlit run streamlit_app.py

# Browser öffnet sich automatisch auf http://localhost:8501
```

## Besonderheiten

- Preise werden auf 0.05 CHF gerundet (wie in der Original-App)
- "Bezug" als Beschreibung wird als Bargeldbezug erkannt
- Monatliche Auswertungen schliessen Bargeldbezüge aus
- Moderne Streamlit UI mit Expander und Formularen
- Responsive Design für Desktop und Mobile

## Datenpersistenz

Für die produktive Verwendung können Sie folgende Optionen für die Datenspeicherung in Betracht ziehen:

1. **Session State** (aktuell) - Daten gehen verloren beim Neustart
2. **File Storage** - JSON-Datei auf dem Server
3. **Database** - SQLite, PostgreSQL etc.
4. **Cloud Storage** - Firebase, Supabase etc.

Um die Datenpersistenz zu verbessern, können Sie die `DataService` Klasse entsprechend anpassen.
