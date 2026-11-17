"""Die beiden festen Maschinen: Pop-Stack (festes Rezept) und gieriger Stapel (West-Abbildung), jeweils ein Durchlauf und die Durchlaufzahl.

Eine Folge ist ein Tupel der Abholränge 1 … n in Ankunftsreihenfolge, alle Ränge verschieden; das Ziel ist die aufsteigende Folge 1 … n.

* **Pop-Stack, festes Rezept** (POP): Der Stapel wird ganz geleert (obere Wagen zuerst), sobald der nächste Wagen größer ist als die Spitze; sonst wird
  gestapelt. Ein Durchlauf kehrt jeden maximal absteigenden Lauf der Folge um.
* **Gieriger Stapel** (WEST): ausgeben, solange die Spitze kleiner ist als der nächste Wagen; dann stapeln (die West-Abbildung der Literatur).

Die **Durchlaufzahl** einer Folge ist die kleinste Zahl von Durchläufen, nach der sie sortiert ist (die sortierte Folge braucht 0). Alles Standardbibliothek.
"""

from __future__ import annotations

POP = "pop"
WEST = "west"
FREI = "frei"
MASCHINEN = (POP, WEST, FREI)
NAME = {POP: "Pop-Stack (festes Rezept)", WEST: "gieriger Stapel", FREI: "Pop-Stack mit freier Leerung"}
KURZ = {POP: "fest", WEST: "gieriger Stapel", FREI: "frei"}


def ist_sortiert(p) -> bool:
    return all(p[i] < p[i + 1] for i in range(len(p) - 1))


def pop_durchlauf(p) -> tuple:
    """Ein Durchlauf des Pop-Stacks mit festem Rezept: leeren, sobald der nächste Wagen größer ist als die Spitze."""
    aus, stapel = [], []
    for x in p:
        if stapel and x > stapel[-1]:
            while stapel:
                aus.append(stapel.pop())
        stapel.append(x)
    while stapel:
        aus.append(stapel.pop())
    return tuple(aus)


def west_durchlauf(p) -> tuple:
    """Ein Durchlauf des gierigen Stapels: ausgeben, solange die Spitze kleiner ist als der nächste Wagen."""
    aus, stapel = [], []
    for x in p:
        while stapel and stapel[-1] < x:
            aus.append(stapel.pop())
        stapel.append(x)
    while stapel:
        aus.append(stapel.pop())
    return tuple(aus)


DURCHLAUF = {POP: pop_durchlauf, WEST: west_durchlauf}


def pop_bloecke(p) -> list[int]:
    """Blocklängen des festen Pop-Durchlaufs: die maximal absteigenden Läufe der Folge (jeder wird umgekehrt)."""
    bloecke, lauf = [], 1
    for i in range(1, len(p)):
        if p[i] < p[i - 1]:
            lauf += 1
        else:
            bloecke.append(lauf)
            lauf = 1
    if p:
        bloecke.append(lauf)
    return bloecke


def spur(p, maschine) -> list[tuple[str, int]]:
    """Ereignisse eines Durchlaufs in Reihenfolge: ("rein", x) für einen gestapelten, ("raus", x) für einen ausgegebenen Wagen."""
    ereignisse, stapel = [], []
    if maschine == POP:
        for x in p:
            if stapel and x > stapel[-1]:
                while stapel:
                    ereignisse.append(("raus", stapel.pop()))
            stapel.append(x)
            ereignisse.append(("rein", x))
    elif maschine == WEST:
        for x in p:
            while stapel and stapel[-1] < x:
                ereignisse.append(("raus", stapel.pop()))
            stapel.append(x)
            ereignisse.append(("rein", x))
    else:
        raise ValueError("Spur nur für die festen Maschinen POP und WEST")
    while stapel:
        ereignisse.append(("raus", stapel.pop()))
    return ereignisse


def verlauf(p, maschine) -> list[tuple]:
    """Die Folge vor dem ersten und nach jedem Durchlauf, bis sie sortiert ist (Länge = Durchlaufzahl + 1)."""
    p = tuple(p)
    schritt = DURCHLAUF[maschine]
    v = [p]
    # Obergrenze n − 1 (gierig: Beweisskizze in der README; fest: Aufzählung n ≤ 9); die Schleifengrenze fängt nur einen Programmfehler ab.
    for _ in range(len(p) + 1):
        if ist_sortiert(v[-1]):
            return v
        v.append(schritt(v[-1]))
    raise RuntimeError("Folge nach n + 1 Durchläufen nicht sortiert (Programmfehler)")


def durchlaufzahl(p, maschine) -> int:
    """Durchlaufzahl der festen Maschine POP oder WEST."""
    schritt = DURCHLAUF[maschine]
    q, t = tuple(p), 0
    while not ist_sortiert(q):
        q = schritt(q)
        t += 1
        if t > len(p) + 1:
            raise RuntimeError("Folge nach n + 1 Durchläufen nicht sortiert (Programmfehler)")
    return t


def streiche(p, i) -> tuple:
    """Streicht den Wagen an Stelle i (0-basiert); die Ränge werden neu nummeriert (1 … n − 1)."""
    v = p[i]
    return tuple(x - 1 if x > v else x for j, x in enumerate(p) if j != i)
