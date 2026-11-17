"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

# --- Zahlenbereiche ---------------------------------------------------------------------------------------------------------------------------
N_MIN, N_MAX = 3, 9              # Länge der Folge (Aufzählung aller n! Folgen und freie Durchlaufzahl sind bis n = 9 gemessen)
K_MIN, K_MAX = 1, 4              # „höchstens k Durchläufe“ (mit freier Leerung sind bei n ≤ 9 nie mehr als 4 nötig; feste Rezepte brauchen bis zu n − 1)
N4_MIN = 4                       # Klasse-Test: ab n = 4 gibt es eine Streichung auf n − 1 ≥ 3
K4_MIN, K4_MAX = 2, 3
N5_WERTE = (9, 10)               # Ankunftsmodell: n = 9 (mit FREI aus der Tabelle) oder n = 10 (nur POP und WEST)
NFOLGEN_MIN, NFOLGEN_MAX, NFOLGEN_STEP = 200, 2000, 200
SEED_MAX = 999999
STROM_SEEDS = (12000, 13000)     # die zwei vorgerechneten Ströme (Zufalls-Seed + Index von D)

# Verweilzeit D in Ankunftsabständen; None steht für ∞ (gleichverteilte Folgen, Modell U)
D_WERTE = (0.5, 1.0, 2.0, 4.0, 8.0, 16.0, None)
D_LABEL = ("0,5", "1", "2", "4", "8", "16", "∞")

# --- Voreinstellungen -------------------------------------------------------------------------------------------------------------------------
DEFAULT_FOLGE = "3 5 2 4 1"
DEFAULT_N1 = 7
DEFAULT_D_INDEX = 3
DEFAULT_SEED = 12000
DEFAULT_N2, DEFAULT_K2 = 9, 2
DEFAULT_N3, DEFAULT_M3 = 9, 0
DEFAULT_N4, DEFAULT_K4, DEFAULT_M4 = 7, 2, 0
DEFAULT_N5 = 10
DEFAULT_NFOLGEN = 2000
FOLGE_MAX_ZEICHEN = 60           # Länge des Eingabefelds (Permalink): längere Eingaben werden abgeschnitten

# --- Farben (Maschinen und Auswahl) ----------------------------------------------------------------------------------------------------------
FARBE = {"pop": "#b8572f", "west": "#2F6B65", "frei": "#4c78a8"}
COLOR_OTHER = "rgba(150,150,150,0.55)"

# --- Presets: nur die Regler, die vom Standard abweichen (die übrigen gelten mit ihrem Standardwert) ------------------------------------------
MODELL_FOLGE = "3 1 2 4 7 5 6 8 9"   # erste Folge des Stroms im Ankunftsmodell V bei n = 9, D = 4, Zufalls-Seed 12000 (tests/test_presets.py prüft das)
PRESETS = {
    "Handbeispiel (3, 5, 2, 4, 1)": {},
    "Kleinster Wagen hinten": {"folge": "2 3 4 5 1", "n3": 5},
    "Zwei Durchläufe, n = 5": {"n2": 5},
    "Alle Folgen, n = 7": {"n2": 7, "n3": 7},
    "Keine Klasse (4, 1, 3, 5, 2)": {"folge": "4 1 3 5 2", "n4": 5},
    "Zug mit Verweilzeit D = 4": {"folge": MODELL_FOLGE},
}
PRESET_HELP = {
    "Handbeispiel (3, 5, 2, 4, 1)": "Die Voreinstellung: der Zug 3, 5, 2, 4, 1 durch die drei Maschinen. Der gierige Stapel braucht 2 Durchläufe, der Pop-Stack mit festem Rezept 4, mit freier Leerung 3.",
    "Kleinster Wagen hinten": "Der Zug 2, 3, 4, 5, 1: beim festen Rezept rückt der Wagen 1 je Durchlauf nur eine Stelle vor, mit freier Leerung genügen 2 Durchläufe. Experiment 3 zeigt n = 5.",
    "Zwei Durchläufe, n = 5": "Alle 120 Folgen der Länge 5, höchstens 2 Durchläufe: 42, 91 oder 102 Folgen, je nachdem, was „k Durchläufe“ meint (Experiment 2).",
    "Alle Folgen, n = 7": "Alle 5 040 Folgen der Länge 7: Verteilung der Durchlaufzahl und Zählreihe. Bei k = 2 liegt der gierige Stapel hier vor der freien Leerung (Experimente 2 und 3).",
    "Keine Klasse (4, 1, 3, 5, 2)": "Der Zug 4, 1, 3, 5, 2 braucht beim festen Pop-Stack 2 Durchläufe; ohne den Wagen 1 bleibt 3, 2, 4, 1 mit 3 Durchläufen (Experiment 4).",
    "Zug mit Verweilzeit D = 4": "Ein Zug aus dem ausgedachten Ankunftsmodell (n = 9, Verweilzeit D = 4, Zufalls-Seed 12000), in Experiment 1 eingetragen. Experiment 5 zeigt die Durchlaufzahlen über 2 000 solche Züge bei n = 10.",
}
