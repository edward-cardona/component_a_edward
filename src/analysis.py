"""Analyse de prix d'actions : rendements journaliers et volatilité glissante.

Usage :
    python src/analysis.py [--window 20]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # backend sans affichage : fonctionne en script / CI
import matplotlib.pyplot as plt
import pandas as pd

# Chemins ancrés sur l'emplacement du fichier, pas sur le répertoire courant :
# le script fonctionne quel que soit l'endroit d'où on le lance.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "sample_prices.csv"
OUTPUT_PATH = PROJECT_ROOT / "outputs" / "plot.png"

REQUIRED_COLUMNS = {"Date", "Close"}


def load_prices(path: Path = DATA_PATH) -> pd.DataFrame:
    """Charge un CSV (Date, Close), trié par date et indexé par Date."""
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")

    df = pd.read_csv(path, parse_dates=["Date"])
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes : {sorted(missing)}")

    return df.sort_values("Date").set_index("Date")


def compute_daily_returns(prices: pd.Series) -> pd.Series:
    """Rendements journaliers simples : (P_t / P_{t-1}) - 1."""
    return prices.pct_change().dropna().rename("daily_return")


def compute_rolling_volatility(returns: pd.Series, window: int = 20) -> pd.Series:
    """Écart-type glissant des rendements sur `window` jours."""
    if window < 2:
        raise ValueError("La fenêtre doit être >= 2 pour calculer un écart-type.")
    return returns.rolling(window=window).std().rename("rolling_volatility")


def plot_analysis(
    prices: pd.Series,
    returns: pd.Series,
    volatility: pd.Series,
    output_path: Path = OUTPUT_PATH,
) -> Path:
    """Trace prix, rendements et volatilité sur trois panneaux et sauvegarde le PNG."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
    axes[0].plot(prices.index, prices, color="tab:blue")
    axes[0].set_ylabel("Prix de clôture")
    axes[0].set_title("Analyse du titre")

    axes[1].bar(returns.index, returns, color="tab:gray", width=1.0)
    axes[1].axhline(0, color="black", linewidth=0.8)
    axes[1].set_ylabel("Rendement journalier")

    axes[2].plot(volatility.index, volatility, color="tab:red")
    axes[2].set_ylabel(f"Volatilité ({volatility.name})")
    axes[2].set_xlabel("Date")

    for ax in axes:
        ax.grid(alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--window", type=int, default=20, help="fenêtre de volatilité (jours)")
    args = parser.parse_args(argv)

    prices = load_prices()["Close"]
    returns = compute_daily_returns(prices)
    volatility = compute_rolling_volatility(returns, window=args.window)
    out = plot_analysis(prices, returns, volatility)

    print(f"{len(prices)} prix chargés, {len(returns)} rendements calculés.")
    print(f"Rendement moyen : {returns.mean():.4%} | volatilité finale : {volatility.iloc[-1]:.4%}")
    print(f"Graphique sauvegardé : {out.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
