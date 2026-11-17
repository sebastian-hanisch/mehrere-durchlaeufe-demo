"""Vorgerechnete Tabellen (Aufzählung aller n! Folgen bis n = 9, Klasse-Test, Bild des Pop-Durchlaufs, Ankunftsmodell in zwei Strömen).

Die Dateien `data/mdl_tables.json` und `data/mdl_frei_n9.bin` erzeugt `tools/mdl_make_tables.py` (numpy); `--check` rechnet n ≤ 8 neu und vergleicht die Dateien exakt,
n = 9 prüft es über die Prüfsumme. Die App rechnet die Aufzählung nicht live: n = 9 hat 362 880 Folgen und je Folge bis zu 256 Zerlegungen je Durchlauf.
`mdl_frei_n9.bin` enthält je Folge der Länge 9 (in lexikographischer Reihenfolge, Rang 0 = sortierte Folge) die freie Durchlaufzahl als ein Byte.
"""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from functools import lru_cache
from math import factorial
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"
TABELLEN = DATA / "mdl_tables.json"
FREI_N9 = DATA / "mdl_frei_n9.bin"


@lru_cache(maxsize=1)
def tabellen() -> dict:
    with open(TABELLEN, encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def frei_n9_bytes() -> bytes:
    daten = FREI_N9.read_bytes()
    if hashlib.sha256(daten).hexdigest() != tabellen()["frei_n9_sha256"]:
        raise ValueError("data/mdl_frei_n9.bin passt nicht zur Prüfsumme in data/mdl_tables.json (tools/mdl_make_tables.py --check)")
    return daten


def lex_rank(p) -> int:
    """Lexikographischer Rang einer Folge aus den Rängen 1 … n (die sortierte Folge hat Rang 0)."""
    n = len(p)
    r = 0
    for i in range(n - 1):
        c = 0
        for j in range(i + 1, n):
            if p[j] < p[i]:
                c += 1
        r += c * factorial(n - 1 - i)
    return r


def frei_n9(p) -> int:
    """Freie Durchlaufzahl einer Folge der Länge 9 aus der vorgerechneten Tabelle."""
    if len(p) != 9:
        raise ValueError("die Tabelle gilt nur für n = 9")
    return frei_n9_bytes()[lex_rank(p)]


# --- Zugriff auf die Zählungen ------------------------------------------------------------------------------------------------------------------

def verteilung(maschine: str, n: int) -> list[int]:
    """Zahl der Folgen mit genau j Durchläufen, j = 0 … Maximum (Summe n!)."""
    return list(tabellen()["verteilung"][maschine][str(n)])


def kumuliert(maschine: str, n: int, k: int) -> int:
    """Zahl der Folgen, die in höchstens k Durchläufen sortiert sind (die sortierte Folge zählt mit)."""
    return sum(verteilung(maschine, n)[: k + 1])


def maximum(maschine: str, n: int) -> int:
    """Größte Durchlaufzahl über alle n! Folgen."""
    return len(verteilung(maschine, n)) - 1


def am_maximum(maschine: str, n: int) -> int:
    """Zahl der Folgen, die die größte Durchlaufzahl brauchen."""
    return verteilung(maschine, n)[-1]


def mittel(maschine: str, n: int) -> Fraction:
    """Mittlere Durchlaufzahl über alle n! Folgen (Modell U, exakt als Bruch)."""
    h = verteilung(maschine, n)
    return Fraction(sum(j * c for j, c in enumerate(h)), factorial(n))


def verletzungen(maschine: str, k: int, n: int) -> int:
    """Zahl der Folgen in „höchstens k Durchläufen“, bei denen das Streichen eines Wagens eine Folge mit mehr als k Durchläufen ergibt (n ≥ 3)."""
    return tabellen()["verletzungen"][maschine][str(k)][str(n)]


def zeuge(maschine: str, k: int):
    """Kleinster Zeuge (erster Fund in lexikographischer Reihenfolge beim kleinsten n) oder None."""
    z = tabellen()["zeugen"][maschine].get(str(k))
    return None if z is None else {**z, "p": tuple(z["p"]), "q": tuple(z["q"])}


def bild(n: int) -> int:
    """Zahl der verschiedenen Ausgaben eines festen Pop-Durchlaufs über alle n! Eingaben."""
    return tabellen()["bild"][n - 1]


def nur_frei(k: int, n: int) -> dict:
    """Folgen, die frei in höchstens k, fest aber in mehr Durchläufen sortiert sind: Anzahl und die ersten (lexikographisch)."""
    z = tabellen()["nur_frei"][str(k)][str(n)]
    return {"anzahl": z["anzahl"], "erste": [tuple(p) for p in z["erste"]]}


def modell_v(strom_seed: int, n: int, d_index: int) -> dict[str, list[int]]:
    """Verteilungen der Durchlaufzahlen über 2 000 Folgen aus dem Strom `strom_seed + d_index` (vorgerechnet)."""
    return {m: list(h) for m, h in tabellen()["modell_v"][str(strom_seed)][str(n)][str(d_index)].items()}
