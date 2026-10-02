#!/usr/bin/env bash
# Pipeline complet : vérifie l'environnement, lance les tests puis l'analyse.
# Usage : ./scripts/process_data.sh [fenetre_volatilite]
set -euo pipefail

# Racine du projet, quel que soit le répertoire d'appel.
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="$PROJECT_ROOT/.venv/bin/python"
WINDOW="${1:-20}"

if [[ ! -x "$PYTHON" ]]; then
    echo "Erreur : environnement virtuel absent. Lancez :" >&2
    echo "  python3 -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2
    exit 1
fi

if [[ ! -f "$PROJECT_ROOT/data/sample_prices.csv" ]]; then
    echo "Erreur : data/sample_prices.csv introuvable." >&2
    exit 1
fi

echo "==> Tests"
"$PYTHON" -m pytest -q "$PROJECT_ROOT/tests"

echo "==> Analyse (fenêtre = $WINDOW jours)"
"$PYTHON" "$PROJECT_ROOT/src/analysis.py" --window "$WINDOW"

echo "==> Terminé"
