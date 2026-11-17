"""Erzeugt die vorgerechneten Tabellen `data/mdl_tables.json` und `data/mdl_frei_n9.bin` (Aufzählung aller n! Folgen bis n = 9) und prüft sie.

    python tools/mdl_make_tables.py            # alles neu rechnen und schreiben (rund 1,5 Minuten, braucht numpy)
    python tools/mdl_make_tables.py --check    # n ≤ 8 neu rechnen und mit der Datei vergleichen, n = 9 über die Prüfsumme und die Summen der Verteilungen;
                                               # dazu das Ankunftsmodell in beiden Strömen neu rechnen (alles „neu gerechnet, exakt verglichen“: nur Ganzzahlen)
    python tools/mdl_make_tables.py --full     # wie --check, aber auch n = 9 neu rechnen und vergleichen

Zähleinheit überall: Folgen (alle n! Anordnungen der Ränge 1 … n, alle Wagen verschieden), beim Ankunftsmodell Zufallsfolgen. Rechenweg hier mit numpy (Folgen als Zeilen,
lexikographischer Rang über den Lehmer-Code); die App rechnet einzelne Folgen in reinem Python (`mdl_machines.py`, `mdl_free.py`): zwei verschiedene Wege.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import mdl_constants as C  # noqa: E402
import mdl_model as MOD  # noqa: E402
import mdl_tables as T  # noqa: E402

N_MAX = 9
MASCH = ("pop", "west", "frei")


def log(*a):
    print(*a, flush=True)


# --- numpy-Bausteine ----------------------------------------------------------------------------------------------------------------------------

def alle_folgen(n: int) -> np.ndarray:
    return np.array(list(itertools.permutations(range(1, n + 1))), dtype=np.int8)


def rang(a: np.ndarray) -> np.ndarray:
    """Lexikographischer Rang jeder Zeile (Werte 1 … n) über den Lehmer-Code."""
    n = a.shape[1]
    r = np.zeros(a.shape[0], dtype=np.int64)
    for i in range(n - 1):
        c = (a[:, i + 1:] < a[:, i:i + 1]).sum(axis=1)
        r += c.astype(np.int64) * math.factorial(n - 1 - i)
    return r


def pop_zeile(p) -> tuple:
    aus, st = [], []
    for x in p:
        if st and x > st[-1]:
            while st:
                aus.append(st.pop())
        st.append(x)
    while st:
        aus.append(st.pop())
    return tuple(aus)


def west_zeile(p) -> tuple:
    aus, st = [], []
    for x in p:
        while st and st[-1] < x:
            aus.append(st.pop())
        st.append(x)
    while st:
        aus.append(st.pop())
    return tuple(aus)


def dist_fest(folgen: np.ndarray, op):
    """Durchlaufzahl jeder Folge (Feld in Rangordnung) und die Ränge der Ausgaben eines Durchlaufs. Runden: Folgen, deren Ausgabe schon bekannt ist, bekommen +1."""
    ausgaben = np.array([op(tuple(p)) for p in folgen.tolist()], dtype=np.int8)
    nachfolger = rang(ausgaben)
    dist = np.full(len(folgen), -1, dtype=np.int8)
    dist[0] = 0
    t = 0
    while (dist < 0).any():
        t += 1
        neu = (dist < 0) & (dist[nachfolger] == t - 1)
        if not neu.any():
            raise RuntimeError("Folgen ohne Weg zur sortierten Folge (Programmfehler)")
        dist[neu] = t
    return dist, nachfolger


def umkehr_indizes(n: int) -> list[np.ndarray]:
    """Zu jeder Zerlegung von n in Blöcke die Stellenauswahl, die jeden Block umkehrt (Zerlegung = Bitmaske der Schnittstellen)."""
    res = []
    for maske in range(1 << (n - 1)):
        idx, start = [], 0
        for i in range(n):
            if i == n - 1 or (maske >> i) & 1:
                idx.extend(range(i, start - 1, -1))
                start = i + 1
        res.append(np.array(idx, dtype=np.int64))
    return res


def dist_frei(n: int) -> np.ndarray:
    """Breitensuche von der sortierten Folge: jede Blockumkehrung ist ihre eigene Umkehrung, der Abstand ist die freie Durchlaufzahl."""
    dist = np.full(math.factorial(n), -1, dtype=np.int8)
    dist[0] = 0
    front = np.arange(1, n + 1, dtype=np.int8)[None, :]
    ops = umkehr_indizes(n)
    d = 0
    while front.shape[0]:
        d += 1
        neue = []
        for idx in ops:
            g = front[:, idx]
            r = rang(g)
            m = dist[r] < 0
            if m.any():
                dist[r[m]] = d
                neue.append(g[m])
        front = np.concatenate(neue) if neue else np.zeros((0, n), dtype=np.int8)
    return dist


def streichen(s: np.ndarray, i: int) -> np.ndarray:
    v = s[:, i]
    q = np.delete(s, i, axis=1)
    return q - (q > v[:, None]).astype(np.int8)


def histogramm(dist: np.ndarray) -> list[int]:
    return [int((dist == j).sum()) for j in range(int(dist.max()) + 1)]


# --- die Tabellen ------------------------------------------------------------------------------------------------------------------------------

def erzeuge_aufzaehlung(n_max: int) -> tuple[dict, np.ndarray | None]:
    folgen = {n: alle_folgen(n) for n in range(1, n_max + 1)}
    dist: dict[str, dict[int, np.ndarray]] = {m: {} for m in MASCH}
    bild = []
    t0 = time.time()
    for n in range(1, n_max + 1):
        dist["pop"][n], nachf = dist_fest(folgen[n], pop_zeile)
        bild.append(int(len(np.unique(nachf))))
        dist["west"][n], _ = dist_fest(folgen[n], west_zeile)
        dist["frei"][n] = dist_frei(n) if n > 1 else np.zeros(1, dtype=np.int8)
        log(f"  Aufzählung n = {n} fertig ({time.time() - t0:.0f} s)")
    out: dict = {
        "verteilung": {m: {str(n): histogramm(dist[m][n]) for n in range(1, n_max + 1)} for m in MASCH},
        "bild": bild,
    }
    # Klasse-Test: Verletzung = Folge in „höchstens k Durchläufen“, bei der das Streichen eines Wagens eine Folge mit mehr als k Durchläufen ergibt
    verl = {m: {str(k): {} for k in (1, 2, 3)} for m in MASCH}
    zeugen = {m: {} for m in MASCH}
    for m in MASCH:
        for k in (1, 2, 3):
            for n in range(3, n_max + 1):
                s_ = folgen[n][dist[m][n] <= k]
                bad = np.zeros(len(s_), dtype=bool)
                erste_stelle = np.full(len(s_), -1, dtype=np.int64)
                for i in range(n):
                    q = streichen(s_, i)
                    schlecht = dist[m][n - 1][rang(q)] > k
                    neu = schlecht & ~bad
                    erste_stelle[neu] = i
                    bad |= schlecht
                verl[m][str(k)][str(n)] = int(bad.sum())
                if bad.any() and str(k) not in zeugen[m]:
                    j = int(np.flatnonzero(bad)[0])
                    i = int(erste_stelle[j])
                    q = streichen(s_[j:j + 1], i)[0]
                    zeugen[m][str(k)] = {
                        "n": n,
                        "p": [int(x) for x in s_[j]],
                        "stelle": i + 1,
                        "q": [int(x) for x in q],
                        "durchlaeufe_q": int(dist[m][n - 1][int(rang(q[None, :])[0])]),
                    }
    out["verletzungen"] = verl
    out["zeugen"] = zeugen
    nur = {}
    for k in (2, 3):
        nur[str(k)] = {}
        for n in range(4, n_max + 1):
            maske = (dist["frei"][n] <= k) & (dist["pop"][n] > k)
            zeilen = folgen[n][maske]
            nur[str(k)][str(n)] = {"anzahl": int(maske.sum()), "erste": [[int(x) for x in z] for z in zeilen[:5]]}
    out["nur_frei"] = nur
    frei9 = dist["frei"][9] if n_max >= 9 else None
    return out, frei9


def erzeuge_modell() -> dict:
    """Ankunftsmodell V: Verteilungen der Durchlaufzahlen, beide Ströme, n = 9 (mit FREI aus der Tabelle) und n = 10, 2 000 Folgen je Zelle."""
    res = {}
    for basis in C.STROM_SEEDS:
        res[str(basis)] = {}
        for n in (9, 10):
            res[str(basis)][str(n)] = {}
            for d in range(len(C.D_WERTE)):
                folgen = MOD.strom(n, d, basis, 2000)
                res[str(basis)][str(n)][str(d)] = MOD.histogramme(folgen, T.frei_n9 if n == 9 else None)
    return res


def begrenze(daten: dict, n_max: int) -> dict:
    """Die Teile der Tabellen, die zu n ≤ n_max gehören (für --check)."""
    def bis(d):
        return {k: v for k, v in d.items() if int(k) <= n_max}
    return {
        "verteilung": {m: bis(daten["verteilung"][m]) for m in MASCH},
        "bild": daten["bild"][:n_max],
        "verletzungen": {m: {k: bis(daten["verletzungen"][m][k]) for k in daten["verletzungen"][m]} for m in MASCH},
        "zeugen": daten["zeugen"],
        "nur_frei": {k: bis(daten["nur_frei"][k]) for k in daten["nur_frei"]},
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="n ≤ 8 neu rechnen und vergleichen, n = 9 über Prüfsumme; Ankunftsmodell neu rechnen")
    ap.add_argument("--full", action="store_true", help="wie --check, aber auch n = 9 neu rechnen")
    a = ap.parse_args()
    t0 = time.time()
    if not (a.check or a.full):
        log("Aufzählung aller n! Folgen bis n = 9 …")
        daten, frei9 = erzeuge_aufzaehlung(N_MAX)
        roh = frei9.astype(np.int8).tobytes()
        T.DATA.mkdir(exist_ok=True)
        T.FREI_N9.write_bytes(roh)
        daten["frei_n9_sha256"] = hashlib.sha256(roh).hexdigest()
        T.tabellen.cache_clear()
        T.frei_n9_bytes.cache_clear()
        # das Ankunftsmodell liest die Tabelle n = 9 (Datei liegt jetzt vor, die Prüfsumme muss in der Datei stehen)
        T.TABELLEN.write_text(json.dumps(daten, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        T.tabellen.cache_clear()
        log("Ankunftsmodell V (beide Ströme) …")
        daten["modell_v"] = erzeuge_modell()
        T.TABELLEN.write_text(json.dumps(daten, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        log(f"geschrieben: {T.TABELLEN.name} und {T.FREI_N9.name} ({time.time() - t0:.0f} s)")
        return 0
    fehler = 0
    gespeichert = T.tabellen()
    n_neu = N_MAX if a.full else 8
    neu, frei9 = erzeuge_aufzaehlung(n_neu)
    if begrenze(neu, n_neu) != begrenze(gespeichert, n_neu):
        fehler += 1
        log(f"FEHLER: Aufzählung bis n = {n_neu} weicht von {T.TABELLEN.name} ab")
    else:
        log(f"ok: Aufzählung bis n = {n_neu} neu gerechnet, exakt gleich")
    roh = T.FREI_N9.read_bytes()
    if hashlib.sha256(roh).hexdigest() != gespeichert["frei_n9_sha256"]:
        fehler += 1
        log("FEHLER: Prüfsumme von mdl_frei_n9.bin stimmt nicht")
    else:
        log("ok: Prüfsumme von mdl_frei_n9.bin")
    h9 = histogramm(np.frombuffer(roh, dtype=np.int8))
    if len(roh) != math.factorial(9) or h9 != gespeichert["verteilung"]["frei"]["9"]:
        fehler += 1
        log("FEHLER: mdl_frei_n9.bin passt nicht zur Verteilung für n = 9")
    else:
        log("ok: Verteilung der Byte-Tabelle gleich der gespeicherten Verteilung für n = 9")
    if a.full and not np.array_equal(frei9, np.frombuffer(roh, dtype=np.int8)):
        fehler += 1
        log("FEHLER: Byte-Tabelle n = 9 weicht von der Neuberechnung ab")
    for m in MASCH:
        if sum(gespeichert["verteilung"][m]["9"]) != math.factorial(9):
            fehler += 1
            log(f"FEHLER: Summe der Verteilung {m}, n = 9, ist nicht 9!")
    log("Ankunftsmodell V neu rechnen …")
    if erzeuge_modell() != gespeichert["modell_v"]:
        fehler += 1
        log("FEHLER: Ankunftsmodell weicht ab")
    else:
        log("ok: Ankunftsmodell (zwei Ströme, n = 9 und 10, sieben D) neu gerechnet, exakt gleich")
    log(f"{'FEHLER: ' + str(fehler) if fehler else 'alles ok'} ({time.time() - t0:.0f} s)")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
