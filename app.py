import streamlit as st
import pandas as pd
import bank_logic

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Wayne Treasury", page_icon="🏦", layout="wide")

# Added a high-end sidebar for the presentation
with st.sidebar:
    st.title("🏦 Wayne Enterprises")
    st.write("Global Treasury & Payroll")
    st.divider()
    st.write("👨‍💻 **System Admin:** Saad")
    st.write("🟢 **Status:** Secure Connection")
    st.write("🔒 **Encryption:** AES-256")

st.title("⚡ Automated Treasury & Payroll Engine")
st.write("B2B Banking Dashboard for **Wayne Enterprises (CORP-001)**")

# --- LOAD LIVE DATABASE ---
corp_df, emp_df, hist_df = bank_logic.load_db()

if corp_df is not None:
    # Get current Corporate Balance
    company_balance = corp_df[corp_df['CompanyID'] == 'CORP-001']['Balance'].values[0]

    # 1. CFO METRIC CARD
    st.write("### 💰 Live Treasury Balance")
    st.metric(label="Available Liquidity", value=f"${company_balance:,.2f}")
    st.divider()

    # Create two columns for a high-end dashboard look
    col1, col2 = st.columns(2)

    # --- LEFT COLUMN: ACTION (PAYROLL) ---
    with col1:
        st.write("### 📤 Execute Bulk Payroll")
        st.info("Upload the monthly CSV containing EmpID and GrossSalary.")
        uploaded_file = st.file_uploader("Upload Payroll CSV", type=["csv"])

        if uploaded_file is not None:
            if st.button("Process One-to-Many Transaction", type="primary"):
                with st.spinner("Verifying corporate liquidity and calculating taxes..."):
                    # Call the master function from your engine
                    success, message = bank_logic.process_payroll('CORP-001', uploaded_file)
                    
                    if success:
                        st.success(message)
                        st.balloons()
                        # Force the app to refresh so the new balances show up immediately
                        st.rerun() 
                    else:
                        st.error(f"❌ TRANSACTION FAILED: {message}")

    # --- RIGHT COLUMN: ANALYTICS (GRAPHS) ---
    with col2:
        st.write("### 📈 Treasury Cash Flow")
        # Filter history for just this company
        company_history = hist_df[hist_df['CompanyID'] == 'CORP-001'].copy()
        
        if not company_history.empty:
            # Group the transactions by Date to make a beautiful chart
            chart_data = company_history.groupby('Date')['Amount'].sum().reset_index()
            st.bar_chart(chart_data.set_index('Date'))
        else:
            st.write("No transaction history found.")

    st.divider()
    
    # --- BOTTOM SECTION: LIVE EMPLOYEE LEDGER ---
    st.write("### 👥 Employee Ledger (Live Updates)")
    company_employees = emp_df[emp_df['CompanyID'] == 'CORP-001']
    
    # Upgraded data table to hide the ugly index numbers
    st.dataframe(
        company_employees[['EmpID', 'EmpName', 'Balance']], 
        use_container_width=True,
        hide_index=True
    )

else:
    st.error("🚨 Database disconnected. Please ensure CSV files are uploaded to GitHub.")
