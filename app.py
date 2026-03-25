import streamlit as st
import pandas as pd
import bank_logic

# --- 1. UI CONFIGURATION ---
st.set_page_config(page_title="Rise Treasury", page_icon="💸", layout="wide")

# --- 2. THE "SAAS" CSS HACK ---
# This CSS overrides Streamlit's default boring look to match your reference images
st.markdown("""
<style>
    /* Main Background color (soft gray/blue like modern dashboards) */
    .stApp {
        background-color: #F4F7FE;
    }
    
    /* Hide default Streamlit clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Make Metric Cards look like floating Glass/White Cards */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: none;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.05);
    }
    
    /* Label text for metrics */
    div[data-testid="stMetricLabel"] {
        color: #A3AED0 !important;
        font-weight: 600;
        font-size: 14px;
    }
    
    /* Value text for metrics */
    div[data-testid="stMetricValue"] {
        color: #2B3674 !important;
        font-weight: 800;
        font-size: 32px;
    }

    /* Style the buttons to look like modern web apps (Gradient Blue) */
    .stButton>button {
        background: linear-gradient(135deg, #4318FF 0%, #868CFF 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 10px 24px;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0px 4px 15px rgba(67, 24, 255, 0.4);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0px 6px 20px rgba(67, 24, 255, 0.6);
    }
    
    /* Style DataFrames to look cleaner */
    .stDataFrame {
        background-color: #FFFFFF;
        border-radius: 15px;
        padding: 10px;
        box-shadow: 0px 5px 20px rgba(0,0,0,0.03);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. STATE MANAGEMENT FOR THE WIZARD ---
# We use this to track where the user is in the payroll process
if 'payroll_step' not in st.session_state:
    st.session_state.payroll_step = 1

# --- 4. THE APP INTERFACE ---

# Load the databases
corp_df, emp_df, hist_df = bank_logic.load_db()

if corp_df is None:
    st.error("🚨 Critical Error: Database files not found.")
    st.stop()

company_balance = corp_df[corp_df['CompanyID'] == 'CORP-001']['Balance'].values[0]

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/money-bag.png", width=60)
    st.title("Rise Global")
    st.markdown("<p style='color: gray; font-size: 14px;'>Treasury OS v2.0</p>", unsafe_allow_html=True)
    st.divider()
    
    menu_selection = st.radio(
        "Navigation",
        ["🏠 Dashboard", "💸 Run Payroll", "👥 Team Directory"]
    )
    st.divider()
    st.write("Logged in as: **Saad (Admin)**")

# --- PAGE 1: DASHBOARD ---
if menu_selection == "🏠 Dashboard":
    st.markdown("<h2 style='color: #2B3674;'>Corporate Overview</h2>", unsafe_allow_html=True)
    st.write("Welcome back. Here is your real-time financial snapshot.")
    
    st.write("<br>", unsafe_allow_html=True)
    
    # Sleek 3-column metric layout
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Available Liquidity", value=f"${company_balance:,.2f}")
    with col2:
        # Calculate total active employees
        active_emps = len(emp_df[emp_df['CompanyID'] == 'CORP-001'])
        st.metric(label="Active Global Team", value=active_emps)
    with col3:
        st.metric(label="Next Scheduled Payroll", value="Mar 30, 2026")
    
    st.write("<br><br>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #2B3674;'>Cash Flow Trends</h3>", unsafe_allow_html=True)
    
    company_history = hist_df[hist_df['CompanyID'] == 'CORP-001'].copy()
    if not company_history.empty:
        chart_data = company_history.groupby('Date')['Amount'].sum().reset_index()
        st.bar_chart(chart_data.set_index('Date'), color="#4318FF")
    else:
        st.info("No transactions recorded yet.")

# --- PAGE 2: RUN PAYROLL (THE IDIOT-PROOF WIZARD) ---
elif menu_selection == "💸 Run Payroll":
    st.markdown("<h2 style='color: #2B3674;'>Global Payroll Engine</h2>", unsafe_allow_html=True)
    st.write("Follow the steps below to securely pay your team.")
    
    # STEP 1: UPLOAD
    if st.session_state.payroll_step == 1:
        st.markdown("""
        <div style='background-color: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);'>
            <h4>Step 1: Upload Timecards</h4>
            <p style='color: gray;'>Upload this month's CSV containing <b>EmpID</b> and <b>GrossSalary</b>.</p>
        </div>
        <br>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("", type=["csv"])

        if uploaded_file is not None:
            # Save file to session state so we don't lose it
            st.session_state.uploaded_file = uploaded_file
            if st.button("Generate Cost Preview ➡️", use_container_width=True):
                st.session_state.payroll_step = 2
                st.rerun()

    # STEP 2: PREVIEW & VALIDATE (The "Accountant" view)
    elif st.session_state.payroll_step == 2:
        uploaded_file = st.session_state.uploaded_file
        uploaded_file.seek(0) # Reset file pointer
        preview_df = pd.read_csv(uploaded_file)
        
        total_payroll = preview_df['GrossSalary'].sum()
        total_taxes = total_payroll * 0.15
        
        st.markdown("### Step 2: Review & Approve")
        st.warning(f"You are about to pay **{len(preview_df)} employees**.")
        
        # Show exactly what is happening to the money
        p1, p2, p3 = st.columns(3)
        p1.metric("Gross Salaries", f"${total_payroll:,.2f}")
        p2.metric("Corporate Taxes (15%)", f"${total_taxes:,.2f}")
        p3.metric("Your Balance After", f"${(company_balance - total_payroll):,.2f}")
        
        st.write("<br>", unsafe_allow_html=True)
        
        colA, colB = st.columns(2)
        with colA:
            if st.button("❌ Cancel & Go Back", use_container_width=True):
                st.session_state.payroll_step = 1
                st.rerun()
        with colB:
            # Only allow approval if they have the money
            if company_balance >= total_payroll:
                if st.button("✅ AUTHORIZE PAYMENT", type="primary", use_container_width=True):
                    with st.spinner("Processing bank transfers..."):
                        uploaded_file.seek(0)
                        success, message = bank_logic.process_payroll('CORP-001', uploaded_file)
                        if success:
                            st.session_state.success_msg = message
                            st.session_state.payroll_step = 3
                            st.rerun()
                        else:
                            st.error(f"Transaction Failed: {message}")
            else:
                st.error("🚨 INSUFFICIENT FUNDS: You cannot authorize this batch.")

    # STEP 3: SUCCESS RECEIPT
    elif st.session_state.payroll_step == 3:
        st.balloons()
        st.success("🎉 Payroll Executed Successfully!")
        st.write(st.session_state.success_msg)
        
        st.markdown("""
        <div style='background-color: #E6F4EA; padding: 20px; border-radius: 10px; border-left: 5px solid #34A853;'>
            <h4>Funds Dispatched</h4>
            <p>The corporate ledger has been updated and employee balances reflect their net pay.</p>
        </div>
        <br>
        """, unsafe_allow_html=True)
        
        if st.button("Run Another Batch", use_container_width=True):
            st.session_state.payroll_step = 1
            st.rerun()

# --- PAGE 3: EMPLOYEE DIRECTORY ---
elif menu_selection == "👥 Team Directory":
    st.markdown("<h2 style='color: #2B3674;'>Team Directory</h2>", unsafe_allow_html=True)
    st.write("Live overview of individual employee balances and IDs.")
    
    company_employees = emp_df[emp_df['CompanyID'] == 'CORP-001']
    st.dataframe(
        company_employees[['EmpID', 'EmpName', 'Balance']], 
        use_container_width=True,
        hide_index=True
    )
