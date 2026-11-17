"""Längere Texte der App (Einleitung, Erklärung, Annahmen, Formeln). Alle Zahlen stehen in tests/test_claims.py."""

NACHBAR = "https://github.com/sebastian-hanisch/"

EINLEITUNG = """
Ein Zug aus n Wagen soll nach seinem **Abholrang** sortiert werden (kleinster Rang zuerst). Die Maschine, ein einziger Behälter, sieht den Zug aber nur einmal je **Durchlauf**; ihre Ausgabe ist die Eingabe des nächsten Durchlaufs.
Gefragt wird deshalb nicht, **ob** ein Zug sortiert wird, sondern **wie viele Durchläufe** er braucht und wie viele Züge in höchstens k Durchläufen fertig sind. Die Antwort hängt daran, **was „k Durchläufe“ überhaupt meint**:
Drei Maschinen mit je einem Behälter geben schon bei n = 5 Wagen und k = 2 die Zahlen **42, 91 und 102** von 120 Folgen.

Die Züge der Experimente 1 und 5 stammen aus einem **ausgedachten Ankunftsmodell**: ein Modell, **keine reale Ankunftsfolge** und kein Fall aus der Praxis. Alle Zahlen gelten für diese Maschinen, alle Wagen verschieden (keine Gleichstände),
Zähleinheit Folgen (Aufzählung aller n! Folgen bis n = 9) bzw. Zufallsfolgen (Ankunftsmodell).

Weiter unten: fünf Experimente, der Abschnitt **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""

SO_FUNKTIONIERT = """
1. **Ein Durchlauf:** Der Zug fährt einmal vollständig durch den Behälter. Die Ausgabe ist die Eingabe des nächsten Durchlaufs. Die **Durchlaufzahl** einer Folge ist die kleinste Zahl von Durchläufen, nach der sie aufsteigend sortiert ist (die sortierte Folge braucht 0); „in k Durchläufen sortierbar“ heißt **höchstens k**.
2. **Drei Maschinen, je ein Behälter:** Der **Pop-Stack mit festem Rezept** leert den Stapel ganz (obere Wagen zuerst), sobald der nächste Wagen größer ist als die Spitze; sonst stapelt er. Der **gierige Stapel** gibt aus, solange die Spitze kleiner ist als der nächste Wagen, und stapelt dann.
   Beim **Pop-Stack mit freier Leerung** darf der Bediener jederzeit leeren: ein Durchlauf ist eine beliebige Zerlegung des Zugs in zusammenhängende Blöcke, jeder Block wird umgekehrt.
3. **Warum die Wahl zählt:** „k Durchläufe“ kann den festen Pop-Stack meinen, den gierigen Stapel oder die freie Leerung (k Pop-Durchläufe mit freier Leerung; die Gleichsetzung mit k Pop-Stacks in Reihe ist eine eigene, nicht an der Literatur geprüfte Überlegung). Die drei geben für k ≥ 2 verschiedene Zahlen; die Experimente 2 bis 4 zählen sie nebeneinander.
"""

KONVENTIONEN = """
| Begriff | Bedeutung in dieser Demo |
|---|---|
| Ziel | die aufsteigende Folge 1, 2, …, n (kleinster Abholrang zuerst) |
| Eingabe | die Folge der Ränge in Ankunftsreihenfolge, alle Wagen verschieden |
| Durchlauf | der Zug fährt einmal durch **einen** Behälter; die Ausgabe ist die Eingabe des nächsten Durchlaufs |
| Durchlaufzahl | kleinste Zahl von Durchläufen bis zur sortierten Folge (sortiert: 0) |
| POP | Pop-Stack, festes Rezept: leeren, sobald der nächste Wagen größer ist als die Spitze |
| WEST | gieriger Stapel: ausgeben, solange die Spitze kleiner ist als der nächste Wagen |
| FREI | Pop-Stack mit freier Leerung: beliebige Zerlegung in Blöcke, jeder Block umgekehrt |
| Ein Durchlauf sortiert | POP: genau die Folgen ohne die Muster 231 und 312; WEST: genau die ohne 231 |
"""

GRENZEN = f"""
| Annahme | Was passiert, wenn sie verletzt ist | Wie es weitergeht |
|---|---|---|
| **Alle Wagen verschieden** | Mit Gleichständen (Wagen derselben Zielgruppe) ist hier nichts gemessen. Durchläufe mit Gruppen und mehreren Gleisen behandelt die [`ablaufberg-demo`]({NACHBAR}ablaufberg-demo); ihr „Durchgang“ ist etwas anderes als der „Durchlauf“ hier. | dort |
| **Ein Behälter, mehrere Durchläufe** | Zwei Durchläufe durch einen gierigen Stapel sind nicht zwei Stapel in Serie: bei n = 4 sortiert der gierige Stapel in zwei Durchläufen 22 von 24 Folgen. | Nachbar-Demo [`zwei-stapel-serie-demo`]({NACHBAR}zwei-stapel-serie-demo) |
| **Feste Rezepte** | „Höchstens k Durchläufe“ ist beim festen Pop-Stack und beim gierigen Stapel keine Klasse unter Streichen eines Wagens (Experiment 4); bei freier Leerung ist es für n ≤ 9 eine. | Muster-Klassen: Erklärseiten zum Abzählen auf der Website |
| **n ≤ 9** | Bei freier Leerung ist das Maximum der Durchlaufzahl für n ≥ 10 nicht gemessen; die App rechnet freie Durchläufe nur bis n = 9. | – |
| **Ankunftsmodell V** | Ausgedacht: nur die Rangfolge der Abfahrten, keine Zeiten, keine Gleise, keine reale Ankunftsfolge. Die Zahlen gelten bei diesem D und n. | – |
"""

FORMELN = r"""
**Lesehilfe.** Gegeben ist eine Folge $\pi = (\pi_1, \dots, \pi_n)$ der Ränge $1, \dots, n$, jeder genau einmal. Gesucht ist die Zahl der Durchläufe, nach der die Folge aufsteigend sortiert ist, und die Zahl der Folgen, die das in höchstens $k$ Durchläufen schaffen.

