import sqlite3
import pandas as pd
from datetime import datetime
import os

def convert_date_format(date_str):
    """Convert date from DD-MM-YYYY to datetime object"""
    try:
        if pd.isna(date_str):
            return None
            
        date_str = str(date_str).strip()
        return datetime.strptime(date_str, '%d-%m-%Y')
    except ValueError as e:
        print(f"Error parsing date {date_str}: {str(e)}")
        return None

def create_monthly_summary(df):
    """Create monthly summary of expenses"""
    # Convert date to datetime if it's not already
    df['date'] = pd.to_datetime(df['date'])
    
    # Extract month and year
    df['month_year'] = df['date'].dt.to_period('M')
    
    # Group by month and category
    monthly_summary = df.pivot_table(
        index='month_year',
        columns='category',
        values='amount',
        aggfunc='sum',
        fill_value=0
    )
    
    # Add total column
    monthly_summary['Total'] = monthly_summary.sum(axis=1)
    
    return monthly_summary

def create_payment_summary(df):
    """Create summary by payment method"""
    payment_summary = df.groupby('payment_method').agg({
        'amount': ['sum', 'count', 'mean'],
        'interest_rate': 'first'
    }).round(2)
    
    payment_summary.columns = ['Total Amount', 'Number of Transactions', 'Average Transaction', 'Interest Rate']
    
    # Calculate potential interest
    payment_summary['Monthly Interest'] = (
        payment_summary['Total Amount'] * payment_summary['Interest Rate'] / 100 / 12
    ).round(2)
    
    return payment_summary

def create_excel_dashboard(db_path, output_path):
    """Create a comprehensive Excel dashboard from SQLite database"""
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        
        # Read the expenses table
        print("Reading database...")
        df = pd.read_sql_query("SELECT * FROM expenses", conn)
        
        # Convert dates
        print("Processing dates...")
        df['date'] = df['date'].apply(convert_date_format)
        
        # Create Excel writer
        print("Creating Excel workbook...")
        writer = pd.ExcelWriter(output_path, engine='xlsxwriter')
        workbook = writer.book
        
        # Create formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#C5D9F1',
            'border': 1
        })
        
        number_format = workbook.add_format({
            'num_format': '$#,##0.00',
            'border': 1
        })
        
        percent_format = workbook.add_format({
            'num_format': '0.00%',
            'border': 1
        })
        
        date_format = workbook.add_format({
            'num_format': 'dd-mm-yyyy',
            'border': 1
        })
        
        # Write raw data
        print("Writing raw data...")
        df.to_excel(writer, sheet_name='Raw Data', index=False)
        raw_sheet = writer.sheets['Raw Data']
        
        # Format raw data sheet
        for idx, col in enumerate(df.columns):
            # Set column width
            max_length = max(df[col].astype(str).apply(len).max(), len(col))
            raw_sheet.set_column(idx, idx, max_length + 2)
            
            # Format headers
            raw_sheet.write(0, idx, col, header_format)
        
        # Create and write monthly summary
        print("Creating monthly summary...")
        monthly_summary = create_monthly_summary(df)
        monthly_summary.to_excel(writer, sheet_name='Monthly Summary')
        monthly_sheet = writer.sheets['Monthly Summary']
        
        # Format monthly summary
        for idx, col in enumerate(monthly_summary.columns):
            monthly_sheet.set_column(idx + 1, idx + 1, 12, number_format)
        monthly_sheet.set_column(0, 0, 15)  # Month-Year column
        
        # Create and write payment method summary
        print("Creating payment summary...")
        payment_summary = create_payment_summary(df)
        payment_summary.to_excel(writer, sheet_name='Payment Summary')
        payment_sheet = writer.sheets['Payment Summary']
        
        # Format payment summary
        payment_sheet.set_column('B:B', 12, number_format)  # Total Amount
        payment_sheet.set_column('C:C', 12)  # Number of Transactions
        payment_sheet.set_column('D:D', 12, number_format)  # Average Transaction
        payment_sheet.set_column('E:E', 12, percent_format)  # Interest Rate
        payment_sheet.set_column('F:F', 12, number_format)  # Monthly Interest
        
        # Save and close
        print("Saving Excel file...")
        writer.close()
        conn.close()
        
        print(f"Dashboard created successfully at {output_path}")
        
    except Exception as e:
        print(f"Error creating dashboard: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    # File paths
    database_path = r"C:\Users\aldog\OneDrive\Desktop\Expenses data base\expenses.db"
    excel_output = r"C:\Users\aldog\OneDrive\Desktop\excel\expense_report.xlsx"
    
    try:
        create_excel_dashboard(database_path, excel_output)
    except Exception as e:
        print(f"\nError creating dashboard: {str(e)}")