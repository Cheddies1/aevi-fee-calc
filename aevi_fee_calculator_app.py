import streamlit as st

st.set_page_config(
    page_title="Aevi Fee Calculator",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("Aevi Fee Calculator")
st.markdown("Use this tool to calculate and compare Aevi platform fees based on different pricing models.")

# Sidebar inputs
st.sidebar.header("Inputs")
st.sidebar.subheader("Estate Details")
avg_ticket = st.sidebar.number_input("Average Ticket Size (€)", min_value=0.01, value=25.00, step=0.01)
avg_txns = st.sidebar.number_input("Transactions per Terminal per Month", min_value=1, value=400)
terminals = st.sidebar.number_input("Number of Transacting Terminals", min_value=1, value=100)

st.sidebar.markdown("---")
st.sidebar.subheader("Pricing Details")
bps_share = st.sidebar.number_input("Aevi BPs Share", min_value=0.0, value=20.0, step=0.1)
fixed_fee_terminal = st.sidebar.number_input("Fixed Fee per Terminal per Month (€)", min_value=0.0, value=0.00, step=0.01)
fixed_fee_txn = st.sidebar.number_input("Fixed Fee per Transaction (€)", min_value=0.0, value=0.00, step=0.01)

pricing_mode = st.selectbox("Pricing Mode", ["Cumulative (AND)", "Compare (OR)", "Benchmark Against Adyen"])

# Constants for cost modelling - EU
interchange_fee_rate = 0.003  # 0.30%
scheme_fee_rate = 0.001       # 0.10%
acquirer_fee_rate = 0.0015    # 15bps

monthly_value = avg_ticket * avg_txns

def calculate_total_cost_per_txn(aevi_fee):
    return (interchange_fee_rate + scheme_fee_rate + acquirer_fee_rate) * avg_ticket + aevi_fee

if pricing_mode == "Cumulative (AND)":
    variable_fee_per_txn = (bps_share / 10000) * avg_ticket
    fixed_fee_per_txn = fixed_fee_txn + (fixed_fee_terminal / avg_txns)
    total_fee_per_txn = variable_fee_per_txn + fixed_fee_per_txn
    monthly_revenue_per_terminal = total_fee_per_txn * avg_txns
    total_monthly_revenue = monthly_revenue_per_terminal * terminals

    # Total cost calc (incl. acquirer, interchange, scheme)
    acquirer_fee = acquirer_fee_rate * avg_ticket
    interchange_fee = interchange_fee_rate * avg_ticket
    scheme_fee = scheme_fee_rate * avg_ticket
    total_cost_txn = acquirer_fee + interchange_fee + scheme_fee + total_fee_per_txn

    # Outputs
    st.subheader("Cumulative Results (AND Mode)")
    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    col1.markdown("Monthly Transaction Value per Terminal:")
    col2.markdown(f"<div style='text-align: right; padding-right: 6px;'><p>€{monthly_value:,.2f}</p></div>", unsafe_allow_html=True)

    col1.markdown("Aevi Variable Fee per Transaction:")
    col2.markdown(f"<div style='text-align: right; padding-right: 6px;'><p>€{variable_fee_per_txn:.4f}</p></div>", unsafe_allow_html=True)

    col1.markdown("Aevi Fixed Fee per Transaction:")
    col2.markdown(f"<div style='text-align: right; padding-right: 6px;'><p>€{fixed_fee_per_txn:.4f}</p></div>", unsafe_allow_html=True)

    col1.markdown("Total Aevi Fee per Transaction:")
    col2.markdown(f"<div style='text-align: right; padding-right: 6px;'><p>€{total_fee_per_txn:.4f}</p></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Estimated Total Cost per Transaction in the EU (Incl. Acquirer, Interchange, Scheme):**")

    col1, col2 = st.columns([2, 1])
    col1.markdown("Total Cost:")
    col2.markdown(f"<div style='text-align: right; padding-right: 6px;'><p>€{total_cost_txn:.4f}</p></div>", unsafe_allow_html=True)

    st.caption("Includes European Acquirer Fee (15bps), Interchange (30bps), Scheme Fee (10bps)")

    st.markdown("---")
    st.subheader("Aevi Revenue")

    col1, col2 = st.columns([2, 1])
    col1.markdown("Monthly Revenue per Terminal:")
    col2.markdown(f"<div style='text-align: right; padding-right: 6px;'><p>€{monthly_revenue_per_terminal:,.2f}</p></div>", unsafe_allow_html=True)

    col1.markdown("Monthly Estate Revenue:")
    col2.markdown(f"<div style='text-align: right; padding-right: 6px;'><p>€{total_monthly_revenue:,.2f}</p></div>", unsafe_allow_html=True)



elif pricing_mode == "Compare (OR)":
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

elif pricing_mode == "Benchmark Against Adyen":
    st.subheader("Adyen Benchmark Comparison")
    st.caption("_This benchmark is based on publicly available data and internal research. Actual charges may differ. This does **not include** adyen acquiring fees, only platform fees_")

    col1, col2, col3 = st.columns(3)

    # Shared benchmark setup
    adyen_txns = avg_txns
    adyen_terminals = terminals

    with col1:
        st.markdown("### Adyen Low (€0.05)")
        fee = 0.05
        per_terminal = fee * adyen_txns
        total = per_terminal * adyen_terminals
        st.write(f"Per Terminal: €{per_terminal:.2f}")
        st.write(f"Total: €{total:,.2f}")

    with col2:
        st.markdown("### Adyen High (€0.12)")
        fee = 0.12
        per_terminal = fee * adyen_txns
        total = per_terminal * adyen_terminals
        st.write(f"Per Terminal: €{per_terminal:.2f}")
        st.write(f"Total: €{total:,.2f}")

    with col3:
        st.markdown("### Current Aevi Model")
        variable_fee_per_txn = (bps_share / 10000) * avg_ticket
        fixed_fee_per_txn = fixed_fee_txn + (fixed_fee_terminal / avg_txns)
        total_fee_per_txn = variable_fee_per_txn + fixed_fee_per_txn
        aevi_per_terminal = total_fee_per_txn * avg_txns
        aevi_total = aevi_per_terminal * terminals
        st.write(f"Per Terminal: €{aevi_per_terminal:.2f}")
        st.write(f"Total: €{aevi_total:,.2f}")


st.markdown("---")

st.caption("This calculator supports flexible pricing models. Contact Aevi to discuss custom scenarios or deeper analysis.")

# Reference scenarios (cumulative mode logic)
st.subheader("Reference Scenarios (Based on Your Pricing)")

scenario_data = [
    ("Worst-case Merchant", 300, 14),
    ("Average SMB", 400, 20),
    ("Tier 1 Retail", 4000, 25)
]

cols = st.columns(3)

for col, (label, txns, ticket) in zip(cols, scenario_data):
    value = txns * ticket
    variable_fee = (bps_share / 10000) * ticket
    fixed_fee = fixed_fee_txn + (fixed_fee_terminal / txns)
    total_fee = variable_fee + fixed_fee
    per_terminal = total_fee * txns
    estate = per_terminal * terminals

    with col:
        st.markdown(f"### {label}")
        st.write(f"**Monthly Value/Terminal:** €{value:,.2f}")
        st.write(f"**Fee/Transaction:** €{total_fee:.4f}")
        st.write(f"**Revenue/Terminal:** €{per_terminal:,.2f}")
        st.write(f"**Estate Revenue:** €{estate:,.2f}")