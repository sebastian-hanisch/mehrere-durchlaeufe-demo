"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

from math import factorial

import plotly.graph_objects as go

import mdl_constants as C
import mdl_evaluation as ev
import mdl_machines as M
import mdl_tables as T


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=340):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


# --- Experiment 1 -----------------------------------------------------------------------------------------------------------------------------

KURZTITEL = {"pop": "Pop-Stack fest", "west": "Gieriger Stapel", "frei": "Pop-Stack frei"}


def build_verlauf(verlauf: list, maschine: str):
    """Die Folge vor dem ersten und nach jedem Durchlauf: eine Zeile je Zustand, Farbe und Zahl = Rang des Wagens."""
    n = len(verlauf[0])
    z = [list(q) for q in verlauf]
    zeilen = ["Eingabe"] + [f"nach {j}" for j in range(1, len(verlauf))]
    k = len(verlauf) - 1
    fig = go.Figure(go.Heatmap(
        z=z, x=[str(i) for i in range(1, n + 1)], y=zeilen, zmin=1, zmax=max(n, 2), colorscale="Viridis", showscale=False,
        text=z, texttemplate="%{text}", textfont=dict(size=15, color="white"), xgap=2, ygap=2, hovertemplate="%{y}, Platz %{x}: Rang %{z}<extra></extra>",
    ))
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(side="top", title_text="Platz im Zug", title_standoff=2, tickmode="array", tickvals=[str(i) for i in range(1, n + 1)])
    fig.update_layout(title=dict(text=f"{KURZTITEL[maschine]}: {k} {'Durchlauf' if k == 1 else 'Durchläufe'}", font=dict(size=14), x=0.0, y=0.98))
    fig.update_layout(margin=dict(l=10, r=10, t=70, b=10))
    return _base_heatmap(fig, 110 + 32 * len(verlauf))


