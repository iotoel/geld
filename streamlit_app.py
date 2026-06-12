import streamlit as st
import bcrypt

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    password = st.text_input("Passwort", type="password")

    if st.button("Anmelden"):
        stored_hash = st.secrets["PASSWORD_HASH"]

        if bcrypt.checkpw(
            password.encode(),
            stored_hash.encode()
        ):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Falsches Passwort")

    st.stop()

import json
import datetime
import os
from typing import List, Dict, Any
import pandas as pd

# Email-Konfiguration
class EmailService:
    def __init__(self):
        self.smtp_server = st.secrets.get("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(st.secrets.get("SMTP_PORT", 587))
        self.sender_email = st.secrets.get("SENDER_EMAIL", "")
        self.sender_password = st.secrets.get("SENDER_PASSWORD", "")
        self.admin_email = st.secrets.get("ADMIN_EMAIL", "")
    
    def is_configured(self) -> bool:
        """Prüft ob Email-Service konfiguriert ist"""
        return all([self.sender_email, self.sender_password, self.admin_email])
    
    def generate_password(self, length: int = 12) -> str:
        """Generiert ein sicheres Zufallspasswort"""
        import secrets
        import string
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(characters) for _ in range(length))
        return password
    
    def send_password_reset_email(self, new_password: str) -> bool:
        """Sendet Email mit neuem Passwort"""
        if not self.is_configured():
            return False
            
        try:
            import smtplib
            import ssl
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            message = MIMEMultipart("alternative")
            message["Subject"] = "🔐 Geld-Tracker - Passwort zurückgesetzt"
            message["From"] = self.sender_email
            message["To"] = self.admin_email
            
            # HTML Email
            html = f"""
            <html>
              <body>
                <h2>🏦 Geld-Tracker Passwort-Reset</h2>
                <p>Ihr Passwort wurde erfolgreich zurückgesetzt.</p>
                <div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px; margin: 20px 0;">
                  <h3>🔑 Neues Passwort:</h3>
                  <p style="font-family: monospace; font-size: 18px; color: #d63384;"><strong>{new_password}</strong></p>
                </div>
                <p><strong>Wichtige Hinweise:</strong></p>
                <ul>
                  <li>Bitte bewahren Sie dieses Passwort sicher auf</li>
                  <li>Ändern Sie es nach dem Login wenn gewünscht</li>
                  <li>Teilen Sie dieses Passwort mit niemandem</li>
                </ul>
                <hr>
                <p><small>Diese Email wurde automatisch generiert. Wenn Sie dies nicht angefordert haben, ignorieren Sie diese Nachricht.</small></p>
              </body>
            </html>
            """
            
            message.attach(MIMEText(html, "html"))
            
            # SSL-Kontext erstellen
            context = ssl.create_default_context()
            
            # Email senden
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, self.admin_email, message.as_string())
            
            return True
            
        except Exception as e:
            print(f"Fehler beim Senden der Email: {e}")
            return False


# Datenmodell für Ausgaben
class Expense:
    def __init__(self, id: int, date: datetime.date, price: float, description: str):
        self.id = id
        self.date = date
        self.price = price
        self.description = description
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'price': self.price,
            'desc': self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Expense':
        return cls(
            id=data['id'],
            date=datetime.datetime.strptime(data['date'], '%Y-%m-%d').date(),
            price=data['price'],
            description=data['desc']
        )
    
    @property
    def is_cash_withdrawal(self) -> bool:
        return self.description == 'Bezug'

