import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import yaml
from pathlib import Path
import logging

class StockTracker:
    def __init__(self, config_file='config.yaml'):
        self.config_file = config_file
        self.load_config()
        self.setup_logging()
        
    def load_config(self):
        """Load configuration from YAML file."""
        if not Path(self.config_file).exists():
            self.create_default_config()
        
        with open(self.config_file, 'r') as f:
            self.config = yaml.safe_load(f)
            
    def create_default_config(self):
        """Create a default configuration file."""
        default_config = {
            'email': {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'sender_email': 'your-email@gmail.com',
                'sender_password': 'your-app-password',  # Use App Password for Gmail
                'recipient_email': 'your-email@gmail.com'
            },
            'check_interval': 3600,  # Default to hourly checks
            'items': {
                'Pokemon Center': {
                    'Charizard Plush': 'https://www.pokemoncenter.com/product/701-29617/',
                    # Add more items here
                },
                'Target': {
                    'Pokemon Cards': 'https://www.target.com/p/pokemon-trading-card-game/',
                    # Add more items here
                },
                # Add more retailers here
            },
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
    
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('stock_tracker.log'),
                logging.StreamHandler()
            ]
        )
    
    def check_pokemon_center(self, url):
        """Check item stock on Pokemon Center website."""
        try:
            response = requests.get(url, headers=self.config['headers'])
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for out of stock indicators
            out_of_stock = soup.find('button', {'class': 'add-to-cart'}, disabled=True)
            return not bool(out_of_stock)
        except Exception as e:
            logging.error(f"Error checking Pokemon Center: {e}")
            return False
    
    def check_target(self, url):
        """Check item stock on Target website."""
        try:
            response = requests.get(url, headers=self.config['headers'])
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for "out of stock" or "sold out" text
            out_of_stock = soup.find(text=lambda t: t and ('out of stock' in t.lower() or 'sold out' in t.lower()))
            return not bool(out_of_stock)
        except Exception as e:
            logging.error(f"Error checking Target: {e}")
            return False

    def send_notification(self, item_name, retailer, url):
        """Send email notification when item is in stock."""
        try:
            msg = MIMEText(f"The item '{item_name}' is now in stock at {retailer}!\nURL: {url}")
            msg['Subject'] = f"In Stock Alert: {item_name}"
            msg['From'] = self.config['email']['sender_email']
            msg['To'] = self.config['email']['recipient_email']
            
            with smtplib.SMTP(self.config['email']['smtp_server'], self.config['email']['smtp_port']) as server:
                server.starttls()
                server.login(
                    self.config['email']['sender_email'],
                    self.config['email']['sender_password']
                )
                server.send_message(msg)
            
            logging.info(f"Notification sent for {item_name} at {retailer}")
        except Exception as e:
            logging.error(f"Error sending notification: {e}")
    
    def add_item(self, retailer, item_name, url):
        """Add a new item to track."""
        if retailer not in self.config['items']:
            self.config['items'][retailer] = {}
        
        self.config['items'][retailer][item_name] = url
        
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
        
        logging.info(f"Added new item: {item_name} at {retailer}")
    
    def remove_item(self, retailer, item_name):
        """Remove an item from tracking."""
        if retailer in self.config['items'] and item_name in self.config['items'][retailer]:
            del self.config['items'][retailer][item_name]
            
            if not self.config['items'][retailer]:
                del self.config['items'][retailer]
            
            with open(self.config_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            
            logging.info(f"Removed item: {item_name} from {retailer}")
    
    def check_stock(self):
        """Check stock for all items in configuration."""
        for retailer, items in self.config['items'].items():
            for item_name, url in items.items():
                logging.info(f"Checking {item_name} at {retailer}")
                
                in_stock = False
                if retailer == "Pokemon Center":
                    in_stock = self.check_pokemon_center(url)
                elif retailer == "Target":
                    in_stock = self.check_target(url)
                # Add more retailers here
                
                if in_stock:
                    self.send_notification(item_name, retailer, url)
    
    def run(self):
        """Run the stock checker continuously."""
        logging.info("Starting stock tracker...")
        while True:
            self.check_stock()
            time.sleep(self.config['check_interval'])

if __name__ == "__main__":
    tracker = StockTracker()
    

    tracker.run()