import streamlit as st

from app_helpers import (
    initialize_session_state,
    load_sidebar,
    render_scenario_metrics,
    run_simulation as run_simulation_action,
)
from tax_config import get_available_years


st.set_page_config(page_title="Comparator Taxe RO - PFA vs Salariat", layout="wide")
st.title("Romanian Tax Comparison: PFA vs Employee")

years = get_available_years()
initialize_session_state(years)

venit_brut, anul_fiscal, run_simulation_clicked = load_sidebar(years)


has_rerun_trigger = run_simulation_action(
    venit_brut, anul_fiscal, user_triggered=run_simulation_clicked
)
if has_rerun_trigger and run_simulation_clicked:
        st.rerun()

active = st.session_state.active_simulation
venit_brut = active["venit_brut"]
anul_fiscal = active["anul_fiscal"]
salariat_results = active["salariat"]
pfa_results = active["pfa"]
salariat_tax_rate = active["salariat_tax_rate"]
pfa_tax_rate = active["pfa_tax_rate"]
net_diff_percent = active["net_diff_percent"]

# Delta in tax rate: positive means this scenario has larger tax burden.
salariat_rate_delta = salariat_tax_rate - pfa_tax_rate
pfa_rate_delta = pfa_tax_rate - salariat_tax_rate

col1, col2 = st.columns(2)

with col1:
    render_scenario_metrics(
        title="Employee",
        results=salariat_results,
        effective_tax_rate=salariat_tax_rate,
        delta_text=f"{salariat_rate_delta:+.2f} pp vs PFA",
    )

with col2:
    render_scenario_metrics(
        title="PFA (Real System)",
        results=pfa_results,
        effective_tax_rate=pfa_tax_rate,
        delta_text=f"{pfa_rate_delta:+.2f} pp vs Employee",
    )

st.metric(
    "Net Income Percentage Difference (PFA vs Employee)",
    f"{net_diff_percent:+.2f}% ",
    (
        "PFA is more advantageous"
        if net_diff_percent > 0
        else "Employee is more advantageous"
        if net_diff_percent < 0
        else "Scenarios are equal"
    ),
)
