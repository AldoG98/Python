import os
import pytesseract
from PIL import Image

# Path to the directory with receipt images
receipts_folder = "C:\\Users\\aldog\\OneDrive\\Desktop\\Scans\\Aldo\\scanned recipts\\9-11-23 to 8-8-24 gas receipts"

# Define categories and keywords
CATEGORIES = {
    "Groceries": ["grocery", "supermarket", "market", "food"],
    "Fuel": ["gas", "fuel", "petrol", "service station"],
    "Dining Out": ["restaurant", "cafe", "diner", "coffee"],
    "Entertainment": ["movie", "cinema", "theater", "concert"],
    "Utilities": ["electricity", "water", "internet", "phone"],
    "Healthcare": ["pharmacy", "clinic", "doctor", "medical"]
}

def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

def categorize_expense(text):
    for category, keywords in CATEGORIES.items():
        if any(keyword.lower() in text.lower() for keyword in keywords):
            return category
    return "Uncategorized"

def analyze_receipts(folder_path):
    results = {}
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        # Check if the path is a file (not a directory)
        if os.path.isfile(file_path):
            text = extract_text_from_image(file_path)
            category = categorize_expense(text)
            results[filename] = category
    return results

# Run the function on the receipts folder
categorized_receipts = analyze_receipts(receipts_folder)
for filename, category in categorized_receipts.items():
    print(f"{filename}: {category}")
