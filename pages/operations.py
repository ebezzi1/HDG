"""
Operations Page — Daily chemical addition calculator.

Operators enter tank measurements and receive precise dosing instructions.
Results can be saved to the history database for audit trail tracking.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from degreasing_calculator import DegreasingInputs, run_calculation
from hdg_history import save_entry

st.header("⚗️ Operations — Chemical Addition Calculator")
st.caption("Enter today's tank measurements to calculate the required degreasing agent addition.")

left, right = st.columns([2, 3], gap="large")

# ── Input Panel ───────────────────────────────────────────────────────────────
with left:
    with st.form("calc_form"):

        # --- Tank Dimensions ---
        st.subheader("Tank Dimensions")
        c1, c2, c3 = st.columns(3)
        with c1:
            L = st.number_input("Length L (m)", min_value=0.001, max_value=50.0,
                                value=3.0, step=0.01, format="%.2f")
        with c2:
            l = st.number_input("Width l (m)", min_value=0.001, max_value=50.0,
                                value=1.0, step=0.01, format="%.2f")
        with c3:
            h = st.number_input("Height h (m)", min_value=0.001, max_value=10.0,
                                value=2.0, step=0.01, format="%.2f")
        st.caption(
            f"Footprint: **{L * l:.2f} m²**  |  Full capacity: **{L * l * h * 1000:.0f} L**"
        )

        st.divider()

        # --- Bath Levels ---
        st.subheader("Bath Levels")
        niveau_boues = st.slider("Sludge Level — niveau_boues (%)", 0, 80, 5, step=1,
                                 help="Percentage of tank height occupied by settled sludge at the bottom.")
        n = st.slider("Reference Empty Space — n (%)", 1, 30, 10, step=1,
                      help="Target percentage of tank height that should remain empty above the solution.")
        Ve = st.slider("Current Empty Space — Ve (%)", 0, 80, 10, step=1,
                       help="Actual measured empty space at the top of the tank right now.")

        used = niveau_boues + Ve
        if used < 100:
            st.caption(
                f"Sludge + current empty = **{used}%**  →  solution occupies **{100 - used}%** of tank height"
            )
        else:
            st.error(f"Sludge ({niveau_boues}%) + empty ({Ve}%) = {used}% — exceeds 100%.")

        st.divider()

        # --- Concentrations ---
        st.subheader("Concentrations (g/L)")
        ca, cb = st.columns(2)
        with ca:
            conc_min       = st.number_input("Min Acceptable", min_value=0.0,
                                             value=30.0, step=0.1, format="%.1f")
            conc_souhaitee = st.number_input("Target (Réf. Conc.)", min_value=0.0,
                                             value=45.0, step=0.1, format="%.1f")
        with cb:
            conc_max = st.number_input("Max Acceptable", min_value=0.0,
                                       value=60.0, step=0.1, format="%.1f")
            conc_i   = st.number_input("Current Concentration", min_value=0.0,
                                       value=35.0, step=0.1, format="%.1f")

        # Live concentration indicator
        if conc_min < conc_max:
            if conc_i < conc_min:
                st.warning(f"Current {conc_i} g/L is **below** minimum ({conc_min} g/L)")
            elif conc_i > conc_max:
                st.error(f"Current {conc_i} g/L is **above** maximum ({conc_max} g/L)")
            else:
                st.success(f"Current {conc_i} g/L is within range [{conc_min} – {conc_max} g/L]")

        st.divider()
        submitted = st.form_submit_button(
            "Calculate",
            type="primary",
            use_container_width=True,
        )

# ── Results Panel ─────────────────────────────────────────────────────────────
with right:
    # Store results in session state so they persist across reruns
    if submitted:
        inputs = DegreasingInputs(
            L=L, l=l, h=h,
            niveau_boues=niveau_boues, n=n, Ve=Ve,
            conc_i=conc_i, conc_souhaitee=conc_souhaitee,
            conc_min=conc_min, conc_max=conc_max,
        )
        outputs, errors = run_calculation(inputs)
        st.session_state['ops_inputs']  = inputs
        st.session_state['ops_outputs'] = outputs
        st.session_state['ops_errors']  = errors

    if 'ops_errors' not in st.session_state:
        st.info("Fill in the measurements and press **Calculate**.")
        st.stop()

    errors  = st.session_state['ops_errors']
    outputs = st.session_state['ops_outputs']
    inputs  = st.session_state['ops_inputs']

    # --- Validation errors ---
    if errors:
        for err in errors:
            st.error(err)
        st.stop()

    # --- Concentration status banner ---
    if outputs.conc_status == "OK":
        st.success(f"Concentration OK — {inputs.conc_i} g/L is within the acceptable range.")
    elif outputs.conc_status == "LOW":
        st.warning(f"CONCENTRATION LOW — {outputs.alert_message}")
    else:
        st.error(f"CONCENTRATION HIGH — {outputs.alert_message}")

    # --- Metric cards ---
    st.subheader("Calculated Volumes")
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("VB (Total)", f"{outputs.VB:.0f} L")
    r2.metric("Vsf (Target)", f"{outputs.Vsf:.0f} L")
    r3.metric("Vsi (Current)", f"{outputs.Vsi:.0f} L")

    mf = outputs.mf
    if mf > 0:
        r4.metric("mf (Addition)", f"{mf:.2f} kg", delta=f"+{mf:.2f} kg")
    elif mf < 0:
        r4.metric("mf (Addition)", f"{mf:.2f} kg",
                  delta=f"{mf:.2f} kg", delta_color="inverse")
    else:
        r4.metric("mf (Addition)", "0.00 kg")

    # --- Primary operator instruction ---
    st.divider()
    st.subheader("Operator Instruction")
    if mf > 0:
        st.info(
            f"**Add {mf:.2f} kg** of degreasing agent to reach the target concentration "
            f"of {inputs.conc_souhaitee} g/L."
        )
    elif mf < 0:
        st.warning(
            f"**Do NOT add degreaser.** The bath is over-concentrated. "
            f"Excess equivalent: **{abs(mf):.2f} kg**. "
            f"Consult supervisor for dilution procedure."
        )
    else:
        st.success("Bath is at target — no addition needed.")

    st.caption(
        f"Fresh tank reference: a completely empty tank at target concentration "
        f"({inputs.conc_souhaitee} g/L) would require **{outputs.m_Total:.2f} kg**."
    )

    # --- Calculation detail expander ---
    with st.expander("Show calculation details", expanded=False):
        st.markdown(
            f"""
