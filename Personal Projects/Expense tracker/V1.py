import datetime
import matplotlib.pyplot as plt
from collections import defaultdict
import json
import os
import calendar
import cv2
import pytesseract
from PIL import Image
import re
import tempfile
from pdf2image import convert_from_path

class ExpenseTracker:
    def __init__(self):
        self.expenses = []
        self.filename = "expenses.json"
        self.load_expenses()

    def add_expense(self, amount, category, payment_method, date=None):
        if date is None:
            date = datetime.date.today()
        self.expenses.append({
            "amount": amount,
            "category": category,
            "payment_method": payment_method,
            "date": date.isoformat()
        })
        print(f"Expense added: ${amount:.2f} for {category} paid by {payment_method} on {date}")
        self.save_expenses()

    def view_expenses(self, start_date=None, end_date=None):
        filtered_expenses = self.expenses
        if start_date and end_date:
            filtered_expenses = [
                exp for exp in self.expenses
                if start_date <= datetime.date.fromisoformat(exp['date']) <= end_date
            ]
        for expense in filtered_expenses:
            print(f"${expense['amount']:.2f} - {expense['category']} "
                  f"(Paid by {expense['payment_method']}) on {expense['date']}")

    def view_expenses_by_month(self, year, month):
        if isinstance(month, str):
            month = list(calendar.month_name).index(month.capitalize())
        
        start_date = datetime.date(year, month, 1)
        end_date = datetime.date(year, month, calendar.monthrange(year, month)[1])
        
        monthly_expenses = [
            exp for exp in self.expenses
            if start_date <= datetime.date.fromisoformat(exp['date']) <= end_date
        ]
        
        total = sum(exp['amount'] for exp in monthly_expenses)
        
        print(f"\nExpenses for {calendar.month_name[month]} {year}:")
        print(f"Total: ${total:.2f}")
        print("\nBreakdown:")
        for expense in monthly_expenses:
            print(f"${expense['amount']:.2f} - {expense['category']} "
                  f"(Paid by {expense['payment_method']}) on {expense['date']}")

    def total_expenses(self):
        return sum(expense['amount'] for expense in self.expenses)

    def expenses_by_category(self):
        categories = defaultdict(float)
        for expense in self.expenses:
            categories[expense['category']] += expense['amount']
        return dict(categories)

    def expenses_by_payment_method(self):
        methods = defaultdict(float)
        for expense in self.expenses:
            methods[expense['payment_method']] += expense['amount']
        return dict(methods)

    def visualize_expenses(self, by="category"):
        if by == "category":
            data = self.expenses_by_category()
        elif by == "payment_method":
            data = self.expenses_by_payment_method()
        else:
            raise ValueError("Invalid visualization type")

        plt.figure(figsize=(10, 6))
        plt.pie(data.values(), labels=data.keys(), autopct='%1.1f%%')
        plt.title(f"Expenses by {by.capitalize()}")
        plt.axis('equal')
        plt.show()

    def visualize_expenses_over_time(self):
        dates = [datetime.date.fromisoformat(expense['date']) for expense in self.expenses]
        amounts = [expense['amount'] for expense in self.expenses]
        plt.figure(figsize=(10, 6))
        plt.plot(dates, amounts, marker='o')
        plt.title("Expenses Over Time")
        plt.xlabel("Date")
        plt.ylabel("Amount ($)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def save_expenses(self):
        with open(self.filename, 'w') as f:
            json.dump(self.expenses, f)

    def load_expenses(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                self.expenses = json.load(f)

    def add_expense_from_receipt(self, receipt_path):
        image = cv2.imread(receipt_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray)
        threshold = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        text = pytesseract.image_to_string(threshold)

        # Extract date
        date_match = re.search(r'DATE\s*(\d{2}/\d{2}/\d{4})', text)
        
        # Extract amount (full sale amount)
        amount_match = re.search(r'(Total|Total Sale)\s*\$?(\d+\.\d{2})', text, re.IGNORECASE)
        
        # Extract payment method
        payment_method_match = re.search(r'(AMERICAN EXPRESS|DEBIT|CAPITAL ONE|SCHOOLS FIRST CREDIT)', text, re.IGNORECASE)

        if date_match:
            date = datetime.datetime.strptime(date_match.group(1), '%m/%d/%Y').date()
        else:
            date = get_date_input("Could not extract date. Please enter manually")

        if amount_match:
            amount = float(amount_match.group(2))
        else:
            amount = float(input("Could not extract amount. Please enter manually: "))

        if payment_method_match:
            payment_method = payment_method_match.group(1).title()
        else:
            payment_method = input("Could not extract payment method. Please enter manually: ")

        category = input("Enter expense category: ")

        self.add_expense(amount, category, payment_method, date)
        print(f"Expense added from receipt: ${amount:.2f} for {category} paid by {payment_method} on {date}")

    def process_receipt_directory(self, directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                print(f"Processing image receipt: {filename}")
                self.add_expense_from_receipt(file_path)
            elif filename.endswith('.pdf'):
                print(f"Processing PDF receipt: {filename}")
                self.process_pdf_receipt(file_path)

    def process_pdf_receipt(self, pdf_path):
        images = convert_from_path(pdf_path)
        for i, image in enumerate(images):
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                image.save(temp_file.name, 'PNG')
                print(f"Processing page {i + 1} of PDF")
                self.add_expense_from_receipt(temp_file.name)
            os.unlink(temp_file.name)

def get_date_input(prompt):
    while True:
        date_str = input(prompt + " (YYYY-MM-DD): ")
        try:
            return datetime.date.fromisoformat(date_str)
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

def main():
    tracker = ExpenseTracker()

    while True:
        print("\nExpense Tracker Menu:")
        print("1. Add Expense Manually")
        print("2. Add Expenses from Receipt Directory")
        print("3. View Expenses")
        print("4. View Expenses by Month")
        print("5. View Total Expenses")
        print("6. View Expenses by Category")
        print("7. View Expenses by Payment Method")
        print("8. Visualize Expenses (Pie Chart)")
        print("9. Visualize Expenses Over Time")
        print("10. Exit")

        choice = input("Enter your choice (1-10): ")

        if choice == '1':
            add_more = 'y'
            while add_more.lower() == 'y':
                amount = float(input("Enter expense amount: "))
                category = input("Enter expense category: ")
                payment_method = input("Enter payment method: ")
                date_str = input("Enter date (YYYY-MM-DD) or leave blank for today: ")
                date = datetime.date.fromisoformat(date_str) if date_str else None
                tracker.add_expense(amount, category, payment_method, date)
                add_more = input("Do you want to add another expense? (y/n): ")
        elif choice == '2':
            directory = input("Enter the path to the directory containing receipt images: ")
            if os.path.isdir(directory):
                tracker.process_receipt_directory(directory)
            else:
                print("Invalid directory path. Please try again.")
        elif choice == '3':
            use_filter = input("Do you want to filter expenses by date range? (y/n): ")
            if use_filter.lower() == 'y':
                start_date = get_date_input("Enter start date")
                end_date = get_date_input("Enter end date")
                tracker.view_expenses(start_date, end_date)
            else:
                tracker.view_expenses()
        elif choice == '4':
            year = int(input("Enter year: "))
            month = input("Enter month (name or number): ")
            if month.isdigit():
                month = int(month)
            tracker.view_expenses_by_month(year, month)
        elif choice == '5':
            print(f"Total Expenses: ${tracker.total_expenses():.2f}")
        elif choice == '6':
            categories = tracker.expenses_by_category()
            for category, amount in categories.items():
                print(f"{category}: ${amount:.2f}")
        elif choice == '7':
            methods = tracker.expenses_by_payment_method()
            for method, amount in methods.items():
                print(f"{method}: ${amount:.2f}")
        elif choice == '8':
            by = input("Visualize by (category/payment_method): ").lower()
            if by in ['category', 'payment_method']:
                tracker.visualize_expenses(by)
            else:
                print("Invalid option. Please choose 'category' or 'payment_method'.")
        elif choice == '9':
            tracker.visualize_expenses_over_time()
        elif choice == '10':
            print("Thank you for using the Expense Tracker!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
