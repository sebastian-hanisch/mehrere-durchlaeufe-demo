# Mehrere Durchläufe: wie oft muss der Zug durch die Maschine? – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-mehrere-durchlaeufe-demo.streamlit.app/)** -->

Eine von mehreren Demos zum Thema **Sortiermaschinen und Permutationen** für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. Die Nachbar-Demos
[`stapel-sortieren-demo`](https://github.com/sebastian-hanisch/stapel-sortieren-demo) (welche Folgen ein Stapel in **einem** Durchlauf sortiert) und
[`maschinen-vergleich-demo`](https://github.com/sebastian-hanisch/maschinen-vergleich-demo) (zehn Maschinen in einer Tabelle) nehmen an, dass der Zug die Maschine **einmal** durchläuft und danach sortiert sein muss. Diese Demo hebt
die Annahme auf: der Zug darf mehrfach durch dieselbe Maschine, und gefragt wird, **wie viele Durchläufe** eine Folge braucht und wie viele Folgen in höchstens k Durchläufen fertig sind. Zwei Durchläufe durch einen Stapel sind dabei **nicht**
„zwei Stapel in Serie“ (dazu [`zwei-stapel-serie-demo`](https://github.com/sebastian-hanisch/zwei-stapel-serie-demo)); Durchläufe mit Gruppen und mehreren Gleisen behandelt die [`ablaufberg-demo`](https://github.com/sebastian-hanisch/ablaufberg-demo)
(dort heißt das „Durchgang“).

**Das Ankunftsmodell ist ausgedacht** (Experimente 1 und 5): ein **Modell, keine reale Ankunftsfolge** und kein Fall aus der Praxis. Wagen i kommt zur Zeit i an und bleibt exponentialverteilt lange (Mittel D Ankunftsabstände); die Abholrangzahl
ist die Reihenfolge der Abfahrten. Es kennt nur die Rangfolge der Abfahrten, keine Zeiten und keine Gleise. Alle Zahlen gelten für die drei Maschinen unten, **alle Wagen verschieden** (keine Gleichstände; mit Zielgruppen nicht gemessen), Zähleinheit
**Folgen** (alle n! Anordnungen der Ränge 1 … n, aufgezählt bis n = 9) bzw. **Zufallsfolgen** im Ankunftsmodell. Die Zählreihen der festen Maschinen stehen in der Literatur und in der OEIS; die freie Leerung (Zahlen für n ≤ 9) und das Ankunftsmodell sind eigene Rechnung dieser Demo. Neu ist nur die Vorführbarkeit mit Zähleinheit.

## Warum dieses Problem

„Wie oft muss der Zug durch die Maschine?“ klingt nach einer Frage mit einer Antwort. Sie hat drei, weil **„k Durchläufe“ keine eindeutige Maschine** ist. Bei n = 5 Wagen und höchstens 2 Durchläufen sortiert der Pop-Stack mit festem Rezept 42 von 120 Folgen,
der gierige Stapel 91, der Pop-Stack mit freier Leerung 102; bei n = 9 sind es 2 106, 49 335 und 22 102 von 362 880. Auch der schlimmste Fall hängt am Rezept: fest braucht manche Folge n − 1 Durchläufe (bei n = 9 sind es 35 346 Folgen
beim Pop-Stack, 5 040 beim gierigen Stapel), frei nie mehr als 4 (n ≤ 9). Und „höchstens zwei Durchläufe“ ist beim festen Rezept keine Mustervermeidungs-Klasse (ein gestrichener Wagen kann einen dritten Durchlauf erzwingen), bei freier Leerung
ist es für n ≤ 9 eine. **Die Kernfragen:** Wie viele Durchläufe braucht mein Zug? Wie viele Züge schaffen k Durchläufe, und was ist im schlimmsten Fall nötig? Wovon hängt die Zahl ab?

## Modell

* **Folge und Ziel:** eine Folge der Ränge 1 … n in Ankunftsreihenfolge, alle verschieden; Ziel ist die aufsteigende Folge 1, 2, …, n. Ein **Durchlauf** ist ein Zug durch **einen** Behälter, die Ausgabe ist die Eingabe des nächsten Durchlaufs.
  **Durchlaufzahl** = kleinste Zahl von Durchläufen bis zur sortierten Folge (sortiert: 0); „in k Durchläufen sortierbar“ heißt höchstens k.
* **Pop-Stack, festes Rezept** (POP): der Stapel wird ganz geleert (obere Wagen zuerst), sobald der nächste Wagen größer ist als die Spitze; sonst wird gestapelt. Ein Durchlauf kehrt jeden maximal absteigenden Lauf um; deterministisch.
* **Gieriger Stapel** (WEST, die West-Abbildung): ausgeben, solange die Spitze kleiner ist als der nächste Wagen, dann stapeln. Hinter „West-k“ steht: dieselbe feste Regel k-mal angewandt.
* **Pop-Stack mit freier Leerung** (FREI): der Bediener darf jederzeit leeren; ein Durchlauf ist eine beliebige Zerlegung der Folge in zusammenhängende Blöcke (2^(n−1) Zerlegungen), jeder Block umgekehrt. Das sind k Pop-Durchläufe mit freier Leerung; die Gleichsetzung mit „k Pop-Stacks in Reihe“ ist eine **eigene, nicht an der Literatur geprüfte Überlegung**
  (keine gelesene Quelle: Hintereinanderschalten ändert nur den Zeitpunkt, nicht die Folge, die beim nächsten Behälter ankommt). FREI enthält POP (der feste Pop-Stack ist eine bestimmte Zerlegung).
* **Konventionen:** Ein Durchlauf sortiert beim festen Pop-Stack genau die Folgen ohne die Muster 231 und 312 (2^(n−1) Folgen) und beim gierigen Stapel genau die ohne 231 (Catalan-Zahl); Eingabe, die ein Stapel sortiert, vermeidet 231, erzeugbare Ausgaben würden 312 vermeiden.
  Hier wird nur sortiert, nie erzeugt. Die Formeln stehen im 📐-Expander der App.
* **Ankunftsmodell V:** Abfahrtszeit T_i = i + E_i, E_i exponentialverteilt mit Mittel D; Abholrang = Rang von T_i unter T_1 … T_n. D → ∞ gibt gleichverteilte Folgen (Modell U). Zufall nur über den ganzzahligen SplitMix64 (`mdl_rng.py`, geprüfte Vorlage unverändert kopiert); der Strom für D Nr. j (D = 0,5; 1; 2; 4; 8; 16; ∞ sind Nr. 0 bis 6)
  ist `SplitMix64(Zufalls-Seed + j)`.
* **Quellen, nur wie gelesen:** Bóna, „A survey of stack-sorting disciplines“, Electron. J. Combin. 9(2), 2003, #A1 (ganz gelesen): der Stapel sortiert die 231-vermeidenden Folgen, die Rekursion der West-Abbildung, die Zählformel für zwei Durchläufe durch den gierigen Stapel (Zeilberger, nur über Bóna, Satz 3.2),
  „West-2 ist keine Klasse“ mit dem Beispiel 35241 sortierbar, 3241 nicht. Claesson/Guðmundsson, „Enumerating permutations sortable by k passes through a pop-stack“, arXiv 1710.04978 (Kopf und Abschnitt 2 gelesen): der Pop-Operator, die rationale erzeugende Funktion für jedes k.
  Pudwell/Smith (zwei Durchläufe durch einen Pop-Stack, arXiv 1801.05005) und Cerbai/Claesson/Ferrari (arXiv 1907.08142) nur im Abstract. Die Reihen der OEIS-Einträge A224232, A293774, A293775 (zwei, drei, vier Pop-Durchläufe) und A134664 (drei Durchläufe durch den gierigen Stapel) stimmen mit den Zahlen unten überein:
  **Zahlengleichheit, kein Beleg**, dass der Eintrag diese Maschine meint (A224232 nennt im Namen nur eine Rekursion). **Nicht gelesen:** West 1990, Zeilberger 1992, Avis/Newborn 1981, Knuth.

## Methodik

* **Einzelne Folgen live** in reinem Python: POP und WEST laufen direkt (`mdl_machines.py`); die freie Durchlaufzahl **einer** Folge bestimmt `mdl_free.py` durch **Treffen in der Mitte**: jede Blockumkehrung ist ihre eigene Umkehrung, und die Zerlegung in lauter einzelne Wagen ändert nichts;
  die Mengen der Folgen, die man von der Folge und von der sortierten Folge aus nach höchstens zwei Durchläufen erreicht, schneiden sich also genau dann, wenn die freie Durchlaufzahl höchstens 4 ist. Mit freier Leerung sind bei n ≤ 9 nie mehr als 4 Durchläufe nötig, **für n ≥ 10 ist das Maximum nicht gemessen**: die App rechnet freie Durchläufe nur bis n = 9.
* **Aufzählung aller n! Folgen: vorgerechnet** (`data/mdl_tables.json`, `data/mdl_frei_n9.bin` mit 362 880 Bytes, Skript `tools/mdl_make_tables.py` mit numpy, Rechenzeit etwa 30 Sekunden). In der App steht überall „vorgerechnet“, wo eine Zahl aus diesen Dateien stammt. `python tools/mdl_make_tables.py --check` rechnet n ≤ 8 und das Ankunftsmodell neu und vergleicht exakt;
  n = 9 prüft es über die Prüfsumme (`--full` rechnet auch n = 9 neu). Die Tests rechnen n ≤ 7 live in reinem Python nach (anderer Weg als die numpy-Erzeugung), n = 8 als langsamer Test (Marke `slow`).
* **Ankunftsmodell:** in der App live für den gewählten Wert D (2 000 Folgen), dazu die **vorgerechnete** Kurve über alle D in zwei unabhängigen Strömen (Zufalls-Seed 12000 und 13000, je 2 000 Folgen, n = 9 und n = 10, sieben Werte von D); alle Zählungen sind Ganzzahlen und plattformfest.
* **Klasse-Test:** Verletzung = eine Folge in „höchstens k Durchläufen“, bei der das Streichen **eines** Wagens (Ränge neu nummeriert) eine Folge ergibt, die mehr als k Durchläufe braucht. Zähleinheit: betroffene Folgen mit höchstens k Durchläufen.
* **Rechenzeit** (Messung dieser README, nicht im Test; ein Rechner, Windows, Python 3.14): Experiment 5 rechnet 2 000 Folgen in 0,7 s (n = 9, mit der freien Leerung aus der Tabelle) bzw. 0,8 s (n = 10); eine einzelne Folge in Experiment 1 braucht bei n ≤ 9 unter 0,05 s, die Seite lädt in etwa 1,3 s.

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen gelten für die drei Maschinen mit allen Wagen verschieden, Zähleinheit Folgen (Aufzählung aller n! Anordnungen) bzw. Zufallsfolgen; die Spalte „Test“ nennt die Funktion in `tests/test_claims.py`, die die Zahl rechnet (Ganzzahlen und Brüche exakt,
Mittelwerte aus Ganzzahlen auf die angegebenen Stellen). Messung dieser README und nicht im Test steht ausdrücklich dabei.

| Nr | Befund (Voraussetzung) | Test |
|---|---|---|
| B1 | **Zwei Durchläufe, n = 5** (alle 120 Folgen): Pop-Stack mit festem Rezept 42 (35,0 %), gieriger Stapel 91 (75,8 %), freie Leerung 102 (85,0 %). **n = 9** (alle 362 880 Folgen): 2 106 (0,58 %), 49 335 (13,6 %), 22 102 (6,1 %). Verteilung n = 5 (Folgen mit 0, 1, 2, … Durchläufen): fest 1, 15, 26, 46, 32; gieriger Stapel 1, 41, 49, 23, 6; frei 1, 15, 86, 18 | `test_b1` |
| B2 | **Ein Durchlauf**, n = 1 … 9: fest und frei je 2^(n−1) Folgen (dieselbe Menge, n ≤ 7), gieriger Stapel Catalan(n). Anteil an allen Folgen: fest 13,3 % (n = 5), 4,4 % (n = 6), 0,07 % (n = 9); gieriger Stapel 35,0 %, 18,3 %, 1,3 % | `test_b2` |
| B3 | **Die Reihenfolge der Maschinen kippt** (zwei Durchläufe, gieriger Stapel gegen freie Leerung): frei schafft mehr bei n = 4, 5, 6 (24 gegen 22, 102 gegen 91, 414 gegen 408), gleich viele bei n = 3 (6), weniger bei n = 7, 8, 9 (1 598 gegen 1 938, 5 982 gegen 9 614, 22 102 gegen 49 335) | `test_b3` |
| B4 | **Größte Durchlaufzahl**, n = 2 … 9: fest und gieriger Stapel genau n − 1; Folgen am Maximum: fest 1, 2, 8, 32, 155, 830, 5 106, 35 346, gieriger Stapel genau (n − 2)! = 1, 2, 6, 24, 120, 720, 5 040 (n = 3 … 9). Frei: Maximum 1, 2, 2, 3, 3, 4, 4, 4 bei 1, 2, 16, 18, 306, 50, 2 952, 81 030 Folgen (n = 2 … 9; höchstens 4 für n ≤ 9). Die erste Vermutung ⌈n/2⌉ gilt bis n = 8 und ist bei n = 9 falsch (4 statt 5) | `test_b4` |
| B5 | **Der kleinste Wagen hinten**, (2, 3, …, n, 1), n = 3 … 9: fest und gieriger Stapel genau n − 1 Durchläufe (der Wagen 1 rückt je Durchlauf eine Stelle vor), frei 2 | `test_b5` |
| B6 | **Mittlere Durchlaufzahl über alle n! Folgen** (Modell U, exakt): n = 5: 2,775 / 1,933 / 2,008 (fest / gieriger Stapel / frei); n = 9: 5,9803 / 4,0925 / 3,1617; n = 4 als Brüche 47/24, 35/24, 13/8 | `test_b6` |
| B7 | **Frei enthält fest:** jede Folge hat freie Durchlaufzahl höchstens gleich der festen (n ≤ 9). Folgen, die frei in höchstens zwei, fest aber in mehr Durchläufen gehen: 8, 60, 302, 1 300, 5 190, 19 996 (n = 4 … 9); die kleinste bei n = 5 ist (1, 3, 4, 5, 2) und braucht fest 3 Durchläufe | `test_b7` |
| B8 | **Keine Klasse beim festen Rezept:** (4, 1, 3, 5, 2) geht beim Pop-Stack in 2 Durchläufen, ohne den Wagen 1 bleibt (3, 2, 4, 1) mit 3; (3, 5, 2, 4, 1) geht beim gierigen Stapel in 2, ohne den Wagen 1 bleibt (3, 2, 4, 1) mit 3. Betroffene Folgen bei höchstens 2 Durchläufen, n = 5 … 9: fest 1, 6, 22, 73, 235; gieriger Stapel 1, 13, 116, 892, 6 364. Bei höchstens 3: fest 0, 8, 60, 299, 1 308; gieriger Stapel 0, 6, 112, 1 390, 14 604. **Frei: 0 betroffene Folgen für k = 1, 2, 3 und n = 3 … 9** (Messung bis n = 9; für die Blockumkehrungen gilt es allgemein, Beweis in den Grenzen). Das Beispiel (3, 5, 2, 4, 1) gehört dem gierigen Stapel: der feste Pop-Stack braucht dafür 4 Durchläufe | `test_b8` |
| B9 | **Der gierige Stapel mit zwei Durchläufen** sortiert dieselbe Menge wie die Muster-Beschreibung Av(2341, 3\bar{5}241), n = 4 … 8 (9 614 Folgen bei n = 8); ein fester Pop-Durchlauf sortiert genau Av(231, 312) (n ≤ 7 als Menge). Die Beschreibung stammt aus zweiter Hand | `test_b9` (n ≤ 7) und `test_oracle_mehrere_durchlaeufe.py` (n = 8) |
| B10 | **Bild gegen Urbild:** ein fester Pop-Durchlauf liefert 1, 1, 3, 11, 49, 263, 1 653, 11 877, 95 991 verschiedene Ausgaben (n = 1 … 9), aber nur 2^(n−1) Folgen sind in einem Durchlauf sortierbar: bei n = 7 sind es 1 653 gegen 64 | `test_b10` |
| B11 | **Ankunftsmodell V**, n = 10, D = 4, je 2 000 Folgen (Zufalls-Seed 12000 + 3 / 13000 + 3): Pop-Stack im Mittel 4,27 / 4,34 Durchläufe, gieriger Stapel 2,25 / 2,24; ein Durchlauf genügt dem Pop-Stack bei 2,5 % / 3,5 % der Züge, dem gierigen Stapel bei 20,0 % / 21,4 %. Der gierige Stapel braucht in **28 von 28 Zellen** (n = 9 und 10, sieben D, zwei Ströme) weniger mittlere Durchläufe als der Pop-Stack. Die beiden Ströme unterscheiden sich bei den Mittelwerten um höchstens 0,103, bei den Anteilen um bis zu 3,65 Prozentpunkte (über alle 28 Zellen, drei Anteile je Zelle) | `test_b11` |
| B12 | **Ankunftsmodell V, n = 9** (beide Ströme): der gierige Stapel braucht weniger als die freie Leerung bei D = 0,5; 1; 2; 4 in beiden Strömen; bei D = 8 wechselt das Vorzeichen (Unterschied höchstens 0,02); die freie Leerung braucht weniger bei D = 16 und ∞. **Gegenprobe:** bei D = ∞ liegen die Mittel (5,98 / 4,09 / 3,16 im Strom 12000) in 4 Standardfehlern um den exakten Wert aus B6 | `test_b12` |
| B13 | **Treffen in der Mitte = Breitensuche:** die freie Durchlaufzahl der App gleich einer Breitensuche über Blockumkehrungen für alle 5 880 Folgen mit n = 5, 6, 7 (120 + 720 + 5 040) und für je 300 Zufallsfolgen mit n = 8 und n = 9 (Zufalls-Seed 7777); gleich einer Vorwärtssuche über die Ausgaben der Pop-Stack-Maschine für alle Folgen n ≤ 5 | `test_b13` und `test_oracle_mehrere_durchlaeufe.py` |
| B14 | **Zahlengleichheit mit der Literatur:** die Zählreihen unten stimmen für n = 1 … 9 mit den Reihen der Einträge A224232, A293774, A293775 und A134664 überein; für k = 2 gilt beim gierigen Stapel die Formel 2(3n)!/((n+1)!(2n+1)!); die Rekursion a(n) = 2(a(n−1) + a(n−3)) + a(n−2) aus dem Namen von A224232 gilt für die Zahlen des festen Pop-Stacks bei n = 4 … 9 (Gleichheit der Zahlen, kein Beweis) | `test_b14` |

**Zählreihen** (Folgen in höchstens k Durchläufen, vorgerechnet; fest / gieriger Stapel / frei):

| n | n! | fest k=1 | k=2 | k=3 | k=4 | gierig k=1 | k=2 | k=3 | frei k=1 | k=2 | k=3 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 4 | 24 | 8 | 16 | 24 | 24 | 14 | 22 | 24 | 8 | 24 | 24 |
| 5 | 120 | 16 | 42 | 88 | 120 | 42 | 91 | 114 | 16 | 102 | 120 |
| 6 | 720 | 32 | 112 | 303 | 565 | 132 | 408 | 606 | 32 | 414 | 720 |
| 7 | 5 040 | 64 | 298 | 1 033 | 2 473 | 429 | 1 938 | 3 494 | 64 | 1 598 | 4 990 |
| 8 | 40 320 | 128 | 792 | 3 544 | 10 468 | 1 430 | 9 614 | 21 426 | 128 | 5 982 | 37 368 |
| 9 | 362 880 | 256 | 2 106 | 12 220 | 44 148 | 4 862 | 49 335 | 137 901 | 256 | 22 102 | 281 850 |

(Test: `test_b4_zaehlreihen_tabelle`.) Die Zählreihe der freien Leerung (1, 2, 6, 24, 102, 414, 1 598, 5 982, 22 102 bei zwei Durchläufen) wurde **nicht** in der OEIS gesucht und nicht auf eine Formel oder eine rationale erzeugende Funktion untersucht; ob sie rational ist, ist offen.

## Befunde und Korrekturen

* **Die Beweisskizze für „höchstens n − 1 Durchläufe“ gilt nur für den gierigen Stapel**, nicht für den festen Pop-Stack. Die erste Fassung sagte, der größte Wagen stehe nach einem Durchlauf hinten; das stimmt beim gierigen Stapel, beim festen Pop-Stack nicht ((3, 1, 2) wird zu (1, 3, 2)).
  Für den festen Pop-Stack ist n − 1 in der Aufzählung für n ≤ 9 gemessen und erreicht (B4), ein Beweis steht hier nicht (`test_nach_einem_gierigen_durchlauf_steht_der_groesste_wagen_hinten_beim_festen_nicht_immer`).
* **Die erste Vermutung ⌈n/2⌉ für die größte freie Durchlaufzahl ist falsch** (B4): sie gilt bis n = 8 und bricht bei n = 9. Das ist ein Beispiel für eine Aussage, die ein kleines n täuschte.
* **Das Beispiel (3, 5, 2, 4, 1) gehört dem gierigen Stapel**, nicht dem Pop-Stack (B8); der kleinste Zeuge für den festen Pop-Stack ist (4, 1, 3, 5, 2).
* **Die erste Rechnung (frühere Messung) ist im Bau exakt reproduziert** worden: Zählreihen, Verteilungen, Klasse-Test, Bild und beide Ströme des Ankunftsmodells stimmen ziffergenau mit der früheren Messung überein (neu geschriebener Code, anderer Rechenweg: numpy bei der Erzeugung, reines Python in der App).
  Geändert hat sich nur die Darstellung: Anteile unter 1 % werden mit zwei Stellen gezeigt (0,58 % statt 0,6 %). Die frühere Messung nannte für den Unterschied der beiden Ströme „höchstens 0,10“ und „bis zu 3,6 Prozentpunkte“ (aus gerundeten Tabellenwerten); exakt sind es 0,103 und 3,65 (B11).
* **Die Zahlen der freien Leerung sind eigene Nachrechnung** in diesem Modell (Aufzählung aller n! Folgen bis n = 9); für n ≥ 10 sind Maximum und Zählung nicht gemessen.

## Ehrliche Grenzen

* **Modell, nicht Fall:** das Ankunftsmodell V ist ausgedacht und kennt nur die Rangfolge der Abfahrten; die Zahlen aus Experiment 5 gelten bei diesem D und n, nicht für einen echten Betrieb. Zwei Ströme mit je 2 000 Folgen sind Bänder: Mittelwerte weichen um höchstens 0,103, Anteile um bis zu 3,65 Prozentpunkte ab (B11).
* **Alle Wagen verschieden:** mit Gleichständen (Zielgruppen) ist nichts gemessen.
* **n ≤ 9:** die Aufzählung endet bei n = 9; „freie Leerung braucht nie mehr als 4 Durchläufe“ ist nur für n ≤ 9 gemessen. „Frei ist eine Klasse“ ist 0 Verletzungen für k = 1, 2, 3 und n = 3 … 9 plus ein Beweis für Blockumkehrungen, für alle n und k: beim Streichen eines Wagens bleibt jeder Block ein zusammenhängender Block (nur kürzer oder leer), und Umkehren und Streichen lassen sich vertauschen; die gestrichene Folge erreicht die sortierte Folge also in höchstens ebenso vielen Durchläufen. Als Aussage über „k Pop-Stacks in Reihe“ bleibt es eine eigene Überlegung (nächster Punkt).
* **Die freie Leerung als „k Pop-Stacks in Reihe“** ist eine eigene Überlegung. Eine Literaturaussage über Pop-Stacks in Reihe (nur aus zweiter Hand bekannt, nicht gelesen) passt nicht zu dieser Lesart: nach ihr bleiben bei unbeschränkt vielen Pop-Stacks Folgen unsortierbar, hier ist jede Folge in höchstens n − 1 festen
  Durchläufen sortiert. Die Ursache ist nicht geklärt; die Aussage wird hier nicht verwendet.
* **Die Muster-Beschreibung von West-2** (B9) ist nur aus zweiter Hand gelesen und mit eigener Rechnung bestätigt (n ≤ 8); die Zählformel für zwei Durchläufe durch den gierigen Stapel stammt von Zeilberger, nur über Bóna gelesen.
* **Zahlengleichheit mit der OEIS** ist kein Beleg dafür, dass der Eintrag dieselbe Maschine meint.
* **Mit echtem Mausklick im Browser** ist nur die Oberfläche geprüft, die AppTest erreicht; die Abbildungen sind Plotly mit gesperrten Achsen.

## Verifikation

* **Kern:** feste Maschinen und freie Leerung gegen Handrechnung an der Mini-Instanz (3, 5, 2, 4, 1) und an n = 4 (alle 24 Folgen von Hand); Randfälle (n = 1, n = 2, sortierte Folge, Umkehrfolge, ungültige Eingaben, Obergrenze n = 9).
* **Orakel** (`tests/test_oracle_mehrere_durchlaeufe.py`, anderer Rechenweg): feste Durchläufe gegen eine Maschine mit expliziten Push/Pop-Konfigurationen und gegen die Rekursion s(L n R) = s(L) s(R) n; freie Leerung auf drei Wegen (Rückwärts-Breitensuche, Vorwärtssuche über die Ausgaben der Maschine,
  Treffen in der Mitte); Zählreihen gegen geschlossene Formeln und die Literaturreihen; Muster-Beschreibungen; alle n! Folgen für n ≤ 7 live, n = 8 als langsamer Test.
* **Eigenschaften** (`tests/test_eigenschaften_mehrere_durchlaeufe.py`): sortierte Folge ist Fixpunkt, Konstante addieren ändert nichts, frei nie schlechter als fest, Mengen wachsen mit k, Streichen erhöht die freie Durchlaufzahl nie, Zählschranke, Modell nahe am exakten Mittel.
* **Claims:** jede Zahl der Befunde in `tests/test_claims.py`; **Verdikte** je Zweig und je Preset in `tests/test_verdicts.py` und `tests/test_presets.py`; **Oberfläche:** AppTest-Rauchtest, Layout (Schnellstart oben in der Seitenleiste, fester Kopf, aktives Preset hervorgehoben, jede Änderung eines Reglers hebt die Markierung auf), Footer, Laufzeit-Importe.
* **Tests:** 194 Tests (`pytest tests/`), davon 3 mit der Marke `slow`.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: fünf Experimente, Annahmen, Formeln |
| `mdl_constants.py` | Regler-Grenzen, Werte von D, Farben, Presets |
| `mdl_machines.py` | feste Maschinen: Pop-Stack und gieriger Stapel, Verlauf, Spur, Durchlaufzahl |
| `mdl_free.py` | Pop-Stack mit freier Leerung: Zerlegungen, Blockumkehr, Treffen in der Mitte |
| `mdl_tables.py` | vorgerechnete Tabellen laden, Prüfsumme, Zugriff |
| `mdl_model.py` | Ankunftsmodell V, Kennzahlen aus der Verteilung |
| `mdl_rng.py` | SplitMix64 (geprüfte Vorlage, unverändert kopiert) |
| `mdl_evaluation.py` | Einstellungen, Eingabeprüfung, Experimente, Verdikte als reine Funktionen |
| `mdl_presets.py` | Permalink, Presets (Schnellstart in der Seitenleiste), Zufalls-Seed-Button, gezogene Züge |
| `mdl_layout.py` | fester Kopf (Stylesheet) |
| `mdl_texts.py` | Einleitung, Erklärung, Annahmen, Formeln |
| `mdl_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `data/mdl_tables.json`, `data/mdl_frei_n9.bin` | vorgerechnete Aufzählung (Verteilungen, Klasse-Test, Bild, Ankunftsmodell), freie Durchlaufzahl aller 362 880 Folgen mit n = 9 |
| `tools/mdl_make_tables.py` | erzeugt und prüft (`--check`, `--full`) die Tabellen |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `requirements-dev.txt` | Laufzeit plus pytest und numpy (Orakel und Erzeugung der Tabellen) |
| `tests/` | Handwerte, Orakel, Eigenschaften, Tabellen, Modell, Claims, Verdikte, Presets, Layout, AppTest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

* **Gleichstände und Zielgruppen** (Wagen derselben Gruppe, Ziel „Gruppen zusammenhängend“): gehören zu Durchläufen mit mehreren Gleisen ([`ablaufberg-demo`](https://github.com/sebastian-hanisch/ablaufberg-demo)).
* **Freie Leerung für n ≥ 10** und die Suche der freien Zählreihe in der OEIS: nicht gemessen bzw. nicht gesucht.
* **Jeder Durchlauf ein freier Stapel** (West-k mit freier Leerung) ist dasselbe wie k Stapel in Serie: dazu [`zwei-stapel-serie-demo`](https://github.com/sebastian-hanisch/zwei-stapel-serie-demo).
* **Catalan-Zahlen, Muster-Klassen und Wachstumsraten** werden nachgerechnet, nicht hergeleitet; Herleitungen stehen in den Erklärseiten zum Abzählen auf der Website.
* **Rationale erzeugende Funktionen** der Pop-Durchläufe (Claesson/Guðmundsson, k ≤ 6): nicht nachgerechnet, nur als Quellenaussage erwähnt.
* **PDF-Export:** keiner.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit und Plotly.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
