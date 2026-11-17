"""Handwerte der festen Maschinen (Mini-Instanz von Hand gerechnet) und ihre Zweige (DEMO-PLAYBOOK §1b)."""

import pytest

import mdl_machines as M
from conftest import alle_folgen


def test_pop_verlauf_des_handbeispiels(mini):
    """Von Hand: 3 stapeln; 5 > 3: leeren, 3 raus; 5, 2 stapeln; 4 > 2: leeren, 2 und 5 raus; 4, 1 stapeln; Ende: 1, 4 raus. Ergebnis 3, 2, 5, 1, 4; weiter bis sortiert: 4 Durchläufe."""
    assert M.pop_durchlauf(mini) == (3, 2, 5, 1, 4)
    assert M.verlauf(mini, M.POP) == [(3, 5, 2, 4, 1), (3, 2, 5, 1, 4), (2, 3, 1, 5, 4), (2, 1, 3, 4, 5), (1, 2, 3, 4, 5)]
    assert M.durchlaufzahl(mini, M.POP) == 4


def test_west_verlauf_des_handbeispiels(mini):
    """Von Hand: 3 stapeln; 5 holt die 3 heraus; 5, 2 stapeln; 4 holt die 2 heraus; 4, 1 stapeln; Ende: 1, 4, 5 raus: 3, 2, 1, 4, 5; ein zweiter Durchlauf sortiert."""
    assert M.west_durchlauf(mini) == (3, 2, 1, 4, 5)
    assert M.verlauf(mini, M.WEST) == [(3, 5, 2, 4, 1), (3, 2, 1, 4, 5), (1, 2, 3, 4, 5)]
    assert M.durchlaufzahl(mini, M.WEST) == 2


def test_spur_des_ersten_pop_durchlaufs(mini):
    assert M.spur(mini, M.POP) == [("rein", 3), ("raus", 3), ("rein", 5), ("rein", 2), ("raus", 2), ("raus", 5), ("rein", 4), ("rein", 1), ("raus", 1), ("raus", 4)]
    assert M.pop_bloecke(mini) == [1, 2, 2]


def test_spur_des_ersten_west_durchlaufs(mini):
    assert M.spur(mini, M.WEST) == [("rein", 3), ("raus", 3), ("rein", 5), ("rein", 2), ("raus", 2), ("rein", 4), ("rein", 1), ("raus", 1), ("raus", 4), ("raus", 5)]


def test_spur_der_freien_maschine_gibt_es_nicht(mini):
    with pytest.raises(ValueError):
        M.spur(mini, M.FREI)


@pytest.mark.parametrize("n", range(3, 9))
def test_kleinster_wagen_hinten_braucht_n_minus_1(n):
    p = tuple(range(2, n + 1)) + (1,)
    assert M.durchlaufzahl(p, M.POP) == n - 1 and M.durchlaufzahl(p, M.WEST) == n - 1


def test_pop_n4_acht_folgen_mit_drei_durchlaeufen():
    """Von Hand (n = 4): die acht Folgen mit 3 Durchläufen."""
    drei = sorted(p for p in alle_folgen(4) if M.durchlaufzahl(p, M.POP) == 3)
    assert drei == [(2, 3, 4, 1), (3, 2, 4, 1), (3, 4, 1, 2), (3, 4, 2, 1), (4, 1, 2, 3), (4, 1, 3, 2), (4, 2, 3, 1), (4, 3, 1, 2)]


def test_zeuge_keine_klasse():
    assert M.verlauf((4, 1, 3, 5, 2), M.POP) == [(4, 1, 3, 5, 2), (1, 4, 3, 2, 5), (1, 2, 3, 4, 5)]
    assert M.streiche((4, 1, 3, 5, 2), 1) == (3, 2, 4, 1)
    assert M.durchlaufzahl((3, 2, 4, 1), M.POP) == 3 and M.durchlaufzahl((3, 2, 4, 1), M.WEST) == 3
    assert M.durchlaufzahl((3, 5, 2, 4, 1), M.WEST) == 2 and M.durchlaufzahl(M.streiche((3, 5, 2, 4, 1), 1), M.WEST) == 3


def test_streichen_nummeriert_neu():
    assert M.streiche((2, 5, 1, 3, 4), 1) == (2, 1, 3, 4)
    assert M.streiche((1,), 0) == ()


def test_randfaelle():
    assert M.durchlaufzahl((), M.POP) == 0 and M.durchlaufzahl((1,), M.WEST) == 0
    assert M.durchlaufzahl((2, 1), M.POP) == 1 and M.durchlaufzahl((2, 1), M.WEST) == 1          # n = 2
    assert M.durchlaufzahl((5, 4, 3, 2, 1), M.POP) == 1 and M.durchlaufzahl((5, 4, 3, 2, 1), M.WEST) == 1   # Umkehrfolge: alles hinein, alles heraus
    assert M.pop_durchlauf((1, 2, 3, 4)) == (1, 2, 3, 4) and M.west_durchlauf((1, 2, 3, 4)) == (1, 2, 3, 4)  # sortierte Folge ist Fixpunkt
    assert M.pop_bloecke(()) == []


def test_beide_zweige_unterscheiden_sich():
    """Zweig-Test (Playbook §0): fest und gierig weichen auf einer Mini-Instanz ab, sonst wäre eine Spalte toter Code."""
    assert M.pop_durchlauf((3, 5, 2, 4, 1)) != M.west_durchlauf((3, 5, 2, 4, 1))


def test_verlauf_nennt_jeden_zustand():
    v = M.verlauf((2, 3, 1), M.POP)
    assert v[0] == (2, 3, 1) and v[-1] == (1, 2, 3) and len(v) - 1 == M.durchlaufzahl((2, 3, 1), M.POP)
    assert M.verlauf((1, 2, 3), M.WEST) == [(1, 2, 3)]
