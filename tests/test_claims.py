"""Claims-Tests: jede Zahl der Befunde B1 bis B14 der README mit ihren Voraussetzungen (DEMO-PLAYBOOK §4, §11a).

Voraussetzung überall: alle Wagen verschieden, Zähleinheit Folgen (Aufzählung aller n! Anordnungen) bzw. Zufallsfolgen (Ankunftsmodell).
Plattform: Zählungen und Verteilungen sind Ganzzahlen und stehen exakt im Test; Mittelwerte aus Ganzzahlen werden auf die in der README genannten Stellen verglichen.
Das Ankunftsmodell rechnet über `exact_log` bitgleich auf jeder Plattform; die zwei Ströme gelten als Band (größter Unterschied der Mittel 0,103, der Anteile 3,65 Prozentpunkte).
Jede README-Zahl wird hier gerechnet **und** im README-Text gesucht (`_readme_has`)."""

import re
from fractions import Fraction as Fr
from math import comb, factorial
from pathlib import Path

import pytest

import mdl_constants as C
import mdl_evaluation as ev
import mdl_free as F
import mdl_machines as M
import mdl_model as MOD
import mdl_tables as T
import mdl_texts as X
from conftest import alle_folgen

ROOT = Path(__file__).resolve().parent.parent
README = re.sub(r"\s+", " ", (ROOT / "README.md").read_text(encoding="utf-8").replace("\\|", "|").replace("\\*", "*"))


def _readme_has(*items):
    for n in items:
        assert re.sub(r"\s+", " ", n) in README, n


def zahl(x: int) -> str:
    return ev.de_int(x)


def reihe(werte) -> str:
    return ", ".join(zahl(w) for w in werte)


# --- B1 ---------------------------------------------------------------------------------------------------------------------------------------

def test_b1_zwei_durchlaeufe_n5_und_n9():
    assert [T.kumuliert(m, 5, 2) for m in ("pop", "west", "frei")] == [42, 91, 102]
    assert [ev.pct(T.kumuliert(m, 5, 2) / 120) for m in ("pop", "west", "frei")] == ["35,0 %", "75,8 %", "85,0 %"]
    assert [T.kumuliert(m, 9, 2) for m in ("pop", "west", "frei")] == [2106, 49335, 22102]
    assert [ev.pct(T.kumuliert(m, 9, 2) / 362880) for m in ("pop", "west", "frei")] == ["0,58 %", "13,6 %", "6,1 %"]
    assert T.verteilung("pop", 5) == [1, 15, 26, 46, 32] and T.verteilung("west", 5) == [1, 41, 49, 23, 6] and T.verteilung("frei", 5) == [1, 15, 86, 18]
    _readme_has("42 von 120 Folgen", "gierige Stapel 91", "freie Leerung 102 (85,0 %)", "42 (35,0 %), gieriger Stapel 91 (75,8 %)", "2 106 (0,58 %), 49 335 (13,6 %), 22 102 (6,1 %)",
                "fest 1, 15, 26, 46, 32; gieriger Stapel 1, 41, 49, 23, 6; frei 1, 15, 86, 18", "2 106, 49 335 und 22 102 von 362 880")


# --- B2 ---------------------------------------------------------------------------------------------------------------------------------------

def test_b2_ein_durchlauf():
    for n in range(1, 10):
        assert T.kumuliert("pop", n, 1) == 2 ** (n - 1) == T.kumuliert("frei", n, 1)
        assert T.kumuliert("west", n, 1) == comb(2 * n, n) // (n + 1)
    for n in range(1, 8):      # dieselbe Menge: genau die Blockumkehrungen der sortierten Folge
        ident = tuple(range(1, n + 1))
        pop = {p for p in alle_folgen(n) if M.durchlaufzahl(p, M.POP) <= 1}
        assert pop == {F.blockumkehr(ident, z) for z in F.zerlegungen(n)} == {p for p in alle_folgen(n) if F.frei_durchlaufzahl(p) <= 1}
    assert [ev.pct(T.kumuliert("pop", n, 1) / factorial(n)) for n in (5, 6, 9)] == ["13,3 %", "4,4 %", "0,07 %"]
    assert [ev.pct(T.kumuliert("west", n, 1) / factorial(n)) for n in (5, 6, 9)] == ["35,0 %", "18,3 %", "1,3 %"]
    _readme_has("fest 13,3 % (n = 5), 4,4 % (n = 6), 0,07 % (n = 9); gieriger Stapel 35,0 %, 18,3 %, 1,3 %", "fest und frei je 2^(n−1) Folgen")


