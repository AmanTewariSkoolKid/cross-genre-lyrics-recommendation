from pathlib import Path
import re
from collections import Counter

import pandas as pd
import numpy as np

REQUIRED_COLS = ["id", "title", "artist", "lyrics"]


def load_dataset(csv_path: Path) -> pd.DataFrame:
    """Load CSV into a DataFrame."""
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Processed CSV not found at {csv_path}")
    return pd.read_csv(csv_path, low_memory=False)


def validate_columns(df: pd.DataFrame) -> None:
    """Ensure required columns exist in the DataFrame."""
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise KeyError(f"Missing required columns: {missing}")


def _count_words(text: str) -> int:
    """Count words by splitting on whitespace and ignoring empty tokens."""
    if not isinstance(text, str):
        return 0
    # find all non-whitespace tokens
    tokens = re.findall(r"\S+", text)
    return len(tokens)


def prepare_word_count(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows with missing lyrics and add `_word_count` column.

    Returns a new DataFrame (copy) with `_word_count` retained for later features.
    """
    df = df.copy()
    df = df[df["lyrics"].notna()].copy()
    df["_word_count"] = df["lyrics"].map(_count_words)
    return df


def print_diagnostics(df: pd.DataFrame) -> None:
    """Print basic diagnostics required by this step."""
    total = len(df)
    # use numpy to compute mean safely (will be float)
    avg = int(round(np.nanmean(df["_word_count"]))) if total > 0 else 0
    mn = int(np.nanmin(df["_word_count"])) if total > 0 else 0
    mx = int(np.nanmax(df["_word_count"])) if total > 0 else 0

    print(f"Songs loaded: {total}")
    print(f"Average word count: {avg}")
    print(f"Min word count: {mn}")
    print(f"Max word count: {mx}")


# Placeholder functions for later feature extraction steps (kept modular)
def extract_lexical_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute lexical features per song and return a new DataFrame.

    Adds the following columns without modifying `lyrics` or `_word_count`:
    - `unique_words`
    - `lexical_diversity` (unique_words / _word_count)
    - `top_word_frequency`
    - `repetition_score` (top_word_frequency / _word_count)
    """
    df = df.copy()
    # Tokenize by lowercasing and extracting alphanumeric tokens (keeps apostrophes)
    tokens = df["lyrics"].str.lower().str.findall(r"[a-z0-9']+")

    # Cache tokens for reuse by downstream feature extractors
    df["_tokens"] = tokens

    # unique_words
    df["unique_words"] = df["_tokens"].map(lambda toks: len(set(toks)) if isinstance(toks, list) else 0).astype(int)

    # top_word_frequency using Counter; safe for non-list or empty inputs
    def _top_freq(toks):
        if not isinstance(toks, list) or len(toks) == 0:
            return 0
        return Counter(toks).most_common(1)[0][1]

    df["top_word_frequency"] = df["_tokens"].map(_top_freq).astype(int)

    # Avoid division by zero by treating zero word counts as NaN then filling with 0
    total_words = df["_word_count"].replace(0, np.nan)
    df["lexical_diversity"] = (df["unique_words"] / total_words).fillna(0)
    df["repetition_score"] = (df["top_word_frequency"] / total_words).fillna(0)

    # Diagnostics
    avg_lexical_div = df["lexical_diversity"].mean() if len(df) > 0 else 0.0
    avg_repetition = df["repetition_score"].mean() if len(df) > 0 else 0.0
    avg_unique = int(round(df["unique_words"].mean())) if len(df) > 0 else 0

    print(f"Average lexical diversity: {avg_lexical_div:.3f}")
    print(f"Average repetition score: {avg_repetition:.3f}")
    print(f"Average unique words: {avg_unique}")

    return df


def extract_structural_features(df: pd.DataFrame) -> pd.DataFrame:
    raise NotImplementedError("extract_structural_features will be implemented later")


def extract_emotion_features(df: pd.DataFrame) -> pd.DataFrame:
    raise NotImplementedError("extract_emotion_features will be implemented later")


def main(csv_path: str | Path = "data/processed/spotify_clean.csv") -> pd.DataFrame:
    """Load, validate, prepare `_word_count`, and print diagnostics.

    Returns the prepared DataFrame (with `_word_count`) for downstream steps.
    """
    path = Path(csv_path)
    df = load_dataset(path)
    validate_columns(df)
    df_prepared = prepare_word_count(df)
    print_diagnostics(df_prepared)

    # Compute lexical features now and return the augmented DataFrame
    df_features = extract_lexical_features(df_prepared)
    return df_features


if __name__ == "__main__":
    main()
