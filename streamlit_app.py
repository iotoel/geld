import streamlit as st
import json
import datetime
from typing import List, Dict, Any
import pandas as pd

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

# Datenverwaltung
class DataService:
    @staticmethod
    def get_expenses() -> List[Expense]:
        if 'expenses' not in st.session_state:
            st.session_state.expenses = []
        return st.session_state.expenses
    
    @staticmethod
    def save_expenses(expenses: List[Expense]):
        st.session_state.expenses = expenses
    
    @staticmethod
    def add_expense(expense: Expense) -> Expense:
        expenses = DataService.get_expenses()
        new_id = max([e.id for e in expenses], default=0) + 1
        new_expense = Expense(new_id, expense.date, expense.price, expense.description)
        expenses.append(new_expense)
        DataService.save_expenses(expenses)
        return new_expense
    
    @staticmethod
    def update_expense(expense: Expense):
        expenses = DataService.get_expenses()
        for i, e in enumerate(expenses):
            if e.id == expense.id:
                expenses[i] = expense
                break
        DataService.save_expenses(expenses)
    
    @staticmethod
    def delete_expense(expense_id: int):
        expenses = DataService.get_expenses()
        expenses = [e for e in expenses if e.id != expense_id]
        DataService.save_expenses(expenses)
    
    @staticmethod
    def get_password() -> str:
        return st.session_state.get('password', '')
    
    @staticmethod
    def set_password(password: str):
        st.session_state.password = password
    
    @staticmethod
    def is_password_set() -> bool:
        return bool(DataService.get_password())

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
            
            if not DataService.is_password_set():
                # Erster Start - Passwort setzen
                DataService.set_password(password)
                st.session_state.logged_in = True
                st.success("Passwort gesetzt! Willkommen beim Geld-Tracker.")
                st.rerun()
            elif DataService.get_password() == password:
                # Korrektes Passwort
                st.session_state.logged_in = True
                st.success("Login erfolgreich!")
                st.rerun()
            else:
                st.error("Falsches Passwort!")

# Hauptseite
def home_page():
    st.title("🏦 Geld-Tracker")
    
    # Logout Button
    if st.button("Logout", key="logout_btn"):
        st.session_state.logged_in = False
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
    
    # Seiten basierend auf Login-Status
    if not st.session_state.logged_in:
        login_page()
    else:
        if 'edit_expense_id' in st.session_state:
            edit_expense_page()
        else:
            home_page()

if __name__ == "__main__":
    main()
