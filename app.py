import streamlit as st
import pandas as pd
import bank_logic
import time

# --- 1. UI CONFIGURATION ---
st.set_page_config(page_title="Wayne Treasury", page_icon="🦇", layout="wide")

# --- 2. PREMIUM CSS STYLING ---
st.markdown("""
<style>
    /* Hide the default Streamlit clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Make the metric card look like a premium floating SaaS card */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0px 8px 24px rgba(149, 157, 165, 0.2);
        text-align: center;
    }
    
    /* Style the big blue button */
    .stButton>button {
        background: linear-gradient(135deg, #4318FF 0%, #868CFF 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 10px 24px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        box-shadow: 0px 6px 20px rgba(67, 24, 255, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. LOAD DATABASE ---
corp_df, emp_df, hist_df = bank_logic.load_db()

# Failsafe if the CSVs are missing
if corp_df is not None and not corp_df.empty:
    company_balance = corp_df[corp_df['CompanyID'] == 'CORP-001']['Balance'].values[0]
else:
    company_balance = 0.00
    st.error("🚨 Database not found. Please ensure CSVs are uploaded.")
    st.stop()

# --- 4. THE IDIOT-PROOF LAYOUT ---
# Squeezes the app into the center of the screen using blank columns
spacer_left, main_content, spacer_right = st.columns([1, 2, 1])

with main_content:
    # Top Spacing & Header
    st.write("<br><br>", unsafe_allow_html=True) 
    st.markdown("<p style='text-align: center; color: #888; font-weight: bold;'>Wayne Enterprises • Corporate Treasury</p>", unsafe_allow_html=True)
    
    # Massive Centered Metric
    st.metric(label="Available Liquidity", value=f"${company_balance:,.2f}")
    st.write("<br>", unsafe_allow_html=True)

    # Clean Upload Section
    st.markdown("### 💸 Run Monthly Payroll")
    st.info("Drop your verified CSV here to automatically dispatch funds to employees.")
    
    uploaded_file = st.file_uploader("", type=["csv"])

    # --- 5. THE EXECUTION ENGINE ---
    if uploaded_file is not None:
        st.write("<br>", unsafe_allow_html=True)
        
        if st.button("AUTHORIZE PAYROLL BATCH", type="primary", use_container_width=True):
            with st.spinner("Processing secure transfer..."):
                
                # Call your backend logic
                success, message = bank_logic.process_payroll('CORP-001', uploaded_file)
                
                if success:
                    st.success(message)
                    st.balloons()
                    
                    # --- THE FIX: FORCE REFRESH ---
                    # This pauses for 2 seconds so the user can read the success message,
                    # then instantly reloads the page so the $850,000 drops down live.
                    time.sleep(2)
                    st.rerun() 
                    
                else:
                    st.error(f"❌ Transaction Blocked: {message}")
