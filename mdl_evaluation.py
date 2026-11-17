"""Auswertung: Einstellungen, Eingabeprüfung, die fünf Experimente und alle Verdikte als reine Funktionen.

Zähleinheit: Folgen (Permutationen der Ränge 1 … n, alle Wagen verschieden), beim Ankunftsmodell Zufallsfolgen. Zahlen über alle n! Folgen kommen aus den vorgerechneten
Tabellen (`mdl_tables.py`), einzelne Folgen werden live gerechnet (`mdl_machines.py`, `mdl_free.py`), das Ankunftsmodell live (`mdl_model.py`).
Jedes Verdikt der App ist eine Funktion `verdict_*(…) -> (Art, Text)` (Streamlit-Aufrufe `st.info` usw.), geprüft in tests/test_verdicts.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import factorial

import mdl_constants as C
import mdl_free as FR
import mdl_machines as M
import mdl_model as MOD
import mdl_tables as T
from mdl_rng import SplitMix64


# --- Formatierung (Dezimalkomma, Tausenderabstand, Minuszeichen) --------------------------------------------------------------------------------

def de(x: float, nd: int = 2) -> str:
    return f"{x:.{nd}f}".replace(".", ",").replace("-", "−")


def de_int(x: int) -> str:
    """147366 -> „147 366“."""
    return f"{abs(int(x)):,}".replace(",", " ") if x >= 0 else "−" + f"{abs(int(x)):,}".replace(",", " ")


def pct(x: float, nd: int | None = None) -> str:
    """Anteil 0–1 als Prozent mit Komma; ohne Angabe eine Stelle, unter 1 Prozent zwei Stellen."""
    if nd is None:
        nd = 2 if 0 < x < 0.01 else 1
    return de(100 * x, nd) + " %"


def folge_text(p) -> str:
    return "(" + ", ".join(str(x) for x in p) + ")"


def d_text(d_index: int) -> str:
    return C.D_LABEL[d_index]


# --- Einstellungen -----------------------------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Settings:
    folge: str = C.DEFAULT_FOLGE
    n1: int = C.DEFAULT_N1
    d_idx: int = C.DEFAULT_D_INDEX
    seed: int = C.DEFAULT_SEED
    n2: int = C.DEFAULT_N2
    k2: int = C.DEFAULT_K2
    n3: int = C.DEFAULT_N3
    m3: int = C.DEFAULT_M3
    n4: int = C.DEFAULT_N4
    k4: int = C.DEFAULT_K4
    m4: int = C.DEFAULT_M4
    n5: int = C.DEFAULT_N5
    nfolgen: int = C.DEFAULT_NFOLGEN


def maschine_von_index(i: int) -> str:
    return M.MASCHINEN[i]


# --- Eingabe -----------------------------------------------------------------------------------------------------------------------------------

def parse_folge(text: str):
    """Eingabe → (Folge, Fehlermeldung). Erlaubt: Zahlen getrennt durch Leerzeichen, Komma oder Semikolon; Klammern werden ignoriert."""
    roh = (text or "").replace("(", " ").replace(")", " ").replace(",", " ").replace(";", " ")
    teile = roh.split()
    if not teile:
        return None, "Bitte eine Folge eingeben, zum Beispiel „3 5 2 4 1“."
    try:
        p = tuple(int(t) for t in teile)
    except ValueError:
        return None, "Bitte nur ganze Zahlen eingeben, getrennt durch Leerzeichen oder Komma."
    n = len(p)
    if n > C.N_MAX:
        return None, f"Die Folge hat {n} Wagen; gemessen und gerechnet wird bis n = {C.N_MAX} (darüber ist die freie Durchlaufzahl nicht gemessen)."
    erwartet = set(range(1, n + 1))
    fehlt = sorted(erwartet - set(p))
    doppelt = sorted({x for x in p if p.count(x) > 1})
    if fehlt or doppelt:
        teile_fehler = []
        if doppelt:
            teile_fehler.append("doppelt: " + ", ".join(str(x) for x in doppelt))
        if fehlt:
            teile_fehler.append("fehlt: " + ", ".join(str(x) for x in fehlt))
        außerhalb = sorted(x for x in set(p) if x not in erwartet)
        if außerhalb:
            teile_fehler.append("außerhalb 1 … n: " + ", ".join(str(x) for x in außerhalb))
        return None, (f"Jeder Rang 1 … {n} muss genau einmal vorkommen ({'; '.join(teile_fehler)}). Gleichstände (gleiche Ränge) sind nicht erlaubt und hier nicht gemessen.")
    return p, None


# --- Experiment 1: eine Folge durch die Maschinen -----------------------------------------------------------------------------------------------

def spur_text(ereignisse) -> str:
    """Stapelspur als Text: „rein 3; raus 3, rein 5; … ; am Ende raus 1, 4“."""
    teile, raus = [], []
    for art, x in ereignisse:
        if art == "raus":
            raus.append(str(x))
        else:
            teile.append(("raus " + ", ".join(raus) + ", " if raus else "") + f"rein {x}")
            raus = []
    if raus:
        teile.append("am Ende raus " + ", ".join(raus))
    return "; ".join(teile)


def bloecke_text(p, bloecke) -> str:
    """„[3] [5 2] [4 1]“: die Blöcke der Folge, die der Durchlauf umkehrt."""
    teile, i = [], 0
    for b in bloecke:
        teile.append("[" + " ".join(str(x) for x in p[i:i + b]) + "]")
        i += b
    return " ".join(teile)


@dataclass
class FolgenErgebnis:
    fehler: str | None
    p: tuple = ()
    n: int = 0
    zahlen: dict | None = None            # Maschine → Durchlaufzahl
    verlauf: dict | None = None           # Maschine → Folge vor dem ersten und nach jedem Durchlauf
    beschreibung: dict | None = None      # Maschine → Text je Durchlauf (Blöcke bzw. Stapelspur)
    weg_frei: list | None = None          # eine gefundene Zerlegung je Durchlauf


def ziehe_folge(art: str, n1: int, d_idx: int, seed: int) -> tuple:
    """Ein Zug aus dem Zufall: art = "zufall" (alle n! Folgen gleich wahrscheinlich, Strom `seed`) oder "modell" (erste Folge des Stroms im Ankunftsmodell V für D Nr. `d_idx`, Strom `seed + d_idx`)."""
    n = max(C.N_MIN, min(C.N_MAX, int(n1)))
    if art == "zufall":
        items = list(range(1, n + 1))
        SplitMix64(seed).shuffle(items)
        return tuple(items)
    if art == "modell":
        return MOD.strom(n, d_idx, seed, 1)[0]
    raise ValueError("art muss \"zufall\" oder \"modell\" sein")


def analyse_folge(text: str) -> FolgenErgebnis:
    p, fehler = parse_folge(text)
    if fehler:
        return FolgenErgebnis(fehler=fehler)
    n = len(p)
    verlauf = {M.POP: M.verlauf(p, M.POP), M.WEST: M.verlauf(p, M.WEST)}
    zahl_frei, weg = FR.frei_durchlaufzahl(p, mit_weg=True)
    verlauf_frei = [p]
    for z in weg:
        verlauf_frei.append(FR.blockumkehr(verlauf_frei[-1], z))
    verlauf[M.FREI] = verlauf_frei
    beschreibung = {
        M.POP: [bloecke_text(q, M.pop_bloecke(q)) for q in verlauf[M.POP][:-1]],
        M.WEST: [spur_text(M.spur(q, M.WEST)) for q in verlauf[M.WEST][:-1]],
        M.FREI: [bloecke_text(q, z) for q, z in zip(verlauf_frei, weg)],
    }
    zahlen = {m: len(verlauf[m]) - 1 for m in M.MASCHINEN}
    return FolgenErgebnis(None, p, n, zahlen, verlauf, beschreibung, weg)


def ist_kleinster_hinten(p) -> bool:
    n = len(p)
    return n >= 3 and tuple(p) == tuple(range(2, n + 1)) + (1,)


def verdict_folge(p, zahlen: dict) -> tuple[str, str]:
    """Verdikt zu einer Folge: Durchlaufzahl der drei Maschinen nebeneinander."""
    n = len(p)
    if M.ist_sortiert(p):
        return "info", f"{folge_text(p)} ist schon sortiert: alle drei Maschinen brauchen 0 Durchläufe."
    text = (f"{folge_text(p)}: gieriger Stapel {zahlen[M.WEST]} Durchläufe, Pop-Stack mit festem Rezept {zahlen[M.POP]}, mit freier Leerung {zahlen[M.FREI]}.")
    if n >= 3 and zahlen[M.POP] == n - 1:
        text += f" Der feste Pop-Stack braucht hier {n - 1} = n − 1 Durchläufe, die größte Zahl, die er bei {n} Wagen braucht (Aufzählung n ≤ 9 in der README)."
    if n >= 3 and zahlen[M.WEST] == n - 1:
        text += f" Der gierige Stapel braucht ebenfalls n − 1 = {n - 1}."
    if ist_kleinster_hinten(p):
        text += " Der kleinste Wagen steht hinten: bei den festen Rezepten rückt er je Durchlauf nur eine Stelle vor, mit freier Leerung genügen 2 Durchläufe."
    if zahlen[M.FREI] < zahlen[M.POP]:
        gespart = zahlen[M.POP] - zahlen[M.FREI]
        text += f" Die freie Leerung spart gegen das feste Rezept {gespart} {'Durchlauf' if gespart == 1 else 'Durchläufe'}."
    return "info", text


# --- Experiment 2: wie viele Folgen schaffen k Durchläufe? --------------------------------------------------------------------------------------

@dataclass
class Zaehlung:
    n: int
    k: int
    gesamt: int
    anzahl: dict      # Maschine → Folgen in höchstens k Durchläufen
    anteil: dict      # Maschine → Anteil an allen n! Folgen


def analyse_zaehlung(n: int, k: int) -> Zaehlung:
    anzahl = {m: T.kumuliert(m, n, k) for m in M.MASCHINEN}
    gesamt = factorial(n)
    return Zaehlung(n, k, gesamt, anzahl, {m: anzahl[m] / gesamt for m in M.MASCHINEN})


def catalan(n: int) -> int:
    from math import comb
    return comb(2 * n, n) // (n + 1)


def kippt_bei_k2() -> dict:
    """Für k = 2: n, bei denen frei mehr Folgen schafft als der gierige Stapel, gleich viele, weniger (aus den Tabellen, n = 3 … 9)."""
    vorn, gleich, hinten = [], [], []
    for n in range(C.N_MIN, C.N_MAX + 1):
        f, w = T.kumuliert(M.FREI, n, 2), T.kumuliert(M.WEST, n, 2)
        (vorn if f > w else gleich if f == w else hinten).append(n)
    return {"frei_vorn": vorn, "gleich": gleich, "frei_hinten": hinten}


def verdict_zaehlung(z: Zaehlung) -> tuple[str, str]:
    n, k = z.n, z.k
    teile = [
        f"{M.NAME[m]} {de_int(z.anzahl[m])} ({pct(z.anteil[m])})" for m in (M.POP, M.WEST, M.FREI)
    ]
    text = f"n = {n}, höchstens {k} {'Durchlauf' if k == 1 else 'Durchläufe'}: " + ", ".join(teile) + f" von {de_int(z.gesamt)} Folgen."
    if k == 1:
        text += (f" Ein Durchlauf: fest und frei schaffen dieselbe Zahl, 2^(n − 1) = {de_int(2 ** (n - 1))}; der gierige Stapel Catalan({n}) = {de_int(catalan(n))}.")
    if k == 2:
        ks = kippt_bei_k2()
        if ks["frei_vorn"] and ks["frei_hinten"]:
            v, h = ks["frei_vorn"], ks["frei_hinten"]
            text += (f" Bei k = 2 schafft die freie Leerung für n = {v[0]} bis {v[-1]} mehr Folgen als der gierige Stapel und für n = {h[0]} bis {h[-1]} weniger "
                     f"(n = {h[0]}: {de_int(T.kumuliert(M.FREI, h[0], 2))} gegen {de_int(T.kumuliert(M.WEST, h[0], 2))}); bei n = {ks['gleich'][0]} sind es gleich viele.")
    return "info", text


# --- Experiment 3: schlimmster Fall und Mittel --------------------------------------------------------------------------------------------------

@dataclass
class Verteilung:
    n: int
    daten: dict       # Maschine → {"verteilung", "mittel" (Fraction), "maximum", "am_maximum"}


def analyse_verteilung(n: int) -> Verteilung:
    daten = {}
    for m in M.MASCHINEN:
        daten[m] = {"verteilung": T.verteilung(m, n), "mittel": T.mittel(m, n), "maximum": T.maximum(m, n), "am_maximum": T.am_maximum(m, n)}
    return Verteilung(n, daten)


def kleinster_hinten_verlauf(n: int, maschine: str):
    """Die Folge (2, …, n, 1) mit Verlauf: (Folge, Verlauf, Durchlaufzahl, Beschreibung je Durchlauf)."""
    p = tuple(range(2, n + 1)) + (1,)
    if maschine == M.FREI:
        d, weg = FR.frei_durchlaufzahl(p, mit_weg=True)
        v = [p]
        for z in weg:
            v.append(FR.blockumkehr(v[-1], z))
        beschr = [bloecke_text(q, z) for q, z in zip(v, weg)]
        return p, v, d, beschr
    v = M.verlauf(p, maschine)
    if maschine == M.POP:
        beschr = [bloecke_text(q, M.pop_bloecke(q)) for q in v[:-1]]
    else:
        beschr = [spur_text(M.spur(q, M.WEST)) for q in v[:-1]]
    return p, v, len(v) - 1, beschr


def verdict_verteilung(v: Verteilung) -> tuple[str, str]:
    n = v.n
    d = v.daten
    gesamt = factorial(n)

    def teil(m, name):
        x = d[m]
        s = f"{name} im Mittel {de(float(x['mittel']), 2)} Durchläufe, Maximum {x['maximum']}"
        if x["maximum"] == n - 1:
            s += " (= n − 1)"
        s += f" bei {de_int(x['am_maximum'])}"
        if m == M.WEST and x["am_maximum"] == factorial(n - 2):
            s += f" = {n - 2}!"
        return s + " Folgen"

    text = (f"n = {n}, alle {de_int(gesamt)} Folgen gleich gewichtet: " + teil(M.POP, "Pop-Stack mit festem Rezept") + "; " + teil(M.WEST, "gieriger Stapel") + "; "
            + teil(M.FREI, "freie Leerung") + ".")
    text += (f" Die Obergrenze n − 1 ist für den gierigen Stapel bewiesen (der größte Wagen steht nach einem Durchlauf hinten, Beweisskizze in der README) und für den festen Pop-Stack in der Aufzählung n ≤ 9 gemessen und erreicht; "
             f"frei sind es bei n ≤ 9 höchstens {max(T.maximum(M.FREI, k) for k in range(C.N_MIN, C.N_MAX + 1))}.")
    return "info", text


# --- Experiment 4: zwei Rezepte, zwei Antworten (die Falle) --------------------------------------------------------------------------------------

@dataclass
class Klassentest:
    n: int
    k: int
    maschine: str
    nur_frei: dict               # {"anzahl", "erste"}
    kleinste_nur_frei: tuple | None
    kleinste_nur_frei_fest: int | None    # feste Durchlaufzahl der kleinsten nur frei sortierbaren Folge
    zeile: list                  # je n: (n, Folgen in höchstens k, betroffene Folgen)
    zeuge: dict | None
    zeuge_verlauf: list | None   # Verlauf des Zeugen p (feste Maschine)
    zeuge_q_verlauf: list | None
    bild: int
    urbild: int


def analyse_klassentest(n: int, k: int, maschine: str) -> Klassentest:
    nf = T.nur_frei(k, n)
    kleinste = nf["erste"][0] if nf["erste"] else None
    fest = M.durchlaufzahl(kleinste, M.POP) if kleinste else None
    zeile = [(m, T.kumuliert(maschine, m, k), T.verletzungen(maschine, k, m)) for m in range(C.N_MIN, C.N_MAX + 1)]
    z = T.zeuge(maschine, k)
    zv = zq = None
    if z is not None and maschine != M.FREI:
        zv = M.verlauf(z["p"], maschine)
        zq = M.verlauf(z["q"], maschine)
    return Klassentest(n, k, maschine, nf, kleinste, fest, zeile, z, zv, zq, T.bild(n), 2 ** (n - 1))


def verdict_klasse(t: Klassentest) -> tuple[str, str]:
    n, k = t.n, t.k
    a, b = T.kumuliert(M.POP, n, k), T.kumuliert(M.FREI, n, k)
    text = f"n = {n}, höchstens {k} Durchläufe: Pop-Stack fest {de_int(a)} Folgen, frei {de_int(b)} von {de_int(factorial(n))}."
    if t.nur_frei["anzahl"]:
        text += (f" {de_int(t.nur_frei['anzahl'])} Folgen gehen nur frei, die kleinste {folge_text(t.kleinste_nur_frei)} braucht fest {t.kleinste_nur_frei_fest} Durchläufe "
                 f"(kleinste in lexikographischer Reihenfolge).")
    else:
        text += " Hier gibt es keine Folge, die nur frei in höchstens so vielen Durchläufen geht."
    ns = f"n = {C.N_MIN} bis {C.N_MAX}"
    if t.maschine == M.FREI:
        text += (f" Bei freier Leerung bleibt „höchstens {k} Durchläufe“ beim Streichen eines Wagens erhalten: 0 betroffene Folgen für {ns} (Aufzählung; für Blockumkehrungen gilt es allgemein, Beweis in der README).")
    else:
        z = t.zeuge
        name = M.NAME[t.maschine]
        betroffen = T.verletzungen(t.maschine, k, n)
        text += (f" {name}: „höchstens {k} Durchläufe“ ist keine Klasse. Zeuge: {folge_text(z['p'])} geht in {k}, ohne den Wagen an Stelle {z['stelle']} bleibt {folge_text(z['q'])} "
                 f"mit {z['durchlaeufe_q']} Durchläufen; bei n = {n} sind {de_int(betroffen)} Folgen betroffen.")
    text += (f" Zum Bild gegen das Urbild: ein fester Pop-Durchlauf liefert bei n = {n} {de_int(t.bild)} verschiedene Ausgaben, aber nur {de_int(t.urbild)} Folgen sind in einem Durchlauf sortierbar.")
    return "warning" if t.maschine != M.FREI else "info", text


# --- Experiment 5: Ankunftsmodell --------------------------------------------------------------------------------------------------------------

@dataclass
class ModellErgebnis:
    n: int
    d_idx: int
    nfolgen: int
    seed: int
    kennzahlen: dict          # Maschine → Kennzahlen (mittel, se, anteil)
    verteilung: dict          # Maschine → Histogramm


def analyse_modell(n: int, d_idx: int, nfolgen: int, seed: int) -> ModellErgebnis:
    folgen = MOD.strom(n, d_idx, seed, nfolgen)
    hist = MOD.histogramme(folgen, T.frei_n9 if n == 9 else None)
    return ModellErgebnis(n, d_idx, nfolgen, seed, {m: MOD.kennzahlen(h) for m, h in hist.items()}, hist)


def vorgerechnet(n: int) -> dict:
    """Die vorgerechneten Zellen für n: {Strom: {d_index: {Maschine: Kennzahlen}}}."""
    res = {}
    for strom in C.STROM_SEEDS:
        res[strom] = {}
        for d in range(len(C.D_WERTE)):
            res[strom][d] = {m: MOD.kennzahlen(h) for m, h in T.modell_v(strom, n, d).items()}
    return res


def zellen_west_besser() -> tuple[int, int]:
    """(Zahl der Zellen, in denen der gierige Stapel weniger mittlere Durchläufe braucht als der feste Pop-Stack, Zahl aller Zellen): n ∈ {9, 10}, 7 D-Werte, 2 Ströme."""
    besser = gesamt = 0
    for n in C.N5_WERTE:
        for strom_zellen in vorgerechnet(n).values():
            for zelle in strom_zellen.values():
                gesamt += 1
                besser += zelle[M.WEST]["mittel"] < zelle[M.POP]["mittel"]
    return besser, gesamt


def frei_gegen_west_n9() -> dict:
    """Für n = 9: je D-Index die Unterschiede „Mittel des gierigen Stapels minus Mittel von FREI“ in den beiden Strömen (positiv: FREI braucht weniger)."""
    v = vorgerechnet(9)
    return {d: tuple(v[s][d][M.WEST]["mittel"] - v[s][d][M.FREI]["mittel"] for s in C.STROM_SEEDS) for d in range(len(C.D_WERTE))}


def verdict_modell(r: ModellErgebnis, besser: tuple[int, int], vergleich9: dict | None) -> tuple[str, str]:
    k = r.kennzahlen
    d = d_text(r.d_idx)
    text = (f"Im Modell V (ausgedacht), n = {r.n}, D = {d}, {de_int(r.nfolgen)} Folgen (Zufalls-Seed {r.seed} + {r.d_idx}): Pop-Stack mit festem Rezept im Mittel "
            f"{de(k[M.POP]['mittel'], 2)} Durchläufe (± {de(k[M.POP]['se'], 2)}), gieriger Stapel {de(k[M.WEST]['mittel'], 2)} (± {de(k[M.WEST]['se'], 2)})")
    if M.FREI in k:
        text += f", freie Leerung {de(k[M.FREI]['mittel'], 2)} (± {de(k[M.FREI]['se'], 2)})"
    text += (f"; in Klammern der Standardfehler des Mittels. Ein Durchlauf genügt dem Pop-Stack bei {pct(k[M.POP]['anteil'][1])} der Züge, dem gierigen Stapel bei {pct(k[M.WEST]['anteil'][1])}.")
    text += (f" In den vorgerechneten Strömen (2 000 Folgen, Zufalls-Seed 12000 und 13000, n = 9 und 10, sieben Werte von D) braucht der gierige Stapel in {besser[0]} von {besser[1]} Zellen weniger "
             f"mittlere Durchläufe als der Pop-Stack.")
    if vergleich9:
        frei_kleiner = [d_text(i) for i, (a, b) in vergleich9.items() if a > 0 and b > 0]
        west_kleiner = [d_text(i) for i, (a, b) in vergleich9.items() if a < 0 and b < 0]
        gemischt = [i for i, (a, b) in vergleich9.items() if a * b <= 0]
        text += (f" Bei n = 9 braucht der gierige Stapel in beiden Strömen weniger als die freie Leerung bei D = {', '.join(west_kleiner)}, die freie Leerung weniger bei D = {', '.join(frei_kleiner)}")
        if gemischt:
            groesst = max(abs(x) for i in gemischt for x in vergleich9[i])
            text += f"; bei D = {', '.join(d_text(i) for i in gemischt)} wechselt das Vorzeichen zwischen den Strömen (Unterschied höchstens {de(groesst, 2)})"
        text += "."
    return "info", text