| Variable | Description | Formula | Value |
|---|---|---|---|
| VB | Total bath volume | L × l × h × 1000 | {outputs.VB:.2f} L |
| Vb | Sludge volume | 1000 × L × l × niveau_boues / 100 | {outputs.Vb:.2f} L |
| Vn | Reference headspace | 1000 × L × l × n / 100 | {outputs.Vn:.2f} L |
| Ve_L | Current empty space | 1000 × L × l × Ve / 100 | {outputs.Ve_L:.2f} L |
| Vsf | Final solution volume | VB − Vb − Vn | {outputs.Vsf:.2f} L |
| Vsi | Initial solution volume | VB − Ve_L − Vb | {outputs.Vsi:.2f} L |
| m_Total | Total mass (fresh tank) | Réf.Conc./1000 × Vsf | {outputs.m_Total:.2f} kg |
| mf | Adjustment mass | (Réf.Conc./1000 × Vsf) − (Conc.i/1000 × Vsi) | {outputs.mf:.2f} kg |
            """
        )

    # --- Save to history ---
    st.divider()
    st.subheader("Save to History")
    note = st.text_input(
        "Operator note (optional)",
        placeholder="e.g. Post-weekend top-up, after sludge drain…",
        key="ops_note",
    )
    if st.button("Save this operation to history", type="secondary"):
        save_entry(inputs, outputs, note)
        st.toast("Saved to history.", icon="✅")
