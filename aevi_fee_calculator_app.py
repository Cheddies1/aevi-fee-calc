import streamlit as st
import pandas as pd

# ===== Constants  =====

EU_INTERCHANGE_CREDIT = 0.003  # 0.30%
EU_SCHEME = 0.001              # 0.10%
EU_ACQUIRER = 0.0015           # 0.15%

US_INTERCHANGE_CREDIT = 0.018   # 1.8%
US_INTERCHANGE_REG_DEBIT = 0.27 # 27c fixed
US_SCHEME = 0.0016              # 0.16%
US_SCHEME_FIXED = 0.02          # 2c
US_ACQUIRER = 0.0015            # 0.15%
US_ACQUIRER_FIXED = 0.08        # 8c

# ===== Helper Functions =====

def calculate_aevi_fees(ticket, txns, bps_share, fixed_fee_terminal, fixed_fee_txn):
    variable_fee = (bps_share / 10000) * ticket
    # Avoid zero division for per-terminal fee
    fixed_fee = fixed_fee_txn + (fixed_fee_terminal / txns if txns else 0)
    total_fee = variable_fee + fixed_fee
    revenue_per_terminal = total_fee * txns
    return variable_fee, fixed_fee, total_fee, revenue_per_terminal

def eu_total_cost_per_txn(aevi_fee, avg_ticket):
    # All in EUR, all % on ticket
    return (EU_INTERCHANGE_CREDIT + EU_SCHEME + EU_ACQUIRER) * avg_ticket + aevi_fee

def us_total_cost_per_txn(aevi_fee, avg_ticket, tx_type="credit"):
    # For this version, just model "US Credit"
    # $1.80 (1.8%) interchange, $0.16 (0.14% + 2c) scheme, $0.23 (0.15% + 8c) acquirer
    # All fixed USD, but let's assume EUR=USD for estimation
    if tx_type == "credit":
        return (US_INTERCHANGE_CREDIT + US_SCHEME + US_ACQUIRER) * avg_ticket \
               + US_SCHEME_FIXED + US_ACQUIRER_FIXED + aevi_fee
    elif tx_type == "reg_debit":
        return US_INTERCHANGE_REG_DEBIT + US_SCHEME + US_SCHEME_FIXED + US_ACQUIRER + US_ACQUIRER_FIXED + aevi_fee
    else:
        return 0  # Or raise an exception


def build_scenario_df(terminals, bps_share, fixed_fee_terminal, fixed_fee_txn, currency):
    data = []
    scenarios = [
        ("Worst-case Merchant", 300, 14),
        ("Average SMB", 400, 20),
        ("Tier 1 Retail", 4000, 25),
    ]
    for label, txns, ticket in scenarios:
        variable_fee, fixed_fee, total_fee, per_terminal = calculate_aevi_fees(
            ticket, txns, bps_share, fixed_fee_terminal, fixed_fee_txn
        )
        estate = per_terminal * terminals
        data.append({
            "Scenario": label,
            f"Monthly Value/Terminal ({currency})": f"{txns * ticket:,.2f}",
            f"Fee/Transaction ({currency})": f"{total_fee:.4f}",
            f"Revenue/Terminal ({currency})": f"{per_terminal:,.2f}",
            f"Estate Revenue ({currency})": f"{estate:,.2f}"
        })
    return pd.DataFrame(data)


# ===== Streamlit App Layout =====

