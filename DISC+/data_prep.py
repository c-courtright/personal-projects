# loads and cleans raw trackman data

import pathlib
import pandas as pd

PITCH_CALL_MAP = {
    "StrikeCalled": "Strike",
    "StrikeSwinging": "Swing",
    "FoulBall": "Swing",
    "FoulBallNotFieldable": "Swing",
    "FoulBallFieldable": "Swing",
    "InPlay": "Swing",
    "BallCalled": "Ball",
    "BallinDirt": "Ball",
}

SWING_RESULT_MAP = {
    "StrikeSwinging": "Whiff",
    "FoulBall": "Contact",
    "FoulBallNotFieldable": "Contact",
    "FoulBallFieldable": "Contact",
    "InPlay": "Contact",
}

EXCLUDED_PITCH_CALLS = ["BallIntentional", "Undefined"]

def _format_batter_name(name:str) -> str:
    last, first = name.split(",", 1)
    return f"{first.strip()} {last.strip()}"


def load_pitches(games_dir:str = "games") -> pd.DataFrame:
    files = sorted(pathlib.Path(games_dir).rglob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found under '{games_dir}'")
    return pd.concat([pd.read_csv(f) for f in files], ignore_index=True)


def load_stats(stats_dir:str = "playerstats/0801") -> pd.DataFrame:
    files = sorted(pathlib.Path(stats_dir).rglob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found under '{stats_dir}'")
    stats = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    return stats.rename(columns={"Name": "Batter"})

def clean_pitches(pitches:pd.DataFrame) -> pd.DataFrame:
    pitches = pitches.dropna(subset=['PlateLocSide', 'PlateLocHeight']).copy()

    pitches['Batter'] = pitches['Batter'].apply(_format_batter_name)

    pitches['PlateLocSide'] = pitches['PlateLocSide']*12 + 9
    pitches['PlateLocHeight'] = pitches['PlateLocHeight']*12 - 18

    pitches = pitches[~pitches['PitchCall'].isin(EXCLUDED_PITCH_CALLS)].copy()

    pitches['Group'] = pitches['PitchCall'].map(PITCH_CALL_MAP)
    pitches['SwingResult'] = pitches['PitchCall'].map(SWING_RESULT_MAP)

    if 'Date' in pitches.columns: pitches['Date'] = pd.to_datetime(pitches['Date'])

    return pitches