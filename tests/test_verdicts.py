"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Verzweigung steht hier."""

from fractions import Fraction

import mdl_evaluation as ev


def test_verdict_folge_handbeispiel():
    kind, text = ev.verdict_folge((3, 5, 2, 4, 1), {"pop": 4, "west": 2, "frei": 3})
    assert kind == "info"
    assert text.startswith("(3, 5, 2, 4, 1): gieriger Stapel 2 Durchläufe, Pop-Stack mit festem Rezept 4, mit freier Leerung 3.")
    assert "4 = n − 1 Durchläufe" in text and "bei 5 Wagen" in text
    assert "Die freie Leerung spart gegen das feste Rezept 1 Durchlauf." in text and "kleinste Wagen" not in text


def test_verdict_folge_kleinster_wagen_hinten():
    kind, text = ev.verdict_folge((2, 3, 4, 5, 1), {"pop": 4, "west": 4, "frei": 2})
    assert "Der gierige Stapel braucht ebenfalls n − 1 = 4." in text
    assert "Der kleinste Wagen steht hinten" in text and "genügen 2 Durchläufe" in text
    assert "spart gegen das feste Rezept 2 Durchläufe" in text


def test_verdict_folge_ohne_zusatz_bei_gleichen_zahlen():
    kind, text = ev.verdict_folge((2, 1, 3), {"pop": 1, "west": 1, "frei": 1})
    assert text == "(2, 1, 3): gieriger Stapel 1 Durchläufe, Pop-Stack mit festem Rezept 1, mit freier Leerung 1."


def test_verdict_folge_sortiert():
    assert ev.verdict_folge((1, 2, 3), {"pop": 0, "west": 0, "frei": 0})[1] == "(1, 2, 3) ist schon sortiert: alle drei Maschinen brauchen 0 Durchläufe."


def test_verdict_zaehlung_k2_n5():
    z = ev.Zaehlung(5, 2, 120, {"pop": 42, "west": 91, "frei": 102}, {"pop": 42 / 120, "west": 91 / 120, "frei": 102 / 120})
    kind, text = ev.verdict_zaehlung(z)
    assert kind == "info"
    assert text.startswith("n = 5, höchstens 2 Durchläufe: Pop-Stack (festes Rezept) 42 (35,0 %), gieriger Stapel 91 (75,8 %), Pop-Stack mit freier Leerung 102 (85,0 %) von 120 Folgen.")
    assert "für n = 4 bis 6 mehr Folgen" in text and "für n = 7 bis 9 weniger (n = 7: 1 598 gegen 1 938)" in text and "bei n = 3 sind es gleich viele" in text


def test_verdict_zaehlung_k1_nennt_catalan_und_zwei_hoch():
    z = ev.Zaehlung(6, 1, 720, {"pop": 32, "west": 132, "frei": 32}, {"pop": 32 / 720, "west": 132 / 720, "frei": 32 / 720})
    text = ev.verdict_zaehlung(z)[1]
    assert "höchstens 1 Durchlauf:" in text and "(4,4 %)" in text and "(18,3 %)" in text
    assert "2^(n − 1) = 32" in text and "Catalan(6) = 132" in text and "Bei k = 2" not in text


def test_verdict_zaehlung_unter_einem_prozent_zwei_stellen():
    z = ev.Zaehlung(9, 2, 362880, {"pop": 2106, "west": 49335, "frei": 22102}, {"pop": 2106 / 362880, "west": 49335 / 362880, "frei": 22102 / 362880})
    text = ev.verdict_zaehlung(z)[1]
    assert "2 106 (0,58 %)" in text and "49 335 (13,6 %)" in text and "22 102 (6,1 %)" in text


def test_verdict_verteilung():
    d = {
        "pop": {"verteilung": [], "mittel": Fraction(47, 24), "maximum": 3, "am_maximum": 8},
        "west": {"verteilung": [], "mittel": Fraction(35, 24), "maximum": 3, "am_maximum": 2},
        "frei": {"verteilung": [], "mittel": Fraction(13, 8), "maximum": 2, "am_maximum": 16},
    }
    kind, text = ev.verdict_verteilung(ev.Verteilung(4, d))
    assert kind == "info"
    assert text.startswith("n = 4, alle 24 Folgen gleich gewichtet: Pop-Stack mit festem Rezept im Mittel 1,96 Durchläufe, Maximum 3 (= n − 1) bei 8 Folgen; ")
    assert "gieriger Stapel im Mittel 1,46 Durchläufe, Maximum 3 (= n − 1) bei 2 = 2! Folgen" in text
    assert "freie Leerung im Mittel 1,62 Durchläufe, Maximum 2 bei 16 Folgen." in text
    assert "frei sind es bei n ≤ 9 höchstens 4." in text


