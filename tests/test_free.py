"""Pop-Stack mit freier Leerung: Handwerte (Mini-Instanz von Hand) und Zweige."""

import pytest

import mdl_free as F
import mdl_machines as M
from conftest import alle_folgen


def test_zerlegungen_von_4_von_hand():
    """Kompositionen von 4: 8 Stück (2^3)."""
    assert sorted(F.zerlegungen(4)) == sorted([(4,), (1, 3), (3, 1), (2, 2), (1, 1, 2), (1, 2, 1), (2, 1, 1), (1, 1, 1, 1)])


def test_zerlegungen_zaehlung():
    assert [len(F.zerlegungen(n)) for n in range(1, 10)] == [2 ** (n - 1) for n in range(1, 10)]
    assert all(sum(z) == 6 for z in F.zerlegungen(6))


def test_blockumkehr_von_hand():
    assert F.blockumkehr((3, 5, 2, 4, 1), (2, 3)) == (5, 3, 1, 4, 2)
    assert F.blockumkehr((3, 5, 2, 4, 1), (1, 1, 1, 1, 1)) == (3, 5, 2, 4, 1)
    assert F.blockumkehr((3, 5, 2, 4, 1), (5,)) == (1, 4, 2, 5, 3)
    with pytest.raises(ValueError):
        F.blockumkehr((1, 2, 3), (2,))


def test_handbeispiel_drei_freie_durchlaeufe(mini):
    """Von Hand (alle 16 Zerlegungen je Durchlauf): nach 1 und nach 2 Durchläufen nicht sortiert, nach 3 ja. Eine Lösung: Blöcke (1, 2, 1, 1), (1, 1, 3), (3, 1, 1)."""
    d, weg = F.frei_durchlaufzahl(mini, mit_weg=True)
    assert d == 3 and len(weg) == 3 and F.weg_anwenden(mini, weg) == (1, 2, 3, 4, 5)
    assert F.weg_anwenden(mini, [(1, 2, 1, 1), (1, 1, 3), (3, 1, 1)]) == (1, 2, 3, 4, 5)
    assert F.weg_anwenden((3, 5, 2, 4, 1), [(1, 2, 1, 1)]) == (3, 2, 5, 4, 1)


def test_kleinster_wagen_hinten_frei_in_zwei():
    for n in range(3, 10):
        p = tuple(range(2, n + 1)) + (1,)
        assert F.frei_durchlaufzahl(p) == 2
    assert F.weg_anwenden((2, 3, 4, 5, 1), [(5,), (1, 4)]) == (1, 2, 3, 4, 5)


def test_randfaelle():
    assert F.frei_durchlaufzahl(()) == 0
    assert F.frei_durchlaufzahl((1,)) == 0
    assert F.frei_durchlaufzahl((2, 1)) == 1
    assert F.frei_durchlaufzahl((1, 2, 3, 4)) == 0
    assert F.frei_durchlaufzahl((4, 3, 2, 1)) == 1
    with pytest.raises(ValueError):
        F.frei_durchlaufzahl(tuple(range(1, 11)))


def test_n4_verteilung_von_hand():
    """Von Hand (n = 4): 1 + 7 + 16 = 24 Folgen mit 0, 1, 2 freien Durchläufen."""
    d = [F.frei_durchlaufzahl(p) for p in alle_folgen(4)]
    assert [d.count(j) for j in range(3)] == [1, 7, 16] and max(d) == 2


def test_frei_enthaelt_fest():
    for p in alle_folgen(5):
        assert F.frei_durchlaufzahl(p) <= M.durchlaufzahl(p, M.POP)


def test_der_weg_wird_immer_korrekt_gefunden():
    for p in alle_folgen(6)[::13]:
        d, weg = F.frei_durchlaufzahl(p, mit_weg=True)
        assert len(weg) == d and F.weg_anwenden(p, weg) == tuple(range(1, 7))
