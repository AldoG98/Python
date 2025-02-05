import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import MonthLocator, DateFormatter
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
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

class ExpenseTracker:
    def __init__(self):
        self.expenses = []
        self.filename = "expenses.json"
        self.feedback_data = []
        self.feedback_filename = "feedback_data.json"
        self.model = None
        self.vectorizer = None
        self.load_expenses()
        self.load_feedback_data()
        self.train_model()

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
        
        plt.figure(figsize=(12, 6))
        plt.plot(dates, amounts, marker='o', linestyle='-', linewidth=2, markersize=6)
        plt.title("Expenses Over Time", fontsize=16)
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("Amount ($)", fontsize=12)
        
        plt.gca().xaxis.set_major_locator(MonthLocator())
        plt.gca().xaxis.set_major_formatter(DateFormatter('%b %Y'))
        plt.gcf().autofmt_xdate()
        
        plt.grid(True, linestyle='--', alpha=0.7)
        
        for i, (date, amount) in enumerate(zip(dates, amounts)):
            if i == 0 or i == len(dates) - 1 or amount == max(amounts) or amount == min(amounts):
                plt.annotate(f'${amount:.2f}', (date, amount), textcoords="offset points", 
                             xytext=(0,10), ha='center', fontweight='bold')
        
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
        processed_image = self.preprocess_image(image)
        text = pytesseract.image_to_string(processed_image)

        predicted_category = self.predict_category(text)




        # Improved regex patterns for better extraction
        date_match = re.search(r'DATE\s*[:.]?\s*(\d{2}[-/]\d{2}[-/]\d{4}|\d{4}[-/]\d{2}[-/]\d{2})', text, re.IGNORECASE)
        amount_match = re.search(r'(FUEL PRICE|TOTAL PRICE|TOTAL)\s*[:.]?\s*[$]?(\d+\.\d{2})', text, re.IGNORECASE)
        payment_method_match = re.search(r'(VISA|MASTERCARD|AMEX|AMERICAN EXPRESS|DEBIT|CREDIT|CASH)', text, re.IGNORECASE)

        if date_match:

            date_str = date_match.group(1)
            date = self.parse_date(date_str)
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

        correct_category = input(f"Is '{predicted_category}' the correct category? If not, please enter the correct category: ")
        if correct_category and correct_category != predicted_category:
            self.add_feedback(text, correct_category)
            self.train_model()
            category = correct_category
        else:
            category = predicted_category

        self.add_expense(amount, category, payment_method, date)
        print(f"Expense added from receipt: ${amount:.2f} for {category} paid by {payment_method} on {date}")

    def parse_date(self, date_str):
        for fmt in ('%m-%d-%Y', '%Y-%m-%d', '%m/%d/%Y', '%Y/%m/%d'):
            try:
                return datetime.datetime.strptime(date_str, fmt).date()
            except ValueError:
                pass
        return get_date_input("Could not parse date. Please enter manually")
    def preprocess_image(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray)
        threshold = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        kernel = np.ones((1,1), np.uint8)
        dilated = cv2.dilate(threshold, kernel, iterations=1)
        return dilated

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

    def add_feedback(self, text, category):
        self.feedback_data.append({"text": text, "category": category})
        self.save_feedback_data()

    def train_model(self):
        if len(self.feedback_data) < 10:
            return

        texts = [item['text'] for item in self.feedback_data]
        categories = [item['category'] for item in self.feedback_data]

        self.vectorizer = CountVectorizer()
        X = self.vectorizer.fit_transform(texts)
        y = categories

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.model = MultinomialNB()
        self.model.fit(X_train, y_train)

        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Model accuracy: {accuracy:.2f}")

    def predict_category(self, text):
        if self.model is None or self.vectorizer is None:
            return "Unknown"

        X = self.vectorizer.transform([text])
        return self.model.predict(X)[0]

    def save_feedback_data(self):
        with open(self.feedback_filename, 'w') as f:
            json.dump(self.feedback_data, f)

    def load_feedback_data(self):
        if os.path.exists(self.feedback_filename):
            with open(self.feedback_filename, 'r') as f:
                self.feedback_data = json.load(f)

    def edit_expense(self, index):
        if 0 <= index < len(self.expenses):
            expense = self.expenses[index]
            print(f"Editing expense: {expense}")
            
            amount = float(input(f"Enter new amount (current: {expense['amount']}): ") or expense['amount'])
            category = input(f"Enter new category (current: {expense['category']}): ") or expense['category']
            payment_method = input(f"Enter new payment method (current: {expense['payment_method']}): ") or expense['payment_method']
            date_str = input(f"Enter new date (YYYY-MM-DD) (current: {expense['date']}): ") or expense['date']
            
            self.expenses[index] = {
                "amount": amount,
                "category": category,
                "payment_method": payment_method,
                "date": date_str
            }
            
            print("Expense updated successfully.")
            self.save_expenses()
        else:
            print("Invalid index. No expense found.")

    def delete_expense(self, index):
        if 0 <= index < len(self.expenses):
            deleted_expense = self.expenses.pop(index)
            print(f"Deleted expense: {deleted_expense}")
            self.save_expenses()
        else:
            print("Invalid index. No expense found.")

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
        print("10. Edit Expense")
        print("11. Delete Expense")
        print("12. Exit")

        choice = input("Enter your choice (1-12): ")

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
                print("Invalid option. Please choose 'category' or 'payment_method.")
        elif choice == '9':
            tracker.visualize_expenses_over_time()
        elif choice == '10':
            tracker.view_expenses()
            index = int(input("Enter the index of the expense you want to edit: "))
            tracker.edit_expense(index)
        elif choice == '11':
            tracker.view_expenses()
            index = int(input("Enter the index of the expense you want to delete: "))
            tracker.delete_expense(index)
        elif choice == '12':
            print("Thank you for using the Expense Tracker!")
            break
        else:

            print("Invalid choice. Please try again.")
if __name__ == "__main__":
    main()
