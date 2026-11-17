"""Eigenschaftstests (metamorph, ORACLE-PLAYBOOK §5.2): Aussagen, die für die Maschinen gelten müssen, ohne dass man das richtige Ergebnis kennt."""

import pytest

import mdl_free as F
import mdl_machines as M
import mdl_model as MOD
import mdl_tables as T
from conftest import alle_folgen
from mdl_rng import SplitMix64


@pytest.mark.parametrize("n", range(1, 8))
def test_sortierte_folge_ist_fixpunkt_und_durchlauf_erhaelt_die_wagenmenge(n):
    ident = tuple(range(1, n + 1))
    assert M.pop_durchlauf(ident) == ident and M.west_durchlauf(ident) == ident and F.frei_durchlaufzahl(ident) == 0
    for p in alle_folgen(n)[::7]:
        assert sorted(M.pop_durchlauf(p)) == sorted(M.west_durchlauf(p)) == list(ident)


def test_konstante_addieren_aendert_die_durchlaufzahl_nicht():
    for p in alle_folgen(6)[::5]:
        q = tuple(x + 10 for x in p)
        for m in (M.POP, M.WEST):
            assert M.durchlaufzahl(q, m) == M.durchlaufzahl(p, m)


def test_frei_nie_schlechter_als_fest_n_bis_7():
    for n in range(2, 8):
        for p in alle_folgen(n):
            assert F.frei_durchlaufzahl(p) <= M.durchlaufzahl(p, M.POP)


def test_mengen_wachsen_mit_k_und_enden_bei_n_fakultaet():
    from math import factorial
    for m in ("pop", "west", "frei"):
        for n in range(1, 10):
            werte = [T.kumuliert(m, n, k) for k in range(0, 10)]
            assert werte == sorted(werte) and werte[0] == 1 and werte[-1] == factorial(n)


def test_zaehlschranke_der_freien_leerung():
    """Höchstens (2^(n−1))^k Folgen in k Durchläufen (jeder Durchlauf eine von 2^(n−1) Zerlegungen)."""
    for n in range(1, 10):
        for k in (1, 2, 3, 4):
            assert T.kumuliert("frei", n, k) <= (2 ** (n - 1)) ** k


def test_zaehlschranke_verlangt_bei_n9_mindestens_3_durchlaeufe_gemessen_sind_4():
    from math import factorial
    assert 256 ** 2 < factorial(9) <= 256 ** 3 and T.maximum("frei", 9) == 4


def test_streichen_erhoeht_die_freie_durchlaufzahl_nie():
    for n in range(2, 8):
        for p in alle_folgen(n)[::3]:
            d = F.frei_durchlaufzahl(p)
            assert all(F.frei_durchlaufzahl(M.streiche(p, i)) <= d for i in range(n))
    rng = SplitMix64(31)
    for _ in range(200):
        items = list(range(1, 10))
        rng.shuffle(items)
        p = tuple(items)
        d = T.frei_n9(p)
        assert all(F.frei_durchlaufzahl(M.streiche(p, i)) <= d for i in range(9))


def test_streichen_kann_die_feste_durchlaufzahl_erhoehen():
    p = (4, 1, 3, 5, 2)
    assert M.durchlaufzahl(p, M.POP) == 2 and M.durchlaufzahl(M.streiche(p, 1), M.POP) == 3


def test_nach_einem_gierigen_durchlauf_steht_der_groesste_wagen_hinten_beim_festen_nicht_immer():
    for n in range(1, 8):
        assert all(M.west_durchlauf(p)[-1] == n for p in alle_folgen(n))
    assert M.pop_durchlauf((3, 1, 2)) == (1, 3, 2)           # fest: der größte Wagen steht danach nicht hinten


def test_durchlaufzahl_hoechstens_n_minus_1_bis_n_7():
    for n in range(2, 8):
        for p in alle_folgen(n):
            assert M.durchlaufzahl(p, M.POP) <= n - 1 and M.durchlaufzahl(p, M.WEST) <= n - 1


def test_modell_d_unendlich_nahe_am_exakten_mittel_modell_u():
    """Mittel über 2 000 gleichverteilte Folgen (n = 9) liegt in 4 Standardfehlern um den exakten Mittelwert aus der Aufzählung."""
    h = MOD.histogramme(MOD.strom(9, 6, 12000, 2000), T.frei_n9)
    for m in ("pop", "west", "frei"):
        k = MOD.kennzahlen(h[m])
        assert abs(k["mittel"] - float(T.mittel(m, 9))) <= 4 * k["se"]


def test_modell_mittel_waechst_mit_der_verweilzeit_im_festen_pop_stack():
    mittel = [MOD.kennzahlen(MOD.histogramme(MOD.strom(8, d, 12000, 600))["pop"])["mittel"] for d in range(len(MOD.C.D_WERTE))]
    assert mittel == sorted(mittel)
