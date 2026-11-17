"""Orakel-Tests: die Maschinen und Zählungen gegen unabhängige Rechenwege (ORACLE-PLAYBOOK §5, §6; DEMO-PLAYBOOK §12).

Anderer Rechenweg als die App (`mdl_machines.py`, `mdl_free.py`, `mdl_tables.py`):

* (a) POP und WEST gegen eine **Maschine mit Push/Pop-Konfigurationen** (Rest der Eingabe, Stapel, Ausgabe; alle Wege durchsucht, n ≤ 6): die Ausgabe des Rezepts ist eine der Ausgaben der
  Maschine; der feste Pop-Durchlauf gegen die Umkehrung der absteigenden Läufe über Listen, der gierige Stapel gegen die Rekursion s(L n R) = s(L) s(R) n der West-Abbildung
  (Lemma 1.2 bei Bóna 2003, nach Quellenbericht; hier als Definition gegen den Stapel-Code geprüft).
* (b) Zählreihen gegen **geschlossene Formeln** (2^(n−1), Catalan, 2(3n)!/((n+1)!(2n+1)!)) und gegen **Literaturwerte** der OEIS-Einträge A224232 (zwei Pop-Durchläufe), A293774 (drei), A293775 (vier),
  A134664 (drei Durchläufe durch den gierigen Stapel): Zahlen so aus den Einträgen gelesen (Zahlengleichheit der Reihen, **kein Beleg**, dass der Eintrag diese Maschine meint; A224232 nennt im Namen nur die Rekursion).
* (c) Freie Leerung auf **drei Wegen**: Rückwärts-Breitensuche über Blockumkehrungen, Vorwärts-Breitensuche über die Ausgaben der Pop-Stack-Maschine (Positionsordnungen aus Konfigurationen, n ≤ 5 alle,
  n = 6 Stichprobe) und Treffen in der Mitte (die App; n ≤ 7 alle, n = 8 und 9 Stichproben gegen numpy bzw. die Byte-Tabelle).
* (d) West-2 gegen die **Muster-Beschreibung** Av(2341, 3\\bar{5}241) als Menge (n ≤ 7, n = 8 langsam; Beschreibung nach Claesson/Guðmundsson laut Quellenbericht, Zweitquelle), ein Pop-Durchlauf gegen Av(231, 312).
* (e) alle n! Folgen für n ≤ 7 live, n = 8 als langsamer Test, n = 9 nur über die Erzeugung der Tabelle (`tools/mdl_make_tables.py --check`).
"""

import itertools
import math
from math import comb, factorial

import pytest

import mdl_free as F
import mdl_machines as M
import mdl_tables as T
from conftest import alle_folgen

# Literaturwerte (OEIS), n = 1 … 9; Quelle und Grenzen siehe Modulkopf
A224232 = [1, 2, 6, 16, 42, 112, 298, 792, 2106]
A293774 = [1, 2, 6, 24, 88, 303, 1033, 3544, 12220]
A293775 = [1, 2, 6, 24, 120, 565, 2473, 10468, 44148]
A134664 = [1, 2, 6, 24, 114, 606, 3494, 21426, 137901]
A307030_BILD = [1, 1, 3, 11, 49, 263, 1653, 11877]   # Zahl der verschiedenen Ausgaben eines Pop-Durchlaufs (Bild), n = 1 … 8, laut Quellenbericht (Zahlengleichheit)


# --- (a) Maschinen mit expliziten Konfigurationen -------------------------------------------------------------------------------------------

def stapel_ausgaben(p):
    """Alle Ausgaben eines gewöhnlichen Stapels: Konfiguration (Rest, Stapel, Ausgabe), jeder Weg aus „einlagern“ und „eine Spitze ausgeben“."""
    erg = set()

    def rek(rest, stapel, aus):
        if not rest and not stapel:
            erg.add(aus)
            return
        if rest:
            rek(rest[1:], stapel + (rest[0],), aus)
        if stapel:
            rek(rest, stapel[:-1], aus + (stapel[-1],))

    rek(tuple(p), (), ())
    return erg


def pop_stack_ausgaben(p):
    """Alle Ausgaben des Pop-Stacks mit freier Leerung: jederzeit darf der ganze Stapel ausgegeben werden (obere zuerst)."""
    erg = set()

    def rek(rest, stapel, aus):
        if not rest and not stapel:
            erg.add(aus)
            return
        if rest:
            rek(rest[1:], stapel + (rest[0],), aus)
        if stapel:
            rek(rest, (), aus + stapel[::-1])

    rek(tuple(p), (), ())
    return erg


def pop_ueber_listen(p):
    """Fester Pop-Durchlauf als Umkehrung der maximal absteigenden Läufe, über Listen statt über den Stapel."""
    laeufe = []
    for x in p:
        if laeufe and laeufe[-1][-1] > x:
            laeufe[-1].append(x)
        else:
            laeufe.append([x])
    return tuple(x for lauf in laeufe for x in reversed(lauf))


