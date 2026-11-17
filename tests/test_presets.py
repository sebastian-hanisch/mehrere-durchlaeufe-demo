"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, je Preset die erwartete Verdikt-Zeile (DEMO-PLAYBOOK §11a Punkt 7)."""

import mdl_constants as C
import mdl_evaluation as ev
import mdl_presets as P

ERSTES = "Handbeispiel (3, 5, 2, 4, 1)"


def settings_von(name):
    return ev.Settings(**{k: P.preset_wert(name, k) for k in P.SETTING_SPECS})


def test_every_preset_has_help_and_only_known_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) <= set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_bounds():
    for name, preset in C.PRESETS.items():
        for key, value in preset.items():
            spec = P.SETTING_SPECS[P.PRESET_KEYS[key]]
            if spec.lo is not None:
                assert spec.lo <= value <= spec.hi, (name, key)


def test_default_preset_is_the_first_and_equals_the_default_settings():
    assert next(iter(C.PRESETS)) == ERSTES
    assert C.PRESETS[ERSTES] == {}
    assert settings_von(ERSTES) == ev.Settings()


def test_every_other_preset_differs_from_the_default():
    for name in C.PRESETS:
        if name != ERSTES:
            assert settings_von(name) != ev.Settings(), name
    assert len({settings_von(n) for n in C.PRESETS}) == len(C.PRESETS)


def test_setting_specs_cover_every_preset_key_and_every_settings_field():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)
    assert set(P.SETTING_SPECS) == set(ev.Settings.__dataclass_fields__)


def test_preset_verdikte():
    """Je Preset die erwartete Verdikt-Zeile (nicht nur der Standard): ein Preset meldet nur, was es zeigt."""
    s = settings_von(ERSTES)
    a = ev.analyse_folge(s.folge)
    assert a.zahlen == {"pop": 4, "west": 2, "frei": 3}

    s = settings_von("Kleinster Wagen hinten")
    a = ev.analyse_folge(s.folge)
    assert a.zahlen == {"pop": 4, "west": 4, "frei": 2} and "Der kleinste Wagen steht hinten" in ev.verdict_folge(a.p, a.zahlen)[1]
    assert ev.analyse_verteilung(s.n3).n == 5

    s = settings_von("Zwei Durchläufe, n = 5")
    assert ev.verdict_zaehlung(ev.analyse_zaehlung(s.n2, s.k2))[1].startswith("n = 5, höchstens 2 Durchläufe: Pop-Stack (festes Rezept) 42 (35,0 %), gieriger Stapel 91 (75,8 %)")

    s = settings_von("Alle Folgen, n = 7")
    text = ev.verdict_zaehlung(ev.analyse_zaehlung(s.n2, s.k2))[1]
    assert "von 5 040 Folgen" in text and "1 598" in text and "1 938" in text

    s = settings_von("Keine Klasse (4, 1, 3, 5, 2)")
    a = ev.analyse_folge(s.folge)
    assert a.zahlen["pop"] == 2
    text = ev.verdict_klasse(ev.analyse_klassentest(s.n4, s.k4, "pop"))[1]
    assert "Zeuge: (4, 1, 3, 5, 2)" in text and "(3, 2, 4, 1) mit 3 Durchläufen" in text

    s = settings_von("Zug mit Verweilzeit D = 4")
    a = ev.analyse_folge(s.folge)
    assert a.fehler is None and a.p == ev.ziehe_folge("modell", 9, 3, 12000) == (3, 1, 2, 4, 7, 5, 6, 8, 9)
    assert a.zahlen == {"pop": 2, "west": 1, "frei": 2}      # von Hand: Pop-Durchlauf 1 gibt 1 3 2 4 5 7 6 8 9, Durchlauf 2 sortiert
    assert "D = 4, 2 000 Folgen" in ev.verdict_modell(ev.analyse_modell(s.n5, s.d_idx, s.nfolgen, s.seed), ev.zellen_west_besser(), None)[1]
