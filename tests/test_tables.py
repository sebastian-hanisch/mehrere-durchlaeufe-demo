"""Vorgerechnete Tabellen: Zugriff, Handwerte (n = 4 von Hand), Prüfsumme, Neuberechnung bis n = 6 mit dem numpy-Weg der Erzeugung."""

import hashlib
import itertools
import sys
from fractions import Fraction
from pathlib import Path

import pytest

import mdl_tables as T

TOOLS = Path(__file__).resolve().parent.parent / "tools"


def test_n4_von_hand():
    """Von Hand (24 Folgen): Pop-Stack 1 + 7 + 8 + 8, gieriger Stapel 1 + 13 + 8 + 2, frei 1 + 7 + 16 Folgen mit 0, 1, 2, 3 Durchläufen."""
    assert T.verteilung("pop", 4) == [1, 7, 8, 8]
    assert T.verteilung("west", 4) == [1, 13, 8, 2]
    assert T.verteilung("frei", 4) == [1, 7, 16]
    assert (T.kumuliert("pop", 4, 1), T.kumuliert("pop", 4, 2), T.kumuliert("pop", 4, 3)) == (8, 16, 24)
    assert (T.kumuliert("west", 4, 1), T.kumuliert("west", 4, 2), T.kumuliert("west", 4, 3)) == (14, 22, 24)
    assert (T.kumuliert("frei", 4, 1), T.kumuliert("frei", 4, 2)) == (8, 24)


def test_mittel_n4_als_brueche():
    """Von Hand: (0·1 + 1·7 + 2·8 + 3·8)/24 = 47/24; (13 + 16 + 6)/24 = 35/24; (7 + 32)/24 = 13/8."""
    assert T.mittel("pop", 4) == Fraction(47, 24)
    assert T.mittel("west", 4) == Fraction(35, 24)
    assert T.mittel("frei", 4) == Fraction(13, 8)


def test_maximum_und_folgen_am_maximum():
    assert [T.maximum("pop", n) for n in range(2, 10)] == list(range(1, 9))
    assert [T.maximum("west", n) for n in range(2, 10)] == list(range(1, 9))
    assert [T.maximum("frei", n) for n in range(2, 10)] == [1, 2, 2, 3, 3, 4, 4, 4]
    assert T.am_maximum("west", 4) == 2 and T.am_maximum("pop", 4) == 8


def test_zugriff_klasse_bild_nur_frei():
    assert T.verletzungen("pop", 2, 5) == 1 and T.verletzungen("pop", 2, 4) == 0
    assert T.zeuge("pop", 2) == {"n": 5, "p": (4, 1, 3, 5, 2), "stelle": 2, "q": (3, 2, 4, 1), "durchlaeufe_q": 3}
    assert T.zeuge("frei", 2) is None
    assert T.bild(4) == 11 and T.bild(7) == 1653
    nf = T.nur_frei(2, 5)
    assert nf["anzahl"] == 60 and nf["erste"][0] == (1, 3, 4, 5, 2) and len(nf["erste"]) == 5


def test_lex_rang_gegen_itertools():
    for n in (1, 2, 4, 6):
        for i, p in enumerate(itertools.permutations(range(1, n + 1))):
            assert T.lex_rank(p) == i


def test_byte_tabelle_pruefsumme_und_laenge():
    roh = T.FREI_N9.read_bytes()
    assert len(roh) == 362880 and max(roh) == 4
    assert hashlib.sha256(roh).hexdigest() == T.tabellen()["frei_n9_sha256"]
    assert roh[0] == 0 and T.frei_n9((1, 2, 3, 4, 5, 6, 7, 8, 9)) == 0
    assert T.frei_n9((2, 3, 4, 5, 6, 7, 8, 9, 1)) == 2
    assert [roh.count(j) for j in range(5)] == T.verteilung("frei", 9)
    with pytest.raises(ValueError):
        T.frei_n9((1, 2, 3))


def test_summe_jeder_verteilung_ist_n_fakultaet():
    from math import factorial
    for m in ("pop", "west", "frei"):
        for n in range(1, 10):
            assert sum(T.verteilung(m, n)) == factorial(n)


def test_neuberechnung_bis_n6_mit_dem_numpy_weg_gleich_der_datei():
    pytest.importorskip("numpy")
    sys.path.insert(0, str(TOOLS))
    import mdl_make_tables as G
    neu, _ = G.erzeuge_aufzaehlung(6)
    assert G.begrenze(neu, 6) == G.begrenze(T.tabellen(), 6)


def test_beschaedigte_byte_tabelle_wird_erkannt(tmp_path, monkeypatch):
    roh = bytearray(T.FREI_N9.read_bytes())
    roh[5] ^= 1
    kopie = tmp_path / "x.bin"
    kopie.write_bytes(bytes(roh))
    monkeypatch.setattr(T, "FREI_N9", kopie)
    T.frei_n9_bytes.cache_clear()
    try:
        with pytest.raises(ValueError):
            T.frei_n9_bytes()
    finally:
        T.frei_n9_bytes.cache_clear()
