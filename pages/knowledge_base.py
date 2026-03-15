"""
Knowledge Base Page — HDG process reference, formula library, and parameter definitions.

Three tabs:
  1. Process Flow — descriptions of all 8 HDG stages with a flow diagram
  2. Formula Library — all degreasing formulas with worked example
  3. Parameter Definitions — dictionary of every variable
"""

import streamlit as st
import plotly.graph_objects as go

st.header("📖 Knowledge Base — HDG Process Reference")

tab_process, tab_formulas, tab_params = st.tabs([
    "Process Flow",
    "Formula Library",
    "Parameter Definitions",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Process Flow
# ══════════════════════════════════════════════════════════════════════════════
with tab_process:
    st.subheader("Hot Dip Galvanizing — Process Overview")
    st.markdown(
        "Hot dip galvanizing coats iron or steel with a zinc layer by immersing the metal "
        "in a bath of molten zinc at approximately **450 °C**. The zinc reacts with iron at "
        "the surface to form a series of zinc-iron alloy layers that protect against corrosion."
    )

    # Flow diagram
    steps  = ["Degreasing", "Rinsing", "Pickling", "Rinsing", "Flux", "Drying", "Zinc Bath", "Inspection"]
    colors = ["#ef5350", "#ef9a9a", "#ffd54f", "#a5d6a7", "#42a5f5", "#ce93d8", "#78909c", "#8d6e63"]
    xs     = [60 + i * 110 for i in range(len(steps))]

    fig_flow = go.Figure()

    for i, (step, color, x) in enumerate(zip(steps, colors, xs)):
        fig_flow.add_shape(
            type="rect", x0=x - 48, y0=25, x1=x + 48, y1=75,
            fillcolor=color,
            line=dict(color="rgba(0,0,0,0.15)", width=1),
        )
        fig_flow.add_annotation(
            x=x, y=50,
            text=f"<b>{i + 1}. {step}</b>",
            showarrow=False,
            font=dict(color="white", size=10),
            align="center",
        )
        if i < len(steps) - 1:
            fig_flow.add_annotation(
                x=xs[i + 1] - 48, y=50,
                ax=x + 48, ay=50,
                arrowhead=2, arrowsize=1.2, arrowwidth=2,
                arrowcolor="#555",
                showarrow=True,
                text="",
            )

    fig_flow.update_layout(
        height=120,
        xaxis=dict(range=[0, max(xs) + 70], visible=False),
        yaxis=dict(range=[0, 100], visible=False),
        margin=dict(l=5, r=5, t=10, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    st.plotly_chart(fig_flow, use_container_width=True)

    st.divider()
    st.subheader("Stage Descriptions")

    stages = [
        (
            "1. Degreasing",
            "#ef5350",
            "Organic surface contaminants — oils, grease, and paint — are removed using a "
            "caustic (alkaline) solution bath. This is the critical first step: any remaining "
            "organic matter will prevent zinc from bonding to the steel.",
            "Caustic soda (NaOH) solution",
            "Concentration: 30–60 g/L · Temperature: 50–80 °C",
        ),
        (
            "2. Rinsing (post-degreasing)",
            "#ef9a9a",
            "The steel is rinsed with water to remove all traces of caustic solution "
            "before entering the acid pickling stage.",
            "Fresh water",
            "Ensure complete removal of caustic residue",
        ),
        (
            "3. Pickling",
            "#ffd54f",
            "Rust, mill scale, and iron oxides are dissolved by immersing the steel in a "
            "dilute hydrochloric acid (HCl) or sulfuric acid (H₂SO₄) bath. This exposes "
            "bare, reactive metal ready for zinc bonding.",
            "HCl (15–18%) or H₂SO₄",
            "Concentration: 10–18% · Temperature: ambient to 40 °C",
        ),
        (
            "4. Rinsing (post-pickling)",
            "#a5d6a7",
            "Acid residues are rinsed off to prevent contaminating the flux solution and "
            "to slow down any re-oxidation of the steel surface.",
            "Fresh water",
            "Monitor rinse water pH",
        ),
        (
            "5. Flux Solution",
            "#42a5f5",
            "The steel is immersed in a flux solution of ammonium zinc chloride "
            "(ZnCl₂·2NH₄Cl). The flux removes residual surface oxides and deposits a "
            "protective salt layer that prevents re-oxidation and promotes zinc adhesion "
            "during galvanizing.",
            "ZnCl₂ · 2NH₄Cl (ammonium zinc chloride)",
            "Concentration: 400–500 g/L · pH: 4–4.5 · Temperature: 50–70 °C",
        ),
        (
            "6. Drying",
            "#ce93d8",
            "The fluxed steel is passed through a drying oven to evaporate all moisture. "
            "Water entering the molten zinc bath would cause violent steam explosions.",
            "Hot air oven",
            "Temperature: 120–150 °C · Must be completely dry before zinc immersion",
        ),
        (
            "7. Zinc Bath",
            "#78909c",
            "The prepared steel is immersed in molten zinc at approximately 450 °C. "
            "Iron and zinc react at the interface to form a series of zinc-iron alloy layers "
            "topped by a pure zinc outer layer. The piece is withdrawn at a controlled speed "
            "to achieve the desired coating thickness.",
            "Molten zinc (≥99.99% purity)",
            "Temperature: 445–455 °C · Immersion time: 3–10 min · Typical coating: ≥45 µm",
        ),
        (
            "8. Cooling & Inspection",
            "#8d6e63",
            "The galvanized steel is cooled (water quench or air cooled) and inspected for "
            "coating thickness, adhesion, and visual quality. Non-conformities — bare spots, "
            "drips, or inclusions — are documented and escalated.",
            "Water or air",
            "Thickness: magnetic gauge · Visual: bare spots, runs, inclusions",
        ),
    ]

    for name, color, desc, chemical, params in stages:
        with st.expander(name, expanded=False):
            d1, d2 = st.columns([3, 1])
            with d1:
                st.markdown(desc)
            with d2:
                st.markdown(f"**Chemical**  \n{chemical}")
                st.markdown(f"**Key parameters**  \n{params}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Formula Library
# ══════════════════════════════════════════════════════════════════════════════
with tab_formulas:
    st.subheader("Degreasing Stage — Formula Library")

    st.info(
        "**Source:** HDG Project specification, 25/10/2023.  \n"
        "**Typo note:** The original PDF showed `Vsf = VB − Vn − Vn` (Vn twice). "
        "The correct physical formula subtracts both sludge (Vb) and headspace (Vn): "
        "`Vsf = VB − Vb − Vn`."
    )

    formulas = [
        (
            "1", "VB", "Total Bath Volume",
            "VB (L) = L × l × h × 1000",
            "Converts tank dimensions from m³ to liters. Multiply length × width × height × 1000.",
        ),
        (
            "2", "Vb", "Sludge Volume",
            "Vb (L) = 1000 × L × l × niveau_boues / 100",
            "Volume occupied by settled sludge at the tank bottom, expressed as a % of tank footprint height.",
        ),
        (
            "3", "Vn", "Reference Headspace",
            "Vn (L) = 1000 × L × l × n / 100",
            "The target empty volume above the solution under normal operating conditions. Prevents spills and allows thermal expansion.",
        ),
        (
            "4", "Vsf", "Final (Target) Solution Volume",
            "Vsf (L) = VB − Vb − Vn",
            "Volume of solution in a correctly filled tank — the TARGET state after removing sludge zone and reference headspace.",
        ),
        (
            "5", "m_Total", "Total Degreaser (fresh tank)",
            "m_Total (kg) = (Réf. Conc. / 1000) × Vsf",
            "Mass of degreasing agent to prepare a completely fresh tank at the target concentration. Reference value only.",
        ),
        (
            "6", "Vsi", "Initial (Current) Solution Volume",
            "Vsi (L) = VB − Ve_L − Vb    where  Ve_L = 1000 × L × l × Ve / 100",
            "Actual current volume of solution, based on the MEASURED empty space (Ve). This may differ from the reference headspace (n).",
        ),
        (
            "7", "mf", "Adjustment Mass — Daily Dosing",
            "mf (kg) = (Réf.Conc./1000 × Vsf) − (Conc.i/1000 × Vsi)",
            "Mass of degreaser to add to reach the target state. "
            "Positive → add product. Negative → bath over-concentrated, dilution required.",
        ),
    ]

    for num, var, name, formula, explanation in formulas:
        st.markdown(f"**{num}. {name}** `({var})`")
        st.code(formula, language=None)
        st.caption(explanation)
        if num != formulas[-1][0]:
            st.divider()

    st.divider()
    st.subheader("Worked Example")
    st.markdown(
        """
**Given:** L = 3 m, l = 1 m, h = 2 m, niveau_boues = 5%, n = 10%, Ve = 10%,
Conc.i = 35 g/L, Réf.Conc. = 45 g/L

| Step | Calculation | Result |
|---|---|---|
| VB | 3 × 1 × 2 × 1000 | **6 000 L** |
| Vb | 1000 × 3 × 1 × 5/100 | **150 L** |
| Vn | 1000 × 3 × 1 × 10/100 | **300 L** |
| Ve_L | 1000 × 3 × 1 × 10/100 | **300 L** |
| Vsf | 6 000 − 150 − 300 | **5 550 L** |
| Vsi | 6 000 − 300 − 150 | **5 550 L** |
| m_Total | 45/1000 × 5 550 | **249.75 kg** |
| mf | (45/1000 × 5 550) − (35/1000 × 5 550) | **55.50 kg** |

**Operator instruction:** Add **55.50 kg** of degreasing agent to the bath.
        """
    )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Parameter Definitions
# ══════════════════════════════════════════════════════════════════════════════
with tab_params:
    st.subheader("Parameter Definitions")

    params = [
        (
            "Réf. Conc. (g/L)", "Reference Concentration",
            "The target operating concentration for the degreasing bath. Must stay between "
            "the minimum and maximum thresholds for effective degreasing.",
            "Plant specification sheet",
        ),
        (
            "VB (L)", "Total Bath Volume",
            "The total internal volume of the degreasing tank in liters, calculated from its "
            "physical dimensions (L × l × h × 1000).",
            "Derived from L, l, h",
        ),
        (
            "Vb (L)", "Sludge Volume",
            "Volume occupied by settled sludge at the bottom of the tank. Sludge accumulates "
            "from the degreasing reaction and drag-in from the work. Must be drained regularly.",
            "Measured via level gauge — entered as % of tank height",
        ),
        (
            "Vn (L)", "Reference Headspace Volume",
            "Target empty volume above the solution under normal operating conditions. "
            "This space prevents overflow and allows safe thermal expansion.",
            "Plant standard — entered as % of tank height",
        ),
        (
            "Vsf (L)", "Final (Target) Solution Volume",
            "Volume of usable solution when the tank is at the target fill level. "
            "Accounts for sludge at the bottom and target headspace at the top. "
            "This is the TARGET state.",
            "Calculated: VB − Vb − Vn",
        ),
        (
            "Ve (%)", "Current Empty Space",
            "Actual measured empty space at the top of the tank right now, as a percentage "
            "of tank height. Measured by the operator with a ruler or level sensor.",
            "Measured by operator at time of calculation",
        ),
        (
            "Ve_L (L)", "Current Empty Space in Liters",
            "Conversion of Ve (%) into liters using the tank footprint: 1000 × L × l × Ve/100.",
            "Derived from Ve, L, l",
        ),
        (
            "Vsi (L)", "Initial (Current) Solution Volume",
            "Actual current volume of solution, calculated from the measured empty space. "
            "May differ from Vsf if the tank is not at the reference fill level.",
            "Calculated: VB − Ve_L − Vb",
        ),
        (
            "Conc.i (g/L)", "Initial / Current Concentration",
            "Measured concentration of the degreasing agent in the bath before any addition. "
            "Determined by titration of a bath sample taken immediately before calculation.",
            "Titration of bath sample",
        ),
        (
            "n (%)", "Reference Empty Space (%)",
            "Target percentage of tank height to remain empty above the solution surface. "
            "Defines the standard operating fill level.",
            "Plant standard",
        ),
        (
            "niveau_boues (%)", "Sludge Level (%)",
            "Current sludge depth expressed as a percentage of tank height. "
            "Used to calculate Vb (the volume unavailable due to sludge).",
            "Visual gauge or level sensor reading",
        ),
        (
            "m_Total (kg)", "Total Degreaser Mass",
            "Total mass of degreasing agent to prepare a completely fresh (empty) tank at "
            "the reference concentration. Used as a sanity-check reference, not the daily dosing value.",
            "Calculated",
        ),
        (
            "mf (kg)", "Adjustment Mass — Primary Output",
            "Mass of degreasing agent to add to bring the bath from its current state to the "
            "target concentration. **Positive → add product. Negative → dilute — do NOT add degreaser.**",
            "Calculated — this is the daily operator instruction",
        ),
    ]

    for param, name, desc, source in params:
        c1, c2 = st.columns([1, 3])
        with c1:
            st.markdown(f"**`{param}`**  \n*{name}*")
        with c2:
            st.markdown(desc)
            st.caption(f"Source / measurement: {source}")
        st.divider()
