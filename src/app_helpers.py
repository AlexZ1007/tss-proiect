from datetime import datetime
from typing import Any, Dict, Tuple

from calculator_pfa import PFACalculator
from calculator_employee import EmployeeCalculator


def initialize_session_state(years: list[int]) -> None:
    if "saved_simulations" not in st_session():
        st_session()["saved_simulations"] = []
    if "active_simulation" not in st_session():
        st_session()["active_simulation"] = None
    if "input_venit_brut" not in st_session():
        st_session()["input_venit_brut"] = 120000.0
    if "input_an_fiscal" not in st_session():
        st_session()["input_an_fiscal"] = years[-1]
    if "load_request_idx" not in st_session():
        st_session()["load_request_idx"] = None
    if "last_run_at" not in st_session():
        st_session()["last_run_at"] = None
    if "flash_message" not in st_session():
        st_session()["flash_message"] = None


def st_session() -> Dict[str, Any]:
    import streamlit as st

    return st.session_state


def apply_pending_load_request() -> None:
    session = st_session()
    if session["load_request_idx"] is None:
        return

    load_idx = session["load_request_idx"]
    if 0 <= load_idx < len(session["saved_simulations"]):
        loaded = session["saved_simulations"][load_idx]["data"]
        session["input_venit_brut"] = float(loaded["venit_brut"])
        session["input_an_fiscal"] = int(loaded["anul_fiscal"])
        session["active_simulation"] = loaded
    session["load_request_idx"] = None


def build_simulation(venit: float, an: int) -> Dict[str, Any]:
    employee = EmployeeCalculator(venit, an).calculate()
    pfa = PFACalculator(venit, an).calculate()
    employee_rate = (employee["total_taxe"] / venit * 100) if venit else 0.0
    pfa_rate = (pfa["total_taxe"] / venit * 100) if venit else 0.0
    if employee["venit_net"]:
        net_diff_pct = ((pfa["venit_net"] - employee["venit_net"]) / employee["venit_net"]) * 100
    else:
        net_diff_pct = 0.0
    return {
        "venit_brut": float(venit),
        "anul_fiscal": int(an),
        "employee": employee,
        "pfa": pfa,
        "employee_tax_rate": employee_rate,
        "pfa_tax_rate": pfa_rate,
        "net_diff_percent": net_diff_pct,
    }


def run_simulation(venit_brut: float, anul_fiscal: int, user_triggered: bool) -> bool:
    session = st_session()
    should_run = user_triggered or session["active_simulation"] is None
    if not should_run:
        return False

    session["active_simulation"] = build_simulation(venit_brut, anul_fiscal)
    session["last_run_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if user_triggered:
        session["flash_message"] = "Simulation run successfully."
    return True


def save_simulation(venit_brut: float, anul_fiscal: int) -> None:
    session = st_session()
    active = build_simulation(venit_brut, anul_fiscal)
    session["active_simulation"] = active
    simulation_name = f"Year {active['anul_fiscal']} | {active['venit_brut']:,.0f} RON"
    session["saved_simulations"].append({"name": simulation_name, "data": active.copy()})
    session["flash_message"] = "Simulation saved."


def load_sidebar(years: list[int]) -> Tuple[float, int, bool, bool]:
    import streamlit as st

    with st.sidebar:
        st.header("Input Data")
        venit_brut = st.number_input(
            "Estimated annual gross income (RON)",
            min_value=0.0,
            key="input_venit_brut",
            step=1000.0,
        )
        anul_fiscal = st.selectbox("Fiscal year", years, key="input_an_fiscal")
        run_simulation_clicked = st.button("Run simulation", use_container_width=True)
        save_simulation_clicked = st.button("Save simulation", use_container_width=True)
        if st.session_state.flash_message:
            st.success(st.session_state.flash_message)
            st.session_state.flash_message = None

        st.divider()
        st.subheader("Previous Simulations")
        has_saved = len(st.session_state.saved_simulations) > 0

        if has_saved:
            st.caption("Select a saved simulation from the list below.")
            scroll_box = st.container(height=320, border=True)
            with scroll_box:
                # Latest simulation first for faster access.
                for idx in range(len(st.session_state.saved_simulations) - 1, -1, -1):
                    sim = st.session_state.saved_simulations[idx]
                    preview = sim["data"]
                    card = st.container(border=True)
                    with card:
                        st.markdown(f"**{sim['name']}**")
                        st.caption(
                            f"Year: {preview['anul_fiscal']} | Gross income: {preview['venit_brut']:,.0f} RON"
                        )
                        if st.button(
                            "Select",
                            key=f"load_sim_{idx}",
                            use_container_width=True,
                        ):
                            st.session_state.load_request_idx = idx
                            st.rerun()
        else:
            st.caption("No saved simulations yet.")

    return float(venit_brut), int(anul_fiscal), run_simulation_clicked, save_simulation_clicked


def render_scenario_metrics(
    title: str,
    results: Dict[str, float],
    effective_tax_rate: float,
    delta_text: str,
) -> None:
    import streamlit as st

    st.subheader(title)
    st.metric("CAS", f"{results['cas']:,.2f} RON")
    st.metric("CASS", f"{results['cass']:,.2f} RON")
    st.metric("Income Tax", f"{results['impozit']:,.2f} RON")
    st.metric("Net Income", f"{results['venit_net']:,.2f} RON")
    st.metric(
        "Effective Tax Rate",
        f"{effective_tax_rate:.2f}%",
        delta_text,
        delta_color="inverse",
    )


def get_active_simulation_values() -> Dict[str, Any]:
    session = st_session()
    active = session["active_simulation"]
    return {
        "venit_brut": active["venit_brut"],
        "anul_fiscal": active["anul_fiscal"],
        "employee_results": active["employee"],
        "pfa_results": active["pfa"],
        "employee_tax_rate": active["employee_tax_rate"],
        "pfa_tax_rate": active["pfa_tax_rate"],
        "net_diff_percent": active["net_diff_percent"],
    }

