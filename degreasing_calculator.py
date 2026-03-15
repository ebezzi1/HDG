"""
HDG Degreasing Tank — Calculation Engine

Pure Python module with no UI dependencies.
All formulas are derived from the HDG Project PDF specification (25/10/2023).

Typo note: The PDF formula 4 showed "Vsf = VB - Vn - Vn" (Vn twice).
The correct formula is Vsf = VB - Vb - Vn (subtracting both sludge and headspace).
"""

from dataclasses import dataclass


@dataclass
class DegreasingInputs:
    L: float             # tank length (m)
    l: float             # tank width (m)
    h: float             # tank height (m)
    niveau_boues: float  # sludge level (%)
    n: float             # reference empty top space (%)
    Ve: float            # current actual empty space (%)
    conc_i: float        # current/initial concentration (g/L)
    conc_souhaitee: float  # target concentration (g/L)
    conc_min: float      # minimum acceptable concentration (g/L)
    conc_max: float      # maximum acceptable concentration (g/L)


@dataclass
class DegreasingOutputs:
    VB: float          # total bath volume (L)
    Vb: float          # sludge volume (L)
    Vn: float          # reference top empty space (L)
    Ve_L: float        # current empty space in liters
    Vsf: float         # final solution volume (L)
    Vsi: float         # initial solution volume (L)
    m_Total: float     # total degreaser for fresh tank at target conc (kg)
    mf: float          # adjustment mass needed (kg) — negative means dilute
    conc_status: str   # "OK", "LOW", or "HIGH"
    alert: bool        # True if concentration is outside the acceptable range
    alert_message: str # Human-readable alert text


def validate_inputs(inputs: DegreasingInputs) -> list:
    """
    Returns a list of human-readable error strings.
    An empty list means all inputs are valid and calculation can proceed.
    """
    errors = []

    # Tank dimensions
    if inputs.L <= 0:
        errors.append("Tank length (L) must be greater than 0.")
    if inputs.l <= 0:
        errors.append("Tank width (l) must be greater than 0.")
    if inputs.h <= 0:
        errors.append("Tank height (h) must be greater than 0.")

    # Percentage fields
    if not (0 <= inputs.niveau_boues < 100):
        errors.append("Sludge level (niveau_boues) must be between 0 and 99%.")
    if not (0 < inputs.n < 100):
        errors.append("Reference empty space (n) must be between 1 and 99%.")
    if not (0 <= inputs.Ve < 100):
        errors.append("Current empty space (Ve) must be between 0 and 99%.")

    # Cross-field percentage checks
    if inputs.niveau_boues + inputs.n >= 100:
        errors.append(
            f"Sludge level ({inputs.niveau_boues}%) + reference empty space ({inputs.n}%) "
            f"must be less than 100%. Currently sums to {inputs.niveau_boues + inputs.n}%."
        )
    if inputs.niveau_boues + inputs.Ve >= 100:
        errors.append(
            f"Sludge level ({inputs.niveau_boues}%) + current empty space ({inputs.Ve}%) "
            f"must be less than 100%. Currently sums to {inputs.niveau_boues + inputs.Ve}%."
        )

    # Concentration checks
    if inputs.conc_i < 0:
        errors.append("Current concentration (conc_i) cannot be negative.")
    if inputs.conc_souhaitee < 0:
        errors.append("Target concentration (conc_souhaitee) cannot be negative.")
    if inputs.conc_min < 0:
        errors.append("Minimum concentration (conc_min) cannot be negative.")
    if inputs.conc_max <= 0:
        errors.append("Maximum concentration (conc_max) must be greater than 0.")
    if inputs.conc_min >= inputs.conc_max:
        errors.append(
            f"Minimum concentration ({inputs.conc_min} g/L) must be less than "
            f"maximum concentration ({inputs.conc_max} g/L)."
        )

    return errors


def calculate_VB(L: float, l: float, h: float) -> float:
    """Total bath volume: VB (L) = L * l * h * 1000"""
    return L * l * h * 1000


def calculate_Vb(L: float, l: float, niveau_boues: float) -> float:
    """Sludge volume: Vb (L) = 1000 * L * l * niveau_boues / 100"""
    return 1000 * L * l * niveau_boues / 100