| Symbol | Bedeutung |
|---|---|
| $\pi$ | eine Folge der Ränge $1, \dots, n$ in Ankunftsreihenfolge |
| $\mathrm{id}$ | die sortierte Folge $(1, 2, \dots, n)$ |
| $P$, $W$ | ein Durchlauf des festen Pop-Stacks bzw. des gierigen Stapels |
| $B_z$ | Blockumkehr zur Zerlegung $z$ von $n$ in Blocklängen (jeder Block wird umgekehrt) |
| $d_X(\pi)$ | Durchlaufzahl: kleinstes $k$ mit $X^k(\pi) = \mathrm{id}$ |
| $S_k^X(n)$ | Menge der Folgen mit $d_X \le k$ |
| $N_k^X(n)$ | Zahl der Folgen in $S_k^X(n)$ |

**Die Maschinen.** Der feste Pop-Stack kehrt jeden maximal absteigenden Lauf von $\pi$ um. Der gierige Stapel ist die West-Abbildung; für $\pi = L\,n\,R$ (der größte Wagen $n$ trennt $L$ und $R$) gilt $W(\pi) = W(L)\,W(R)\,n$. Die freie Leerung wählt in jedem Durchlauf eine Zerlegung $z$ aus den $2^{n-1}$ möglichen und wendet $B_z$ an; die freie Durchlaufzahl ist die kleinste Zahl solcher Blockumkehrungen von $\pi$ zu $\mathrm{id}$.

**Ein Durchlauf.** $N_1^{P}(n) = 2^{n-1}$ (die Folgen ohne die Muster 231 und 312), $N_1^{W}(n) = C_n = \frac{1}{n+1}\binom{2n}{n}$ (Catalan-Zahl, die Folgen ohne 231), $N_1^{\text{frei}}(n) = 2^{n-1}$.

**Zwei Durchläufe durch den gierigen Stapel.** $N_2^{W}(n) = \frac{2\,(3n)!}{(n+1)!\,(2n+1)!}$ (Zeilberger, nach Bóna 2003, Satz 3.2).

**Obergrenze für den gierigen Stapel (Beweisskizze).** Nach einem Durchlauf steht der größte Wagen $n$ am Ende: er wird nie ausgegeben, bevor ein größerer kommt, bleibt also unten im Stapel. In jedem weiteren Durchlauf bewirkt $n$ am Ende nur das ohnehin fällige Leeren; die übrigen $n-1$ Wagen verhalten sich wie eine Folge der Länge $n-1$. Mit Induktion folgt $d_W(\pi) \le n-1$. Für den festen Pop-Stack gilt das Argument nicht (der größte Wagen steht nach einem Durchlauf nicht immer hinten, etwa bei $(3, 1, 2)$); dort ist $d_P \le n-1$ für $n \le 9$ in der Aufzählung gemessen und wird erreicht, ein Beweis steht hier nicht.

**Mittel über alle Folgen (Modell U).** $\bar d_X(n) = \frac{1}{n!} \sum_{\pi} d_X(\pi)$.

**Ankunftsmodell V.** Wagen $i$ kommt zur Zeit $i$ an und bleibt $E_i$ lang, $E_i$ exponentialverteilt mit Mittel $D$. Die Abfahrtszeit ist $T_i = i + E_i$, der Abholrang von Wagen $i$ ist der Rang von $T_i$ unter $T_1, \dots, T_n$. Für $D \to \infty$ entstehen gleichverteilte Folgen (Modell U). Das Modell ist ausgedacht und kennt nur die Rangfolge der Abfahrten.

**Quellen.** Der Pop-Operator als Umkehrung absteigender Läufe und die rationale erzeugende Funktion der in $k$ Durchläufen sortierbaren Folgen: Claesson und Guðmundsson, Enumerating permutations sortable by k passes through a pop-stack, arXiv 1710.04978 (Kopf und Abschnitt 2 gelesen). West-2 und die Zählformel: Bóna, A survey of stack-sorting disciplines, Electron. J. Combin. 9(2), 2003, #A1 (ganz gelesen); die Originale von West und Zeilberger sind nicht gelesen. Die Zahlen der Reihen zu zwei, drei und vier Pop-Durchläufen stimmen mit den OEIS-Einträgen A224232, A293774 und A293775 überein (Zahlengleichheit, kein Beleg für die Zuordnung). Die freie Leerung als $k$ Pop-Stacks in Reihe ist eine eigene Überlegung ohne gelesene Quelle.
"""
