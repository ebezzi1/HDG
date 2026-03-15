"""
Dashboard Page — Real-time tank status visualization.

Shows the most recently saved operation from history:
  - Dynamic 2D tank cross-section
  - Concentration gauge with min/max thresholds
  - Status alert banner
  - Key metric cards
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import plotly.graph_objects as go
from hdg_history import get_last_entry

st.header("🏭 Tank Status Dashboard")
st.caption("Showing the most recently saved operation. Go to **Operations** to run a new calculation.")

entry = get_last_entry()

if entry is None:
    st.info(
        "No data recorded yet. Go to **Operations** to run your first calculation "
        "and save it to history."
    )
    st.stop()

# ── Status banner ─────────────────────────────────────────────────────────────
ts             = entry['timestamp']
status         = entry['conc_status']
conc_i         = entry['conc_i']
conc_min       = entry['conc_min']
conc_max       = entry['conc_max']
conc_souhaitee = entry['conc_souhaitee']

st.caption(f"Last updated: **{ts}**")

if status == "OK":
    st.success(f"Concentration OK — {conc_i} g/L is within range  [{conc_min} – {conc_max} g/L]")
elif status == "LOW":
    st.warning(
        f"⚠ ACTION REQUIRED — Concentration LOW: {conc_i} g/L is below the minimum ({conc_min} g/L). "
        f"Chemical addition is required."
    )
else:
    st.error(
        f"⛔ ACTION REQUIRED — Concentration HIGH: {conc_i} g/L is above the maximum ({conc_max} g/L). "
        f"Dilution is required."
    )

# ── Two-column layout ─────────────────────────────────────────────────────────
col_tank, col_gauge = st.columns([1, 1], gap="large")

# ── Visual Tank ───────────────────────────────────────────────────────────────
with col_tank:
    st.subheader("Tank Cross-Section")

    VB           = entry['vol_bath']
    niveau_boues = entry['niveau_boues']   # sludge fills 0 → niveau_boues %
    Ve           = entry['ve_pct']         # solution surface at (100 − Ve) %
    n            = entry['n']              # reference surface at (100 − n) %
    Vb           = entry['vol_sludge']
    Vsi          = entry['vol_initial']
    Ve_L         = entry['vol_empty']

    sludge_top   = niveau_boues            # sludge top y-coordinate (% of height)
    solution_top = 100 - Ve               # current solution surface
    ref_line_y   = 100 - n               # reference (target) surface

    fig_tank = go.Figure()

    # --- Tank background (inside walls) ---
    fig_tank.add_shape(
        type="rect", x0=20, y0=0, x1=80, y1=100,
        fillcolor="#eef2f7",
        line=dict(color="#1a1a2e", width=5),
    )

    # --- Sludge layer ---
    if sludge_top > 0:
        fig_tank.add_shape(
            type="rect", x0=20, y0=0, x1=80, y1=sludge_top,
            fillcolor="rgba(139, 69, 19, 0.78)",
            line=dict(color="rgba(100, 50, 10, 0.9)", width=1),
        )

    # --- Solution layer ---
    if solution_top > sludge_top:
        fig_tank.add_shape(
            type="rect", x0=20, y0=sludge_top, x1=80, y1=solution_top,
            fillcolor="rgba(66, 133, 244, 0.50)",
            line=dict(width=0),
        )

    # --- Reference level line (target fill level — dashed green) ---
    fig_tank.add_shape(
        type="line", x0=14, y0=ref_line_y, x1=86, y1=ref_line_y,
        line=dict(color="#00c853", width=2.5, dash="dash"),
    )

    # --- Current solution surface (solid blue line) ---
    fig_tank.add_shape(
        type="line", x0=20, y0=solution_top, x1=80, y1=solution_top,
        line=dict(color="#1565c0", width=2),
    )

    # --- Annotations ---
    # Total volume label above tank
    fig_tank.add_annotation(
        x=50, y=108,
        text=f"<b>VB = {VB:.0f} L</b>",
        showarrow=False,
        font=dict(size=13, color="#1a1a2e"),
    )

    # Sludge label
    if sludge_top >= 5:
        fig_tank.add_annotation(
            x=50, y=sludge_top / 2,
            text=f"<b>Sludge (Vb)</b><br>{Vb:.0f} L",
            showarrow=False,
            font=dict(size=11, color="white"),
            bgcolor="rgba(100, 50, 10, 0.55)",
            borderpad=4,
        )

    # Solution label
    sol_height = solution_top - sludge_top
    if sol_height >= 10:
        fig_tank.add_annotation(
            x=50, y=sludge_top + sol_height / 2,
            text=f"<b>Solution (Vsi)</b><br>{Vsi:.0f} L",
            showarrow=False,
            font=dict(size=11, color="#0d2b6e"),
            bgcolor="rgba(255,255,255,0.65)",
            borderpad=4,
        )

    # Headspace label
    headspace = 100 - solution_top
    if headspace >= 5:
        fig_tank.add_annotation(
            x=50, y=solution_top + headspace / 2,
            text=f"Headspace<br>{Ve_L:.0f} L",
            showarrow=False,
            font=dict(size=10, color="#555"),
        )

    # Reference line label
    fig_tank.add_annotation(
        x=88, y=ref_line_y,
        text=f"<i>Vn ref ({n:.0f}%)</i>",
        showarrow=False,
        font=dict(size=9, color="#00c853"),
        xanchor="left",
    )

    # Left side percentage ticks
    for pct, label in [(sludge_top / 2, f"{sludge_top:.0f}%"),
                        (sludge_top + sol_height / 2, f"{sol_height:.0f}%"),
                        (solution_top + headspace / 2, f"{headspace:.0f}%")]:
        fig_tank.add_annotation(
            x=18, y=pct, text=label,
            showarrow=False, font=dict(size=8, color="#777"),
            xanchor="right",
        )

    fig_tank.update_layout(
        height=420,
        margin=dict(l=30, r=90, t=45, b=10),
        xaxis=dict(range=[0, 100], visible=False),
        yaxis=dict(range=[-3, 115], visible=False),
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False,
    )
    st.plotly_chart(fig_tank, use_container_width=True)

# ── Concentration Gauge ───────────────────────────────────────────────────────
with col_gauge:
    st.subheader("Concentration Gauge")

    gauge_max = max(conc_max * 1.35, conc_i * 1.15, 80.0)

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=conc_i,
        delta={
            "reference": conc_souhaitee,
            "valueformat": ".1f",
            "suffix": " g/L",
            "increasing": {"color": "#e53935"},
            "decreasing": {"color": "#43a047"},
        },
        number={"suffix": " g/L", "font": {"size": 30}},
        gauge={
            "axis": {
                "range": [0, gauge_max],
                "ticksuffix": " g/L",
                "tickfont": {"size": 10},
            },
            "bar": {"color": "#1565c0", "thickness": 0.28},
            "bgcolor": "white",
            "borderwidth": 1,
            "bordercolor": "#ddd",
            "steps": [
                {"range": [0, conc_min],        "color": "#ffcdd2"},
                {"range": [conc_min, conc_max],  "color": "#c8e6c9"},
                {"range": [conc_max, gauge_max], "color": "#ffccbc"},
            ],
            "threshold": {
                "line": {"color": "#1a73e8", "width": 4},
                "thickness": 0.80,
                "value": conc_souhaitee,
            },
        },
        title={"text": "Current Concentration", "font": {"size": 14}},
    ))
    fig_gauge.update_layout(
        height=290,
        margin=dict(l=20, r=20, t=60, b=10),
        paper_bgcolor="white",
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

    # Concentration reference table
    st.markdown(
        f"""
        | | Value |
        |:---|---:|
        | **Current (Conc.i)** | {conc_i:.1f} g/L |
        | **Target (Réf. Conc.)** | {conc_souhaitee:.1f} g/L |
        | **Minimum** | {conc_min:.1f} g/L |
        | **Maximum** | {conc_max:.1f} g/L |
        """
    )

# ── Bottom metric cards ───────────────────────────────────────────────────────
st.divider()

mf = entry['mass_adj']
m1, m2, m3, m4 = st.columns(4)

m1.metric("Total Bath Volume (VB)",   f"{entry['vol_bath']:.0f} L")
m2.metric("Current Solution (Vsi)",   f"{entry['vol_initial']:.0f} L")
m3.metric("Target Solution (Vsf)",    f"{entry['vol_final']:.0f} L")

if mf > 0:
    m4.metric("Addition Required (mf)", f"{mf:.2f} kg",
              delta=f"+{mf:.2f} kg", delta_color="normal")
elif mf < 0:
    m4.metric("Addition Required (mf)", f"{mf:.2f} kg",
              delta=f"{mf:.2f} kg", delta_color="inverse")
else:
    m4.metric("Addition Required (mf)", "0.00 kg")

if entry.get('operator_note'):
    st.caption(f"Operator note: *{entry['operator_note']}*")