def west_rekursiv(p):
    """West-Abbildung über die Rekursion s(L n R) = s(L) s(R) n."""
    if not p:
        return ()
    i = p.index(max(p))
    return west_rekursiv(p[:i]) + west_rekursiv(p[i + 1:]) + (p[i],)


@pytest.mark.parametrize("n", range(1, 7))
def test_feste_durchlaeufe_gegen_die_konfigurationsmaschine(n):
    for p in alle_folgen(n):
        ausgaben = pop_stack_ausgaben(p)
        assert M.pop_durchlauf(p) in ausgaben
        assert pop_ueber_listen(p) == M.pop_durchlauf(p)
        assert M.west_durchlauf(p) in stapel_ausgaben(p)
        assert west_rekursiv(p) == M.west_durchlauf(p)


@pytest.mark.parametrize("n", range(1, 7))
def test_zahl_der_ausgaben_des_freien_pop_stacks(n):
    assert len(pop_stack_ausgaben(tuple(range(1, n + 1)))) == 2 ** (n - 1)
    assert len(stapel_ausgaben(tuple(range(1, n + 1)))) == math.comb(2 * n, n) // (n + 1)       # Catalan: Ausgaben eines Stapels bei Eingabe 1 … n


def test_freie_ausgaben_gleich_blockumkehrungen():
    for n in range(1, 7):
        for p in alle_folgen(n)[::5]:
            assert pop_stack_ausgaben(p) == {F.blockumkehr(p, z) for z in F.zerlegungen(n)}


# --- (b) Formeln und Literaturwerte ----------------------------------------------------------------------------------------------------------

def folgen_in_hoechstens(maschine, n, k):
    return sum(1 for p in alle_folgen(n) if M.durchlaufzahl(p, maschine) <= k)


def test_formeln_fuer_ein_und_zwei_durchlaeufe_aus_der_tabelle():
    for n in range(1, 10):
        assert T.kumuliert("pop", n, 1) == 2 ** (n - 1) == T.kumuliert("frei", n, 1)
        assert T.kumuliert("west", n, 1) == comb(2 * n, n) // (n + 1)
        assert T.kumuliert("west", n, 2) == 2 * factorial(3 * n) // (factorial(n + 1) * factorial(2 * n + 1))


def test_literaturreihen_aus_der_tabelle():
    for n in range(1, 10):
        assert T.kumuliert("pop", n, 2) == A224232[n - 1]
        assert T.kumuliert("pop", n, 3) == A293774[n - 1]
        assert T.kumuliert("pop", n, 4) == A293775[n - 1]
        assert T.kumuliert("west", n, 3) == A134664[n - 1]


def test_rekursion_des_eintrags_a224232_gilt_fuer_die_eigenen_zahlen():
    """Rekursion aus dem Eintragsnamen: a(n) = 2(a(n−1) + a(n−3)) + a(n−2) ab n = 4; Gleichheit der Zahlen, kein Beweis."""
    a = [1] + [T.kumuliert("pop", n, 2) for n in range(1, 10)]
    assert all(a[n] == 2 * (a[n - 1] + a[n - 3]) + a[n - 2] for n in range(4, 10))


@pytest.mark.parametrize("n", range(1, 8))
def test_live_zaehlung_gleich_tabelle_und_literatur(n):
    """Live aufgezählt (reines Python, anderer Weg als die numpy-Erzeugung der Tabelle) gleich der Tabelle."""
    for m, ks in (("pop", (1, 2, 3, 4)), ("west", (1, 2, 3))):
        d = [M.durchlaufzahl(p, m) for p in alle_folgen(n)]
        h = [d.count(j) for j in range(max(d) + 1)]
        assert h == T.verteilung(m, n)
        for k in ks:
            assert T.kumuliert(m, n, k) == sum(h[: k + 1])


# --- (c) freie Leerung auf drei Wegen ----------------------------------------------------------------------------------------------------------

def breitensuche_rueckwaerts(n):
    """Abstand jeder Folge von der sortierten Folge über Blockumkehrungen (jede ist ihre eigene Umkehrung)."""
    ident = tuple(range(1, n + 1))
    zs = F.zerlegungen(n)
    dist = {ident: 0}
    front = [ident]
    d = 0
    while front:
        d += 1
        neu = []
        for p in front:
            for z in zs:
                q = F.blockumkehr(p, z)
                if q not in dist:
                    dist[q] = d
                    neu.append(q)
        front = neu
    return dist


