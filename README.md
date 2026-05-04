# Geld-Tracker Android App

Eine Android-App mit Flutter, die dieselbe Funktionalität wie die PHP-Website bietet.

## Funktionalität

- **Login mit Passwort** - Sicherer Zugang zur App
- **Ausgaben erfassen** - Datum, Preis und Beschreibung eingeben
- **Monatsübersicht** - Alle Ausgaben nach Monaten sortiert (ohne Bargeldbezüge)
- **Bargeldbezug-Statistiken** - Anzahl und Summe der Bargeldbezüge pro Monat
- **Bearbeiten/Löschen** - Einträge können jederzeit angepasst werden
- **Lokale Datenspeicherung** - Alle Daten werden lokal auf dem Gerät gespeichert

## Architektur

- **Models** - `Expense` Klasse für Dateneinträge
- **Services** - `DataService` für lokale Speicherung mit SharedPreferences
- **Screens** - Verschiedene UI-Seiten:
  - `LoginScreen` - Passwort-Login
  - `HomeScreen` - Hauptübersicht mit Monatsstatistiken
  - `AddExpenseScreen` - Neue Ausgaben hinzufügen
  - `MonthScreen` - Detaillierte Monatsansicht
  - `EditExpenseScreen` - Bestehende Einträge bearbeiten

## Installation

1. Flutter SDK installieren
2. Android Studio mit Android SDK installieren
3. Dependencies installieren:
   ```bash
   flutter pub get
   ```
4. App starten:
   ```bash
   flutter run
   ```

## Datenmigration

Die App verwendet dasselbe JSON-Format wie die PHP-Website. Bestehende Daten können manuell migriert werden.

## Besonderheiten

- Preise werden auf 0.05 CHF gerundet (wie in der Original-Website)
- "Bezug" als Beschreibung wird als Bargeldbezug erkannt
- Monatliche Auswertungen schliessen Bargeldbezüge aus
- Moderne Material Design 3 UI
