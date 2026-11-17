"""Gemeinsame Fixtures und Marken (DEMO-PLAYBOOK §1b): die Mini-Instanz, an der jede Einheit von Hand geprüft wird, und die Marke `slow` für die Aufzählung bis n = 8."""

import itertools
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: Aufzählung aller 40 320 Folgen der Länge 8 (einige Sekunden)")


@pytest.fixture
def mini():
    """Handbeispiel: fünf Wagen mit den Abholrängen 3, 5, 2, 4, 1 in Ankunftsreihenfolge; Ziel 1, 2, 3, 4, 5."""
    return (3, 5, 2, 4, 1)


def alle_folgen(n):
    return list(itertools.permutations(range(1, n + 1)))
