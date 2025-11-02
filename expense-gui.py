import sys
import sqlite3
from contextlib import closing
from PyQt5.QtWidgets import *
from decimal import Decimal
from datetime import datetime


filenames = 'expense.json'
DB = "expense.db"

def create_connect ():
    return sqlite3.connect(DB)

def create_db ():
    with closing(create_connect()) as conn, conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT Null,                -- ISO string: YYYY-MM-DD
            amount TEXT NOT Null,
            category TEXT NOT Null,
            description TEXT
            )
        """)

def list_expense (filename: str = filenames) -> list:
    with closing(create_connect()) as conn, conn :
        cursor = conn.execute("""
            SELECT *
            FROM expenses
            ORDER BY datetime(date) DESC
            """)
        return cursor.fetchall()


def insert_db(amount: str = None, category: str = None, description: str = None) -> int :
    date = datetime.now().strftime("%Y-%m-%d")
    with closing(create_connect()) as conn, conn :
        cursor = conn.execute("""
            INSERT INTO expenses(date, amount, category, description)
            VALUES(?, ?, ?, ?)""", (date, amount, category, description))
        return cursor.lastrowid

def daily_sum(day: str):
    with closing(create_connect()) as conn :
        cursor = conn.execute("""
            SELECT
                COUNT(*) AS count,
                SUM(CAST(amount AS REAL)) AS Total
            FROM expenses
            WHERE substr(date, 1, 10) = ?
        """, (day, ))
        row = cursor.fetchone()
        count = row[0] or 0
        total = float(row[1] if row[1] is not None else 0.0)
        return total, count

class Window(QWidget):
    def __init__(self) :
        super().__init__()
        create_db()
        self.setWindowTitle("Expense Tracker")

        self.label = QLabel()
        self.label1 = QLabel()
        self.label2 = QLabel()

        self.expense_edit = QLineEdit()
        self.expense_edit.setPlaceholderText("Amount e.g. 13.99")

        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Description")

        self.date_input_edit = QLineEdit()
        self.date_input_edit.setPlaceholderText("Date in format YYYY-MM-DD")

        self.combo_box = QComboBox()
        self.combo_box.addItem("Select Category")
        self.combo_box.addItems(["Personal", "Home/Family", "Grocery", "Transport", "Bills", "Others"])

        self.currency_box = QComboBox()
        self.currency_box.addItem("Select your currency")
        self.currency_box.addItems(["CAD", "USD", "JPY", "EUR", "CNY", "THB", "SGD"])

        self.form = QFormLayout()
        self.form.addRow("Expense:", self.expense_edit)
        self.form.addRow("Description:", self.description_edit)
        self.form.addRow("Date for summary format YYYY-MM-DD", self.date_input_edit)


        self.button = QPushButton("Save")
        self.button.setCheckable(True)
        self.button.clicked.connect(self.clicked_saved)
        self.button.setMinimumWidth(120)
        self.button.setMinimumHeight(60)

        self.button1 = QPushButton("Summary")
        self.button1.setCheckable(True)
        self.button1.clicked.connect(self.clicked_summary)
        self.button1.setMinimumWidth(120)
        self.button1.setMinimumHeight(60)

        left = QVBoxLayout()
        left.addLayout(self.form)
        left.addWidget(self.combo_box)
        left.addWidget(self.currency_box)

        right = QHBoxLayout()
        right.addWidget(self.button)
        right.addWidget(self.button1)

        main = QVBoxLayout()
        main.addLayout(left)
        main.addLayout(right)
        main.addWidget(self.label)
        main.addWidget(self.label1)
        main.addWidget(self.label2)


        self.setLayout(main)

    def clicked_saved(self):
        amount_text = self.expense_edit.text().strip()
        description = self.description_edit.text().strip()
        category = self.combo_box.currentText()
        date = datetime.now().strftime("%Y-%m-%d")

        try:
            amount = str(amount_text)
            if amount == '0' :
                print('Invalid Amount')
        except (InvalidOperation, ValueError):
            QMessageBox.warning(self, "Invalid Amount", "Please Enter a valid amout")
            self.expense_edit.setFocus()
            return

        exp_dict = {
            "date" : date,
            "amount" : amount,
            "category" : category,
            "description" : description,
        }

        insert_db(amount, category, description)
        #Reset All Input field
        curr = self.currency_box.currentText()
        self.label.setText(f"Saved : {date}| {amount} {curr} | {category} | {description} |")
        self.expense_edit.clear()
        self.description_edit.clear()
        self.combo_box.setCurrentIndex(0)

    def clicked_summary(self):
        day = self.date_input_edit.text().strip()
        curr = self.currency_box.currentText()
        total, count = daily_sum(day)
        avg = total / count if count else 0.0
        if count == 0:
            self.label2.setText(f"No Transaction Record on {day}")
        else :
            self.label1.setText(f"Transaction Amount {count} | Amount Spend {total:.2f} {curr} | Average / Transaction {avg:.2f} {curr}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())

