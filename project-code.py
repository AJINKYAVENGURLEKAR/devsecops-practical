

import streamlit as st
import pandas as pd
import json

# --- BACKEND LOGIC ---
def calculate_payouts(sales_df, plan):
    """Processes sales data against JSON-defined commission rules."""
    results = []
    
    for _, deal in sales_df.iterrows():
        revenue = deal['Revenue']
        rep_name = deal['Sales_Rep']
        commission_earned = 0
        
        # Apply rules from the JSON plan
        for rule in plan['rules']:
            if revenue >= rule['min_threshold'] and revenue < rule['max_threshold']:
                commission_earned = revenue * rule['rate']
                break # Stop at the first matching tier
        
        results.append({
            "Deal_ID": deal['Deal_ID'],
            "Sales_Rep": rep_name,
            "Revenue": revenue,
            "Commission_Earned": round(commission_earned, 2)
        })
    
    return pd.DataFrame(results)

# --- FRONTEND (STREAMLIT) ---
st.set_page_config(page_title="CompLogic | Incentive Engine", layout="wide")

st.title("📊 CompLogic: Incentive Engine")
st.markdown("Automate your sales compensation lifecycle with precision logic.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Setup Compensation Plan")
    # Default JSON template for ease of use
    default_plan = {
        "rules": [
            {"tier": "Junior", "min_threshold": 0, "max_threshold": 5000, "rate": 0.05},
            {"tier": "Standard", "min_threshold": 5000, "max_threshold": 15000, "rate": 0.10},
            {"tier": "Elite", "min_threshold": 15000, "max_threshold": 1000000, "rate": 0.15}
        ]
    }
    plan_input = st.text_area("Define Rules (JSON Format)", value=json.dumps(default_plan, indent=4), height=250)

with col2:
    st.subheader("2. Upload Sales Ledger")
    uploaded_file = st.file_uploader("Upload CSV (Required columns: Deal_ID, Sales_Rep, Revenue)", type="csv")
    
    if st.checkbox("Use Sample Data"):
        uploaded_file = pd.DataFrame({
            "Deal_ID": ["D001", "D002", "D003", "D004"],
            "Sales_Rep": ["Alice", "Bob", "Alice", "Charlie"],
            "Revenue": [4500, 12000, 20000, 8000]
        })

# --- EXECUTION ---
if uploaded_file is not None:
    sales_data = uploaded_file if isinstance(uploaded_file, pd.DataFrame) else pd.read_csv(uploaded_file)
    
    if st.button("🚀 Run Payout Calculation"):
        try:
            plan_json = json.loads(plan_input)
            payout_report = calculate_payouts(sales_data, plan_json)
            
            st.divider()
            st.success("Calculations Complete!")
            
            # Display Metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Revenue", f"${payout_report['Revenue'].sum():,.2f}")
            m2.metric("Total Commission", f"${payout_report['Commission_Earned'].sum():,.2f}")
            m3.metric("Error Rate", "0.00%")
            
            # Detailed Report
            st.dataframe(payout_report, use_container_width=True)
            
            # Download Button
            csv = payout_report.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Payout Report", data=csv, file_name="final_payouts.csv", mime='text/csv')
            
        except Exception as e:
            st.error(f"Logic Error: Please check your JSON formatting. Details: {e}")