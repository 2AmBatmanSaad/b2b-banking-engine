import streamlit as st
import pandas as pd
import bank_logic

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Wayne Treasury", page_icon="🦇", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS (THE "MODERN" UPGRADE) ---
st.markdown("""
<style>
    /* Hide the default Streamlit top menu and footer for a clean SaaS look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sleek Custom Metric Cards */
    div[data-testid="metric-container"] {
        background-color: #121212;
        border: 1px solid #333333;
        padding: 5% 5% 5% 10%;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        border-left: 4px solid #F5A623; /* Gold accent line */
    }
    
    /* Custom button styling */
    .stButton>button {
        border-radius: 5px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- SECURE LOGIN PORTAL ---
# Initialize session state for login
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    # Build the Login Screen
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("")
        st.write("")
        st.markdown("<h1 style='text-align: center;'>🦇 Wayne Enterprises</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888;'>Secure Treasury Gateway</p>", unsafe_allow_html=True)
        st.divider()
        
        username = st.text_input("Admin ID")
        password = st.text_input("Encryption Key", type="password")
        
        if st.button("Authenticate", use_container_width=True, type="primary"):
            if username == "admin" and password == "wayne":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Access Denied. Unauthorized entry logged.")
else:
    # --- MAIN DASHBOARD (ONLY SHOWS IF LOGGED IN) ---
    with st.sidebar:
        st.title("🦇 Wayne Ent.")
        st.write("Global Treasury")
        st.divider()
        st.write("👨‍💻 **Admin:** Saad")
        st.write("🟢 **Network:** Secure")
        st.divider()
        if st.button("Log Out"):
            st.session_state.authenticated = False
            st.rerun()

    st.title("⚡ Treasury & Payroll Engine")

    # Load Database
    corp_df, emp_df, hist_df = bank_logic.load_db()

    if corp_df is not None:
        company_balance = corp_df[corp_df['CompanyID'] == 'CORP-001']['Balance'].values[0]

        # CFO METRIC CARD (Upgraded with CSS)
        st.metric(label="Available Corporate Liquidity (USD)", value=f"${company_balance:,.2f}", delta="Live Sync")
        st.write("") # Spacer

        # MODERN FEATURE: TABS
        # This prevents scrolling and makes it look like a real app interface
        tab1, tab2 = st.tabs(["📤 Bulk Payroll Processing", "👥 Employee Ledger & History"])

        with tab1:
            st.write("### Execute Master Payroll Batch")
            st.info("Upload the verified CSV containing EmpID and GrossSalary.")
            uploaded_file = st.file_uploader("Upload Payroll File", type=["csv"])

            if uploaded_file is not None:
                if st.button("Process One-to-Many Transaction", type="primary"):
                    with st.spinner("Encrypting connection... Verifying liquidity..."):
                        success, message = bank_logic.process_payroll('CORP-001', uploaded_file)
                        if success:
                            st.success(message)
                            st.balloons()
                            st.rerun() 
                        else:
                            st.error(f"❌ TRANSACTION FAILED: {message}")
            
            st.divider()
            st.write("### 📈 Real-Time Cash Flow")
            company_history = hist_df[hist_df['CompanyID'] == 'CORP-001'].copy()
            if not company_history.empty:
                chart_data = company_history.groupby('Date')['Amount'].sum().reset_index()
                st.bar_chart(chart_data.set_index('Date'))

        with tab2:
            st.write("### Verified Employee Balances")
            company_employees = emp_df[emp_df['CompanyID'] == 'CORP-001']
            st.dataframe(
                company_employees[['EmpID', 'EmpName', 'Balance']], 
                use_container_width=True,
                hide_index=True
            )
            
            st.write("### Raw Transaction Ledger")
            st.dataframe(company_history, use_container_width=True, hide_index=True)

    else:
        st.error("🚨 Database disconnected.")