def _klasse(maschine, zeuge, nur_frei, kleinste):
    return ev.Klassentest(7, 2, maschine, nur_frei, kleinste, 3 if kleinste else None, [], zeuge, None, None, 1653, 64)


def test_verdict_klasse_fest():
    z = {"n": 5, "p": (4, 1, 3, 5, 2), "stelle": 2, "q": (3, 2, 4, 1), "durchlaeufe_q": 3}
    kind, text = ev.verdict_klasse(_klasse("pop", z, {"anzahl": 1300, "erste": [(1, 2, 3, 5, 6, 7, 4)]}, (1, 2, 3, 5, 6, 7, 4)))
    assert kind == "warning"
    assert text.startswith("n = 7, höchstens 2 Durchläufe: Pop-Stack fest 298 Folgen, frei 1 598 von 5 040.")
    assert "1 300 Folgen gehen nur frei, die kleinste (1, 2, 3, 5, 6, 7, 4) braucht fest 3 Durchläufe" in text
    assert "„höchstens 2 Durchläufe“ ist keine Klasse. Zeuge: (4, 1, 3, 5, 2) geht in 2, ohne den Wagen an Stelle 2 bleibt (3, 2, 4, 1) mit 3 Durchläufen; bei n = 7 sind 22 Folgen betroffen." in text
    assert "1 653 verschiedene Ausgaben, aber nur 64 Folgen" in text


def test_verdict_klasse_frei_und_ohne_nur_frei_folgen():
    kind, text = ev.verdict_klasse(_klasse("frei", None, {"anzahl": 0, "erste": []}, None))
    assert kind == "info" and "Hier gibt es keine Folge, die nur frei" in text
    assert "0 betroffene Folgen für n = 3 bis 9" in text and "Beweis in der README" in text


def _modell(d_idx=3, n=10, frei=False):
    kz = {"pop": {"n": 2000, "mittel": 4.27, "se": 0.04, "anteil": {1: 0.025, 2: 0.138, 3: 0.358}},
          "west": {"n": 2000, "mittel": 2.25, "se": 0.02, "anteil": {1: 0.2, 2: 0.658, 3: 0.912}}}
    if frei:
        kz["frei"] = {"n": 2000, "mittel": 2.42, "se": 0.01, "anteil": {1: 0.052, 2: 0.54, 3: 0.984}}
    return ev.ModellErgebnis(n, d_idx, 2000, 12000, kz, {})


def test_verdict_modell_n10():
    kind, text = ev.verdict_modell(_modell(), (28, 28), None)
    assert kind == "info"
    assert text.startswith("Im Modell V (ausgedacht), n = 10, D = 4, 2 000 Folgen (Zufalls-Seed 12000 + 3): Pop-Stack mit festem Rezept im Mittel 4,27 Durchläufe (± 0,04), gieriger Stapel 2,25 (± 0,02);")
    assert "Ein Durchlauf genügt dem Pop-Stack bei 2,5 % der Züge, dem gierigen Stapel bei 20,0 %." in text
    assert "in 28 von 28 Zellen weniger mittlere Durchläufe" in text and "freie Leerung" not in text


def test_verdict_modell_n9_mit_frei_und_gemischten_vorzeichen():
    vergleich = {0: (-0.055, -0.061), 3: (-0.35, -0.33), 4: (-0.003, 0.0195), 5: (0.37, 0.337)}
    kind, text = ev.verdict_modell(_modell(frei=True, n=9), (28, 28), vergleich)
    assert ", freie Leerung 2,42 (± 0,01)" in text
    assert "weniger als die freie Leerung bei D = 0,5, 4" in text and "die freie Leerung weniger bei D = 16" in text
    assert "bei D = 8 wechselt das Vorzeichen zwischen den Strömen (Unterschied höchstens 0,02)" in text


def test_formatierung():
    assert ev.de(3.14159, 2) == "3,14" and ev.de(-1.5, 1) == "−1,5"
    assert ev.de_int(362880) == "362 880" and ev.de_int(7) == "7" and ev.de_int(1000) == "1 000"
    assert ev.pct(0.35) == "35,0 %" and ev.pct(0.00071) == "0,07 %" and ev.pct(0.0, 1) == "0,0 %"
    assert ev.folge_text((3, 5, 2, 4, 1)) == "(3, 5, 2, 4, 1)"
