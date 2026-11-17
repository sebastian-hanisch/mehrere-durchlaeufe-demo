"""End-to-end Smoke-Test via Streamlits offiziellem AppTest-Framework: laedt app.py mit den
Standardeinstellungen, klickt jeden Preset-Button und faehrt jeden Slider an seine Grenzen und prueft, dass
kein Python-Fehler auftritt - insbesondere `streamlit.errors.StreamlitDuplicateElementId` (mehrere
st.plotly_chart-Aufrufe ohne eindeutiges key= koennen zufaellig identischen Inhalt rendern und kollidieren)
und `StreamlitAPIException` bei Slidern mit berechneten Grenzen (min == max)."""

import os

from streamlit.testing.v1 import AppTest

import mdl_evaluation as ev

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))  # unter Last (parallele Läufe) reichen 180 s nicht immer; Umgebungsvariable zum Anpassen
AUTOPLAY_MARKER = "\u25b6"  # Auto-Play-Buttons (Animation mit sleep) im Smoke-Test auslassen


def _fresh_app() -> AppTest:
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    return at


def test_app_loads_without_exception():
    _fresh_app()


def test_every_button_click_does_not_raise():
    labels = [b.label for b in _fresh_app().button]
    assert labels, "keine Buttons gefunden"
    for index, label in enumerate(labels):
        if AUTOPLAY_MARKER in label:
            continue
        at = _fresh_app()
        at.button[index].click().run(timeout=TIMEOUT)
        assert not at.exception, (label, [str(e) for e in at.exception])


def test_every_slider_at_its_min_and_max_does_not_raise():
    labels = [s.label for s in _fresh_app().slider]
    assert labels, "keine Slider gefunden"
    for index, label in enumerate(labels):
        for edge in ("min", "max"):
            at = _fresh_app()
            slider = at.slider[index]
            value = slider.min if edge == "min" else slider.max
            if isinstance(slider.value, int):
                value = int(value)
            slider.set_value(value).run(timeout=TIMEOUT)
            assert not at.exception, (label, edge, [str(e) for e in at.exception])


# --- Ergänzungen zur Vorlage: Inhalte der App ------------------------------------------------------------------------------------------------

def _texte(at):
    return " ".join([w.value for w in at.info] + [w.value for w in at.warning] + [w.value for w in at.success] + [m.value for m in at.markdown])


def test_standardseite_zeigt_die_fuenf_experimente_und_den_modellhinweis():
    at = _fresh_app()
    titel = [s.value for s in at.subheader]
    assert [t.split(":")[0] for t in titel if t.startswith("🔬")] == [f"🔬 Experiment {i}" for i in range(1, 6)]
    text = _texte(at)
    assert "keine reale Ankunftsfolge" in text and "3, 5, 2, 4, 1" in text


def test_jedes_preset_laeuft_ohne_fehler_und_zeigt_ein_verdikt():
    for name in ("Kleinster Wagen hinten", "Zwei Durchläufe, n = 5", "Alle Folgen, n = 7", "Keine Klasse (4, 1, 3, 5, 2)", "Zug mit Verweilzeit D = 4"):
        at = _fresh_app()
        at.sidebar.button(key=f"preset_{name}").click().run(timeout=TIMEOUT)
        assert not at.exception, (name, [str(e) for e in at.exception])
        assert len(at.info) + len(at.warning) >= 5, name


def test_fehlerhafte_eingabe_gibt_eine_meldung_und_keinen_absturz():
    at = _fresh_app()
    at.text_input(key="folge").set_value("1 2 2").run(timeout=TIMEOUT)
    assert not at.exception
    assert any("doppelt: 2" in w.value for w in at.warning)
    at.text_input(key="folge").set_value("1 2 3 4 5 6 7 8 9 10").run(timeout=TIMEOUT)
    assert not at.exception and any("bis n = 9" in w.value for w in at.warning)


def test_gezogene_zuege_landen_im_eingabefeld_und_werden_ausgewertet():
    at = _fresh_app()
    at.slider(key="n1").set_value(6).run(timeout=TIMEOUT)
    for knopf, art in (("🎲 Zufall", "zufall"), ("🚂 Modell V", "modell")):
        at.button[[b.label for b in at.button].index(knopf)].click().run(timeout=TIMEOUT)
        assert not at.exception, [str(e) for e in at.exception]
        erwartet = " ".join(map(str, ev.ziehe_folge(art, 6, at.select_slider(key="d_idx").value, at.number_input(key="seed").value)))
        assert at.text_input(key="folge").value == erwartet


def test_ankunftsmodell_n9_und_n10_und_alle_werte_von_d():
    for n5 in (9, 10):
        for d in (0, 6):
            at = _fresh_app()
            at.radio(key="n5").set_value(n5).run(timeout=TIMEOUT)
            at.select_slider(key="d_idx").set_value(d).run(timeout=TIMEOUT)
            assert not at.exception, (n5, d, [str(e) for e in at.exception])
