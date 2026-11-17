"""Mehrere Durchläufe: wie oft muss der Zug durch die Maschine? - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Ein Zug aus n Wagen soll nach dem Abholrang sortiert werden; die Maschine hat einen Behälter und sieht den Zug einmal je Durchlauf. Die Demo zählt, wie viele Durchläufe eine Folge
braucht und wie viele Folgen in höchstens k Durchläufen fertig sind, für drei Maschinen (Pop-Stack mit festem Rezept, gieriger Stapel, Pop-Stack mit freier Leerung).
Die Ankunftsfolgen des Experiments 5 stammen aus einem ausgedachten Modell (keine reale Ankunftsfolge).

Lauffähig mit: streamlit run app.py
"""

from math import factorial, sqrt

import streamlit as st

import mdl_constants as C
import mdl_evaluation as ev
import mdl_machines as M
import mdl_tables as T
import mdl_texts as X
from mdl_layout import dunkles_design, kopf_css
from mdl_presets import (
    SETTING_SPECS,
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
    zug_ziehen,
)
from mdl_visualization import (
    build_anteil_linien,
    build_bild_urbild,
    build_histogramm,
    build_modell_balken,
    build_modell_linie,
    build_verlauf,
)

st.set_page_config(page_title="Mehrere Durchläufe – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _folge(text):
    return ev.analyse_folge(text)


@st.cache_data(show_spinner=False)
def _zaehlung(n, k):
    return ev.analyse_zaehlung(n, k)


@st.cache_data(show_spinner=False)
def _verteilung(n):
    return ev.analyse_verteilung(n)


@st.cache_data(show_spinner=False)
def _klasse(n, k, maschine):
    return ev.analyse_klassentest(n, k, maschine)


@st.cache_data(show_spinner="Züge werden gerechnet (bei 2 000 Folgen etwa eine bis zwei Sekunden) …")
def _modell(n, d_idx, nfolgen, seed):
    return ev.analyse_modell(n, d_idx, nfolgen, seed)


def md_table(headers, rows) -> str:
    """Markdown-Tabelle aus Textzellen (Dezimalkomma und Tausenderabstand kommen aus den Formatfunktionen, nicht aus der Locale des Browsers)."""
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    out += ["| " + " | ".join(str(c).replace("|", "/") for c in r) + " |" for r in rows]
    return "\n".join(out)


def verlaufs_tabelle(verlauf, beschreibung, kopf) -> str:
    return md_table(["Durchlauf", "Folge davor", kopf], [[j + 1, ev.folge_text(verlauf[j]), beschreibung[j]] for j in range(len(beschreibung))])


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in mdl_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🔁 Mehrere Durchläufe: wie oft muss der Zug durch die Maschine?")
st.markdown(X.EINLEITUNG)

with st.expander("So funktioniert die Maschine", expanded=True):
    st.markdown(X.SO_FUNKTIONIERT)

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Ankunftsmodell V (ausgedacht, Experimente 1 und 5)**")
    st.select_slider("Verweilzeit D (in Ankunftsabständen)", options=list(range(len(C.D_WERTE))), format_func=lambda i: C.D_LABEL[i], key="d_idx",
                     help="Mittlere Verweilzeit der Wagen im Modell V, in Abständen zwischen zwei Ankünften. Klein: der Zug ist fast sortiert. ∞: alle n! Folgen gleich wahrscheinlich.")
    st.number_input("Zufalls-Seed", *bounds("seed"), key="seed", step=1,
                    help="Bestimmt die Zufallsfolge und das Ankunftsmodell (ganzzahliger SplitMix64). Der Strom für D ist Zufalls-Seed plus Nummer von D (0 für 0,5 bis 6 für ∞).")
    st.button("🎲 Neuer Zufalls-Seed", width="stretch", on_click=randomize_seed)

sync_query_params({state_key: st.session_state[state_key] for state_key in SETTING_SPECS})

s = ev.Settings(**{state_key: st.session_state[state_key] for state_key in SETTING_SPECS})
mach4 = M.MASCHINEN[s.m4]

# --- Kernfragen ----------------------------------------------------------------------------------------------------------------------------

a1 = _folge(s.folge)
a2 = _zaehlung(s.n2, s.k2)
a3 = _verteilung(s.n3)

st.markdown("## ❓ Kernfragen")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("**1. Wie viele Durchläufe braucht mein Zug?**")
    if a1.fehler:
        st.markdown("#### –")
        st.caption("Durchläufe: fest / gieriger Stapel / frei. Die Eingabe in Experiment 1 ist ungültig.")
    else:
        st.markdown(f"#### {a1.zahlen[M.POP]} / {a1.zahlen[M.WEST]} / {a1.zahlen[M.FREI]}")
        st.caption(f"Durchläufe: fest / gieriger Stapel / frei, für die Folge {ev.folge_text(a1.p)}. Experiment 1.")
with c2:
    st.markdown("**2. Wie viele Züge schaffen k Durchläufe?**")
    st.markdown("#### " + " / ".join(ev.de_int(a2.anzahl[m]) for m in (M.POP, M.WEST, M.FREI)))
    st.caption(f"Folgen in höchstens {s.k2} Durchläufen bei n = {s.n2}: fest / gieriger Stapel / frei, von {ev.de_int(a2.gesamt)} Folgen. Experiment 2.")
with c3:
    st.markdown("**3. Wovon hängt die Zahl ab?**")
    st.markdown("#### " + " / ".join(str(a3.daten[m]["maximum"]) for m in (M.POP, M.WEST, M.FREI)))
    st.caption(f"Größte Durchlaufzahl bei n = {s.n3}: fest / gieriger Stapel / frei. Sie hängt vom Rezept des Behälters ab. Experimente 3 und 4.")

st.markdown("---")

# --- Experiment 1 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 1: Ein Zug durch die drei Maschinen")
st.caption("Die Folge nach jedem Durchlauf, für alle drei Maschinen nebeneinander. Bei freier Leerung ist die gezeigte Zerlegung **eine von mehreren** möglichen Lösungen mit der kleinsten Zahl von Durchläufen.")
q1, q2 = st.columns([3, 2])
with q1:
    st.text_input("Folge der Ränge in Ankunftsreihenfolge (Zahlen 1 bis n, jede genau einmal; n höchstens 9)", key="folge", max_chars=C.FOLGE_MAX_ZEICHEN,
                  help="Zum Beispiel „3 5 2 4 1“: der Wagen mit Rang 3 kommt zuerst an, der mit Rang 1 zuletzt. Die Knöpfe rechts schreiben einen gezogenen Zug in dieses Feld.")
with q2:
    st.slider("Zahl der Wagen n für einen gezogenen Zug", *bounds("n1"), key="n1", help="Länge des Zuges, den die beiden Knöpfe darunter ziehen.")
    z1, z2 = st.columns(2)
    z1.button("🎲 Zufall", width="stretch", on_click=zug_ziehen, args=("zufall",),
              help="Zieht eine Folge, bei der alle n! Anordnungen gleich wahrscheinlich sind (Zufalls-Seed aus der Seitenleiste).")
    z2.button("🚂 Modell V", width="stretch", on_click=zug_ziehen, args=("modell",),
              help="Zieht die erste Folge des Stroms im Ankunftsmodell V (Verweilzeit D und Zufalls-Seed aus der Seitenleiste).")
if a1.fehler:
    st.warning(a1.fehler)
else:
    st.caption(f"Zug: {ev.folge_text(a1.p)}.")
    cols = st.columns(3)
    for col, m in zip(cols, (M.POP, M.WEST, M.FREI)):
        with col:
            st.plotly_chart(build_verlauf(a1.verlauf[m], m), width="stretch", key=f"verlauf_{m}")
    with st.expander("Blöcke und Stapelspur je Durchlauf"):
        st.markdown("**Pop-Stack, festes Rezept:** die Blöcke sind die maximal absteigenden Läufe der Folge; jeder wird umgekehrt.")
        st.markdown(verlaufs_tabelle(a1.verlauf[M.POP], a1.beschreibung[M.POP], "Blöcke (je Block umgekehrt)") if a1.zahlen[M.POP] else "Schon sortiert: kein Durchlauf nötig.")
        st.markdown("**Gieriger Stapel:** Spur der Stapeloperationen.")
        st.markdown(verlaufs_tabelle(a1.verlauf[M.WEST], a1.beschreibung[M.WEST], "Spur") if a1.zahlen[M.WEST] else "Schon sortiert: kein Durchlauf nötig.")
        st.markdown("**Freie Leerung:** eine gefundene Zerlegung (eine von mehreren möglichen).")
        st.markdown(verlaufs_tabelle(a1.verlauf[M.FREI], a1.beschreibung[M.FREI], "Blöcke (je Block umgekehrt)") if a1.zahlen[M.FREI] else "Schon sortiert: kein Durchlauf nötig.")
    kind, text = ev.verdict_folge(a1.p, a1.zahlen)
    getattr(st, kind)(text)

st.markdown("---")

# --- Experiment 2 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 2: Wie viele Folgen schaffen höchstens k Durchläufe?")
st.caption("Alle n! Folgen aufgezählt (vorgerechnet, `tools/mdl_make_tables.py`, neu gerechnet und exakt verglichen bis n = 8). Zähleinheit: Folgen, alle Wagen verschieden.")
e1, e2 = st.columns(2)
e1.slider("Zahl der Wagen n", *bounds("n2"), key="n2", help="Länge des Zuges; alle n! Folgen sind aufgezählt.")
e2.slider("Höchstens k Durchläufe", *bounds("k2"), key="k2", help="Zahl der erlaubten Durchläufe; mit freier Leerung sind bei n ≤ 9 nie mehr als 4 nötig, feste Rezepte brauchen bis zu n − 1.")
m1, m2, m3 = st.columns(3)
for col, m in zip((m1, m2, m3), (M.POP, M.WEST, M.FREI)):
    col.metric(M.NAME[m], ev.de_int(a2.anzahl[m]), delta=ev.pct(a2.anteil[m]) + " aller Folgen", delta_color="off")
st.plotly_chart(build_anteil_linien(s.n2, s.k2), width="stretch", key="chart_anteil")
zeilen = []
for n in range(C.N_MIN, C.N_MAX + 1):
    z = ev.analyse_zaehlung(n, s.k2)
    zeilen.append([("**" + str(n) + "**") if n == s.n2 else n, ev.de_int(z.gesamt)] + [ev.de_int(z.anzahl[m]) for m in (M.POP, M.WEST, M.FREI)])
st.markdown(md_table(["n", "alle Folgen (n!)", "Pop-Stack fest", "gieriger Stapel", "Pop-Stack frei"], zeilen))
st.caption(f"Folgen in höchstens {s.k2} {'Durchlauf' if s.k2 == 1 else 'Durchläufen'}, je Maschine. Die gewählte Zeile ist fett.")
kind, text = ev.verdict_zaehlung(a2)
getattr(st, kind)(text)

st.markdown("---")

# --- Experiment 3 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 3: Im schlimmsten Fall und im Mittel")
st.caption("Verteilung der Durchlaufzahl über alle n! Folgen (alle gleich gewichtet, Modell U), vorgerechnet.")
f1, f2 = st.columns([2, 3])
f1.slider("Zahl der Wagen n", *bounds("n3"), key="n3", help="Länge des Zuges; alle n! Folgen sind aufgezählt.")
f2.radio("Maschine (Histogramm und Spur)", options=[0, 1, 2], format_func=lambda i: M.NAME[M.MASCHINEN[i]], key="m3", horizontal=True,
         help="Welche Maschine das Histogramm und die Spur der Folge (2, …, n, 1) zeigt; die Tabelle zeigt immer alle drei.")
m3name = M.MASCHINEN[s.m3]
st.plotly_chart(build_histogramm(s.n3, m3name), width="stretch", key="chart_hist")
st.markdown(md_table(
    ["Maschine", "mittlere Durchlaufzahl", "größte Durchlaufzahl", "Folgen mit der größten"],
    [[M.NAME[m], ev.de(float(a3.daten[m]["mittel"]), 4), a3.daten[m]["maximum"], ev.de_int(a3.daten[m]["am_maximum"])] for m in (M.POP, M.WEST, M.FREI)],
))
p_h, v_h, d_h, b_h = ev.kleinster_hinten_verlauf(s.n3, m3name)
st.markdown(f"**Der kleinste Wagen hinten, {ev.folge_text(p_h)}, bei {M.NAME[m3name]}: {d_h} Durchläufe.**")
st.markdown(verlaufs_tabelle(v_h, b_h, "Spur" if m3name == M.WEST else "Blöcke (je Block umgekehrt)"))
kind, text = ev.verdict_verteilung(a3)
getattr(st, kind)(text)

st.markdown("---")

# --- Experiment 4 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 4: Zwei Rezepte, zwei Antworten (die Falle)")
st.caption("„k Durchläufe“ ist keine eindeutige Maschine, und „sortierbar“ ist nicht „Ausgabe eines Pop-Durchlaufs“. Klasse-Test: Streichen eines Wagens (Ränge neu nummeriert); eine Verletzung ist eine Folge in höchstens k Durchläufen, "
           "bei der das Streichen eines Wagens eine Folge ergibt, die mehr als k Durchläufe braucht.")
g1, g2, g3 = st.columns(3)
g1.slider("Zahl der Wagen n", *bounds("n4"), key="n4", help="Länge des Zuges für die Liste der nur frei sortierbaren Folgen und das Bild gegen das Urbild.")
g2.slider("Höchstens k Durchläufe", *bounds("k4"), key="k4", help="Zahl der erlaubten Durchläufe für Liste und Klasse-Test (2 oder 3).")
g3.radio("Maschine zum Streichen", options=[0, 1, 2], format_func=lambda i: M.NAME[M.MASCHINEN[i]], key="m4",
         help="Für welche Maschine der Klasse-Test gezeigt wird.")
a4 = _klasse(s.n4, s.k4, mach4)
st.markdown(f"**Folgen, die frei in höchstens {s.k4} Durchläufen gehen, fest aber mehr brauchen (n = {s.n4}): {ev.de_int(a4.nur_frei['anzahl'])}.** Die kleinsten fünf in lexikographischer Reihenfolge:")
if a4.nur_frei["erste"]:
    st.markdown(", ".join(ev.folge_text(p) for p in a4.nur_frei["erste"]))
else:
    st.caption("Keine solche Folge bei dieser Länge.")
st.markdown(md_table(
    ["n", f"Folgen in höchstens {s.k4} Durchläufen ({M.NAME[mach4]})", "davon betroffen (Streichen ergibt mehr Durchläufe)"],
    [[("**" + str(n) + "**") if n == s.n4 else n, ev.de_int(a), ev.de_int(b)] for n, a, b in a4.zeile],
))
if a4.zeuge is not None and mach4 != M.FREI:
    z = a4.zeuge
    st.markdown(f"**Kleinster Zeuge:** {ev.folge_text(z['p'])} geht in {s.k4} Durchläufen; ohne den Wagen an Stelle {z['stelle']} bleibt {ev.folge_text(z['q'])} mit {z['durchlaeufe_q']} Durchläufen.")
    w1, w2 = st.columns(2)
    with w1:
        st.plotly_chart(build_verlauf(a4.zeuge_verlauf, mach4), width="stretch", key="chart_zeuge_p")
    with w2:
        st.plotly_chart(build_verlauf(a4.zeuge_q_verlauf, mach4), width="stretch", key="chart_zeuge_q")
st.plotly_chart(build_bild_urbild(), width="stretch", key="chart_bild")
st.caption("Bild: Zahl der verschiedenen Ausgaben eines festen Pop-Durchlaufs über alle n! Eingaben. Urbild der sortierten Folge: Zahl der Folgen, die ein Durchlauf sortiert (2^(n − 1)).")
kind, text = ev.verdict_klasse(a4)
getattr(st, kind)(text)

st.markdown("---")

# --- Experiment 5 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 5: Ankunftsmodell, Verweilzeit D")
st.caption("Ausgedachtes Modell, keine reale Ankunftsfolge: Wagen i kommt zur Zeit i an und bleibt exponentialverteilt lange (Mittel D); die Abfahrtsreihenfolge ist der Rang. D und Zufalls-Seed stehen in der Seitenleiste. "
           "Zähleinheit: Zufallsfolgen. Bei n = 9 ist die freie Leerung aus der vorgerechneten Aufzählung abgelesen, bei n = 10 nicht gemessen.")
h1, h2 = st.columns(2)
h1.radio("Zahl der Wagen n", options=list(C.N5_WERTE), key="n5", horizontal=True, help="n = 9 zeigt auch die freie Leerung (aus der Tabelle), n = 10 nur die beiden festen Maschinen.")
h2.slider("Zahl der Folgen", *bounds("nfolgen"), key="nfolgen", step=C.NFOLGEN_STEP, help="Folgen im Strom für den gewählten Wert D (Rechenzeit bei 2 000 Folgen etwa eine bis zwei Sekunden).")
a5 = _modell(s.n5, s.d_idx, s.nfolgen, s.seed)
st.plotly_chart(build_modell_balken(a5), width="stretch", key="chart_modell_balken")
zeilen = []
for m in a5.kennzahlen:
    kz = a5.kennzahlen[m]
    zeilen.append([M.NAME[m], f"{ev.de(kz['mittel'], 2)} ± {ev.de(kz['se'], 2)}"]
                  + [f"{ev.pct(kz['anteil'][k])} ± {ev.de(100 * sqrt(kz['anteil'][k] * (1 - kz['anteil'][k]) / kz['n']), 1)}" for k in (1, 2, 3)])
st.markdown(md_table(["Maschine", "mittlere Durchläufe ± Standardfehler", "höchstens 1", "höchstens 2", "höchstens 3"], zeilen))
st.caption("Anteile der Züge in höchstens 1, 2, 3 Durchläufen, ± Standardfehler in Prozentpunkten.")
st.markdown("**Vorgerechnet: mittlere Durchlaufzahl über alle Werte von D** (zwei unabhängige Ströme zu je 2 000 Folgen, Zufalls-Seed 12000 durchgezogen und 13000 gestrichelt; der Rhombus ist Ihre Rechnung oben).")
st.plotly_chart(build_modell_linie(s.n5, a5), width="stretch", key="chart_modell_linie")
if s.n5 == 9:
    exakt = " / ".join(ev.de(float(T.mittel(m, 9)), 4) for m in (M.POP, M.WEST, M.FREI))
    st.caption(f"Gegenprobe Modell U: bei D = ∞ sind alle Folgen gleich wahrscheinlich; der exakte Mittelwert über alle {ev.de_int(factorial(9))} Folgen ist {exakt} (fest / gieriger Stapel / frei).")
kind, text = ev.verdict_modell(a5, ev.zellen_west_besser(), ev.frei_gegen_west_n9() if s.n5 == 9 else None)
getattr(st, kind)(text)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(X.GRENZEN)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown("**Konventionen**")
    st.markdown(X.KONVENTIONEN)
    st.markdown(X.FORMELN)

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
