import streamlit as st
import pandas as pd
import bank_logic

# --- 1. UI CONFIGURATION (Centered for a cleaner, app-like feel) ---
st.set_page_config(page_title="Wayne Treasury", page_icon="🦇", layout="centered")

# --- 2. MINIMALIST CSS ---
st.markdown("""
<style>
    /* Hide default Streamlit clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Make the metric card look expensive and isolated */
    div[data-testid="metric-container"] {
        background-color: #111111;
        border: 1px solid #333333;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. THE SECURE LOGIN PORTAL ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    # Push the login box down to the middle of the screen
    st.write("<br><br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🦇 Wayne Ent.</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888;'>Authorized Personnel Only</p>", unsafe_allow_html=True)
        st.write("")
        
        username = st.text_input("Admin ID", placeholder="Hint: admin")
        password = st.text_input("Encryption Key", type="password", placeholder="Hint: wayne")
        
        st.write("")
        if st.button("Authenticate", use_container_width=True, type="primary"):
            if username == "admin" and password == "wayne":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Invalid Credentials")

else:
    # --- 4. THE CLEAN APP INTERFACE ---
    
    # Load the databases
    corp_df, emp_df, hist_df = bank_logic.load_db()

    if corp_df is None:
        st.error("🚨 Critical Error: Database files not found.")
        st.stop()

    company_balance = corp_df[corp_df['CompanyID'] == 'CORP-001']['Balance'].values[0]

    # --- SIDEBAR NAVIGATION ---
    with st.sidebar:
        st.title("🦇 Wayne Ent.")
        st.write("Admin: **Saad**")
        st.divider()
        
        # This is the magic! A simple menu that changes the page.
        menu_selection = st.radio(
            "Navigation Menu",
            ["📊 Treasury Dashboard", "📤 Run Bulk Payroll", "👥 Employee Ledger"]
        )
        
        st.divider()
        if st.button("Log Out", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

    # --- PAGE 1: TREASURY DASHBOARD ---
    if menu_selection == "📊 Treasury Dashboard":
        st.title("Treasury Dashboard")
        st.write("Live snapshot of corporate liquidity and cash flow.")
        
        st.write("<br>", unsafe_allow_html=True)
        st.metric(label="Total Available Liquidity", value=f"${company_balance:,.2f}")
        st.write("<br>", unsafe_allow_html=True)
        
        st.write("### Cash Flow History")
        company_history = hist_df[hist_df['CompanyID'] == 'CORP-001'].copy()
        if not company_history.empty:
            chart_data = company_history.groupby('Date')['Amount'].sum().reset_index()
            st.bar_chart(chart_data.set_index('Date'))
        else:
            st.info("No transactions recorded yet.")

    # --- PAGE 2: RUN BULK PAYROLL ---
    elif menu_selection == "📤 Run Bulk Payroll":
        st.title("Run Bulk Payroll")
        st.write("Upload your monthly CSV to initiate a one-to-many transaction.")
        st.divider()
        
        uploaded_file = st.file_uploader("Upload CSV File (EmpID, GrossSalary)", type=["csv"])

        if uploaded_file is not None:
            st.success("File verified. Ready for execution.")
            if st.button("Execute Payroll Batch", type="primary", use_container_width=True):
                with st.spinner("Connecting to bank... Validating liquidity..."):
                    success, message = bank_logic.process_payroll('CORP-001', uploaded_file)
                    if success:
                        st.success(message)
                        st.balloons()
                    else:
                        st.error(f"❌ Transaction Blocked: {message}")

    # --- PAGE 3: EMPLOYEE LEDGER ---
    elif menu_selection == "👥 Employee Ledger":
        st.title("Employee Ledger")
        st.write("Live overview of individual employee balances.")
        st.divider()
        
        company_employees = emp_df[emp_df['CompanyID'] == 'CORP-001']
        st.dataframe(
            company_employees[['EmpID', 'EmpName', 'Balance']], 
            use_container_width=True,
            hide_index=True
        )
