# HDG Degreasing Tank Management — Workflow SOP

## Objective
Determine the precise chemical addition (kg) needed to bring a degreasing bath to its target concentration, accounting for current sludge level and empty space. Ensure operator safety by alerting when concentration is out of the acceptable range.

---

## Tools Used
| Tool | Purpose |
|---|---|
| `tools/degreasing_calculator.py` | Pure calculation engine — all formula logic |
| `tools/hdg_history.py` | SQLite audit trail (read/write operations) |
| `tools/hdg_app.py` | Multi-page Streamlit application (primary entry point) |
| `tools/pages/dashboard.py` | Visual tank status dashboard |
| `tools/pages/operations.py` | Daily calculation and dosing page |
| `tools/pages/history.py` | Audit trail with trend chart and CSV export |
| `tools/pages/knowledge_base.py` | Process reference, formula library, definitions |
| `tools/hdg_dashboard.py` | Legacy single-page dashboard (still functional) |

## How to Run
```bash
# From project root
pip install -r requirements.txt

# Full multi-page application (recommended)
streamlit run tools/hdg_app.py

# Legacy single-page dashboard
streamlit run tools/hdg_dashboard.py
```
Application opens at http://localhost:8501

---

## Required Inputs

| Variable | Description | Unit | Typical Range | How to Measure |
|---|---|---|---|---|
| L | Tank length | m | 1–10 | Physical measurement (fixed) |
| l | Tank width | m | 0.5–5 | Physical measurement (fixed) |
| h | Tank height | m | 0.5–3 | Physical measurement (fixed) |
| niveau_boues | Sludge level | % of tank height | 0–20% | Visual gauge or level sensor |
| n | Reference empty top space | % of tank height | 5–15% | Defined by plant standard |
| Ve | Current actual empty space | % of tank height | 5–20% | Measure distance from surface to rim, convert to % |
| conc_i | Current bath concentration | g/L | 20–80 | Chemical titration of bath sample |
| conc_souhaitee | Target concentration (Réf. Conc.) | g/L | Plant-specific | Plant specification sheet |
| conc_min | Minimum acceptable concentration | g/L | Plant-specific | Plant specification sheet |
| conc_max | Maximum acceptable concentration | g/L | Plant-specific | Plant specification sheet |

---

## Step-by-Step Operator Procedure

1. **Record tank dimensions** (L, l, h) — these are fixed and can be pre-filled in the dashboard.
2. **Measure sludge level** — read the visual gauge or sensor; enter as percentage of tank height.
3. **Measure current empty space (Ve)** — measure the distance from the bath surface to the top rim of the tank. Convert: `Ve (%) = (distance_cm / h_cm) × 100`.
4. **Take a bath sample** — titrate to obtain the current concentration (`conc_i`) in g/L.
5. **Open the dashboard** and enter all measured values plus plant spec concentrations.
6. **Press "Calculate Additions"** — the dashboard computes all volumes and the required addition.
7. **Read the mf output**:
   - `mf > 0`: Add exactly `mf` kg of degreasing agent to the bath.
   - `mf < 0`: Do NOT add chemical. Bath is over-concentrated. Follow dilution procedure (consult supervisor).
   - `mf = 0`: Bath is at target — no action required.
8. **Check the concentration alert banner** — if it shows LOW or HIGH, treat as a priority action regardless of the mf value.

---

## Formula Reference

All formulas from HDG Project PDF specification (25/10/2023):

| # | Formula | Notes |
|---|---|---|
| 1 | `VB (L) = L × l × h × 1000` | Total bath volume |
| 2 | `Vb (L) = 1000 × L × l × niveau_boues / 100` | Sludge volume |
| 3 | `Vn (L) = 1000 × L × l × n / 100` | Reference top empty space |
| 4 | `Vsf (L) = VB − Vb − Vn` | Final solution volume |
| 5 | `m_Total (kg) = conc_souhaitée / 1000 × Vsf` | Total degreaser for fresh tank at target |
| 6 | `Vsi (L) = VB − Ve_L − Vb` | Initial (current) solution volume |
| 7 | `mf (kg) = (conc_souhaitée/1000 × Vsf) − (conc_i/1000 × Vsi)` | Adjustment mass (signed) |

Where `Ve_L (L) = 1000 × L × l × Ve / 100`.

---

## Edge Cases and Known Issues

| Scenario | Behaviour | Action |
|---|---|---|
| `Vsf ≤ 0` | Dashboard shows validation error | Sludge + headspace exceed tank volume — drain sludge before any chemical addition |
| `Vsi ≤ 0` | Clamped to 0; warning shown | Tank may be nearly empty or reading incorrect — verify measurements |
| `mf < 0` | Red warning displayed; "dilution required" instruction shown | Do NOT add degreaser; contact supervisor for water dilution procedure |
| `niveau_boues + Ve ≥ 100%` | Validation error, calculation blocked | Check sensor readings; physically inspect tank |
| `conc_min ≥ conc_max` | Validation error | Correct the plant spec concentration inputs |

**PDF typo (Formula 4):** The source PDF showed `Vsf = VB − Vn − Vn` (Vn appeared twice). The physically correct formula subtracts both Vb (sludge) and Vn (headspace): `Vsf = VB − Vb − Vn`. This is what the calculator implements.

---

## Output
- `mf` in kg — primary operator instruction, displayed prominently in the dashboard
- No cloud upload required for normal use; operators can screenshot the results panel for the plant logbook
- All intermediate values (VB, Vb, Vn, Vsf, Vsi, m_Total) available in the "Show calculation details" expander

---

## Version History
| Version | Date | Change |
|---|---|---|
| v1.0 | 2026-03-10 | Initial implementation — degreasing stage calculation engine and Streamlit dashboard |
| v2.0 | 2026-03-10 | Full multi-page application — visual tank dashboard, operations page, SQLite history with trend chart and CSV export, knowledge base |
