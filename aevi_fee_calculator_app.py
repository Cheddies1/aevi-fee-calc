import streamlit as st

st.set_page_config(page_title="Aevi Fee Calculator", layout="centered")

st.title("Aevi Fee Calculator")

st.markdown("Use this tool to calculate and compare Aevi platform fees based on different pricing models.")

# Sidebar inputs
st.sidebar.header("Inputs")

avg_ticket = st.sidebar.number_input("Average Ticket Size (€)", min_value=0.01, value=25.00, step=0.01)
avg_txns = st.sidebar.number_input("Transactions per Terminal per Month", min_value=1, value=400)
terminals = st.sidebar.number_input("Number of Transacting Terminals", min_value=1, value=100)

bps_share = st.sidebar.number_input("Aevi BPs Share", min_value=0.0, value=20.0, step=0.1)
fixed_fee_terminal = st.sidebar.number_input("Fixed Fee per Terminal per Month (€)", min_value=0.0, value=0.00, step=0.01)
fixed_fee_txn = st.sidebar.number_input("Fixed Fee per Transaction (€)", min_value=0.0, value=0.00, step=0.01)

pricing_mode = st.selectbox("Pricing Mode", ["Cumulative (AND)", "Compare (OR)"])

# Calculations
monthly_value = avg_ticket * avg_txns

if pricing_mode == "Cumulative (AND)":
    variable_fee_per_txn = (bps_share / 10000) * avg_ticket
    fixed_fee_per_txn = fixed_fee_txn + (fixed_fee_terminal / avg_txns)
    total_fee_per_txn = variable_fee_per_txn + fixed_fee_per_txn
    monthly_revenue_per_terminal = total_fee_per_txn * avg_txns
    total_monthly_revenue = monthly_revenue_per_terminal * terminals

    # Outputs
    st.subheader("Cumulative Results (AND Mode)")

    st.write(f"**Monthly Transaction Value per Terminal:** €{monthly_value:,.2f}")
    st.write(f"**Aevi Variable Fee per Transaction:** €{variable_fee_per_txn:.4f}")
    st.write(f"**Aevi Fixed Fee per Transaction:** €{fixed_fee_per_txn:.4f}")
    st.write(f"**Total Aevi Fee per Transaction:** €{total_fee_per_txn:.4f}")
    st.markdown("---")
    st.write(f"**Monthly Revenue per Terminal:** €{monthly_revenue_per_terminal:,.2f}")
    st.write(f"**Total Aevi Revenue per Month (Estate):** €{total_monthly_revenue:,.2f}")

else:
    # OR mode - show each pricing model separately
    st.subheader("Comparative Results (OR Mode)")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### BPs Only")
        bps_only_per_terminal = (bps_share / 10000) * avg_ticket * avg_txns
        bps_only_total = bps_only_per_terminal * terminals
        st.write(f"Per Terminal: €{bps_only_per_terminal:,.2f}")
        st.write(f"Total: €{bps_only_total:,.2f}")

    with col2:
        st.markdown("### Fixed per Transaction Only")
        fixed_txn_per_terminal = fixed_fee_txn * avg_txns
        fixed_txn_total = fixed_txn_per_terminal * terminals
        st.write(f"Per Terminal: €{fixed_txn_per_terminal:,.2f}")
        st.write(f"Total: €{fixed_txn_total:,.2f}")

    with col3:
        st.markdown("### Fixed per Terminal Only")
        fixed_terminal_total = fixed_fee_terminal * terminals
        st.write(f"Per Terminal: €{fixed_fee_terminal:,.2f}")
        st.write(f"Total: €{fixed_terminal_total:,.2f}")

st.markdown("---")
st.caption("This calculator supports flexible pricing models. Contact Aevi to discuss custom scenarios or deeper analysis.")