def _base_heatmap(fig, height):
    fig.update_layout(height=height, plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


# --- Experiment 2 -----------------------------------------------------------------------------------------------------------------------------

def build_anteil_linien(n_gewaehlt: int, k: int):
    """Anteil der Folgen in höchstens k Durchläufen über n (logarithmische Achse); der gewählte Wert ist hervorgehoben."""
    ns = list(range(C.N_MIN, C.N_MAX + 1))
    fig = go.Figure()
    for m in M.MASCHINEN:
        anteile = [100 * T.kumuliert(m, n, k) / factorial(n) for n in ns]
        fig.add_trace(go.Scatter(x=ns, y=anteile, mode="lines+markers", name=M.NAME[m], line=dict(color=C.FARBE[m], width=2.5),
                                 hovertemplate=M.NAME[m] + ", n = %{x}: %{y:.3g} % aller Folgen<extra></extra>"))
        i = ns.index(n_gewaehlt)
        fig.add_trace(go.Scatter(x=[n_gewaehlt], y=[anteile[i]], mode="markers", marker=dict(size=14, color=C.FARBE[m], line=dict(color="black", width=2)), showlegend=False, hoverinfo="skip"))
    fig.update_xaxes(title_text="Zahl der Wagen n", dtick=1)
    fig.update_yaxes(title_text=f"Anteil in höchstens {k} Durchläufen (%)", type="log")
    return _base(fig, 340)


# --- Experiment 3 -----------------------------------------------------------------------------------------------------------------------------

def build_histogramm(n: int, maschine: str):
    h = T.verteilung(maschine, n)
    fig = go.Figure(go.Bar(x=list(range(len(h))), y=h, marker_color=C.FARBE[maschine], text=[ev.de_int(c) for c in h], textposition="outside", cliponaxis=False,
                           hovertemplate="%{x} Durchläufe: %{y} Folgen<extra></extra>"))
    fig.update_xaxes(title_text="Zahl der Durchläufe", dtick=1)
    fig.update_yaxes(title_text="Zahl der Folgen", range=[0, max(h) * 1.18])
    fig.update_layout(title=dict(text=f"{M.NAME[maschine]}, n = {n}: Folgen je Durchlaufzahl (Summe {ev.de_int(sum(h))})", font=dict(size=14), x=0.0))
    return _base(fig, 340)


# --- Experiment 4 -----------------------------------------------------------------------------------------------------------------------------

def build_bild_urbild():
    """Verschiedene Ausgaben eines festen Pop-Durchlaufs (Bild) gegen die Zahl der in einem Durchlauf sortierbaren Folgen (Urbild der sortierten Folge)."""
    ns = list(range(C.N_MIN, C.N_MAX + 1))
    fig = go.Figure()
    fig.add_trace(go.Bar(x=ns, y=[2 ** (n - 1) for n in ns], name="in einem Durchlauf sortierbar (2^(n − 1))", marker_color=C.FARBE["pop"]))
    fig.add_trace(go.Bar(x=ns, y=[T.bild(n) for n in ns], name="verschiedene Ausgaben eines Durchlaufs (Bild)", marker_color=C.COLOR_OTHER))
    fig.update_layout(barmode="group")
    fig.update_xaxes(title_text="Zahl der Wagen n", dtick=1)
    fig.update_yaxes(title_text="Zahl der Folgen", type="log")
    return _base(fig, 320)


# --- Experiment 5 -----------------------------------------------------------------------------------------------------------------------------

def build_modell_balken(r):
    """Mittlere Durchlaufzahl je Maschine mit Standardfehler des Mittels (live gerechnet)."""
    maschinen = list(r.kennzahlen)
    fig = go.Figure(go.Bar(
        x=[M.NAME[m] for m in maschinen], y=[r.kennzahlen[m]["mittel"] for m in maschinen], marker_color=[C.FARBE[m] for m in maschinen],
        error_y=dict(type="data", array=[r.kennzahlen[m]["se"] for m in maschinen], visible=True),
        text=[ev.de(r.kennzahlen[m]["mittel"], 2) for m in maschinen], textposition="outside", cliponaxis=False,
        hovertemplate="%{x}: im Mittel %{y:.2f} Durchläufe<extra></extra>",
    ))
    fig.update_yaxes(title_text="mittlere Zahl der Durchläufe", range=[0, max(r.n, 1)])
    fig.update_layout(title=dict(text=f"n = {r.n}, D = {ev.d_text(r.d_idx)}: {ev.de_int(r.nfolgen)} Züge im Ankunftsmodell V", font=dict(size=14), x=0.0))
    return _base(fig, 320)


def build_modell_linie(n: int, live=None):
    """Vorgerechnete mittlere Durchlaufzahl gegen D (beide Ströme: durchgezogen Zufalls-Seed 12000, gestrichelt 13000); der live gerechnete Punkt ist hervorgehoben."""
    vor = ev.vorgerechnet(n)
    fig = go.Figure()
    for m in (M.POP, M.WEST, M.FREI):
        if m == M.FREI and n != 9:
            continue
        for strom, dash in zip(C.STROM_SEEDS, ("solid", "dash")):
            fig.add_trace(go.Scatter(
                x=list(C.D_LABEL), y=[vor[strom][d][m]["mittel"] for d in range(len(C.D_WERTE))], mode="lines+markers",
                name=f"{M.NAME[m]}, Strom {strom}", line=dict(color=C.FARBE[m], width=2, dash=dash), marker=dict(size=6),
                hovertemplate=M.NAME[m] + f", Strom {strom}, D = " + "%{x}: %{y:.2f}<extra></extra>",
            ))
    if live is not None:
        for m, kz in live.kennzahlen.items():
            fig.add_trace(go.Scatter(x=[ev.d_text(live.d_idx)], y=[kz["mittel"]], mode="markers", marker=dict(size=14, color=C.FARBE[m], line=dict(color="black", width=2), symbol="diamond"),
                                     showlegend=False, hovertemplate="live: %{y:.2f}<extra></extra>"))
    fig.update_xaxes(title_text="Verweilzeit D (Ankunftsabstände; ∞ = alle Folgen gleich wahrscheinlich)", type="category")
    fig.update_yaxes(title_text="mittlere Zahl der Durchläufe", range=[0, 7.5])
    fig.update_layout(legend=dict(orientation="h", y=-0.45, font=dict(size=10)))
    return _base(fig, 420)
