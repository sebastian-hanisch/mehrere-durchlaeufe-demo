"""Randfälle, an denen Kernroutinen erfahrungsgemäß brechen (DEMO-PLAYBOOK §12): n = 1, n = 2, Eingaben mit Fehlern, Obergrenze n = 9, Gleichstände."""

import pytest

import mdl_evaluation as ev
import mdl_free as F
import mdl_machines as M


def test_n_gleich_1_und_2():
    for m in (M.POP, M.WEST):
        assert M.durchlaufzahl((1,), m) == 0 and M.durchlaufzahl((2, 1), m) == 1 and M.durchlaufzahl((1, 2), m) == 0
    assert F.frei_durchlaufzahl((1,)) == 0 and F.frei_durchlaufzahl((2, 1)) == 1


def test_analyse_n1_und_n2():
    r = ev.analyse_folge("1")
    assert r.fehler is None and r.zahlen == {"pop": 0, "west": 0, "frei": 0} and r.verlauf["pop"] == [(1,)]
    r2 = ev.analyse_folge("2 1")
    assert r2.zahlen == {"pop": 1, "west": 1, "frei": 1}


def test_sortierte_folge_und_umkehrfolge():
    r = ev.analyse_folge("1 2 3 4 5 6")
    assert r.zahlen == {"pop": 0, "west": 0, "frei": 0} and ev.verdict_folge(r.p, r.zahlen)[1].endswith("0 Durchläufe.")
    u = ev.analyse_folge("6 5 4 3 2 1")
    assert u.zahlen == {"pop": 1, "west": 1, "frei": 1}


@pytest.mark.parametrize("text,stichwort", [
    ("", "Bitte eine Folge"),
    ("a b", "nur ganze Zahlen"),
    ("1 2 2", "doppelt: 2"),
    ("1 3", "fehlt: 2"),
    ("0 1 2", "außerhalb"),
    ("1 2 3 4 5 6 7 8 9 10", "bis n = 9"),
])
def test_ungueltige_eingaben_geben_eine_meldung_statt_einer_zahl(text, stichwort):
    p, fehler = ev.parse_folge(text)
    assert p is None and stichwort in fehler
    assert ev.analyse_folge(text).fehler == fehler


def test_gueltige_eingaben_in_verschiedenen_schreibweisen():
    assert ev.parse_folge("(3, 5, 2, 4, 1)")[0] == (3, 5, 2, 4, 1)
    assert ev.parse_folge("3;5;2;4;1")[0] == (3, 5, 2, 4, 1)
    assert ev.parse_folge("  3   5 2 4 1 ")[0] == (3, 5, 2, 4, 1)
    assert ev.parse_folge("1 2 3 4 5 6 7 8 9")[0] == tuple(range(1, 10))      # n = 9 ist die Obergrenze, inklusive


def test_frei_fuer_n_groesser_9_ist_nicht_gemessen():
    with pytest.raises(ValueError, match="nicht gemessen"):
        F.frei_durchlaufzahl(tuple(range(1, 11)))


def test_zufallsfolge_und_modell_liefern_gueltige_folgen_in_den_grenzen():
    for art in ("zufall", "modell"):
        for n1 in (3, 9):
            p = ev.ziehe_folge(art, n1, 6, 99)
            assert sorted(p) == list(range(1, n1 + 1)) and ev.analyse_folge(" ".join(map(str, p))).fehler is None
    assert len(ev.ziehe_folge("zufall", 99, 6, 99)) == 9 and len(ev.ziehe_folge("zufall", 1, 6, 99)) == 3      # n wird auf 3 bis 9 begrenzt
    with pytest.raises(ValueError):
        ev.ziehe_folge("x", 5, 0, 1)


def test_gleichstaende_sind_nicht_erlaubt():
    assert ev.parse_folge("2 2 1")[1].startswith("Jeder Rang 1 … 3 muss genau einmal vorkommen")
    assert "Gleichstände" in ev.parse_folge("2 2 1")[1]


def test_klassentest_fuer_k_ohne_zeugen_frei():
    t = ev.analyse_klassentest(4, 2, "frei")
    assert t.zeuge is None and t.zeuge_verlauf is None and all(b == 0 for _, _, b in t.zeile)