st.set_page_config(
    page_title="Aevi Fee Calculator",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("Aevi Fee Calculator")
st.markdown("Use this tool to calculate and compare Aevi platform fees based on different pricing models.")

# ---- Sidebar Inputs ----
st.sidebar.header("Inputs")
currency = st.sidebar.selectbox("Currency", ["€", "$"], index=0, help="Choose display currency for all outputs")
st.sidebar.subheader("Estate Details")
avg_ticket = st.sidebar.number_input(f"Average ticket size ({currency})", min_value=1, value=10, help="What is the average transaction size in the estate? Normally between €10 and €25")
avg_txns = st.sidebar.number_input("Transactions per terminal", min_value=1, value=400, help="SMB close to 400, Tier 1 4000+ - everything else somewhere in the middle")
terminals = st.sidebar.number_input("Number of transacting terminals", min_value=1, value=100, help="What is our likely max estate size?")

st.sidebar.markdown("---")
st.sidebar.subheader("Pricing Details")
bps_share = st.sidebar.number_input("Basis point share", min_value=0, value=0, step=1, help="Basis points (e.g., 20 = 0.20%) scales well with transaction value")
fixed_fee_terminal = st.sidebar.number_input(f"Fee per Terminal per Month ({currency})", min_value=0.0, value=0.00, step=0.01, help="Basic flat per terminal per month rate")
fixed_fee_txn = st.sidebar.number_input(f"Fixed Fee per Transaction ({currency})", min_value=0.0, value=0.00, step=0.001, format="%.3f", help="fixed euro or dollar-cent fee per transaction - often useful for high volume low value")

pricing_mode = st.selectbox("Pricing Mode", ["Cumulative (AND)", "Compare (OR)", "Benchmark Against Adyen"])


monthly_value = avg_ticket * avg_txns

# ---- Main Calculation ----

if pricing_mode == "Cumulative (AND)":
    variable_fee_per_txn, fixed_fee_per_txn, total_fee_per_txn, monthly_revenue_per_terminal = calculate_aevi_fees(
        avg_ticket, avg_txns, bps_share, fixed_fee_terminal, fixed_fee_txn
    )
    total_monthly_revenue = monthly_revenue_per_terminal * terminals

    # Total cost per transaction in EU and US
    total_cost_txn_eu = eu_total_cost_per_txn(total_fee_per_txn, avg_ticket)
    total_cost_txn_us = us_total_cost_per_txn(total_fee_per_txn, avg_ticket, tx_type="credit")

    st.subheader("Cumulative Results (AND Mode)")
    st.markdown("---")

    col1, col2 = st.columns([2, 1])
    col1.markdown("Monthly Transaction Value per Terminal:")
    col2.markdown(f"<div style='text-align: right; padding-right: 6px;'><p>{currency}{monthly_value:,.2f}</p></div>", unsafe_allow_html=True)
    col1.markdown("Aevi Variable Fee per Transaction:")
    col2.markdown(f"<div style='text-align: right; padding-right: 6px;'><p>{currency}{variable_fee_per_txn:.4f}</p></div>", unsafe_allow_html=True)
    col1.markdown("Aevi Fixed Fee per Transaction:")
    col2.markdown(f"<div style='text-align: right; padding-right: 6px;'><p>{currency}{fixed_fee_per_txn:.4f}</p></div>", unsafe_allow_html=True)
    col1.markdown("Total Aevi Fee per Transaction:")
    col2.markdown(f"<div style='text-align: right; padding-right: 6px;'><p>{currency}{total_fee_per_txn:.4f}</p></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        f"""
        <div style='
            border: 2px solid var(--primary-color,#0074e8);
            background: var(--secondary-background-color,#f2f7fc);
            color: var(--text-color,#222);
            border-radius: 10px;
            padding: 18px 18px 18px 18px;
            margin: 12px 0 18px 0;
        '>
            <b style='font-size: 1.15em;'>Aevi Revenue 💸</b>
            <div style='display: flex; justify-content: space-between; margin-top: 12px;'>
                <span>Monthly Revenue per Terminal:</span>
                <span style='min-width: 120px; text-align: right;'><b>{currency} {monthly_revenue_per_terminal:,.2f}</b></span>
            </div>
            <div style='display: flex; justify-content: space-between; margin-top: 6px;'>
                <span>Monthly Estate Revenue:</span>
                <span style='min-width: 120px; text-align: right;'><b>{currency} {total_monthly_revenue:,.2f}</b></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )




    st.markdown("---")
    st.markdown("**Estimated Total Cost per Transaction in the EU (Incl. Acquirer, Interchange, Scheme):**")
    col1, col2 = st.columns([2, 1])
    col1.markdown("Total Cost (EU Credit):")
    col2.markdown(f"<div style='text-align: right; padding-right: 6px;'><p>€{total_cost_txn_eu:.4f}</p></div>", unsafe_allow_html=True)
    st.caption("Includes European Acquirer Fee (15bps), Interchange (30bps), Scheme Fee (10bps)")

    st.markdown("**Estimated Total Cost per Transaction in the US (Incl. Acquirer, Interchange, Scheme):**")
    col1, col2 = st.columns([2, 1])
    col1.markdown("Total Cost (US Credit):")
    col2.markdown(f"<div style='text-align: right; padding-right: 6px;'><p>${total_cost_txn_us:.4f}</p></div>", unsafe_allow_html=True)
    st.caption("US: Interchange (180bps), Scheme Fee (16bps and 2c), Acquirer (15bps and 8c)")


    # ---- Reference Scenario Table (only in AND mode) ----
    st.markdown("---")
    st.subheader("Reference Scenarios (Based on Your Pricing)")
    st.caption(f"Worst case merchant - 300TRX average {currency}14 / Average - 400TRX average {currency}20 / T1 - 4000 average {currency}25")
    scenario_df = build_scenario_df(terminals, bps_share, fixed_fee_terminal, fixed_fee_txn, currency)
    st.dataframe(scenario_df, use_container_width=True)

elif pricing_mode == "Compare (OR)":
    st.subheader("Comparative Results (OR Mode)")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### BPs Only")
        bps_only_per_terminal = (bps_share / 10000) * avg_ticket * avg_txns
        bps_only_total = bps_only_per_terminal * terminals
        st.write(f"Per Terminal: {currency}{bps_only_per_terminal:,.2f}")
        st.write(f"Total: {currency}{bps_only_total:,.2f}")

    with col2:
        st.markdown("### Fixed per Transaction Only")
        fixed_txn_per_terminal = fixed_fee_txn * avg_txns
        fixed_txn_total = fixed_txn_per_terminal * terminals
        st.write(f"Per Terminal: {currency}{fixed_txn_per_terminal:,.2f}")
        st.write(f"Total: {currency}{fixed_txn_total:,.2f}")

    with col3:
        st.markdown("### Fixed per Terminal Only")
        fixed_terminal_total = fixed_fee_terminal * terminals
        st.write(f"Per Terminal: {currency}{fixed_fee_terminal:,.2f}")
        st.write(f"Total: {currency}{fixed_terminal_total:,.2f}")

elif pricing_mode == "Benchmark Against Adyen":
    st.subheader("Adyen Benchmark Comparison")
    st.caption("_This benchmark is based on publicly available data and internal research. Actual charges may differ. This does **not include** Adyen acquiring fees, only platform fees_")

    col1, col2, col3 = st.columns(3)
    adyen_txns = avg_txns
    adyen_terminals = terminals

    with col1:
        st.markdown(f"### Adyen Low ({currency}0.05)")
        fee = 0.05
        per_terminal = fee * adyen_txns
        total = per_terminal * adyen_terminals
        st.write(f"Per Terminal: {currency}{per_terminal:.2f}")
        st.write(f"Total: {currency}{total:,.2f}")

    with col2:
        st.markdown(f"### Adyen High ({currency}0.12)")
        fee = 0.12
        per_terminal = fee * adyen_txns
        total = per_terminal * adyen_terminals
        st.write(f"Per Terminal: {currency}{per_terminal:.2f}")
        st.write(f"Total: {currency}{total:,.2f}")

    with col3:
        st.markdown("### Current Aevi Model")
        variable_fee_per_txn, fixed_fee_per_txn, total_fee_per_txn, aevi_per_terminal = calculate_aevi_fees(
            avg_ticket, avg_txns, bps_share, fixed_fee_terminal, fixed_fee_txn
        )
        aevi_total = aevi_per_terminal * terminals
        st.write(f"Per Terminal: {currency}{aevi_per_terminal:.2f}")
        st.write(f"Total: {currency}{aevi_total:,.2f}")

st.markdown("---")