@pytest.mark.parametrize("n", range(2, 8))
def test_freie_durchlaufzahl_treffen_in_der_mitte_gleich_breitensuche(n):
    dist = breitensuche_rueckwaerts(n)
    assert len(dist) == factorial(n)                                      # jede Folge ist frei sortierbar
    assert all(F.frei_durchlaufzahl(p) == dist[p] for p in alle_folgen(n))
    h = [list(dist.values()).count(j) for j in range(max(dist.values()) + 1)]
    assert h == T.verteilung("frei", n)


@pytest.mark.parametrize("n", range(2, 6))
def test_freie_durchlaufzahl_vorwaerts_ueber_die_maschine(n):
    """Positionsordnungen der Pop-Stack-Maschine aus Konfigurationen; Vorwärts-Breitensuche von jeder Folge bis zur sortierten."""
    ident = tuple(range(1, n + 1))
    ordnungen = sorted(pop_stack_ausgaben(ident))
    for p in alle_folgen(n):
        gesehen, front, d = {p}, [p], 0
        while ident not in gesehen:
            d += 1
            neu = []
            for q in front:
                for o in ordnungen:
                    r = tuple(q[k - 1] for k in o)
                    if r not in gesehen:
                        gesehen.add(r)
                        neu.append(r)
            front = neu
        assert F.frei_durchlaufzahl(p) == d


def test_freie_durchlaufzahl_vorwaerts_n6_stichprobe():
    ident = tuple(range(1, 7))
    ordnungen = sorted(pop_stack_ausgaben(ident))
    for p in alle_folgen(6)[::37]:
        gesehen, front, d = {p}, [p], 0
        while ident not in gesehen:
            d += 1
            neu = []
            for q in front:
                for o in ordnungen:
                    r = tuple(q[k - 1] for k in o)
                    if r not in gesehen:
                        gesehen.add(r)
                        neu.append(r)
            front = neu
        assert F.frei_durchlaufzahl(p) == d


def test_freie_durchlaufzahl_n9_stichprobe_gegen_die_byte_tabelle():
    from mdl_rng import SplitMix64
    rng = SplitMix64(7777)
    for _ in range(300):
        items = list(range(1, 10))
        rng.shuffle(items)
        p = tuple(items)
        assert F.frei_durchlaufzahl(p) == T.frei_n9(p)


# --- (d) Muster-Beschreibungen ---------------------------------------------------------------------------------------------------------------

def enthaelt(p, muster):
    L = len(muster)
    for idx in itertools.combinations(range(len(p)), L):
        w = [p[i] for i in idx]
        if all((w[a] < w[b]) == (muster[a] < muster[b]) for a in range(L) for b in range(a + 1, L)):
            return True
    return False


def west2_laut_muster(p):
    """West-2 = Av(2341, 3\\bar{5}241): kein 2341, und jedes 3241 liegt in einem 35241 (ein Wagen größer als die 4 steht zwischen 3 und 2)."""
    if enthaelt(p, (2, 3, 4, 1)):
        return False
    for i, j, k, l in itertools.combinations(range(len(p)), 4):
        a, b, c, d = p[i], p[j], p[k], p[l]
        if d < b < a < c and not any(p[m] > c for m in range(i + 1, j)):
            return False
    return True


@pytest.mark.parametrize("n", range(3, 8))
def test_west2_gleich_muster_beschreibung_und_pop_eins_gleich_av_231_312(n):
    for p in alle_folgen(n):
        assert (M.durchlaufzahl(p, M.WEST) <= 2) == west2_laut_muster(p)
        assert (M.durchlaufzahl(p, M.POP) <= 1) == (not enthaelt(p, (2, 3, 1)) and not enthaelt(p, (3, 1, 2)))


# --- (e) n = 8 langsam ------------------------------------------------------------------------------------------------------------------------

@pytest.mark.slow
def test_n8_aufzaehlung_gegen_tabelle_und_muster():
    folgen = alle_folgen(8)
    for m in ("pop", "west"):
        d = [M.durchlaufzahl(p, m) for p in folgen]
        assert [d.count(j) for j in range(max(d) + 1)] == T.verteilung(m, 8)
    assert sum(1 for p in folgen if west2_laut_muster(p)) == T.kumuliert("west", 8, 2) == 9614
    assert all(west2_laut_muster(p) == (M.durchlaufzahl(p, M.WEST) <= 2) for p in folgen)


@pytest.mark.slow
def test_n8_frei_treffen_in_der_mitte_gegen_numpy_und_tabelle():
    pytest.importorskip("numpy")
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
    import mdl_make_tables as G
    dist = G.dist_frei(8)
    assert [int((dist == j).sum()) for j in range(int(dist.max()) + 1)] == T.verteilung("frei", 8)
    from mdl_rng import SplitMix64
    rng = SplitMix64(7777)
    for _ in range(300):
        items = list(range(1, 9))
        rng.shuffle(items)
        p = tuple(items)
        assert F.frei_durchlaufzahl(p) == int(dist[T.lex_rank(p)])