# --- B3 ---------------------------------------------------------------------------------------------------------------------------------------

def test_b3_die_reihenfolge_kippt():
    f = {n: T.kumuliert("frei", n, 2) for n in range(3, 10)}
    w = {n: T.kumuliert("west", n, 2) for n in range(3, 10)}
    assert [n for n in f if f[n] > w[n]] == [4, 5, 6] and [n for n in f if f[n] == w[n]] == [3] and [n for n in f if f[n] < w[n]] == [7, 8, 9]
    assert [(f[n], w[n]) for n in (4, 5, 6)] == [(24, 22), (102, 91), (414, 408)] and (f[3], w[3]) == (6, 6)
    assert [(f[n], w[n]) for n in (7, 8, 9)] == [(1598, 1938), (5982, 9614), (22102, 49335)]
    _readme_has("frei schafft mehr bei n = 4, 5, 6 (24 gegen 22, 102 gegen 91, 414 gegen 408), gleich viele bei n = 3 (6), weniger bei n = 7, 8, 9 (1 598 gegen 1 938, 5 982 gegen 9 614, 22 102 gegen 49 335)")


# --- B4 ---------------------------------------------------------------------------------------------------------------------------------------

def test_b4_groesste_durchlaufzahl():
    assert all(T.maximum("pop", n) == n - 1 == T.maximum("west", n) for n in range(2, 10))
    assert [T.am_maximum("pop", n) for n in range(2, 10)] == [1, 2, 8, 32, 155, 830, 5106, 35346]
    assert [T.am_maximum("west", n) for n in range(3, 10)] == [factorial(n - 2) for n in range(3, 10)] == [1, 2, 6, 24, 120, 720, 5040]
    assert [T.maximum("frei", n) for n in range(2, 10)] == [1, 2, 2, 3, 3, 4, 4, 4]
    assert [T.am_maximum("frei", n) for n in range(2, 10)] == [1, 2, 16, 18, 306, 50, 2952, 81030]
    assert all(T.maximum("frei", n) == -(-n // 2) for n in range(2, 9)) and T.maximum("frei", 9) == 4 != -(-9 // 2)
    assert T.am_maximum("pop", 9) == 35346 and T.am_maximum("west", 9) == 5040
    _readme_has("fest 1, 2, 8, 32, 155, 830, 5 106, 35 346", "gieriger Stapel genau (n − 2)! = 1, 2, 6, 24, 120, 720, 5 040 (n = 3 … 9)", "Maximum 1, 2, 2, 3, 3, 4, 4, 4 bei 1, 2, 16, 18, 306, 50, 2 952, 81 030 Folgen (n = 2 … 9; höchstens 4 für n ≤ 9)",
                "gilt bis n = 8 und ist bei n = 9 falsch (4 statt 5)", "35 346 Folgen beim Pop-Stack, 5 040 beim gierigen Stapel")


def test_b4_zaehlreihen_tabelle():
    for n in range(4, 10):
        zeile = [n, factorial(n)] + [T.kumuliert("pop", n, k) for k in (1, 2, 3, 4)] + [T.kumuliert("west", n, k) for k in (1, 2, 3)] + [T.kumuliert("frei", n, k) for k in (1, 2, 3)]
        _readme_has("| " + " | ".join(zahl(x) for x in zeile) + " |")
    _readme_has("1, 2, 6, 24, 102, 414, 1 598, 5 982, 22 102")
    assert [T.kumuliert("frei", n, 2) for n in range(1, 10)] == [1, 2, 6, 24, 102, 414, 1598, 5982, 22102]


# --- B5 ---------------------------------------------------------------------------------------------------------------------------------------

def test_b5_kleinster_wagen_hinten():
    for n in range(3, 10):
        p = tuple(range(2, n + 1)) + (1,)
        assert M.durchlaufzahl(p, M.POP) == n - 1 == M.durchlaufzahl(p, M.WEST) and F.frei_durchlaufzahl(p) == 2
    v = M.verlauf((2, 3, 4, 5, 1), M.POP)
    assert [q.index(1) for q in v] == [4, 3, 2, 1, 0]            # der Wagen 1 rückt je Durchlauf eine Stelle vor
    v = M.verlauf((2, 3, 4, 5, 1), M.WEST)
    assert [q.index(1) for q in v] == [4, 3, 2, 1, 0]
    _readme_has("n = 3 … 9: fest und gieriger Stapel genau n − 1 Durchläufe (der Wagen 1 rückt je Durchlauf eine Stelle vor), frei 2")


# --- B6 ---------------------------------------------------------------------------------------------------------------------------------------

def test_b6_mittel_modell_u():
    assert [ev.de(float(T.mittel(m, 5)), 3) for m in ("pop", "west", "frei")] == ["2,775", "1,933", "2,008"]
    assert [ev.de(float(T.mittel(m, 9)), 4) for m in ("pop", "west", "frei")] == ["5,9803", "4,0925", "3,1617"]
    assert [T.mittel(m, 4) for m in ("pop", "west", "frei")] == [Fr(47, 24), Fr(35, 24), Fr(13, 8)]
    _readme_has("n = 5: 2,775 / 1,933 / 2,008", "n = 9: 5,9803 / 4,0925 / 3,1617", "n = 4 als Brüche 47/24, 35/24, 13/8")


# --- B7 ---------------------------------------------------------------------------------------------------------------------------------------

def test_b7_frei_enthaelt_fest_und_nur_frei():
    assert [T.nur_frei(2, n)["anzahl"] for n in range(4, 10)] == [8, 60, 302, 1300, 5190, 19996]
    assert all(T.nur_frei(2, n)["anzahl"] == T.kumuliert("frei", n, 2) - T.kumuliert("pop", n, 2) for n in range(4, 10))     # FREI enthält POP: die Differenz der Zählungen ist die Zahl der Folgen nur frei
    p = T.nur_frei(2, 5)["erste"][0]
    assert p == (1, 3, 4, 5, 2) and M.durchlaufzahl(p, M.POP) == 3 and F.frei_durchlaufzahl(p) == 2
    _readme_has("8, 60, 302, 1 300, 5 190, 19 996 (n = 4 … 9)", "(1, 3, 4, 5, 2) und braucht fest 3 Durchläufe")


@pytest.mark.slow
def test_b7_frei_nie_schlechter_als_fest_n8_und_n9():
    pytest.importorskip("numpy")
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    import mdl_make_tables as G
    for n in (8, 9):
        folgen = G.alle_folgen(n)
        fest, _ = G.dist_fest(folgen, G.pop_zeile)
        assert (G.dist_frei(n) <= fest).all()


# --- B8 ---------------------------------------------------------------------------------------------------------------------------------------

def test_b8_keine_klasse():
    assert M.durchlaufzahl((4, 1, 3, 5, 2), M.POP) == 2 and M.durchlaufzahl(M.streiche((4, 1, 3, 5, 2), 1), M.POP) == 3
    assert M.durchlaufzahl((3, 5, 2, 4, 1), M.WEST) == 2 and M.durchlaufzahl((3, 5, 2, 4, 1), M.POP) == 4 and M.durchlaufzahl(M.streiche((3, 5, 2, 4, 1), 1), M.WEST) == 3
    assert [T.verletzungen("pop", 2, n) for n in range(5, 10)] == [1, 6, 22, 73, 235]
    assert [T.verletzungen("west", 2, n) for n in range(5, 10)] == [1, 13, 116, 892, 6364]
    assert [T.verletzungen("pop", 3, n) for n in range(5, 10)] == [0, 8, 60, 299, 1308]
    assert [T.verletzungen("west", 3, n) for n in range(5, 10)] == [0, 6, 112, 1390, 14604]
    assert all(T.verletzungen(m, 1, n) == 0 for m in ("pop", "west", "frei") for n in range(3, 10))
    assert all(T.verletzungen("frei", k, n) == 0 for k in (1, 2, 3) for n in range(3, 10))
    assert T.zeuge("pop", 2)["p"] == (4, 1, 3, 5, 2) and T.zeuge("west", 2)["p"] == (3, 5, 2, 4, 1)
    assert T.zeuge("pop", 3)["p"] == (3, 5, 1, 4, 6, 2) and T.zeuge("west", 3)["p"] == (2, 4, 6, 3, 5, 1)
    _readme_has("fest 1, 6, 22, 73, 235; gieriger Stapel 1, 13, 116, 892, 6 364", "fest 0, 8, 60, 299, 1 308; gieriger Stapel 0, 6, 112, 1 390, 14 604", "0 betroffene Folgen für k = 1, 2, 3 und n = 3 … 9",
                "(4, 1, 3, 5, 2) geht beim Pop-Stack in 2 Durchläufen, ohne den Wagen 1 bleibt (3, 2, 4, 1) mit 3", "(3, 5, 2, 4, 1) geht beim gierigen Stapel in 2, ohne den Wagen 1 bleibt (3, 2, 4, 1) mit 3",
                "der feste Pop-Stack braucht dafür 4 Durchläufe", "(3, 1, 2) wird zu (1, 3, 2)")
    assert M.pop_durchlauf((3, 1, 2)) == (1, 3, 2)


# --- B9 ---------------------------------------------------------------------------------------------------------------------------------------

def test_b9_west2_und_pop_eins_als_muster():
    from test_oracle_mehrere_durchlaeufe import enthaelt, west2_laut_muster
    for n in range(4, 8):
        assert {p for p in alle_folgen(n) if M.durchlaufzahl(p, M.WEST) <= 2} == {p for p in alle_folgen(n) if west2_laut_muster(p)}
        assert {p for p in alle_folgen(n) if M.durchlaufzahl(p, M.POP) <= 1} == {p for p in alle_folgen(n) if not enthaelt(p, (2, 3, 1)) and not enthaelt(p, (3, 1, 2))}
    assert T.kumuliert("west", 8, 2) == 9614
    _readme_has("Av(2341, 3\\bar{5}241), n = 4 … 8 (9 614 Folgen bei n = 8)", "genau Av(231, 312) (n ≤ 7 als Menge)")


# --- B10 --------------------------------------------------------------------------------------------------------------------------------------

def test_b10_bild_gegen_urbild():
    assert [T.bild(n) for n in range(1, 10)] == [1, 1, 3, 11, 49, 263, 1653, 11877, 95991]
    assert T.bild(7) == 1653 and 2 ** 6 == 64
    for n in range(1, 8):
        assert len({M.pop_durchlauf(p) for p in alle_folgen(n)}) == T.bild(n)
    _readme_has("1, 1, 3, 11, 49, 263, 1 653, 11 877, 95 991 verschiedene Ausgaben (n = 1 … 9)", "bei n = 7 sind es 1 653 gegen 64")


# --- B11 bis B13: Ankunftsmodell ---------------------------------------------------------------------------------------------------------------

def test_b11_modell_n10_d4():
    kz = {s: {m: MOD.kennzahlen(h) for m, h in T.modell_v(s, 10, 3).items()} for s in C.STROM_SEEDS}
    assert [ev.de(kz[s]["pop"]["mittel"], 2) for s in C.STROM_SEEDS] == ["4,27", "4,34"]
    assert [ev.de(kz[s]["west"]["mittel"], 2) for s in C.STROM_SEEDS] == ["2,25", "2,24"]
    assert [ev.pct(kz[s]["pop"]["anteil"][1]) for s in C.STROM_SEEDS] == ["2,5 %", "3,5 %"]
    assert [ev.pct(kz[s]["west"]["anteil"][1]) for s in C.STROM_SEEDS] == ["20,0 %", "21,4 %"]
    assert ev.zellen_west_besser() == (28, 28)
    # Band über die beiden Ströme: größter Unterschied der Mittelwerte und der Anteile über alle 28 Zellen
    gm = ga = 0.0
    for n in C.N5_WERTE:
        v = ev.vorgerechnet(n)
        for d in range(len(C.D_WERTE)):
            for m in v[12000][d]:
                a, b = v[12000][d][m], v[13000][d][m]
                gm = max(gm, abs(a["mittel"] - b["mittel"]))
                ga = max(ga, max(abs(a["anteil"][k] - b["anteil"][k]) for k in (1, 2, 3)))
    assert round(gm, 3) == 0.103 and round(100 * ga, 2) == 3.65, (gm, ga)
    _readme_has("4,27 / 4,34 Durchläufe, gieriger Stapel 2,25 / 2,24", "2,5 % / 3,5 % der Züge, dem gierigen Stapel bei 20,0 % / 21,4 %", "in **28 von 28 Zellen**", "um höchstens 0,103, bei den Anteilen um bis zu 3,65 Prozentpunkte")


def test_b11_modell_wird_im_bau_neu_gerechnet():
    """Die zwei Zellen aus B11 neu gerechnet (nicht nur aus der Datei gelesen)."""
    for strom in C.STROM_SEEDS:
        h = MOD.histogramme(MOD.strom(10, 3, strom, 2000))
        assert h == {m: T.modell_v(strom, 10, 3)[m] for m in ("pop", "west")}


def test_b12_modell_n9_frei_gegen_gierig_und_gegenprobe():
    v = ev.frei_gegen_west_n9()
    assert all(a < 0 and b < 0 for d, (a, b) in v.items() if d <= 3)               # D = 0,5; 1; 2; 4: der gierige Stapel braucht in beiden Strömen weniger
    assert v[4][0] < 0 < v[4][1] and max(abs(x) for x in v[4]) <= 0.02 + 1e-9       # D = 8: Vorzeichen wechselt
    assert all(a > 0 and b > 0 for d, (a, b) in v.items() if d >= 5)               # D = 16 und ∞
    k = {m: MOD.kennzahlen(h) for m, h in T.modell_v(12000, 9, 6).items()}
    assert [ev.de(k[m]["mittel"], 2) for m in ("pop", "west", "frei")] == ["5,98", "4,09", "3,16"]
    for m in ("pop", "west", "frei"):
        assert abs(k[m]["mittel"] - float(T.mittel(m, 9))) <= 4 * k[m]["se"]
    _readme_has("bei D = 0,5; 1; 2; 4 in beiden Strömen", "bei D = 8 wechselt das Vorzeichen (Unterschied höchstens 0,02)", "bei D = 16 und ∞", "(5,98 / 4,09 / 3,16 im Strom 12000) in 4 Standardfehlern")


# --- B13 --------------------------------------------------------------------------------------------------------------------------------------

def test_b13_treffen_in_der_mitte():
    from test_oracle_mehrere_durchlaeufe import breitensuche_rueckwaerts
    gesamt = 0
    for n in (5, 6, 7):
        dist = breitensuche_rueckwaerts(n)
        assert all(F.frei_durchlaufzahl(p) == dist[p] for p in dist)
        gesamt += len(dist)
    assert gesamt == 5880 == 120 + 720 + 5040
    _readme_has("alle 5 880 Folgen mit n = 5, 6, 7 (120 + 720 + 5 040)", "je 300 Zufallsfolgen mit n = 8 und n = 9 (Zufalls-Seed 7777)")


# --- B14 --------------------------------------------------------------------------------------------------------------------------------------

def test_b14_literatur_zahlengleichheit():
    from test_oracle_mehrere_durchlaeufe import A134664, A224232, A293774, A293775
    for n in range(1, 10):
        assert T.kumuliert("pop", n, 2) == A224232[n - 1] and T.kumuliert("pop", n, 3) == A293774[n - 1] and T.kumuliert("pop", n, 4) == A293775[n - 1] and T.kumuliert("west", n, 3) == A134664[n - 1]
        assert T.kumuliert("west", n, 2) == 2 * factorial(3 * n) // (factorial(n + 1) * factorial(2 * n + 1))
    a = [1] + [T.kumuliert("pop", n, 2) for n in range(1, 10)]
    assert all(a[n] == 2 * (a[n - 1] + a[n - 3]) + a[n - 2] for n in range(4, 10))
    _readme_has("A224232, A293774, A293775 und A134664", "2(3n)!/((n+1)!(2n+1)!)", "a(n) = 2(a(n−1) + a(n−3)) + a(n−2)")


# --- Texte der App und der README -------------------------------------------------------------------------------------------------------------

def test_zahlen_der_einleitung_und_der_annahmen():
    assert (T.kumuliert("pop", 5, 2), T.kumuliert("west", 5, 2), T.kumuliert("frei", 5, 2)) == (42, 91, 102)
    assert "**42, 91 und 102** von 120 Folgen" in X.EINLEITUNG
    assert T.kumuliert("west", 4, 2) == 22 and factorial(4) == 24 and "22 von 24 Folgen" in X.GRENZEN


def test_planungswoerter_kommen_in_texten_nicht_vor():
    """README, App-Texte, Docstrings und Tests nennen keine Planungswörter; die Fußzeile „Mehr zu den Demos“ des Portfolios ist kein Planungstext und die Zeile mit der Wortliste selbst auch nicht."""
    muster = re.compile(r"(Stück|Linie|Linien|Vormessung|Plan Z\d|V1|V2|sm_v\w*|Phase 0|trägt|tragen|Saatwert|läuft lokal)")
    dateien = [ROOT / "README.md", ROOT / "app.py"] + sorted(ROOT.glob("mdl_*.py")) + sorted((ROOT / "tools").glob("*.py")) + sorted((ROOT / "tests").glob("test_*.py"))
    for datei in dateien:
        if datei.name == "mdl_rng.py":
            continue
        for nr, zeile in enumerate(datei.read_text(encoding="utf-8").splitlines(), 1):
            if "Mehr zu den Demos" in zeile or "muster = re.compile" in zeile:
                continue
            assert not muster.search(zeile), (datei.name, nr, muster.search(zeile).group(0))


def test_readme_ohne_veraltete_oder_unpassende_woerter():
    assert "Zufalls-Seed" in README and "Saatwert" not in README
    assert "geplant" not in README.lower()