# Datenverwaltung mit Datei-Persistenz
class DataService:
    DATA_FILE = "geld_data.json"
    
    @staticmethod
    def load_data() -> Dict[str, Any]:
        """Lädt alle Daten aus der JSON-Datei"""
        if os.path.exists(DataService.DATA_FILE):
            try:
                with open(DataService.DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {"expenses": []}
    
    @staticmethod
    def save_data(data: Dict[str, Any]):
        """Speichert alle Daten in die JSON-Datei"""
        try:
            with open(DataService.DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            st.error(f"Fehler beim Speichern der Daten: {e}")
    
    @staticmethod
    def get_expenses() -> List[Expense]:
        """Lädt Ausgaben aus der Datei"""
        data = DataService.load_data()
        return [Expense.from_dict(exp) for exp in data.get("expenses", [])]
    
    @staticmethod
    def save_expenses(expenses: List[Expense]):
        """Speichert Ausgaben in die Datei"""
        data = DataService.load_data()
        data["expenses"] = [exp.to_dict() for exp in expenses]
        DataService.save_data(data)
    
    @staticmethod
    def add_expense(expense: Expense) -> Expense:
        """Fügt neue Ausgabe hinzu"""
        expenses = DataService.get_expenses()
        new_id = max([e.id for e in expenses], default=0) + 1
        new_expense = Expense(new_id, expense.date, expense.price, expense.description)
        expenses.append(new_expense)
        DataService.save_expenses(expenses)
        return new_expense
    
    @staticmethod
    def update_expense(expense: Expense):
        """Aktualisiert bestehende Ausgabe"""
        expenses = DataService.get_expenses()
        for i, e in enumerate(expenses):
            if e.id == expense.id:
                expenses[i] = expense
                break
        DataService.save_expenses(expenses)
    
    @staticmethod
    def delete_expense(expense_id: int):
        """Löscht Ausgabe"""
        expenses = DataService.get_expenses()
        expenses = [e for e in expenses if e.id != expense_id]
        DataService.save_expenses(expenses)
    
    @staticmethod
    def get_password_hash() -> str:
        """Lädt lokalen Passwort-Hash aus der Datei"""
        data = DataService.load_data()
        return data.get("password_hash", "")

    @staticmethod
    def set_password_hash(password_hash: str):
        """Speichert einen Passwort-Hash lokal"""
        data = DataService.load_data()
        data["password_hash"] = password_hash
        DataService.save_data(data)

    @staticmethod
    def verify_password(password: str) -> bool:
        """Verifiziert das Passwort gegen Secrets oder lokale Datei"""
        stored_hash = st.secrets.get("PASSWORD_HASH", "")
        if stored_hash:
            try:
                if bcrypt.checkpw(password.encode(), stored_hash.encode()):
                    return True
            except ValueError:
                pass

        local_hash = DataService.get_password_hash()
        if local_hash:
            try:
                return bcrypt.checkpw(password.encode(), local_hash.encode())
            except ValueError:
                pass

        return False

    @staticmethod
    def reset_password(new_password: str):
        """Speichert ein neues Passwort lokal"""
        hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        DataService.set_password_hash(hashed)

    @staticmethod
    def change_password(old_password: str, new_password: str) -> bool:
        """Ändert das Passwort nur wenn das alte korrekt ist"""
        if DataService.verify_password(old_password):
            DataService.reset_password(new_password)
            return True
        return False
    
    @staticmethod
    def import_json_data(json_content: str) -> bool:
        """Importiert JSON-Daten und ersetzt vorhandene Daten"""
        try:
            # JSON parsen
            imported_data = json.loads(json_content)
            
            # Backup der aktuellen Daten erstellen
            current_data = DataService.load_data()
            backup_data = {
                "backup_timestamp": datetime.datetime.now().isoformat(),
                "backup_data": current_data
            }
            
            # Importierte Daten validieren
            if not DataService.validate_json_data(imported_data):
                return False
            
            # Backup speichern
            backup_filename = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_path = os.path.join(os.path.dirname(DataService.DATA_FILE), backup_filename)
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            # Importierte Daten speichern (wichtig: lokalen Passwort-Hash behalten)
            merged_data = imported_data.copy()

            if "password_hash" in current_data:
                merged_data["password_hash"] = current_data["password_hash"]

            DataService.save_data(merged_data)
            return True
            
        except Exception as e:
            print(f"Fehler beim Import: {e}")
            return False
    
    @staticmethod
    def validate_json_data(data: Dict[str, Any]) -> bool:
        """Validiert die importierten JSON-Daten"""
        try:
            # Grundstruktur prüfen
            if not isinstance(data, dict):
                return False
            
            # Expenses prüfen
            if "expenses" in data:
                expenses = data["expenses"]
                if not isinstance(expenses, list):
                    return False
                
                for expense in expenses:
                    if not isinstance(expense, dict):
                        return False
                    
                    # Benötigte Felder prüfen
                    required_fields = ["id", "date", "price", "desc"]
                    for field in required_fields:
                        if field not in expense:
                            return False
                    
                    # Datentypen prüfen
                    if not isinstance(expense["id"], int):
                        return False
                    if not isinstance(expense["price"], (int, float)):
                        return False
                    if not isinstance(expense["desc"], str):
                        return False
                    
                    # Datum prüfen
                    try:
                        datetime.datetime.fromisoformat(expense["date"].replace('Z', '+00:00'))
                    except:
                        return False
            
            return True
            
        except Exception:
            return False

# Hilfsfunktionen
def format_month(month_key: str) -> str:
    year, month = month_key.split('-')
    month_names = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
    return f'{month_names[int(month) - 1]} {year}'

def get_monthly_totals(expenses: List[Expense]) -> Dict[str, float]:
    monthly_totals = {}
    for expense in expenses:
        if expense.is_cash_withdrawal:
            continue
        month_key = f'{expense.date.year}-{expense.date.month:02d}'
        monthly_totals[month_key] = monthly_totals.get(month_key, 0) + expense.price
    return monthly_totals

def get_cash_stats(expenses: List[Expense]) -> Dict[str, Dict[str, Any]]:
    cash_stats = {}
    for expense in expenses:
        if not expense.is_cash_withdrawal:
            continue
        month_key = f'{expense.date.year}-{expense.date.month:02d}'
        if month_key not in cash_stats:
            cash_stats[month_key] = {'count': 0, 'sum': 0.0}
        cash_stats[month_key]['count'] += 1
        cash_stats[month_key]['sum'] += expense.price
    return cash_stats

def round_price(price: float) -> float:
    """Rundet Preis auf 0.05 CHF"""
    return round(price * 20) / 20

# Keine Setup-Seite mehr: Konfiguration über Streamlit Cloud Secrets

# Login-Seite
def login_page():
    st.title("🏦 Geld-Tracker")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("---")
        
        password = st.text_input("Passwort", type="password", key="login_password")
        
        if st.button("Login", use_container_width=True):
            if not password:
                st.error("Passwort darf nicht leer sein")
                return
            
            if DataService.verify_password(password):
                st.session_state.logged_in = True
                st.success("Login erfolgreich!")
                st.rerun()
            else:
                st.error("Falsches Passwort!")

        if not st.secrets.get("PASSWORD_HASH") and not DataService.get_password_hash():
            st.warning("🚨 Kein Login-Passwort gefunden. Bitte legen Sie das Secret PASSWORD_HASH in Streamlit Cloud an.")
        
        # Admin-Board Link
        st.markdown("---")
        st.markdown("🔐 [Admin-Board für Passwort-Verwaltung](?admin=1)")
        
        
# Admin-Board
def admin_board():
    st.title("🔐 Admin-Board")
    st.markdown("---")
    st.caption("Passwort-Verwaltung für den Geld-Tracker")
    
    email_service = EmailService()
    
    tab1, tab2 = st.tabs(["🔄 Passwort ändern", "🔑 Passwort vergessen"])
    
    with tab1:
        st.subheader("Passwort ändern (wenn Sie es kennen)")
        
        with st.form("change_password_form"):
            old_password = st.text_input("Altes Passwort", type="password")
            new_password = st.text_input("Neues Passwort", type="password")
            confirm_password = st.text_input("Passwort bestätigen", type="password")
            
            submitted = st.form_submit_button("🔄 Passwort ändern", use_container_width=True)
            
            if submitted:
                if not old_password or not new_password or not confirm_password:
                    st.error("Bitte alle Felder ausfüllen")
                elif new_password != confirm_password:
                    st.error("Neue Passwörter stimmen nicht überein")
                elif len(new_password) < 6:
                    st.error("Passwort muss mindestens 6 Zeichen lang sein")
                else:
                    if DataService.change_password(old_password, new_password):
                        st.success("✅ Passwort erfolgreich geändert!")
                        st.balloons()
                    else:
                        st.error("❌ Altes Passwort ist falsch")
    
    with tab2:
        st.subheader("Passwort vergessen (neues Passwort anfordern)")
        
        if email_service.is_configured():
            st.info(f"📧 Neues Passwort wird an: **{email_service.admin_email}**")
            st.success("✅ Email-Service konfiguriert")
            
            if st.button("📧 Neues Passwort per Email senden", use_container_width=True):
                with st.spinner("Generiere neues Passwort und sende Email..."):
                    new_password = email_service.generate_password()
                    
                    if email_service.send_password_reset_email(new_password):
                        DataService.reset_password(new_password)
                        st.success("✅ Email wurde erfolgreich gesendet!")
                        st.info("📧 Bitte überprüfen Sie Ihr Email-Postfach.")
                    else:
                        st.error("❌ Fehler beim Senden der Email!")
                        st.warning("⚠️ Passwort wurde nicht geändert. Bitte prüfen Sie die Email-Konfiguration und das SENDER_PASSWORD Secret.")
        else:
            st.error("❌ Email-Service nicht konfiguriert")
            st.warning("⚠️ Bitte legen Sie die erforderlichen Secrets in Streamlit Cloud an: SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD, ADMIN_EMAIL")
        
        st.markdown("---")
        st.caption("💡 Die Email-Konfiguration wird über Streamlit Cloud Secrets verwaltet.")
    
# Hauptseite
def home_page():
    st.title("🏦 Geld-Tracker")
    
    # Navigation
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Logout", key="logout_btn"):
            st.session_state.logged_in = False
            st.rerun()
    with col2:
        if st.button("🔐 Admin-Board", key="admin_btn"):
            st.session_state.show_admin = True
            st.rerun()
    
    expenses = DataService.get_expenses()
    
    # Neue Ausgabe erfassen
    with st.expander("📝 Neue Ausgabe erfassen", expanded=True):
        with st.form("add_expense_form"):
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input("Datum", datetime.date.today())
                price = st.number_input("Preis (CHF)", min_value=0.0, step=0.05, format="%.2f")
            with col2:
                description = st.text_input("Beschreibung")
            
            submitted = st.form_submit_button("Ausgabe hinzufügen", use_container_width=True)
            if submitted and description:
                rounded_price = round_price(price)
                new_expense = Expense(0, date, rounded_price, description)
                DataService.add_expense(new_expense)
                st.success(f"Ausgabe von {rounded_price:.2f} CHF hinzugefügt!")
                expenses = DataService.get_expenses()
                st.rerun()
    
    # Monatsübersicht
    st.markdown("---")
    st.subheader("📊 Monatsübersicht (ohne Bargeldbezüge)")
    
    monthly_totals = get_monthly_totals(expenses)
    if monthly_totals:
        sorted_months = sorted(monthly_totals.keys(), reverse=True)
        
        for month in sorted_months:
            total = monthly_totals[month]
            color = "🔴" if total < 0 else "🟢"
            st.markdown(f"### {color} {format_month(month)}: {total:.2f} CHF")
            
            # Details für diesen Monat
            month_expenses = [e for e in expenses 
                            if f'{e.date.year}-{e.date.month:02d}' == month 
                            and not e.is_cash_withdrawal]
            
            if month_expenses:
                df = pd.DataFrame([
                    {
                        'Datum': e.date.strftime('%d.%m.%Y'),
                        'Beschreibung': e.description,
                        'Preis': f"{e.price:.2f} CHF"
                    }
                    for e in sorted(month_expenses, key=lambda x: x.date, reverse=True)
                ])
                st.dataframe(df, use_container_width=True)
                
                # Bearbeiten/Löschen Optionen
                selected_expense = st.selectbox(
                    "Ausgabe bearbeiten/löschen:",
                    options=[(e.id, f"{e.date.strftime('%d.%m.%Y')} - {e.description} ({e.price:.2f} CHF)") 
                            for e in month_expenses],
                    format_func=lambda x: x[1],
                    key=f"select_{month}"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Bearbeiten", key=f"edit_{month}"):
                        st.session_state.edit_expense_id = selected_expense[0]
                        st.rerun()
                with col2:
                    if st.button("Löschen", key=f"delete_{month}"):
                        DataService.delete_expense(selected_expense[0])
                        st.success("Ausgabe gelöscht!")
                        st.rerun()
    else:
        st.info("Keine Ausgaben vorhanden")
    
    # Bargeldbezüge
    st.markdown("---")
    st.subheader("💵 Bargeldbezüge")
    
    cash_stats = get_cash_stats(expenses)
    if cash_stats:
        sorted_cash_months = sorted(cash_stats.keys(), reverse=True)
        
        cash_data = []
        for month in sorted_cash_months:
            stats = cash_stats[month]
            cash_data.append({
                'Monat': format_month(month),
                'Anzahl': stats['count'],
                'Summe': f"{stats['sum']:.2f} CHF"
            })
        
        df_cash = pd.DataFrame(cash_data)
        st.dataframe(df_cash, use_container_width=True)
    else:
        st.info("Keine Bargeldbezüge vorhanden")

# Ausgabe bearbeiten
def edit_expense_page():
    st.title("✏️ Ausgabe bearbeiten")
    
    if 'edit_expense_id' not in st.session_state:
        st.warning("Keine Ausgabe zum Bearbeiten ausgewählt")
        return
    
    expenses = DataService.get_expenses()
    expense = next((e for e in expenses if e.id == st.session_state.edit_expense_id), None)
    
    if not expense:
        st.error("Ausgabe nicht gefunden")
        return
    
    with st.form("edit_expense_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Datum", expense.date)
            price = st.number_input("Preis (CHF)", min_value=0.0, step=0.05, format="%.2f", value=expense.price)
        with col2:
            description = st.text_input("Beschreibung", expense.description)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.form_submit_button("Speichern", use_container_width=True):
                rounded_price = round_price(price)
                updated_expense = Expense(expense.id, date, rounded_price, description)
                DataService.update_expense(updated_expense)
                st.success("Ausgabe aktualisiert!")
                del st.session_state.edit_expense_id
                st.rerun()
        with col2:
            if st.form_submit_button("Abbrechen", use_container_width=True):
                del st.session_state.edit_expense_id
                st.rerun()

# Haupt-App
def main():
    # Session State initialisieren
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'show_admin' not in st.session_state:
        st.session_state.show_admin = False
    
    # Admin-Board über URL-Parameter erreichbar
    if 'admin' in st.query_params:
        st.session_state.show_admin = True
    
    # Seiten basierend auf Login-Status
    if st.session_state.get('show_admin', False):
        admin_board()
        if st.button("🏠 Zurück zum Login"):
            st.session_state.show_admin = False
            st.query_params.clear()
            st.rerun()
    elif not st.session_state.logged_in:
        login_page()
    elif 'edit_expense_id' in st.session_state:
        edit_expense_page()
    else:
        home_page()

if __name__ == "__main__":
    main()
