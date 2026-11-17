"""Ankunftsmodell V: Handrechnung der Rangbildung, Zufallsquelle, Kennzahlen aus der Verteilung, vorgerechnete Zellen neu gerechnet und exakt verglichen (nur Ganzzahlen)."""

import pytest

import mdl_constants as C
import mdl_machines as M
import mdl_model as MOD
import mdl_tables as T
from mdl_rng import SplitMix64


class FesteExponentiale:
    """Ersatz für den Zufallsgenerator: gibt vorgegebene Verweilzeiten zurück."""

    def __init__(self, werte):
        self.werte = list(werte)

    def expovariate(self, mittel):
        return self.werte.pop(0) * mittel


def test_rangbildung_von_hand():
    """n = 3, Verweilzeiten 2,5 / 0,1 / 0,2: Abfahrten 1 + 2,5 = 3,5; 2 + 0,1 = 2,1; 3 + 0,2 = 3,2. Reihenfolge der Abfahrten: Wagen 2, Wagen 3, Wagen 1; also Ränge (3, 1, 2)."""
    assert MOD.ankunftsfolge(FesteExponentiale([2.5, 0.1, 0.2]), 3, 1.0) == (3, 1, 2)


def test_kleine_verweilzeit_gibt_die_sortierte_folge_und_grosse_ueberholt():
    assert MOD.ankunftsfolge(FesteExponentiale([0.01, 0.02, 0.03, 0.04]), 4, 1.0) == (1, 2, 3, 4)
    assert MOD.ankunftsfolge(FesteExponentiale([9.0, 0.1, 0.1, 0.1]), 4, 1.0) == (4, 1, 2, 3)


def test_jede_folge_ist_eine_permutation_und_der_strom_ist_reproduzierbar():
    for d in range(len(C.D_WERTE)):
        folgen = MOD.strom(9, d, 12000, 50)
        assert all(sorted(p) == list(range(1, 10)) for p in folgen)
        assert folgen == MOD.strom(9, d, 12000, 50)
    assert MOD.strom(9, 3, 12000, 20) != MOD.strom(9, 3, 12001, 20)


def test_d_unendlich_ist_gleichverteilt_d_klein_fast_sortiert():
    klein = MOD.strom(8, 0, 500, 400)
    sortiert = sum(M.ist_sortiert(p) for p in klein)
    assert sortiert / 400 > 0.5                         # D = 0,5: die meisten Züge sind schon sortiert (gemessen 0,5 bis 0,6)
    inf = MOD.strom(8, 6, 500, 400)
    assert sum(M.ist_sortiert(p) for p in inf) <= 2     # unter 40 320 Folgen ist die sortierte eine


def test_kennzahlen_von_hand():
    """Verteilung [1, 2, 1] (vier Folgen mit 0, 1, 1, 2 Durchläufen): Mittel 1; Σj²c = 6, Varianz (6 − 16/4)/3 = 2/3, Standardfehler √(2/3/4)."""
    k = MOD.kennzahlen([1, 2, 1])
    assert k["n"] == 4 and k["mittel"] == 1.0
    assert k["se"] == pytest.approx((2 / 3 / 4) ** 0.5)
    assert k["anteil"] == {1: 0.75, 2: 1.0, 3: 1.0}
    assert MOD.kennzahlen([5])["se"] == 0.0


def test_histogramme_ohne_und_mit_frei():
    folgen = [(3, 5, 2, 4, 1), (1, 2, 3)]
    h = MOD.histogramme(folgen)
    assert set(h) == {"pop", "west"}
    assert h["pop"] == [1, 0, 0, 0, 1] and h["west"] == [1, 0, 1]      # (1, 2, 3): 0 Durchläufe; (3, 5, 2, 4, 1): fest 4, gierig 2
    h2 = MOD.histogramme([(3, 5, 2, 4, 1)], frei=lambda p: 3)
    assert h2["west"][2] == 1 and h2["pop"][4] == 1 and h2["frei"][3] == 1


def test_rng_ist_reproduzierbar():
    a, b = SplitMix64(42), SplitMix64(42)
    assert [a.next_u64() for _ in range(5)] == [b.next_u64() for _ in range(5)]
    items = list(range(1, 11))
    SplitMix64(1).shuffle(items)
    assert sorted(items) == list(range(1, 11))
    assert all(SplitMix64(3).expovariate(2.0) > 0 for _ in range(1))


@pytest.mark.parametrize("n,strom,d", [(10, 12000, 3), (10, 13000, 3), (9, 12000, 3), (9, 13000, 6), (10, 12000, 0)])
def test_vorgerechnete_zellen_neu_gerechnet_und_exakt_gleich(n, strom, d):
    folgen = MOD.strom(n, d, strom, 2000)
    neu = MOD.histogramme(folgen, T.frei_n9 if n == 9 else None)
    assert neu == T.modell_v(strom, n, d)
