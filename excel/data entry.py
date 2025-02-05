import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
from datetime import datetime
import re

class ExpenseSystem:
    def __init__(self):
        # Database path
        self.db_path = "C:\\Users\\aldog\\OneDrive\\Desktop\\Expenses data base\\expenses.db"
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Categories and payment methods
        self.categories = [
            "Housing", "Transportation", "Food", "Utilities",
            "Healthcare", "Entertainment", "Shopping", "Others"
        ]
        
        self.payment_methods = {
            "American Express (AMEX)": {"interest_rate": 25.66},
            "Capital One": {"interest_rate": 29.80},
            "Schools First Credit Card": {"interest_rate": 16.75},
            "Debit Card": {"interest_rate": 0},
            "Cash": {"interest_rate": 0}
        }
        
        # Initialize database
        self.setup_database()
        
    def setup_database(self):
        """Create database and table if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                amount REAL NOT NULL,
                payment_method TEXT,
                interest_rate REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()

    def add_expense(self, date, category, description, amount, payment_method):
        """Add a new expense to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get interest rate for the payment method
        interest_rate = self.payment_methods[payment_method]["interest_rate"]
        
        cursor.execute('''
            INSERT INTO expenses (
                date, category, description, amount, payment_method, 
                interest_rate
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (date, category, description, amount, payment_method, interest_rate))
        
        conn.commit()
        conn.close()

class ExpenseEntry:
    def __init__(self):
        self.expense_system = ExpenseSystem()
        self.setup_gui()

    def validate_date(self, date_str):
        """Validate date format DD-MM-YYYY"""
        try:
            # Check if the format matches DD-MM-YYYY
            if not re.match(r'^\d{2}-\d{2}-\d{4}$', date_str):
                return False
            
            # Parse the date string
            day, month, year = map(int, date_str.split('-'))
            
            # Create datetime object to validate the date
            datetime(year, month, day)
            
            return True
        except ValueError:
            return False

    def setup_gui(self):
        """Create GUI for expense entry"""
        self.root = tk.Tk()
        self.root.title("Expense Entry System")
        self.root.geometry("600x400")

        # Create main frame
        input_frame = ttk.Frame(self.root, padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Date entry with format instruction
        ttk.Label(input_frame, text="Date (DD-MM-YYYY):").grid(row=0, column=0, sticky=tk.W)
        self.date_entry = ttk.Entry(input_frame)
        self.date_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        current_date = datetime.now().strftime('%d-%m-%Y')
        self.date_entry.insert(0, current_date)

        # Category dropdown
        ttk.Label(input_frame, text="Category:").grid(row=1, column=0, sticky=tk.W)
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(input_frame, textvariable=self.category_var)
        self.category_dropdown['values'] = self.expense_system.categories
        self.category_dropdown.grid(row=1, column=1, sticky=(tk.W, tk.E))

        # Description entry
        ttk.Label(input_frame, text="Description:").grid(row=2, column=0, sticky=tk.W)
        self.description_entry = ttk.Entry(input_frame)
        self.description_entry.grid(row=2, column=1, sticky=(tk.W, tk.E))

        # Amount entry
        ttk.Label(input_frame, text="Amount:").grid(row=3, column=0, sticky=tk.W)
        self.amount_entry = ttk.Entry(input_frame)
        self.amount_entry.grid(row=3, column=1, sticky=(tk.W, tk.E))

        # Payment method dropdown
        ttk.Label(input_frame, text="Payment Method:").grid(row=4, column=0, sticky=tk.W)
        self.payment_var = tk.StringVar()
        self.payment_dropdown = ttk.Combobox(input_frame, textvariable=self.payment_var)
        self.payment_dropdown['values'] = list(self.expense_system.payment_methods.keys())
        self.payment_dropdown.grid(row=4, column=1, sticky=(tk.W, tk.E))

        # Submit button
        submit_button = ttk.Button(input_frame, text="Submit", command=self.submit_expense)
        submit_button.grid(row=5, column=0, columnspan=2, pady=10)

        # Add some instructions
        instructions = ("Instructions:\n"
                      "1. Date must be in DD-MM-YYYY format\n"
                      "2. All fields are required\n"
                      "3. Amount must be a number")
        instruction_label = ttk.Label(input_frame, text=instructions, justify=tk.LEFT)
        instruction_label.grid(row=6, column=0, columnspan=2, pady=10, sticky=tk.W)

    def submit_expense(self):
        """Handle expense submission with validation"""
        try:
            # Get values
            date = self.date_entry.get()
            category = self.category_var.get()
            description = self.description_entry.get()
            amount_str = self.amount_entry.get()
            payment_method = self.payment_var.get()

            # Validate date format
            if not self.validate_date(date):
                messagebox.showerror("Error", "Invalid date format. Please use DD-MM-YYYY")
                return

            # Validate all fields are filled
            if not all([category, description, amount_str, payment_method]):
                messagebox.showerror("Error", "All fields are required")
                return

            # Validate amount is a number
            try:
                amount = float(amount_str)
                if amount <= 0:
                    raise ValueError("Amount must be greater than 0")
            except ValueError:
                messagebox.showerror("Error", "Amount must be a positive number")
                return

            # Add expense to database
            self.expense_system.add_expense(
                date, category, description, amount, payment_method
            )

            # Clear entries
            self.description_entry.delete(0, tk.END)
            self.amount_entry.delete(0, tk.END)
            
            messagebox.showinfo("Success", "Expense added successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error adding expense: {str(e)}")

    def run(self):
        """Start the GUI"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ExpenseEntry()
    app.run()