import pandas as pd
from datetime import datetime
import uuid

# --- 1. DATABASE FUNCTIONS (Handling the CSVs) ---

def load_db():
    """Loads the CSV files into memory as Pandas DataFrames."""
    try:
        corp_df = pd.read_csv('corporate_accounts.csv')
        emp_df = pd.read_csv('employee_accounts.csv')
        hist_df = pd.read_csv('transaction_history.csv')
        return corp_df, emp_df, hist_df
    except FileNotFoundError as e:
        return None, None, None

def save_db(corp_df, emp_df, hist_df):
    """Saves the updated DataFrames back into the CSV files permanently."""
    corp_df.to_csv('corporate_accounts.csv', index=False)
    emp_df.to_csv('employee_accounts.csv', index=False)
    hist_df.to_csv('transaction_history.csv', index=False)

# --- 2. VALIDATION FUNCTIONS ---

def verify_liquidity(corp_df, company_id, amount_needed):
    """Checks if the company has enough cash to process the batch."""
    company_data = corp_df[corp_df['CompanyID'] == company_id]
    
    if company_data.empty:
        return False, "Error: Corporate Account not found."
        
    current_balance = company_data['Balance'].values[0]
    
    if current_balance >= amount_needed:
        return True, current_balance
    else:
        return False, f"Insufficient Funds. Balance: ${current_balance:,.2f}, Needed: ${amount_needed:,.2f}"

# --- 3. THE MASTER PAYROLL ALGORITHM ---

def process_payroll(company_id, uploaded_file):
    """
    Executes the One-to-Many transaction.
    1. Validates liquidity.
    2. Deducts from Corporate Vault.
    3. Calculates Taxes (15%).
    4. Deposits Net Pay to Employees.
    5. Logs the transactions to the ledger.
    """
    # Load the databases
    corp_df, emp_df, hist_df = load_db()
    if corp_df is None:
        return False, "Database files not found. Check your file names."

    # Read the HR payroll upload
    try:
        payroll_df = pd.read_csv(uploaded_file)
    except Exception:
        return False, "Invalid CSV uploaded."

    # Calculate Totals
    total_gross = payroll_df['GrossSalary'].sum()
    total_tax = total_gross * 0.15  # Flat 15% corporate tax rate
    
    # Step 1: Validate Liquidity (Does the company have enough money?)
    is_liquid, msg = verify_liquidity(corp_df, company_id, total_gross)
    if not is_liquid:
        return False, msg # Fails validation, stops the process, returns error

    # Step 2: Deduct Total Gross from the Corporate Account
    corp_df.loc[corp_df['CompanyID'] == company_id, 'Balance'] -= total_gross

    # Step 3 & 4: Loop through employees, calculate tax, and deposit Net Pay
    for index, row in payroll_df.iterrows():
        emp_id = row['EmpID']
        gross_pay = row['GrossSalary']
        net_pay = gross_pay * 0.85 # (100% - 15% tax)
        
        # Add net pay to the specific employee's balance
        emp_df.loc[emp_df['EmpID'] == emp_id, 'Balance'] += net_pay

    # Step 5: Log the transactions to the Immutable Ledger (History)
    today_date = datetime.now().strftime('%Y-%m-%d')
    
    new_transactions = pd.DataFrame([
        {'TxnID': f"TXN-{uuid.uuid4().hex[:6].upper()}", 'Date': today_date, 'CompanyID': company_id, 'Type': 'Payroll_Run', 'Amount': -total_gross},
        {'TxnID': f"TXN-{uuid.uuid4().hex[:6].upper()}", 'Date': today_date, 'CompanyID': company_id, 'Type': 'Tax_Withholding', 'Amount': -total_tax}
    ])
    
    # Combine old history with new transactions
    hist_df = pd.concat([hist_df, new_transactions], ignore_index=True)

    # Step 6: Save everything back to the CSV files permanently
    save_db(corp_df, emp_df, hist_df)

    return True, f"Successfully processed payroll for {len(payroll_df)} employees. Total Gross: ${total_gross:,.2f}"