def calculate_Vn(L: float, l: float, n: float) -> float:
    """Reference empty space volume: Vn (L) = 1000 * L * l * n / 100"""
    return 1000 * L * l * n / 100


def calculate_Ve_L(L: float, l: float, Ve: float) -> float:
    """Current empty space in liters: Ve_L = 1000 * L * l * Ve / 100"""
    return 1000 * L * l * Ve / 100


def calculate_Vsf(VB: float, Vb: float, Vn: float) -> float:
    """
    Final solution volume: Vsf (L) = VB - Vb - Vn
    Note: PDF had a typo (Vn appeared twice). Correct: subtract both Vb and Vn.
    Clamped to 0 if result is negative (over-sludged tank scenario).
    """
    return max(0.0, VB - Vb - Vn)


def calculate_Vsi(VB: float, Ve_L: float, Vb: float) -> float:
    """
    Initial solution volume: Vsi (L) = VB - Ve_L - Vb
    Clamped to 0 if result is negative.
    """
    return max(0.0, VB - Ve_L - Vb)


def calculate_m_Total(conc_souhaitee: float, Vsf: float) -> float:
    """Total degreaser mass for a fresh tank: m_Total (kg) = conc_souhaitee / 1000 * Vsf"""
    return (conc_souhaitee / 1000) * Vsf


def calculate_mf(
    conc_souhaitee: float, Vsf: float, conc_i: float, Vsi: float
) -> float:
    """
    Adjustment mass needed: mf (kg) = (conc_souhaitee/1000 * Vsf) - (conc_i/1000 * Vsi)
    Positive  → add this many kg of degreaser
    Negative  → bath is over-concentrated; dilution required (do NOT add degreaser)
    """
    return (conc_souhaitee / 1000 * Vsf) - (conc_i / 1000 * Vsi)


def evaluate_concentration_status(
    conc_i: float, conc_min: float, conc_max: float
) -> tuple:
    """
    Returns (status_str, alert_bool, alert_message).
    status_str: "OK", "LOW", or "HIGH"
    """
    if conc_i < conc_min:
        msg = (
            f"Current concentration ({conc_i} g/L) is BELOW the minimum "
            f"({conc_min} g/L). Chemical addition is required."
        )
        return ("LOW", True, msg)
    elif conc_i > conc_max:
        msg = (
            f"Current concentration ({conc_i} g/L) is ABOVE the maximum "
            f"({conc_max} g/L). Dilution is required."
        )
        return ("HIGH", True, msg)
    else:
        return ("OK", False, "")


def run_calculation(inputs: DegreasingInputs) -> tuple:
    """
    Main entry point. Returns (DegreasingOutputs | None, list[str]).
    If the errors list is non-empty, outputs is None.
    Computes all variables in dependency order.
    """
    errors = validate_inputs(inputs)
    if errors:
        return (None, errors)

    VB = calculate_VB(inputs.L, inputs.l, inputs.h)
    Vb = calculate_Vb(inputs.L, inputs.l, inputs.niveau_boues)
    Vn = calculate_Vn(inputs.L, inputs.l, inputs.n)
    Ve_L = calculate_Ve_L(inputs.L, inputs.l, inputs.Ve)
    Vsf = calculate_Vsf(VB, Vb, Vn)
    Vsi = calculate_Vsi(VB, Ve_L, Vb)
    m_Total = calculate_m_Total(inputs.conc_souhaitee, Vsf)
    mf = calculate_mf(inputs.conc_souhaitee, Vsf, inputs.conc_i, Vsi)
    conc_status, alert, alert_message = evaluate_concentration_status(
        inputs.conc_i, inputs.conc_min, inputs.conc_max
    )

    outputs = DegreasingOutputs(
        VB=VB,
        Vb=Vb,
        Vn=Vn,
        Ve_L=Ve_L,
        Vsf=Vsf,
        Vsi=Vsi,
        m_Total=m_Total,
        mf=mf,
        conc_status=conc_status,
        alert=alert,
        alert_message=alert_message,
    )
    return (outputs, [])
