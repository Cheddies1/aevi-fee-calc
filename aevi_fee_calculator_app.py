
import streamlit as st

st.set_page_config(page_title="Aevi Fee Calculator", layout="centered")

st.title("Aevi Fee Calculator")

st.markdown("Use this tool to calculate per-terminal and estate-wide Aevi platform fees based on your business inputs.")

# Sidebar inputs
st.sidebar.header("Inputs")

avg_ticket = st.sidebar.number_input("Average Ticket Size (€)", min_value=0.01, value=25.00, step=0.01)
avg_txns = st.sidebar.number_input("Transactions per Terminal per Month", min_value=1, value=400)
terminals = st.sidebar.number_input("Number of Transacting Terminals", min_value=1, value=100)

bps_share = st.sidebar.number_input("Aevi BPs Share", min_value=0.0, value=20.0, step=0.1)
fixed_fee_terminal = st.sidebar.number_input("Fixed Fee per Terminal per Month (€)", min_value=0.0, value=0.00, step=0.01)
fixed_fee_txn = st.sidebar.number_input("Fixed Fee per Transaction (€)", min_value=0.0, value=0.00, step=0.01)

# Calculations
monthly_volume = avg_ticket * avg_txns
variable_fee_per_txn = (bps_share / 10000) * avg_ticket
total_fee_per_txn = variable_fee_per_txn + fixed_fee_txn

monthly_revenue_per_terminal = (variable_fee_per_txn * avg_txns) + (fixed_fee_txn * avg_txns) + fixed_fee_terminal
total_monthly_revenue = monthly_revenue_per_terminal * terminals

# Outputs
st.subheader("Results")

st.write(f"**Monthly Transaction Volume per Terminal:** €{monthly_volume:,.2f}")
st.write(f"**Aevi Variable Fee per Transaction:** €{variable_fee_per_txn:.4f}")
st.write(f"**Total Aevi Fee per Transaction:** €{total_fee_per_txn:.4f}")
st.write(f"**Monthly Revenue per Terminal:** €{monthly_revenue_per_terminal:,.2f}")
st.write(f"**Total Aevi Revenue per Month (Estate):** €{total_monthly_revenue:,.2f}")

st.markdown("---")
st.caption("This tool is a simplified revenue model. For detailed or custom pricing scenarios, consult the Aevi team.")
