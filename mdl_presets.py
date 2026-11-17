"""Permalink (Begrenzen), Presets und Zufalls-Seed-Button (Standardmuster aus dem Demo-Portfolio).

Alle Einstellungen der App stehen in SETTING_SPECS (Seitenleiste und Experimente): so hebt jede Änderung eines Reglers die Markierung des aktiven Presets auf.
Ein Preset nennt nur die Regler, die vom Standard abweichen; alle anderen setzt es auf ihren Standardwert zurück."""

import random
from dataclasses import dataclass

import streamlit as st

import mdl_constants as C
import mdl_evaluation as ev


@dataclass(frozen=True)
class SettingSpec:
    url_param: str
    caster: type
    default: object
    lo: float | None = None
    hi: float | None = None


SETTING_SPECS = {
    "folge": SettingSpec("folge", str, C.DEFAULT_FOLGE),
    "n1": SettingSpec("n1", int, C.DEFAULT_N1, C.N_MIN, C.N_MAX),
    "d_idx": SettingSpec("d", int, C.DEFAULT_D_INDEX, 0, len(C.D_WERTE) - 1),
    "seed": SettingSpec("seed", int, C.DEFAULT_SEED, 0, C.SEED_MAX),
    "n2": SettingSpec("n2", int, C.DEFAULT_N2, C.N_MIN, C.N_MAX),
    "k2": SettingSpec("k2", int, C.DEFAULT_K2, C.K_MIN, C.K_MAX),
    "n3": SettingSpec("n3", int, C.DEFAULT_N3, C.N_MIN, C.N_MAX),
    "m3": SettingSpec("m3", int, C.DEFAULT_M3, 0, 2),
    "n4": SettingSpec("n4", int, C.DEFAULT_N4, C.N4_MIN, C.N_MAX),
    "k4": SettingSpec("k4", int, C.DEFAULT_K4, C.K4_MIN, C.K4_MAX),
    "m4": SettingSpec("m4", int, C.DEFAULT_M4, 0, 2),
    "n5": SettingSpec("n5", int, C.DEFAULT_N5, min(C.N5_WERTE), max(C.N5_WERTE)),
    "nfolgen": SettingSpec("nfolgen", int, C.DEFAULT_NFOLGEN, C.NFOLGEN_MIN, C.NFOLGEN_MAX),
}
PRESET_KEYS = {key: key for key in SETTING_SPECS}


def init_session_state_defaults():
    for state_key, spec in SETTING_SPECS.items():
        if state_key not in st.session_state:
            st.session_state[state_key] = spec.default


def bounds(state_key):
    spec = SETTING_SPECS[state_key]
    return spec.lo, spec.hi


def load_permalink_settings():
    """Einmal je Sitzung: Werte aus der Adresszeile übernehmen, auf die Reglergrenzen begrenzt (Text auf die erlaubte Länge)."""
    if "permalink_loaded" in st.session_state:
        return
    qp = st.query_params
    for state_key, spec in SETTING_SPECS.items():
        if spec.url_param in qp:
            try:
                value = spec.caster(qp[spec.url_param])
            except (ValueError, TypeError):
                continue
            if isinstance(value, str):
                value = value[: C.FOLGE_MAX_ZEICHEN]
            if spec.lo is not None:
                value = max(spec.lo, value)
            if spec.hi is not None:
                value = min(spec.hi, value)
            st.session_state[state_key] = value
    st.session_state["permalink_loaded"] = True


def sync_query_params(values):
    """`values`: {state_key: aktueller Wert}; die Adresszeile spiegelt die Konfiguration."""
    try:
        for state_key, value in values.items():
            st.query_params[SETTING_SPECS[state_key].url_param] = str(value)
    except Exception:
        pass


def preset_wert(name, state_key):
    """Wert eines Reglers im Preset; was das Preset nicht nennt, gilt als Standardwert."""
    return C.PRESETS[name].get(PRESET_KEYS[state_key], SETTING_SPECS[state_key].default)


def apply_preset(name):
    for state_key in SETTING_SPECS:
        st.session_state[state_key] = preset_wert(name, state_key)


def aktives_preset():
    """Name des Presets, dessen Werte GENAU den aktuellen Einstellungen entsprechen, sonst None.

    Zustandslos: verglichen wird jeder Regler aus SETTING_SPECS (ein Preset ohne Eintrag für einen Regler meint dessen
    Standardwert) mit dem Session State. Ein später ergänzter Regler braucht nur seinen Eintrag in SETTING_SPECS,
    dann hebt auch seine Änderung die Markierung auf (tests/test_layout.py prüft das für jeden Regler)."""
    for name in C.PRESETS:
        if all(st.session_state.get(state_key, spec.default) == preset_wert(name, state_key) for state_key, spec in SETTING_SPECS.items()):
            return name
    return None


def sidebar_presets():
    """Schnellstart oben in der Seitenleiste; das aktive Preset ist hervorgehoben (`type="primary"`)."""
    if not C.PRESETS:
        return
    st.header("🎯 Schnellstart")
    st.caption("Ein Beispielszenario laden:")
    aktiv = aktives_preset()
    for name in C.PRESETS:
        st.button(
            name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP.get(name, ""), key=f"preset_{name}",
            type="primary" if aktiv == name else "secondary",
        )


def zug_ziehen(art):
    """Schreibt einen gezogenen Zug in das Eingabefeld (Zufallsfolge oder Ankunftsmodell V); n, D und Zufalls-Seed stehen im Session State."""
    st.session_state["folge"] = " ".join(str(x) for x in ev.ziehe_folge(art, st.session_state["n1"], st.session_state["d_idx"], st.session_state["seed"]))


def randomize_seed():
    st.session_state["seed"] = random.randint(0, C.SEED_MAX)
