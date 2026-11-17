"""Pop-Stack mit freier Leerung (FREI): ein Durchlauf ist eine beliebige Zerlegung der Folge in zusammenhängende Blöcke, jeder Block wird umgekehrt.

Das gibt 2^(n−1) Zerlegungen je Durchlauf. FREI sind k Pop-Durchläufe mit freier Leerung; die Gleichsetzung mit k Pop-Stacks in Reihe ist eine eigene, nicht an der Literatur geprüfte Überlegung (ohne gelesene Quelle: Hintereinanderschalten ändert nur den
Zeitpunkt, nicht die Folge, die beim nächsten Behälter ankommt) und enthält den festen Pop-Stack (er ist eine bestimmte Zerlegung: die maximal absteigenden Läufe).

Die freie Durchlaufzahl **einer** Folge wird durch Treffen in der Mitte bestimmt: Jede Blockumkehrung ist ihre eigene Umkehrung, und die Zerlegung in lauter einzelne Wagen
ändert nichts. Die Mengen der Folgen, die man von der Folge und von der sortierten Folge aus nach höchstens zwei Durchläufen erreicht, schneiden sich also genau dann, wenn die
Durchlaufzahl höchstens 4 ist. Bei n ≤ 9 ist nie mehr als 4 nötig (Aufzählung aller n! Folgen, tools/mdl_make_tables.py); für n ≥ 10 ist das Maximum nicht gemessen.
"""

from __future__ import annotations

from functools import lru_cache
from operator import itemgetter

N_MAX = 9  # Obergrenze der Live-Rechnung: darüber ist das Maximum der freien Durchlaufzahl nicht gemessen


def zerlegungen(n: int) -> list[tuple[int, ...]]:
    """Alle Zerlegungen von n in Blocklängen (Kompositionen von n): 2^(n−1) Stück, in fester Reihenfolge."""
    if n < 1:
        raise ValueError("n muss mindestens 1 sein")
    res = []
    for maske in range(1 << (n - 1)):
        z, lauf = [], 1
        for i in range(n - 1):
            if (maske >> i) & 1:
                z.append(lauf)
                lauf = 1
            else:
                lauf += 1
        z.append(lauf)
        res.append(tuple(z))
    return res


def blockumkehr(p, bloecke) -> tuple:
    """Kehrt jeden Block der Zerlegung um (Blocklängen in Reihenfolge, Summe = len(p))."""
    if sum(bloecke) != len(p):
        raise ValueError("Die Blocklängen müssen zur Länge der Folge passen")
    aus, i = [], 0
    for b in bloecke:
        aus.extend(reversed(p[i:i + b]))
        i += b
    return tuple(aus)


@lru_cache(maxsize=None)
def _greifer(n: int):
    """Je Zerlegung ein itemgetter, der die Blockumkehrung als eine Auswahl von Stellen ausführt (schnell, Standardbibliothek)."""
    zs = zerlegungen(n)
    ergebnis = []
    for z in zs:
        idx, i = [], 0
        for b in z:
            idx.extend(range(i + b - 1, i - 1, -1))
            i += b
        ergebnis.append(itemgetter(*idx) if n > 1 else (lambda p: p))
    return zs, tuple(ergebnis)


@lru_cache(maxsize=None)
def _von_der_sortierten(n: int):
    """Mengen der Folgen, die man von 1 … n aus nach genau 1 und genau 2 Durchläufen erreicht, je mit einer Zerlegung (Index in `zs`) als Weg."""
    zs, gr = _greifer(n)
    ident = tuple(range(1, n + 1))
    b0 = {ident: ()}
    b1 = {}
    for i, g in enumerate(gr):
        b1.setdefault(g(ident), (i,))
    b2 = {}
    for q, w1 in b1.items():
        for j, g in enumerate(gr):
            b2.setdefault(g(q), w1 + (j,))
    return b0, b1, b2


def frei_durchlaufzahl(p, mit_weg: bool = False):
    """Freie Durchlaufzahl einer Folge (n ≤ 9). Mit `mit_weg=True` zusätzlich eine Liste von Zerlegungen (eine von mehreren möglichen Lösungen)."""
    p = tuple(p)
    n = len(p)
    if n > N_MAX:
        raise ValueError(f"nicht gemessen: Obergrenze n = {N_MAX}")
    if n == 0:
        return (0, []) if mit_weg else 0
    zs, gr = _greifer(n)
    b = _von_der_sortierten(n)
    a0 = {p: ()}
    a1 = {}
    for i, g in enumerate(gr):
        a1.setdefault(g(p), (i,))
    a = [a0, a1, None]
    # Weg der Länge d = j + m mit j = d // 2 Durchläufen von der Folge und m von der sortierten Folge aus; da die Zerlegung in lauter einzelne Wagen nichts ändert,
    # sind die Mengen „nach genau j Durchläufen“ zugleich die „nach höchstens j“, und die erste Länge d mit Treffer ist die Durchlaufzahl.
    for d in range(0, 5):
        j = d // 2
        m = d - j
        if j == 2 and a[2] is None:
            a[2] = {}
            for q, z1 in a1.items():
                for k, g in enumerate(gr):
                    a[2].setdefault(g(q), z1 + (k,))
        treffer = next((x for x in a[j] if x in b[m]), None)
        if treffer is not None:
            if not mit_weg:
                return d
            weg = [zs[i] for i in a[j][treffer]] + [zs[i] for i in reversed(b[m][treffer])]
            return d, weg
    raise RuntimeError("Folge braucht mehr als 4 freie Durchläufe (bei n ≤ 9 nicht beobachtet)")


def weg_anwenden(p, weg) -> tuple:
    """Wendet eine Liste von Zerlegungen der Reihe nach an (Kontrolle einer gefundenen Lösung)."""
    q = tuple(p)
    for z in weg:
        q = blockumkehr(q, z)
    return q
