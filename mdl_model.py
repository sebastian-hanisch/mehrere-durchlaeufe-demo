"""Ankunftsmodell V (ausgedacht, keine reale Ankunftsfolge) und Durchlaufzahlen über Zufallsfolgen.

**Modell V:** Wagen i kommt zur Zeit i an und bleibt exponentialverteilt lange (Mittel D Ankunftsabstände); die Abholrangzahl ist die Reihenfolge der Abfahrten. D = ∞ bedeutet
gleichverteilte Folgen (alle n! Anordnungen gleich wahrscheinlich, Modell U). Das Modell kennt nur die **Rangfolge** der Abfahrten, keine Zeiten und keine Gleise.
Es ist **ein Modell, kein Fall**: In keiner gelesenen Quelle gibt es eine reale Ankunftsfolge, die Zahlen gelten nur für dieses Modell bei diesem D und n.

**Zufall** nur über den ganzzahligen SplitMix64 (`mdl_rng.py`, Exponentialverteilung über `exact_log`: auf jeder Plattform bitgleich). Der Strom für einen Wert D ist
`SplitMix64(Zufalls-Seed + Index von D)`; die Folgen eines Stroms entstehen nacheinander. Die Zahl der Durchläufe ist ganzzahlig, die Zählungen sind deshalb exakt.
"""

from __future__ import annotations

from math import sqrt

import mdl_constants as C
import mdl_machines as M
from mdl_rng import SplitMix64


def ankunftsfolge(rng: SplitMix64, n: int, mittel) -> tuple:
    """Eine Folge der Abholränge 1 … n in Ankunftsreihenfolge. `mittel` ist D oder None (= ∞, gleichverteilt)."""
    if mittel is None:
        items = list(range(1, n + 1))
        rng.shuffle(items)
        return tuple(items)
    abfahrt = sorted((i + rng.expovariate(mittel), i) for i in range(1, n + 1))
    rang = [0] * (n + 1)
    for r, (_, i) in enumerate(abfahrt, 1):
        rang[i] = r
    return tuple(rang[1:])


def strom(n: int, d_index: int, seed: int, nfolgen: int) -> list[tuple]:
    """`nfolgen` Folgen der Länge n aus dem Strom `seed + d_index` mit dem D-Wert Nr. `d_index` aus C.D_WERTE."""
    rng = SplitMix64(seed + d_index)
    mittel = C.D_WERTE[d_index]
    return [ankunftsfolge(rng, n, mittel) for _ in range(nfolgen)]


def histogramme(folgen, frei=None) -> dict[str, list[int]]:
    """Zahl der Folgen mit genau j Durchläufen je Maschine; `frei` ist eine Funktion Folge → freie Durchlaufzahl (oder None: ohne FREI)."""
    ergebnis = {M.POP: [], M.WEST: []}
    if frei is not None:
        ergebnis[M.FREI] = []
    for p in folgen:
        werte = {M.POP: M.durchlaufzahl(p, M.POP), M.WEST: M.durchlaufzahl(p, M.WEST)}
        if frei is not None:
            werte[M.FREI] = frei(p)
        for m, j in werte.items():
            h = ergebnis[m]
            if len(h) <= j:
                h.extend([0] * (j + 1 - len(h)))
            h[j] += 1
    return ergebnis


def kennzahlen(hist: list[int]) -> dict:
    """Mittel, Standardfehler des Mittels und kumulierte Anteile (höchstens 1, 2, 3 Durchläufe) aus der Verteilung der Durchlaufzahlen."""
    n = sum(hist)
    s1 = sum(j * c for j, c in enumerate(hist))
    s2 = sum(j * j * c for j, c in enumerate(hist))
    mittel = s1 / n
    var = (s2 - s1 * s1 / n) / (n - 1) if n > 1 else 0.0
    return {
        "n": n,
        "mittel": mittel,
        "se": sqrt(max(var, 0.0) / n),
        "anteil": {k: sum(hist[: k + 1]) / n for k in (1, 2, 3)},
    }
