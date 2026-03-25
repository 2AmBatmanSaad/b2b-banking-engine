import streamlit as st
import pandas as pd
import bank_logic

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Wayne Treasury", page_icon="🦇", layout="wide")

# Hide the default Streamlit menus to make it look like a real app
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Make the metric card look premium and massive */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0px 8px 24px rgba(149, 157, 165, 0.2);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Load Database
corp_df, emp_df, hist_df = bank_logic.load_db()
if corp_df is not None:
    company_balance = corp_df[corp_df['CompanyID'] == 'CORP-001']['Balance'].values[0]
else:
    company_balance = 0.00

# --- THE IDIOT-PROOF LAYOUT ---
# We use empty columns on the left and right to squeeze the app into the center
spacer_left, main_content, spacer_right = st.columns([1, 2, 1])

with main_content:
    # 1. The Focal Point (Massive numbers, nothing else)
    st.write("<br><br>", unsafe_allow_html=True) # Adds breathing room at the top
    st.markdown("<p style='text-align: center; color: #888;'>Wayne Enterprises • Corporate Treasury</p>", unsafe_allow_html=True)
    
    st.metric(label="Available Liquidity", value=f"${company_balance:,.2f}")
    st.write("<br>", unsafe_allow_html=True)

    # 2. The Single Action (The "One Job" Rule)
    st.markdown("### 💸 Run Monthly Payroll")
    st.info("Drop your verified CSV here to automatically dispatch funds to employees.")
    
    uploaded_file = st.file_uploader("", type=["csv"])

    if uploaded_file is not None:
        st.write("<br>", unsafe_allow_html=True)
        # 3. The Big Shiny Button
        if st.button("AUTHORIZE PAYROLL BATCH", type="primary", use_container_width=True):
            with st.spinner("Processing secure transfer..."):
                success, message = bank_logic.process_payroll('CORP-001', uploaded_file)
                if success:
                    st.success(message)
                    st.balloons()
                else:
                    st.error(f"❌ Transaction Blocked: {message}")
